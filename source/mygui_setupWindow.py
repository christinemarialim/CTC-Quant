import os
import sys
import PyQt5
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QComboBox, QRadioButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QLineEdit, QFileDialog
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from modules import getfiles_batch, getfiles_sample
from mygui_ancillary import analysisConfig
from mygui_statusWindow import *

class SetupWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowIcon(QIcon('../CTC-Quant Icon.png'))
    self.setWindowTitle("New Project")
    self.setFixedSize(QSize(350, 500)) # set the size of the window.
    self.SBw = None  # Status of status bar window.
    self._configs = analysisConfig('', '', '', '', '', 7.32, 7.32, 0.02, 9, 'Lung Cancer', 'High', 'Batch')
    ## create first option for batch vs single analysis.
    ## if want combobox instead can change to that. 
    batchOption = QHBoxLayout()
    batchOption.addWidget(QLabel('Analysis type:'))
    BatchButton = QRadioButton('Batch')
    BatchButton.setChecked(True)
    BatchButton.toggled.connect(lambda:self.batch_btnstate(BatchButton))
    batchOption.addWidget(BatchButton)
    SingleButton = QRadioButton('Single Sample')
    SingleButton.toggled.connect(lambda:self.batch_btnstate(SingleButton))
    batchOption.addWidget(SingleButton)
    batchOption.setAlignment(Qt.AlignLeft)
    ## create option to open directory selection.
    filedirOption = QHBoxLayout()
    filedirOption.addWidget(QLabel('Directory:'))
    dir_button = QPushButton('Open file')
    dir_button.clicked.connect(self._getDirpath)
    filedirOption.addWidget(dir_button)
    self.dir_path_label = QLabel('')
    filedirOption.addWidget(self.dir_path_label)
    filedirOption.setAlignment(Qt.AlignLeft)
    ## create option to open dapi image.
    dapiOption = QHBoxLayout()
    dapiOption.addWidget(QLabel('Nuclei Stain Image:'))
    dapi_button = QPushButton('Open file')
    dapi_button.clicked.connect(lambda:self._getFilename(channel = 'dapi'))
    dapiOption.addWidget(dapi_button)
    self.dapi_label = QLabel('')
    dapiOption.addWidget(self.dapi_label)
    dapiOption.setAlignment(Qt.AlignLeft)
    ## create option to open ck image.
    ckOption = QHBoxLayout()
    ckOption.addWidget(QLabel('Ck Image:'))
    ck_button = QPushButton('Open file')
    ck_button.clicked.connect(lambda:self._getFilename(channel = 'ck'))
    ckOption.addWidget(ck_button)
    self.ck_label = QLabel('')
    ckOption.addWidget(self.ck_label)
    ckOption.setAlignment(Qt.AlignLeft)
    ## create option to open cd45 image.
    cd45Option = QHBoxLayout()
    cd45Option.addWidget(QLabel('Cd45 Image:'))
    cd45_button = QPushButton('Open file')
    cd45_button.clicked.connect(lambda:self._getFilename(channel = 'cd45'))
    cd45Option.addWidget(cd45_button)
    self.cd45_label = QLabel('')
    cd45Option.addWidget(self.cd45_label)
    cd45Option.setAlignment(Qt.AlignLeft)
    ## create option to open vimentin image.
    vimOption = QHBoxLayout()
    vimOption.addWidget(QLabel('Vimentin Image:'))
    vim_button = QPushButton('Open file')
    vim_button.clicked.connect(lambda:self._getFilename(channel = 'vim'))
    vimOption.addWidget(vim_button)
    self.vim_label = QLabel('')
    vimOption.addWidget(self.vim_label)
    vimOption.setAlignment(Qt.AlignLeft)
    ## create box to input image height settings.
    imgHOption = QHBoxLayout()
    imgHOption.addWidget(QLabel('Image Height (in mm):'))
    self.imgH = QLineEdit('7.32')
    imgHOption.addWidget(self.imgH)
    imgHOption.setAlignment(Qt.AlignLeft)
    ## create box to input image width settings.
    imgWOption = QHBoxLayout()
    imgWOption.addWidget(QLabel('Image Width (in mm):'))
    self.imgW = QLineEdit('7.32')
    imgWOption.addWidget(self.imgW)
    imgWOption.setAlignment(Qt.AlignLeft)
    ## create box to input denoise weight settings.
    denoiseWOption = QHBoxLayout()
    denoiseWOption.addWidget(QLabel('Denoise weight:'))
    self.dw = QLineEdit('0.02')
    denoiseWOption.addWidget(self.dw)
    denoiseWOption.setAlignment(Qt.AlignLeft)
    ## create box to input minimum cell diameter settings.
    minDOption = QHBoxLayout()
    minDOption.addWidget(QLabel('Minimum cell diameter (in um):'))
    self.mD = QLineEdit('9')
    minDOption.addWidget(self.mD)
    minDOption.setAlignment(Qt.AlignLeft)
    ## create filter confidence settings.
    filtconfOption = QHBoxLayout()
    filtconfOption.addWidget(QLabel('Filter confidence:'))
    highconfButton = QRadioButton('High')
    highconfButton.setChecked(True)
    highconfButton.toggled.connect(lambda:self.filtconf_btnstate(highconfButton))
    filtconfOption.addWidget(highconfButton)
    lowconfButton = QRadioButton('Low')
    lowconfButton.toggled.connect(lambda:self.filtconf_btnstate(lowconfButton))
    filtconfOption.addWidget(lowconfButton)
    filtconfOption.setAlignment(Qt.AlignLeft)
    ## create cancer type settings.
    modelOption = QHBoxLayout()
    modelOption.addWidget(QLabel('Cancer type:'))
    self.modelList = QComboBox()
    self.modelList.addItems(["Lung Cancer", "Breast Cancer", "Nasopharyngeal Cancer"])
    self.modelList.setCurrentIndex(0)
    self.modelList.currentTextChanged.connect(self.text_changed)
    modelOption.addWidget(self.modelList)
    modelOption.setAlignment(Qt.AlignLeft)
    ## create button to begin analysis.
    layout_button = QHBoxLayout()
    layout_button.addStretch(1)
    run_button = QPushButton("Run")
    run_button.clicked.connect(self.launch_statusBar_window)
    layout_button.addWidget(run_button)
    ## arrange options in overall layout. 
    layout_setup = QVBoxLayout()
    layout_setup.addWidget(QLabel('Select Analysis Preferences'))
    layout_setup.addLayout(batchOption) # add batch option. 
    layout_setup.addLayout(filedirOption) # add filedirectory option.
    layout_setup.addLayout(dapiOption) # add dapi image option.
    layout_setup.addLayout(ckOption) # add ck image option.
    layout_setup.addLayout(cd45Option) # add cd45 image option. 
    layout_setup.addLayout(vimOption) # add vimentin image option. 
    layout_setup.addWidget(QLabel('Input Image Metadata'))
    layout_setup.addLayout(imgHOption) # add image height input box.
    layout_setup.addLayout(imgWOption) # add image width input box.
    layout_setup.addWidget(QLabel('Select Pre-processing Preferences'))
    layout_setup.addLayout(denoiseWOption) # add denoise weight input box.
    layout_setup.addLayout(minDOption) # add minimum cell diameter input box.
    layout_setup.addLayout(filtconfOption) # add minimum cell diameter input box.
    layout_setup.addLayout(modelOption) # add selection of cancer type model.
    layout_setup.addLayout(layout_button) # add create button.
    ## display.
    setup_widget = QWidget()
    setup_widget.setLayout(layout_setup)
    self.setCentralWidget(setup_widget)
  ## batch option status. 
  def batch_btnstate(self, b):
    if b.text() == "Batch":
      if b.isChecked() == True: 
        self._configs._analysisType = "Batch"
      else: self._configs._analysisType = "Single Sample"
    if b.text() == "Single Sample":
      if b.isChecked() == True: 
        self._configs._analysisType = "Single Sample"
      else: self._configs._analysisType = "Batch"
  ## get filename function. 
  def _getDirpath(self):
    self._configs.dir_path = QFileDialog.getExistingDirectory()
    self.dir_path_label.setText(self._configs.dir_path)
  ## get filename function. 
  def _getFilename(self, channel):
    filepath = QFileDialog.getOpenFileName()
    filepath_split = filepath[0].split('/')
    filename = filepath_split[len(filepath_split)-1]
    if channel == 'dapi': 
      self._configs._dapiFilename = filename
      self.dapi_label.setText(filename)
    elif channel == 'ck': 
      self._configs._ckFilename = filename
      self.ck_label.setText(filename)
    elif channel == 'cd45': 
      self._configs._cd45Filename = filename
      self.cd45_label.setText(filename)
    elif channel == 'vim': 
      self._configs._vimFilename = filename
      self.vim_label.setText(filename)
  ## filter confidence status. 
  def filtconf_btnstate(self, b):
    if b.text() == "High":
      if b.isChecked() == True:
        self._configs._conflevel = "High"
    if b.text() == "Low":
      if b.isChecked() == True: self._configs._conflevel = "Low"
      else: self._configs._conflevel = "High"
  ## select cancer type model: 
  def text_changed(self): 
    self._cancerModel = str(self.modelList.currentText())
  ## create function to launch main window.
  def launch_statusBar_window(self, checked):
    if self._configs._analysisType == 'Batch': self._configs.dirlist = getfiles_batch(self._configs.dir_path)
    elif self._configs._analysisType == 'Single Sample': self._configs.dirlist = getfiles_sample(self._configs.dir_path)
    self._configs.img_height = float(self.imgH.text())
    self._configs.img_width = float(self.imgW.text())
    self._configs.denoise_weight = float(self.dw.text())
    self._configs.min_cellD = float(self.mD.text())
    if self.SBw is None:
      self.SBw = StatusBar(self._configs)
    self.SBw.show()
    self.close()
