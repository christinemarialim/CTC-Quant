import os
import sys
import PyQt5
from PyQt5.QtWidgets import QApplication
os.chdir('C:/Users/chris/Desktop/JM-imgs/source')
from mygui_setupWindow import *

if __name__ == '__main__':
  app = QApplication([])
  w = SetupWindow()
  w.show()
  sys.exit(app.exec())