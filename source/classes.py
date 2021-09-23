from modules import * 

class ChannelImg:
  def __init__(self, channel_name, sampledir, filename, img_height, img_width, denoise_weight = 0.02,
  	selem_rad = 6, circularity_cutoff = 0.35, conf = 'High'):
  	## Inputs:: 
  	## channel_name: name of the channel eg. dapi (or whatever the user prefers). 
  	## sampledir: path to directory of sample containing all channel images from that sample. 
    ## filename: name of the image file. 
    ## img_height: img height measurement (in mm).
    ## img_width: img height measurement (in mm).
    ## denoise_weight: weight for tv denoising. Default = 0.02. 
    ## selem_rad: radius of structure element. Default = 6. 
    ## circularity_cutoff: circularity threshold for elongated artifacts.
    ## conf: confidence level for intensity filtering. "Low" can be used for very clean images & passing more signal.
    self.channel_name = channel_name
    img_details, img_org = readimg(sampledir, filename, img_height, img_width)
    self.details = img_details
    self.org = img_org
    img_norm = preprocess(img_org, img_details, denoise_weight, selem_rad, circularity_cutoff , conf)
    self.norm = img_norm
    

class Sample:
  def __init__(self, batch_id, sample_id, sample_dir, dapi, ck, cd45, vim):
    ## Inputs:: 
    ## sample_id: identifier number of sample. 
    ## dapi/ck/cd45/vim: dictionary including original compressed image, masked image, normalised image, and image details for each channel.
    self.batch_id = batch_id
    self.sample_id = sample_id
    self.sample_dir = sample_dir
    self.dapi = dapi
    self.ck = ck
    self.cd45 = cd45
    self.vim = vim
    labels = seg_fn(dapi, ck, cd45, vim, min_cell_size = 9)
    self.labels = labels
    self.profile_record = seg_profiling(dapi, ck, cd45, vim, labels, min_cell_size = 9) # list of cells profiled. 