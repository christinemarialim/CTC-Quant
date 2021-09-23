import os
import sys
import PyQt5
import pandas as pd
import skimage
from skimage import measure
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QProgressBar
from PyQt5.QtCore import QSize, Qt, QAbstractTableModel, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from mygui_ancillary import _generateCrops, CropsViewer

class SaveWorker(QObject):
  finished = pyqtSignal()
  progress = pyqtSignal()
  def __init__(self, export_path, df, imgList, analysisType, parent = None):
    super().__init__()
    self.export_path = export_path
    self.results = df
    self.total_cell_num = len(df)
    self._imgList = imgList
    self.analysisType = analysisType
  ###
  def _exportImg(self):
    for n in range(self.total_cell_num):
      self.progress.emit()
      for i in range(len(self.results)):
        k = int(self.results.sample_num[i]) - 1
        self.outline, self.dapi_exp, self.ck_exp, self.cd45_exp, self.vim_exp = _generateCrops(self.results, self._imgList[k], i)
        contours = measure.find_contours(self.outline, 0.7)
        fig = CropsViewer(self)
        fig.ax1.imshow(self.dapi_exp)
        for contour in contours: fig.ax1.plot(contour[:, 1], contour[:, 0], linewidth=2)
        fig.ax2.imshow(self.ck_exp)
        for contour in contours: fig.ax2.plot(contour[:, 1], contour[:, 0], linewidth=2)
        fig.ax3.imshow(self.cd45_exp)
        for contour in contours: fig.ax3.plot(contour[:, 1], contour[:, 0], linewidth=2)
        fig.ax4.imshow(self.vim_exp)
        for contour in contours: fig.ax4.plot(contour[:, 1], contour[:, 0], linewidth=2)
        # set the title to subplots
        fig.ax1.set_title("dapi")
        fig.ax1.axis("off")
        fig.ax2.set_title("ck")
        fig.ax2.axis("off")
        fig.ax3.set_title("cd45")
        fig.ax3.axis("off")
        fig.ax4.set_title("vimentin")
        fig.ax4.axis("off")
        if self.analysisType == 'Batch':
          export_name = self.export_path+'/'+str(self.results.batch_id[i])+'_'+str(self.results.sample_id[i])+'_'+str(i)+'_'+str(self.results.celltype_label[i])+'.jpeg'
        elif self.analysisType == 'Single Sample':
          export_name = self.export_path+'/'+str(self.results.sample_id[i])+'_'+str(i)+'_'+str(self.results.celltype_label[i])+'.jpeg'
        fig.print_figure(export_name)
      self.finished.emit()

class saveWindow(QMainWindow):
  def __init__(self, export_path, df, imgList, analysisType):
    super().__init__()
    self.setWindowIcon(QIcon('../CTC-Quant Icon.png'))
    self.setWindowTitle("cqCTC")
    self.setFixedSize(QSize(500, 100)) # set the size of the window.
    self.export_path = export_path
    self.results = df
    self.total_cell_num = len(df)
    self._imgList = imgList
    self.analysisType = analysisType
    self.i = 0
    # Setup
    self.setup_UI()
    self.runSaveThread()
  def setup_UI(self):
    layout = QVBoxLayout()
    self.current_cell_label = QLabel('Saving cell '+str(0)+' of '+str(self.total_cell_num))
    layout.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.current_cell_label)
    ## display.
    widget = QWidget()
    widget.setLayout(layout)
    self.setCentralWidget(widget)
  def runSaveThread(self):
    self.thread = QThread() # Create a QThread object
    self.worker = SaveWorker(self.export_path, self.results, self._imgList, self.analysisType) # Create a worker object
    self.worker.moveToThread(self.thread) # Move worker to the thread
    self.thread.started.connect(self.worker._exportImg) # Connect signals and slots
    self.worker.finished.connect(self.thread.quit)
    self.worker.finished.connect(self.worker.deleteLater)
    self.thread.finished.connect(self.thread.deleteLater)
    self.worker.progress.connect(self.reportProgress)
    self.thread.start() # Start the thread
    ## final resets:
    self.thread.finished.connect(self.exitSaveWindow)
  ## create function to report current progress percentage.
  def reportProgress(self):
    self.i = self.i + 1
    self.current_cell_label.setText('Saving cell '+str(self.i)+' of '+str(self.total_cell_num))
  ## create function to launch main window.
  def exitSaveWindow(self):
    self.close()
  