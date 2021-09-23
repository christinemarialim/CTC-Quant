import os
import sys
import matplotlib
matplotlib.use('Qt5Agg')
import PyQt5
import pandas as pd
import numpy as np
import skimage
from skimage.transform import rescale
from skimage.color import rgb2gray
from PyQt5.QtCore import QSize, Qt, QAbstractTableModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from modules import getfiles_batch, getfiles_sample

class analysisConfig:
  def __init__(self, dir_path, _dapiFilename, _ckFilename, _cd45Filename, _vimFilename, img_height, img_width, denoise_weight, min_cellD, cancer_type_model, filt_conf = 'High',  _analysisType = "Batch", dirlist = []):
    self.dir_path = dir_path
    self._dapiFilename = _dapiFilename 
    self._ckFilename = _ckFilename 
    self._cd45Filename = _cd45Filename 
    self._vimFilename = _vimFilename 
    self.img_height = img_height # measurement should be in (mm).
    self.img_width = img_width # measurement should be in (mm).
    self.denoise_weight = denoise_weight # default is 0.02.
    self.min_cellD = min_cellD # default is 9. 
    self._cancerModel = cancer_type_model
    self.filt_conf = filt_conf # default is 'high'
    self._analysisType = _analysisType # default is "Batch", alternatively "Single Sample". 
    self.dirlist = dirlist

class ImgViewer(FigureCanvasQTAgg):
  def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
    fig = Figure(figsize = (width, height), dpi = dpi)
    self.axes = fig.add_subplot(111)
    super(ImgViewer, self).__init__(fig)

class CropsViewer(FigureCanvasQTAgg):
  def __init__(self, parent = None, width = 2, height = 2, dpi = 100):
    fig = Figure(figsize = (width, height), dpi = dpi)
    self.ax1 = fig.add_subplot(221)
    self.ax2 = fig.add_subplot(222)
    self.ax3 = fig.add_subplot(223)
    self.ax4 = fig.add_subplot(224)
    super(CropsViewer, self).__init__(fig)

## function to generate first stand-in whole and cropped-image preview:
def _generateImgs(df, imgList, k = 0, j = 0):
  imgPreview_org = np.dstack((imgList[k].cd45.org*3, imgList[k].ck.org*3, imgList[k].dapi.org*3))
  imgPreview_norm = np.dstack((imgList[k].cd45.norm*3, imgList[k].ck.norm*3, imgList[k].dapi.norm*3))
  imgPreview_oneCell, dapi_crop, ck_crop, cd45_crop, vim_crop = _generateCrops(df, imgList[k], j)
  return imgPreview_org, imgPreview_norm, imgPreview_oneCell, dapi_crop, ck_crop, cd45_crop, vim_crop

## function to generate first stand-in cropped-image preview:
def _generateCrops(df, SampleObj, j = 0):
  imgPreview_norm = np.dstack((SampleObj.cd45.norm*3, SampleObj.ck.norm*3, SampleObj.dapi.norm*3))
  bbox_s = str(df.bbox[j]).replace('(', '')
  bbox_s = bbox_s.replace(')', '')
  bbox_s = bbox_s.replace(',', '').split()
  Xmin, Ymin, Xmax, Ymax = int(bbox_s[0]), int(bbox_s[1]), int(bbox_s[2]), int(bbox_s[3])
  if (Xmin-2) >= 0: Xmin = Xmin-2
  if (Xmax+2) <= SampleObj.dapi.norm.shape[1]: Xmax = Xmax+2
  if (Ymin-2) >= 0: Ymin = Ymin-2
  if (Ymax+2) <= SampleObj.dapi.norm.shape[0]: Ymax = Ymax+2
  dapi_norm_crop = SampleObj.dapi.norm[Xmin:Xmax, Ymin:Ymax]
  dapi_norm_crop = rescale(dapi_norm_crop*3, 4, anti_aliasing=False)
  ck_norm_crop = SampleObj.ck.norm[Xmin:Xmax, Ymin:Ymax]
  ck_norm_crop = rescale(ck_norm_crop*3, 4, anti_aliasing=False)
  vim_norm_crop = SampleObj.vim.norm[Xmin:Xmax, Ymin:Ymax]
  vim_norm_crop = rescale(vim_norm_crop*3, 4, anti_aliasing=False)
  imgPreview_oneCell = np.dstack((vim_norm_crop, ck_norm_crop, dapi_norm_crop))
  imgPreview_oneCell = rgb2gray(imgPreview_oneCell)
  cd45_norm_crop = SampleObj.cd45.norm[Xmin:Xmax, Ymin:Ymax]
  cd45_norm_crop = rescale(cd45_norm_crop*3, 4, anti_aliasing=False)
  empty = np.zeros(cd45_norm_crop.shape)
  dapi_norm_crop = np.dstack([empty, empty, dapi_norm_crop])
  dapi_norm_crop = rgb2gray(dapi_norm_crop)
  cd45_norm_crop = np.dstack([cd45_norm_crop, empty, empty])
  cd45_norm_crop = rgb2gray(cd45_norm_crop)
  ck_norm_crop = np.dstack([empty, ck_norm_crop, empty])
  ck_norm_crop = rgb2gray(ck_norm_crop)
  vim_norm_crop = np.dstack([empty, vim_norm_crop, empty])
  vim_norm_crop = rgb2gray(vim_norm_crop)
  return imgPreview_oneCell, dapi_norm_crop, ck_norm_crop, cd45_norm_crop, vim_norm_crop

class ResTable(QAbstractTableModel):
  def __init__(self, data):
    QAbstractTableModel.__init__(self)
    self._data = data
  def rowCount(self, parent = None):
    return self._data.shape[0]
  def columnCount(self, parent = None):
    return self._data.shape[1]
  def data(self, index, role = Qt.DisplayRole):
    if index.isValid():
      if role == Qt.DisplayRole:
        return str(self._data.iloc[index.row(), index.column()])
    return None
  def headerData(self, col, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self._data.columns[col]
    return None

## function to count cell types to generate summary results table:
def count_celltypes(df, configs):
  sample_num = len(configs.dirlist)
  counts_df = pd.DataFrame(columns = ['sample_id', 'epCTC', 'bipCTC', 'mCTC', 'clusters', 'wbc'])
  for i in range(sample_num):
    df_sub = df[df.sample_num == i+1]
    df_m = df_sub[df_sub.celltype_label == 'mCTC']
    counts = {'sample_id': configs.dirlist[i]['sample_id'], 
    'epCTC': df_sub[df_sub.celltype_label == 'epCTC'].shape[0],
    'bipCTC': df_sub[df_sub.celltype_label == 'bipCTC'].shape[0],
    'mCTC': df_sub[df_sub.celltype_label == 'mCTC'].shape[0],
    'clusters': df_m[df_m.cluster == 'Y'].shape[0],
    'wbc': df_sub[df_sub.celltype_label == 'wbc'].shape[0]}
    counts = pd.DataFrame(counts, index=[0])
    counts_df = counts_df.append(counts)
  return counts_df