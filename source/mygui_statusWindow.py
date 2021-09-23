import os
import sys
import PyQt5
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QProgressBar
from PyQt5.QtCore import QSize, Qt, QAbstractTableModel, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from classes import * 
from classification import classify
from mygui_mainWindow import MainWindow

class Worker(QObject):
  finished = pyqtSignal()
  newSample = pyqtSignal()
  progress = pyqtSignal()
  finalResults = pyqtSignal(list, object)
  def __init__(self, total_sample_num, configs, parent = None):
    super().__init__()
    self.total_sample_num = total_sample_num
    self._configs = configs
    self.imgList = []
    self.results_all = pd.DataFrame(columns = ["batch_id", "sample_num", "sample_id", "sample_dir", "bbox", "cell_area", "cell_perimeter", "cell_diameter", "circularity_idx", "dapi_avg", "ck_avg", "cd45_avg", "vim_avg"])
  ###
  def _runAnalysis(self):
    for n in range(self.total_sample_num):
      self.newSample.emit()
      sampledir = self._configs.dirlist[n]['sample_dir']
      self.progress.emit() 
      dapi = ChannelImg("dapi", sampledir, filename = self._configs._dapiFilename, img_height = self._configs.img_height, img_width = self._configs.img_width)
      self.progress.emit() 
      ck = ChannelImg("ck", sampledir, filename = self._configs._ckFilename, img_height = self._configs.img_height, img_width = self._configs.img_width)
      self.progress.emit() 
      cd45 = ChannelImg("cd45", sampledir, filename = self._configs._cd45Filename, img_height = self._configs.img_height, img_width = self._configs.img_width)
      self.progress.emit() 
      vim = ChannelImg("vimentin", sampledir, filename = self._configs._vimFilename, img_height = self._configs.img_height, img_width = self._configs.img_width)
      self.progress.emit() 
      ## segment, profile segments in 'Sample' class
      sample = Sample(self._configs.dirlist[n]['batch_id'], self._configs.dirlist[n]['sample_id'], self._configs.dirlist[n]['sample_dir'], dapi, ck, cd45, vim)
      self.progress.emit()
      self.imgList.append(sample)
      results = pd.DataFrame(sample.profile_record)
      results['sample_num'] = n+1
      results['sample_id'] = sample.sample_id
      results['batch_id'] = sample.batch_id
      results['sample_dir'] = sample.sample_dir
      results = results[["batch_id", "sample_num", "sample_id", "sample_dir", "bbox", "cell_area", "cell_perimeter", "cell_diameter", "circularity_idx", "dapi_avg", "ck_avg", "cd45_avg", "vim_avg"]]
      results_classified = classify(results, dapi, ck, cd45, vim, self._configs.min_cellD, self._configs._cancerModel)
      self.results_all = self.results_all.append(results_classified)
      self.progress.emit()
    self.progress.emit()
    self.finalResults.emit(self.imgList, self.results_all)
    self.finished.emit()

class StatusBar(QMainWindow):
  def __init__(self, configs):
    super().__init__()
    self.setWindowIcon(QIcon('../CTC-Quant Icon.png'))
    self.setWindowTitle("cqCTC")
    self.setFixedSize(QSize(500, 100)) # set the size of the window.
    self.w = None
    self._configs = configs
    self._imgList = [] # create list to store image Sample class. 
    self.results_all = pd.DataFrame(columns = ["batch_id", "sample_num", "sample_id", "sample_dir", "bbox", "cell_area", "cell_perimeter", "cell_diameter", "circularity_idx", "dapi_avg", "ck_avg", "cd45_avg", "vim_avg"])
    self.total_sample_num = len(self._configs.dirlist)
    self.current_sample_num = 0
    self.i = 0
    # Setup
    self.setup_UI()
    self.runAnalysisThread()
  def setup_UI(self):
    layout_status = QVBoxLayout()
    self.current_num_label = QLabel('Analysing sample '+str(0)+' of '+str(self.total_sample_num))
    layout_status.addWidget(self.current_num_label)
    self.progressBAR = QProgressBar(self)
    self.progressBAR.setMaximum(100)
    self.progressBAR.setValue(self.i)
    layout_status.addWidget(self.progressBAR)
    layout_status.setAlignment(Qt.AlignCenter)
    ## create button to view results of analysis.
    layout_viewResbutton = QHBoxLayout()
    layout_viewResbutton.addStretch(1)
    self.viewRes_button = QPushButton("View Results")
    self.viewRes_button.setEnabled(False) # disable button at first.
    self.viewRes_button.clicked.connect(self.launch_main_window)
    layout_viewResbutton.addWidget(self.viewRes_button)
    layout_status.addLayout(layout_viewResbutton)
    ## display.
    status_widget = QWidget()
    status_widget.setLayout(layout_status)
    self.setCentralWidget(status_widget)
  def runAnalysisThread(self):
    self.thread = QThread() # Create a QThread object
    self.worker = Worker(self.total_sample_num, self._configs) # Create a worker object
    self.worker.moveToThread(self.thread) # Move worker to the thread
    self.thread.started.connect(self.worker._runAnalysis) # Connect signals and slots
    self.worker.finished.connect(self.thread.quit)
    self.worker.finished.connect(self.worker.deleteLater)
    self.thread.finished.connect(self.thread.deleteLater)
    self.worker.newSample.connect(self.reportNewSample)
    self.worker.progress.connect(self.reportProgress)
    self.worker.finalResults.connect(self._getResults)
    self.thread.start() # Start the thread
    ## final resets:
    self.thread.finished.connect(lambda: self.viewRes_button.setEnabled(True))
    self.thread.finished.connect(lambda: self.current_num_label.setText('Analysis Complete'))
  ## create function to report progress.
  def reportNewSample(self):
    self.current_sample_num = self.current_sample_num + 1
    self.current_num_label.setText("Analysing sample "+str(self.current_sample_num)+" of "+str(self.total_sample_num))
    self.i = 0
    self.progressIdx = 0
    self.progressBAR.setValue(self.i)
  ## create function to report current progress percentage.
  def reportProgress(self):
    progressList = [0,2,15,15,15,15,25,3,10]
    self.progressIdx = self.progressIdx + 1
    self.i = self.i + progressList[self.progressIdx]
    self.progressBAR.setValue(self.i)
  ## create function to report current progress percentage.
  def _getResults(self, l, df):
    self._imgList = l
    self.results_all = df
  ## create function to launch main window.
  def launch_main_window(self, checked):
    print(self._imgList)
    if self.w is None:
      self.w = MainWindow(self._configs, self._imgList, self.results_all)
    self.w.show()
    self.close()
  