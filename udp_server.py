from socket import *
from ToolBox import *
from threading import Thread, Lock
from PySide2.QtWidgets import QApplication
import json
import MainServer



app = QApplication([])
MainWindow = MainServer.mainServer()
MainWindow.launch()
app.exec_()


