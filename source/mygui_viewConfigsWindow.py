import PyQt5
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QSize, Qt, QAbstractTableModel
from PyQt5.QtGui import QIcon

class viewConfigWindow(QMainWindow):
  def __init__(self, configs):
    super().__init__()
    self.setWindowIcon(QIcon('../CTC-Quant Icon.png'))
    self.setWindowTitle("Project Configs")
    self.setFixedSize(QSize(350, 450)) # set the size of the window.
    self._configs = configs
    ## create window layout.
    layout = QVBoxLayout()
    layout.addWidget(QLabel('Analysis Type: '+self._configs._analysisType))
    layout.addWidget(QLabel('Directory: '+self._configs.dir_path))
    layout.addWidget(QLabel('Dapi Filename: '+self._configs._dapiFilename))
    layout.addWidget(QLabel('Ck Filename: '+self._configs._ckFilename))
    layout.addWidget(QLabel('Cd45 Filename: '+self._configs._cd45Filename))
    layout.addWidget(QLabel('Vimentin Filename: '+self._configs._vimFilename))
    layout.addWidget(QLabel('Image Height (in mm): '+str(self._configs.img_height)))
    layout.addWidget(QLabel('Image Width (in mm): '+str(self._configs.img_width)))
    layout.addWidget(QLabel('Min Cell Diameter (in mm): '+str(self._configs.min_cellD)))
    layout.addWidget(QLabel('Denoise Weight: '+str(self._configs.denoise_weight)))
    layout.addWidget(QLabel('Filter Confidence: '+self._configs.filt_conf))
    layout.addWidget(QLabel('Cancer Type: '+self._configs._cancerModel))
    button_layout = QHBoxLayout()
    button_layout.addStretch(1)
    ok_button = QPushButton('Ok')
    ok_button.clicked.connect(self.ok)
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)
    ## display.
    widget = QWidget()
    widget.setLayout(layout)
    self.setCentralWidget(widget)
  ## batch option status. 
  def ok(self):
    self.close()
