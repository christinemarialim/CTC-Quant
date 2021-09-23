import skimage
import math
import numpy as np
from skimage.measure import block_reduce, find_contours
  
def img_compress(img, block_size = (3,3)):
  ## Fn: to compress image via downsampling using mean function. 
  ## Inputs:: 
  ## img: original image for compression. 
  ## block_size: kernel size used for downsampling, current default = (3,3).
  return block_reduce(img, block_size = block_size, func = np.mean).astype('uint8')

def get_img_details(orgimg, compress_img, height, width):
  ## Fn: get the details regarding the input image.
  ## Inputs::
  ## orgimg: original image before compression.
  ## compress_img: image that has been downsampled. 
  ## height: measurement (in mm).
  ## width: measurement (in mm).
  orgdim = orgimg.shape # returns original image dimensions in (Y,X). 
  newdim = compress_img.shape # returns compressed image dimensions in (Y,X). 
  pxh = (height/newdim[0])*(10**(3)) # returns pixel height in um.
  pxw = (width/newdim[0])*(10**(3)) # returns pixel width in um.
  pxarea = pxh * pxw # returns pixel area in um^2.
  return {"orgdim": orgdim, "newdim": newdim, "pxheight": pxh, "pxwidth": pxw, "pxarea": pxarea}

def circularity_idx(contour, img_details):
  ## Fn: calculates a circularity index for a given segment. 
  ## Inputs::
  ## contour: outline of segment for which you are finding circularity
  ## img_details = dictionary of image details generated using the readimg function.
  pxheight, pxwidth, pxarea = img_details['pxheight'], img_details['pxwidth'], img_details['pxarea']
  contour = np.vstack([contour, contour[0]]) # add first point to the back
  area_pixels, perimeter = 0, 0
  for i in range(len(contour)-1):
    y1, x1 = contour[i]
    y2, x2 = contour[i+1]
    eu_dist = math.sqrt(((y2-y1)*pxheight)**2 + ((x2-x1)*pxwidth)**2)
    perimeter = perimeter + eu_dist
    area_pixels = area_pixels + (x1*y2) - (x2*y1)
  area_pixels = area_pixels*0.5
  area = area_pixels*pxarea
  return (4*math.pi*area)/(perimeter**2), area, perimeter

def profile_stats(img, img_details, features, region_data):
  ## Fn: profile parameters of the cell segment. 
  ## Inputs:: 
  ## img: multichannel image. 
  ## img_details = dictionary of image details generated using the readimg function.
  ## features: feature segments (ie.labels) output from seg_fn module. 
  ## region_data: information of said region. 
  ## area: area of cell segment (in um^2). 
  rowmin, colmin, rowmax, colmax = region_data.bbox
  if rowmin != 0: rowmin = rowmin-1
  if colmin != 0: colmin = colmin-1
  if rowmax != 0: rowmax = rowmax+1
  if colmax != 0: colmax = colmax+1
  roi = features[rowmin:rowmax, colmin:colmax]
  roi[roi != region_data.label] = 0
  contour = find_contours(roi, (region_data.label-1))[0]
  circ_idx, cont_area, cont_perimeter = circularity_idx(contour, img_details) # get circularity index. 
  cont_diameter = 2*(math.sqrt(cont_area/math.pi))
  roi = img[rowmin:rowmax, colmin:colmax] # crop roi.
  roi_reshape = roi.reshape(-1, 4) # reshape roi data. 
  dapi_count, ck_count, cd45_count, vim_count = np.sum(roi_reshape > 0, axis = 0)
  # from literature: average dapi size is 6um diameter, whole cell is larger than nucleus. 
  if dapi_count > np.ceil((math.pi*3*3)/img_details['pxarea']): 
    dapi_avg = np.sum(roi_reshape[:,0], axis = 0) / cont_area
  else: dapi_avg = 0
  if ck_count > np.ceil((math.pi*3*3)/img_details['pxarea']): 
    ck_avg = np.sum(roi_reshape[:,1], axis = 0) / cont_area
  else: ck_avg = 0
  if cd45_count > np.ceil((math.pi*3*3)/img_details['pxarea']):
    cd45_avg = np.sum(roi_reshape[:,2], axis = 0) / cont_area
  else: cd45_avg = 0
  if vim_count > np.ceil((math.pi*3*3)/img_details['pxarea']):
    vim_avg = np.sum(roi_reshape[:,3], axis = 0) / cont_area
  else: vim_avg = 0
  return {"bbox": region_data.bbox, "cell_area": cont_area, "cell_perimeter": cont_perimeter, "cell_diameter": cont_diameter, "circularity_idx": circ_idx, "dapi_avg": dapi_avg, "ck_avg": ck_avg, "cd45_avg": cd45_avg, "vim_avg": vim_avg}