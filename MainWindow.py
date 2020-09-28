from PySide2.QtWidgets import QTableWidgetItem

from ToolBox import *
from threading import Thread, Lock
import MessageBox
from MySignal import mySignal

class MainWindow(Obj):
    def __init__(self, dataSocket, address, username, admin, adminDic):
        super(MainWindow, self).__init__(dataSocket, address, 'src/client_ui/MainWindow.ui')
        self.ui.setWindowTitle("用户："+username)
        self.ui.send.clicked.connect(self.handleSend)
        self.username = username
        self.admin = admin.strip(',').split(',')
        self.adminDic =adminDic
        self.lock = Lock()

        self.ui.admin.addItems(self.admin)
        self.ui.admin.currentIndexChanged.connect(self.handleSelectionChange)
        self.ui.book.clicked.connect(self.handleBook)
        self.initadminInfo()

        self.ms = mySignal()
        self.ms.receivedMessage.connect(self.print2Gui)
        self.ms.update.connect(self.updateWindow)
        self.choose = self.admin[0]

        self.updateWindow()

    def handleBook(self):
        message = HandleMessage.generate(TYPE_BOOK, self.username, self.choose)
        UDPMessage.sendUDPMessage(self.dataSocket, self.address, message)

    def handleSelectionChange(self):
        self.choose = self.ui.admin.currentText()
        if self.choose == '':
            return
        total = self.adminDic[self.choose]["Total"]
        self.ui.queue.setRowCount(total)
        Activate = self.adminDic[self.choose]["Activate"]
        isActivate = QTableWidgetItem()
        isActivate.setText(Activate)
        self.ui.detail.setItem(0,1,isActivate)

        n = len(self.adminDic[self.choose]["Usr"])
        number = QTableWidgetItem()
        number.setText(str(n))
        self.ui.detail.setItem(0,2,number)

        n = total - n
        number = QTableWidgetItem()
        number.setText(str(n))
        self.ui.detail.setItem(0, 3, number)

        number = QTableWidgetItem()
        number.setText(str(n))
        self.ui.detail.setItem(0, 4, number)

        i = 0
        self.ui.queue.clear()
        for each in self.adminDic[self.choose]["Usr"]:
            item = QTableWidgetItem()
            item.setText(each)
            self.ui.queue.setItem(i, 0, item)
            i += 1

    def print2Gui(self,widget,text):
        widget.append(str(text))
        self.ui.MessageBox.ensureCursorVisible()

    def handleSend(self):
        text = self.ui.toSend.toPlainText()
        if len(text) == 0:
            MessageBox.MessageBox("发送内容不能为空", "警告").launch()
        else:
            if len(text) > 140:
                MessageBox.MessageBox('长度超过上限', '警告').launch()
                # 最多140个中文字符
            else:
                message = HandleMessage.generate(TYPE_MESSAGE, self.username, text)
                UDPMessage.sendUDPMessage(self.dataSocket, self.address, message)
                self.ui.toSend.clear()

    def launch(self):
        thread = Thread (target=MainWindow.__listen, args=(self,), daemon=True)
        thread.start()
        self.ui.show()
        self.ui.exec_()

    def __listen(self):
        try:
            while True:
                data, address = UDPMessage.receiveUDPMessage(self.dataSocket)
                ans = HandleMessage.read(data)
                if ans[0] == 'MessageBox':
                    self.ms.receivedMessage.emit(self.ui.MessageBox, ans[1])
                elif ans[0] == 'update':
                    self.ms.update.emit()
                    self.lock.acquire()
                    self.admin = ans[1].strip(',').split(',')
                    self.adminDic = ans[2]
                    self.lock.release()
                elif ans[0] == 'book':
                    self.ms.receivedMessage.emit(self.ui.MessageBox, ans[2])
                elif ans[0] == 'kick':
                    self.ms.receivedMessage.emit(self.ui.MessageBox, ans[1])
        except OSError:
            return

    def initadminInfo(self):
        self.ui.adminInfo.setRowCount(0)
        admin = self.admin
        for each in admin:
            self.ui.adminInfo.insertRow(0)
            item = QTableWidgetItem()
            item.setText(each)
            self.ui.adminInfo.setItem(0, 0, item)


    def updateWindow(self):
        self.initadminInfo()
        self.handleSelectionChange()
        self.ui.admin.clear()
        self.ui.admin.addItems(self.admin)