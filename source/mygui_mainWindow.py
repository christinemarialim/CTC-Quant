import os
import io
import sys
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
import PyQt5
from PyQt5.QtWidgets import QMainWindow, QMenu, QLabel, QPushButton, QWidget, QComboBox, QRadioButton, QAction, QToolBar, QVBoxLayout, QHBoxLayout, QStackedLayout, QLineEdit, QTableView, QFileDialog
from PyQt5.QtCore import QSize, Qt, QAbstractTableModel
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mygui_ancillary import ImgViewer, _generateImgs, CropsViewer, _generateCrops, ResTable, count_celltypes
from mygui_viewConfigsWindow import viewConfigWindow
from mygui_saveWindow import saveWindow

class MainWindow(QMainWindow):
  def __init__(self, configs, imgList, resTable):
    super().__init__()
    self.setWindowIcon(QIcon('../CTC-Quant Icon.png'))
    self.setWindowTitle("cqCTC")
    self.setFixedSize(QSize(1400, 930)) # set the size of the window.
    self.NPw = None  # Status of 'new project' window.
    self._configs, self.imgList, self.resTable = configs, imgList, resTable # store data input from analysis.
    self._imgList = imgList
    self._results = resTable # with all details
    self.resSummaryTable = count_celltypes(resTable, self._configs)
    self.resDetailsTable = resTable[resTable['celltype_label'].isin(['epCTC', 'bipCTC', 'mCTC'])]
    self.resDetailsTable = self.resDetailsTable.reset_index()
    self.k = 0
    self.j = 0
    self.imgPreview_org, self.imgPreview_norm, self.imgPreview_oneCell, self.dapi_crop, self.ck_crop, self.cd45_crop, self.vim_crop = _generateImgs(self.resDetailsTable, self._imgList, self.k, self.j)
    self._createActions() # create actions to be inserted into menubar options in next line.
    self._createMenuBar() # insert menubar.
    self._createToolBars()
    ## create space for top two buttons to toggle between original image and pre-processed image.
    layout_toggle = QHBoxLayout()
    self.pprocessedimg_button = QPushButton("Pre-processed")
    self.pprocessedimg_button.setStyleSheet("background-color: #b0b0b0;")
    self.pprocessedimg_button.clicked.connect(self._viewPPimg)
    layout_toggle.addWidget(self.pprocessedimg_button)
    self.orgimg_button = QPushButton("Orginal")
    self.orgimg_button.clicked.connect(self._viewOrgimg)
    layout_toggle.addWidget(self.orgimg_button)
    layout_toggle.addStretch(1)
    ## plot images in the next horizontal box | stack original and pre-processed full image.
    layout_imgview = QHBoxLayout()
    self.imgplt = ImgViewer(self)
    self.imgplt.axes.imshow(self.imgPreview_norm)
    self.imgplt2 = ImgViewer(self)
    self.imgplt2.axes.imshow(self.imgPreview_org)
    self.imgplt3 = ImgViewer(self)
    self.imgplt3.axes.imshow(self.imgPreview_oneCell)
    self.imgplt4 = CropsViewer(self)
    self.imgplt4.ax1.imshow(self.dapi_crop)
    self.imgplt4.ax2.imshow(self.ck_crop)
    self.imgplt4.ax3.imshow(self.cd45_crop)
    self.imgplt4.ax4.imshow(self.vim_crop)
    # set the title to subplots
    self.imgplt4.ax1.set_title("dapi")
    self.imgplt4.ax1.axis("off")
    self.imgplt4.ax2.set_title("ck")
    self.imgplt4.ax2.axis("off")
    self.imgplt4.ax3.set_title("cd45")
    self.imgplt4.ax3.axis("off")
    self.imgplt4.ax4.set_title("vimentin")
    self.imgplt4.ax4.axis("off")
    self.layout_imgstack = QStackedLayout()
    self.layout_imgstack.addWidget(self.imgplt)
    self.layout_imgstack.addWidget(self.imgplt2)
    self.layout_imgstack.setCurrentIndex(0)
    layout_imgview.addLayout(self.layout_imgstack, 1)
    layout_imgview.addWidget(self.imgplt3, 1)
    layout_imgview.addWidget(self.imgplt4, 1)
    ## buttons to toggle between results summary and results details.
    layout_resButtons = QHBoxLayout()
    self.resSum_button = QPushButton("Summary")
    self.resSum_button.setStyleSheet("background-color: #b0b0b0;")
    self.resSum_button.clicked.connect(self._viewResSum)
    layout_resButtons.addWidget(self.resSum_button)
    self.deets_button = QPushButton("Details")
    self.deets_button.clicked.connect(self._viewDeets)
    layout_resButtons.addWidget(self.deets_button)
    layout_resButtons.addStretch(1)
    ## stack table of results.
    self.layout_ResStack = QStackedLayout()
    resSum_df = ResTable(self.resSummaryTable)
    viewResSumdf = QTableView()
    viewResSumdf.setModel(resSum_df)
    viewResSumdf.resize(600, 600)
    self.layout_ResStack.addWidget(viewResSumdf)
    resDeets_df = ResTable(self.resDetailsTable)
    viewDeets_df = QTableView()
    viewDeets_df.setModel(resDeets_df)
    viewDeets_df.doubleClicked.connect(self.updateCrops)
    viewDeets_df.resize(600, 600)
    self.layout_ResStack.addWidget(viewDeets_df)
    ## piece grid together
    layout_page = QVBoxLayout()
    layout_page.addLayout(layout_toggle)
    layout_page.addLayout(layout_imgview)
    layout_page.addLayout(layout_resButtons)
    layout_page.addLayout(self.layout_ResStack)
    ## display. 
    widget = QWidget()
    widget.setLayout(layout_page)
    # Set the central widget of the Window.
    self.setCentralWidget(widget)
  ## create menubar. 
  def _createMenuBar(self):
    # create menubar: 
    menuBar = self.menuBar()
    fileMenu = QMenu("&File", self)
    menuBar.addMenu(fileMenu)
    fileMenu.addAction(self.newAction)
    fileMenu.addAction(self.saveAction)
    fileMenu.addAction(self.exportAction)
    fileMenu.addAction(self.exitAction)
    settingsMenu = menuBar.addMenu("&Settings")
    settingsMenu.addAction(self.viewConfigs)
  ## create actions in menubar. 
  def _createActions(self):
    # create actions for the menubar: 
    self.newAction = QAction("&New", self)
    self.newAction.triggered.connect(self.launch_NewProject_window)
    self.saveAction = QAction("&Save", self)
    self.saveAction.triggered.connect(self._saveRes)
    self.exportAction = QAction("&Export Images", self)
    self.exportAction.triggered.connect(self._exportCrops)
    self.exitAction = QAction("&Exit", self)
    self.exitAction.triggered.connect(self._exit)
    self.viewConfigs = QAction("&View Configurations", self)
    self.viewConfigs.triggered.connect(self._viewConfigs)
  ## create toolbar for holding area:
  def _createToolBars(self):
    holdingToolBar = self.addToolBar("File")
    self.addToolBar(Qt.TopToolBarArea, holdingToolBar)
  ## function to view pre-processed image tab: 
  def _viewPPimg(self):
    self.layout_imgstack.setCurrentIndex(0)
    self.orgimg_button.setStyleSheet("background-color: ;")
    self.pprocessedimg_button.setStyleSheet("background-color: #b0b0b0;")
  ## function to view original image tab: 
  def _viewOrgimg(self):
    self.layout_imgstack.setCurrentIndex(1)
    self.orgimg_button.setStyleSheet("background-color: #b0b0b0;")
    self.pprocessedimg_button.setStyleSheet("background-color: ;")
  ## function to view results summary tab: 
  def _viewResSum(self):
    self.layout_ResStack.setCurrentIndex(0)
    self.resSum_button.setStyleSheet("background-color: #b0b0b0;")
    self.deets_button.setStyleSheet("background-color: ;")
  ## function to view pre-processed image tab: 
  def _viewDeets(self):
    self.layout_ResStack.setCurrentIndex(1)
    self.resSum_button.setStyleSheet("background-color: ;")
    self.deets_button.setStyleSheet("background-color: #b0b0b0;")
  ## function to update cell crops: 
  def updateCrops(self, index):
    row = index.row()
    self.j = row
    new_k = self.resDetailsTable.sample_num[row] - 1
    if self.k != new_k:
      self.k = new_k
      self.imgPreview_org, self.imgPreview_norm, self.imgPreview_oneCell, self.dapi_crop, self.ck_crop, self.cd45_crop, self.vim_crop = _generateImgs(self.resDetailsTable, self._imgList, self.k, self.j)
      self.imgplt.axes.clear()  # clear the axes content
      self.imgplt.axes.imshow(self.imgPreview_norm)
      self.imgplt.draw()
      self.imgplt2.axes.clear()
      self.imgplt2.axes.imshow(self.imgPreview_org)
      self.imgplt2.draw()
    elif self.k == new_k:
      self.imgPreview_oneCell, self.dapi_crop, self.ck_crop, self.cd45_crop, self.vim_crop = _generateCrops(self.resDetailsTable, self._imgList[self.k], self.j)
    self.imgplt3.axes.clear()
    self.imgplt3.axes.imshow(self.imgPreview_oneCell)
    self.imgplt3.draw()
    self.imgplt4.ax1.clear()
    self.imgplt4.ax2.clear()
    self.imgplt4.ax3.clear()
    self.imgplt4.ax4.clear()
    self.imgplt4.ax1.imshow(self.dapi_crop)
    self.imgplt4.ax2.imshow(self.ck_crop)
    self.imgplt4.ax3.imshow(self.cd45_crop)
    self.imgplt4.ax4.imshow(self.vim_crop)
    self.imgplt4.ax1.set_title("dapi")
    self.imgplt4.ax1.axis("off")
    self.imgplt4.ax2.set_title("ck")
    self.imgplt4.ax2.axis("off")
    self.imgplt4.ax3.set_title("cd45")
    self.imgplt4.ax3.axis("off")
    self.imgplt4.ax4.set_title("vimentin")
    self.imgplt4.ax4.axis("off")
    self.imgplt4.draw()
  ## create function to launch new project window.
  def launch_NewProject_window(self, checked):
    if self.NPw is None:
      self.NPw = SetupWindow()
    self.NPw.show()
  ## create function to save results to csv.
  def _saveRes(self):
    options = QFileDialog.Options()
    fileName, o = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","csv Files (*.csv)", options=options)
    self.resDetailsTable.to_csv(fileName, index = False)
    fileName_summary = fileName.split('.csv')[0]+' - summary.csv'
    self.resSummaryTable.to_csv(fileName_summary, index = False)
  ## create function to export CTC image crops.
  def _exportCrops(self):
    export_path = QFileDialog.getExistingDirectory(self, "Select folder", expanduser("~"), QFileDialog.ShowDirsOnly)
    self.sWindow = saveWindow(export_path, self.resDetailsTable, self._imgList, self._configs._analysisType)
    self.sWindow.show()
  ## create function to exit project window.
  def _exit(self):
    self.close()
  ## create function to view analysis configurations.
  def _viewConfigs(self, checked):
    self.ConfigWindow = viewConfigWindow(self._configs)
    self.ConfigWindow.show()
