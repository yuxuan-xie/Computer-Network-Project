from socket import socket, AF_INET, SOCK_DGRAM

from PySide2.QtWidgets import QTableWidgetItem

from MySignal import mySignal
from ToolBox import *
from threading import *

IP = ''
PORT = 4396
BUFFER_LENGTH = 1024
address = (IP, PORT)

class mainServer(Obj):
    def __init__(self):
        super(mainServer, self).__init__(dataSocket=None, address=None, filepath='src/server_ui/MainWindow.ui')
        self.listenSocket = socket(AF_INET, SOCK_DGRAM)
        self.listenSocket.bind((IP, PORT))

        self.ms = mySignal()
        self.ms.command.connect(self.update)
        self.ms.receivedMessage.connect(self.update)
        self.ms.update.connect(self.updateWithSend)

        self.numberOfMask = 1000
        self.onlineUser = {}
        self.dic = self.readUserID()
        self.admin = self.readAdmin()
        self.adminDic = self.initAdminDic()
        self.choose = self.admin[0]

        self.ui.setWindowTitle('控制台')
        self.ui.admin.addItems(self.admin)
        self.ui.admin.currentIndexChanged.connect(self.handleSelectionChange)
        self.initadminInfo()

        self.ui.add.clicked.connect(self.handleAdd)
        self.ui.delete_2.clicked.connect(self.handleDelete)
        self.ui.kick.clicked.connect(self.handleKick)
        self.ui.send.clicked.connect(self.handleSend)
        self.ui.start.clicked.connect(self.handleStart)
        self.ui.handOut.clicked.connect(self.handleHandOut)

        self.lock = Lock()
        self.updateWindow()

    def handleHandOut(self):
        if self.adminDic[self.choose]["Activate"] == "是":
            self.adminDic[self.choose]["Activate"] = "否"
        else:
            self.ms.command.emit(self.ui.command, "该区域未启动口罩预约！")
            return
        message = HandleMessage.generate(TYPE_MESSAGE_BACK, "Server Admin", "您的口罩已发放，请尽快前往所预约行政区内的定点场所领取！")
        for each in self.adminDic[self.choose]['Usr']:
            if each in self.onlineUser:
                UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
        message = self.generateLoginSuccessMessage()
        for each in self.onlineUser:
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
        self.updateWindow()

    def handleStart(self):
        if self.adminDic[self.choose]["Activate"] == "否":
            self.adminDic[self.choose]["Activate"] = "是"
        else:
            self.ms.command.emit(self.ui.command, "该区域已启动口罩预约！")
            return
        message = self.generateLoginSuccessMessage()
        for each in self.onlineUser:
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
        self.initadminInfo()
        self.handleSelectionChange()

    def handleSend(self):
        text = self.ui.toSend.toPlainText()
        if len(text) == 0:
            self.ms.command.emit(self.ui.command, "发送内容不能为空")
        else:
            if len(text) > 140:
                self.ms.command.emit(self.ui.command, "长度超过上限")
                # 最多140个中文字符
            else:
                user = self.ui.targetUser.text()
                if user == '':
                    message = HandleMessage.generate(TYPE_MESSAGE_BACK, "Server Admin", text)
                    for eachUser in self.onlineUser:
                        UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[eachUser], message)
                        self.ms.receivedMessage.emit(self.ui.MessageBox, '来自：' + "Server Admin" + '\n' + '正文：\n' + text + '\n' + '------------------------------')
                else:
                    message = HandleMessage.generate(TYPE_MESSAGE_BACK, "Server Admin", text)
                    if self.onlineUser.get(user) is None:
                        self.ms.command.emit(self.ui.command, f'user {user} is offline!')
                    else:
                        UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[user], message)
                        self.ms.receivedMessage.emit(self.ui.MessageBox,
                                                     '来自：' + "Server Admin" + '\n' +'发往：' + user + '\n' + '正文：\n' + text + '\n' + '------------------------------')
                self.ui.toSend.clear()
                self.ui.targetUser.clear()

    def handleKick(self):
        toKick = self.ui.toKick.text()
        self.ui.toKick.clear()
        if toKick not in self.adminDic[self.choose]["Usr"]:
            self.ms.command.emit(self.ui.command, f'User {toKick} not found!')
            return
        self.adminDic[self.choose]["Usr"].remove(toKick)
        message = self.generateLoginSuccessMessage()
        for each in self.onlineUser:
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
        if toKick in self.onlineUser:
            message = HandleMessage.generate(TYPE_KICK, self.choose)
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[toKick], message)
        self.updateWindow()

    def handleDelete(self):
        toDelete = self.ui.toDelete.text()
        self.ui.toDelete.clear()
        if toDelete not in self.adminDic:
            self.ms.command.emit(self.ui.command, f'admin {toDelete} not found!')
            return
        elif self.adminDic[toDelete]['Activate'] == '是':
            self.ms.command.emit(self.ui.command, f'admin {toDelete} can not be deleted now!')
            return
        else:
            self.adminDic.pop(toDelete, None)
            self.admin.remove(toDelete)
        message = self.generateLoginSuccessMessage()
        for each in self.onlineUser:
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
        self.updateWindow()

    def handleAdd(self):
        toAdd = self.ui.toAdd.text()
        self.ui.toAdd.clear()
        if toAdd in self.adminDic:
            self.ms.command.emit(self.ui.command, "无法创建同名行政区")
            return
        temp = {toAdd:{
            "Usr": ["admin"],
            "Activate": "否",
            "Total":self.numberOfMask
        }}
        self.adminDic.update(temp)
        self.admin.append(toAdd)
        message = self.generateLoginSuccessMessage()
        for each in self.onlineUser:
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
        self.updateWindow()

    def update(self, widget, text):
        widget.append(str(text))
        self.ui.MessageBox.ensureCursorVisible()

    def launch(self):
        thread = Thread(target=mainServer.__listen, args=(self,), daemon=True)
        thread.start()
        self.ui.show()

    def __listen(self):
        self.ms.command.emit(self.ui.command, f"启动成功，正在端口{PORT}等待连接")
        while True:
            datagram, address = self.listenSocket.recvfrom(BUFFER_LENGTH)
            datagram = datagram.decode()
            datagram = json.loads(datagram)
            switch = {
                TYPE_LOGIN: self.login,
                TYPE_REGISTER: self.register,
                TYPE_FORGET_PASSWORD: self.forgetPassword,
                TYPE_QUIT: self.quit,
                TYPE_MESSAGE: self.groupMessage,
                TYPE_BOOK: self.book
            }

            case = switch.get(datagram["Type"], self.default)
            thread = Thread(target=case, args=(datagram, address))
            thread.start()

    def book(self, datagram, address):
        self.lock.acquire()
        username = datagram['1']
        admin = datagram['2']
        if self.adminDic[admin]['Activate'] == '是':
            if self.adminDic[admin]['Total'] - len(self.adminDic[admin]['Usr']) > 0:
                if self.check(username):
                    self.adminDic[admin]['Usr'].append(username)
                    self.ms.update.emit()
                    message = HandleMessage.generate(TYPE_BOOK_OK, admin)
                else:
                    message = HandleMessage.generate(TYPE_BOOK_REJECT, admin)
            else:
                message = HandleMessage.generate(TYPE_BOOK_FULL, admin)
        else:
            message = HandleMessage.generate(TYPE_BOOK_NOT_ACTIVATE, admin)
        UDPMessage.sendUDPMessage(self.listenSocket, address, message)
        self.lock.release()

    def readUserID(self):
        dic = {"test": "test"}
        f = open(file='UserID.txt', encoding='utf-8')
        for eachLine in f.readlines():
            userInfo = eachLine.split(',', 1)
            username = userInfo[0]
            password = userInfo[1]
            password = password.strip('\n')
            dic_temp = {username: password}
            dic.update(dic_temp)
        f.close()
        return dic

    def readAdmin(self):
        vec = []
        f = open('Admin.txt', encoding='utf-8')
        for eachLine in f.readlines():
            admin = eachLine.strip('\n')
            vec.append(admin)
        f.close()
        return vec

    def login(self, datagram, address):
        self.lock.acquire()
        username = datagram['1']
        password = datagram['2']
        result = self.dic.get(username, None)
        if result == password:
            if self.onlineUser.get(username, None) is None:
                userInfo = {username: address}
                self.onlineUser.update(userInfo)
                self.ms.command.emit(self.ui.command, self.onlineUser.__str__())
                ans = TYPE_LOGIN_SUCCESS
            else:
                ans = TYPE_REJECT
        else:
            ans = TYPE_FAIL

        if ans is TYPE_LOGIN_SUCCESS:
            message = self.generateLoginSuccessMessage()
        else:
            message = HandleMessage.generate(ans)
        self.lock.release()
        UDPMessage.sendUDPMessage(self.listenSocket, address, message)

    def register(self, datagram, address):
        self.lock.acquire()
        username = datagram['1']
        password = datagram['2']
        result = self.dic.get(username, None)
        if result is None:
            temp = {username: password}
            self.dic.update(temp)
            ans = TYPE_OK
            f = open(file='UserID.txt', mode='a', encoding='utf-8')
            f.write(username + ',' + password + '\n')
            f.flush()
            f.close()
        else:
            ans = TYPE_FAIL
        self.lock.release()
        message = HandleMessage.generate(ans)
        UDPMessage.sendUDPMessage(self.listenSocket, address, message)

    def forgetPassword(self, datagram, address):
        self.lock.acquire()
        username = datagram['1']
        password = datagram['2']
        result = self.dic.get(username, None)
        if result is None:
            ans = TYPE_FAIL
        else:
            ans = TYPE_OK
            f = open(file='UserID.txt', mode='r+', encoding='utf-8')
            t = f.read()
            old = datagram['1'] + ',' + self.dic[datagram['1']] + '\n'
            new = datagram['1'] + ',' + datagram['2'] + '\n'
            t = t.replace(old, new)
            f.seek(0, 0)
            f.write(t)
            f.flush()
            f.close()
            temp = {username: password}
            self.dic.update(temp)
        self.lock.release()
        message = HandleMessage.generate(ans)
        UDPMessage.sendUDPMessage(self.listenSocket, address, message)

    def groupMessage(self, datagram, address):
        self.lock.acquire()
        message = HandleMessage.generate(TYPE_MESSAGE_BACK, datagram['1'], datagram['2'])
        for each in self.onlineUser:
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
        self.lock.release()
        self.ms.receivedMessage.emit(self.ui.MessageBox, '来自：' + datagram['1'] + '\n' + '正文：\n' + datagram['2'] + '\n' + '------------------------------')

    def quit(self, datagram, address):
        self.lock.acquire()
        username = datagram['1']
        self.onlineUser.pop(username, None)
        self.lock.release()

    def default(self, datagram):
        # TODO
        pass

    def initAdminDic(self):
        admin = self.admin
        adminDic = {}
        for each in admin:
            dic_stat = {
                "Usr":["admin"],
                "Activate":"否",
                "Total":self.numberOfMask
                        }
            dic_temp = {each:dic_stat}
            adminDic.update(dic_temp)
        return adminDic

    def handleSelectionChange(self):
        self.ui.queue.setRowCount(self.numberOfMask)
        self.choose = self.ui.admin.currentText()
        if self.choose == '':
            return

        Activate = self.adminDic[self.choose]["Activate"]
        isActivate = QTableWidgetItem()
        isActivate.setText(Activate)
        self.ui.detail.setItem(0,1,isActivate)

        n = len(self.adminDic[self.choose]["Usr"])
        number = QTableWidgetItem()
        number.setText(str(n))
        self.ui.detail.setItem(0,2,number)

        n = self.numberOfMask - n
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

    def initadminInfo(self):
        self.ui.adminInfo.setRowCount(0)
        admin = self.admin
        for each in admin:
            self.ui.adminInfo.insertRow(0)
            item = QTableWidgetItem()
            item.setText(each)
            self.ui.adminInfo.setItem(0, 0, item)

    def wrapLoginSuccess(self):
        ret = ''
        for each in self.admin:
            ret = ret + each + ','
        return ret

    def generateLoginSuccessMessage(self):
        message = {
            'Type': TYPE_LOGIN_SUCCESS,
            '1': self.wrapLoginSuccess(),
            '2': self.adminDic
        }
        return message

    def updateWindow(self):
        self.initadminInfo()
        self.handleSelectionChange()
        self.ui.admin.clear()
        self.ui.admin.addItems(self.admin)

    def check(self, username):
        for each in self.adminDic:
            if username in self.adminDic[each]['Usr']:
                return False
        return True

    def updateWithSend(self):
        self.updateWindow()
        message = self.generateLoginSuccessMessage()
        for each in self.onlineUser:
            UDPMessage.sendUDPMessage(self.listenSocket, self.onlineUser[each], message)
