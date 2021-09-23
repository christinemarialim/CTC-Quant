import numpy as np
import sklearn
import scipy.ndimage as ndimage
import skimage
from skimage.measure import regionprops
import pickle

def log2int(df):
  ## Fn: this function takes a log2 of all the average intensities. 
  df['dapi_log2'] = np.log2(df['dapi_avg']+0.01)
  df['ck_log2'] = np.log2(df['ck_avg']+0.01)
  df['cd45_log2'] = np.log2(df['cd45_avg']+0.01)
  df['vim_log2'] = np.log2(df['vim_avg']+0.01)
  return df

def filtInt(df):
  ## Fn: this function is to filter dapi intensities of interest (within middle 95% of population). 
  df = df[df.dapi_log2 > np.quantile(df.dapi_log2, 0.025)]
  df = df[df.dapi_log2 < np.quantile(df.dapi_log2, 0.975)]
  return df

def readmodel(modelName):
  ## Fn: this function imports the trained classification model. 
  if modelName == "Lung Cancer": 
    scaler = pickle.load(open('../model/RFCscaler_lung.pkl', 'rb'))
    model = pickle.load(open('../model/RFC_lung.sav', 'rb'))
  if modelName == "Nasopharyngeal Cancer": 
    scaler = pickle.load(open('../model/RFCscaler_npc.pkl', 'rb'))
    model = pickle.load(open('../model/RFC_npc.sav', 'rb'))
  if modelName == "Breast Cancer": 
    scaler = pickle.load(open('../model/RFCscaler_breast.pkl', 'rb'))
    model = pickle.load(open('../model/RFC_breast.sav', 'rb'))
  return scaler, model

def _findClusters(df, dapi, ck, cd45, vim, details, j, min_cell_area):
  ## Fn: function to estimate mCTC clusters. 
  ## dapi/ck/cd45/vim: ChannelImg class object for the relevant channel.
  ## min_cell_area: minimum area to be a cell (in um^2). 
  bbox_s = str(df.bbox[j]).replace('(', '')
  bbox_s = bbox_s.replace(')', '')
  bbox_s = bbox_s.replace(',', '').split()
  Xmin, Ymin, Xmax, Ymax = int(bbox_s[0]), int(bbox_s[1]), int(bbox_s[2]), int(bbox_s[3])
  # 
  img_flat = dapi.norm*3 + ck.norm + cd45.norm + vim.norm
  img_flat = img_flat[Xmin:Xmax, Ymin:Ymax]
  if img_flat.max() > 0:
    img_flat *= 255.0/img_flat.max()
    img_flat = img_flat.astype('uint8') 
    img_mask_flat = img_flat > 0
    markersF, num_featuresF = ndimage.label(img_mask_flat)
    for region in regionprops(markersF):
      if region.area*details['pxarea'] < min_cell_area: markersF = np.where(markersF == region.label, 0, markersF) 
    markersF = markersF > 0
  #
    dapi_norm_crop = dapi.norm[Xmin:Xmax, Ymin:Ymax]
    dapi_norm = dapi_norm_crop
    dapi_norm *= 255.0/dapi_norm.max()
    dapi_norm = dapi_norm.astype('uint8') 
    img_mask = markersF*dapi_norm > 0
    markersD, num_featuresD = ndimage.label(img_mask)
    if num_featuresD > 2: cluster_stat = 'Y'
    else: cluster_stat = 'N'
  return cluster_stat

def classify(df, dapi, ck, cd45, vim, min_cell_size, modelName = "Lung Cancer"):
  ## Fn: this function classifies the cells based on the trained model.
  ## min_cell_size: minimum diameter to be a cell (in um).
  df_log2 = log2int(df)
  df_Int = filtInt(df_log2)
  results = df_Int # to store results
  feature_names = ['ck_log2', 'cd45_log2', 'vim_log2', 'cell_diameter']
  scaler, model = readmodel(modelName)
  data = scaler.transform(df_Int[feature_names])
  results['celltype_label'] = model.predict(data)
  mctcList = list(results[results.celltype_label == 'mCTC'].index)
  results['cluster'] = ''
  for i in mctcList: 
    results.loc[i,'cluster'] = _findClusters(df = df, dapi = dapi, ck = ck, cd45 = cd45, vim = vim, details = dapi.details, j = i, min_cell_area = 3.14159*(min_cell_size/2)*(min_cell_size/2))
  return results