import os
import math
import skimage
import numpy as np
import pandas as pd
import scipy.ndimage as ndimage
from os.path import join
from skimage import io
from skimage.restoration import denoise_tv_chambolle
from skimage.morphology import white_tophat, disk
from skimage.measure import find_contours, regionprops
from skimage.filters import gaussian, threshold_otsu, threshold_multiotsu
from skimage.exposure import equalize_adapthist
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from funcs import * 

############## Auxiliary modules ##############
def getfiles(datadir):
  ## Fn: outputs list of paths to all samples (for multi-batch analysis).
  ## datadir: path to directory with samples as subdirectories (where each sample directory contains indiv channel images).
  dirlist = []
  for d in os.listdir(datadir):
    dirpath = datadir+d+'/'
    for d2 in os.listdir(dirpath): dirlist.append({"batch_id": d, "sample_id": d2, "sample_dir": dirpath+d2+'/'}) # returns path to each sample directory, and sample_id. 
  return dirlist

def getfiles_batch(datadir):
  ## Fn: outputs list of paths to all samples (for single-batch analysis).
  ## datadir: path to directory with samples as subdirectories (where each sample directory contains indiv channel images).
  dirlist = []
  string_split = datadir.split('/')
  d = string_split[len(string_split)-1]
  for d2 in os.listdir(datadir): dirlist.append({"batch_id": d, "sample_id": d2, "sample_dir": datadir+'/'+d2+'/'}) # returns path to each sample directory, and sample_id. 
  return dirlist

def getfiles_sample(datadir):
  ## Fn: outputs list of paths to all samples (for single-sample analysis).
  ## datadir: path to directory with samples as subdirectories (where each sample directory contains indiv channel images).
  dirlist = []
  d = ''
  string_split = datadir.split('/')
  d2 = string_split[len(string_split)-1]
  dirlist.append({"batch_id": d, "sample_id": d2, "sample_dir": datadir+'/'}) # returns path to each sample directory, and sample_id. 
  return dirlist

def readimg(sampledir, filename, img_height = 7.32, img_width = 7.32):
  ## Fn: loads image, compresses and gets image metadata.
  ## Inputs:: 
  ## sampledir: path to directory of sample containing all channel images from that sample. 
  ## filename: name of the image file. 
  ## img_height: img height measurement (in mm).
  ## img_width: img height measurement (in mm).
  filepath = ''.join([sampledir,filename])
  print("loading image...")
  orgimg = io.imread(filepath)
  if len(orgimg.shape)>2: orgimg = orgimg[:,:,0]+orgimg[:,:,1]+orgimg[:,:,2]
  print("compressing image...")
  img = img_compress(orgimg) # outputs compressed original image before any pre-processing. 
  img_details = get_img_details(orgimg, compress_img = img, height = img_height, width = img_width) # outputs dictionary with image metadata.
  return img_details, img 

############## Image Processing modules ############## 
def generate_mask(img, img_details, selem_rad = 6, circularity_cutoff = 0.35, conf = 'High'):
  ## Fn: to generate mask extracting potential cell segments rid of artifacts.
  ## Inputs::
  ## img: denoised image for masking. 
  ## img_details = dictionary of image details generated using the readimg function. 
  ## selem_rad: radius of structure element. Default = 6. 
  ## circularity_cutoff: circularity threshold for elongated artifacts.
  ## conf: confidence level for intensity filtering. "Low" can be used for very clean images & passing more signal.  
  w_tophat = white_tophat(img, disk(selem_rad)) # rm bright spots that are too large. 
  contours = find_contours(w_tophat, threshold_otsu(w_tophat)) # contour detection (to identify elongated contours).
  contours_discard = [] # list to store elongated contours to rm. 
  for contour in contours:
   circ_idx, cont_area, cont_perimeter = circularity_idx(contour, img_details)
   if circ_idx < circularity_cutoff: contours_discard.append(contour)
  if len(contours_discard) > 0:
    print("removing artifacts...")
    int_mask = np.zeros_like(img, dtype='bool') # create intermediate mask to rm elongated contours. 
    for contour in contours_discard:
      int_mask[np.round(contour[:, 0]).astype('int'), np.round(contour[:, 1]).astype('int')] = 1
    int_mask = np.invert(ndimage.binary_fill_holes(int_mask))
    img_contrm = w_tophat * int_mask # image with elongated artifacts rm.
  else:
    img_contrm = w_tophat
  if conf == 'High':
    mask = img_contrm >= threshold_multiotsu(img_contrm, classes = 3)[1] # generate final mask w higher otsu thresholding.
  if conf == 'Low': 
    mask = img_contrm >= threshold_multiotsu(img_contrm, classes = 3)[0] # generate final mask w lower otsu thresholding.
  return mask

def preprocess(img, img_details, denoise_weight = 0.02, selem_rad = 6, circularity_cutoff = 0.3, conf = 'High'):
  ## Fn: preprocessing images in a single channel. 
  ## Inputs::
  ## img: already compressed image. 
  ## img_details = dictionary of image details generated using the readimg function. 
  ## denoise_weight: weight for tv denoising. Default = 0.02. 
  img_denoise = denoise_tv_chambolle(img, weight = denoise_weight, multichannel = False) # get denoised image.
  print("normalizing...")
  img_norm = equalize_adapthist(img_denoise) # normalised extracted image.
  print("generating mask...")
  mask = generate_mask(img_norm, img_details)
  img_masked = img_norm*mask # mask out areas of image counted as potential cell segments after all artifacts have been rm.
  img_masked2 = img_masked.astype('float64')
  return img_masked2

############## Segmentation, Classification and Quantification modules ############## 
def seg_fn(dapi, ck, cd45, vim, min_cell_size = 9):
  ## Fn: watershed function to segment potential cells. 
  ## dapi/ck/cd45/vim: ChannelImg class object for the relevant channel.
  ## min_cell_size: minimum diameter to be a cell (in um). 
  img_flat = dapi.norm*3 + ck.norm + cd45.norm + vim.norm
  img_flat *= 255.0/img_flat.max()
  img_flat = img_flat.astype('uint8') 
  img_mask = img_flat > 0
  ## start watershed segmentation ##
  distance = ndimage.distance_transform_edt(img_mask)
  coords = peak_local_max(distance, min_distance = math.ceil((min_cell_size)/dapi.details['pxwidth']), footprint = disk(3))
  marker_mask = np.zeros(distance.shape, dtype = bool)
  marker_mask[tuple(coords.T)] = True
  markers, num_features = ndimage.label(marker_mask)
  labels = watershed(-distance, markers, mask = img_mask)
  return labels

def seg_profiling(dapi, ck, cd45, vim, labels, min_cell_size = 9):
  ## Fn: Profiling characteristics of each potential cell segment (generated by watershed segmentation in seg_fn module). 
  ## dapi/ck/cd45/vim: dictionary including original compressed image, masked image, normalised image, and image details for each channel.
  ## min_cell_size: minimum diameter to be a cell (in um). 
  img = np.dstack((dapi.norm, ck.norm, cd45.norm, vim.norm)) # create multichannel dstack image.
  features = labels + 7
  features[features <= 7] = 0
  img *= 255.0/img.max()
  img = img.astype('uint8')
  record = []
  min_cell_area = math.pi*(min_cell_size/2)*(min_cell_size/2)
  for region in regionprops(features):
    if region.area*dapi.details['pxarea'] > min_cell_area:
      results = profile_stats(img, img_details = dapi.details, features = features, region_data = region)
      if results['dapi_avg'] > 0 and results['cell_area'] >= min_cell_area: 
        record.append(results) # if it has no dapi staining it's not a cell.
  print('number of segments profiled:', len(record))
  return record