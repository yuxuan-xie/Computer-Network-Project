from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import *


class MessageBox:
    def __init__(self, message, title):
        self.ui = QUiLoader().load('src/client_ui/messageBox.ui')
        self.ui.message.setText(message)
        self.ui.setWindowTitle(title)
        self.ui.setWindowModality(Qt.ApplicationModal)
        self.ui.confirm.clicked.connect(self.handleConfirm)

    def handleConfirm(self):
        self.ui.close()
        pass

    def launch(self):
        self.ui.show()
        self.ui.exec_()
        


