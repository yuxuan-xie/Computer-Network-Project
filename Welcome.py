from PySide2.QtCore import *
from ToolBox import *
import MessageBox
import MainWindow


class Login(Obj):
    def __init__(self, dataSocket, address):
        super(Login, self).__init__(dataSocket, address, 'src/client_ui/login.ui')
        self.username = None
        self.message = None
        self.ui.login.clicked.connect(self.handleLogin)
        self.ui.regis.clicked.connect(self.handleRegister)
        self.ui.forget_password.clicked.connect(self.handleForgetPassword)
        self.ui.setWindowModality(Qt.ApplicationModal)


    def handleForgetPassword(self):
        forgetPassword = ForgetPassword(self.dataSocket, self.address)
        forgetPassword.ui.show()
        forgetPassword.ui.exec_()


    def handleLogin(self):
        # print('login clicked!')
        username = self.ui.username.text()
        password = self.ui.password.text()
        # 发送数据报
        message = HandleMessage.generate(TYPE_LOGIN, username, password)
        UDPMessage.sendUDPMessage(self.dataSocket, self.address, message)
        # 接受数据报
        data, address = UDPMessage.receiveUDPMessage(self.dataSocket)
        ans = HandleMessage.read(data)

        title = '登录结果'
        if ans and (ans != False):
            message = '登录成功'
            MessageBox.MessageBox(message, title).launch()
            self.ui.close()
            MainWindow.MainWindow(self.dataSocket, self.address, username, ans[1], ans[2]).launch()
            self.username = username
        else:
            if ans is None:
                message = '您已登录，无法重复登录'
                MessageBox.MessageBox(message, title).launch()
            else:
                message = '用户名或密码错误'
                MessageBox.MessageBox(message, title).launch()


    def handleRegister(self):
        Register(self.dataSocket, self.address).launch()
        # print('Register clicked!')
        

class Register(Obj):
    def __init__(self, dataSocket, address):
        super(Register, self).__init__(dataSocket, address, 'src/client_ui/register.ui')
        self.ui.regis.clicked.connect(self.handleRegister)
        self.ui.setWindowModality(Qt.ApplicationModal)


    def handleRegister(self):
        username = self.ui.username.text()
        password = self.ui.password.text()
        confirm_password = self.ui.confirm_password.text()
        if (len(password)<8 or len(password)>16) or (len(username) != 11):
                message = '手机号/密码长度不符合规范\n密码长度需大于8位小于16位'
                title = '警告'
                MessageBox.MessageBox(message, title).launch()
        else:
            if password != confirm_password:
                message = '两次密码输入不匹配！'
                title = '警告'
                MessageBox.MessageBox(message, title).launch()
            else:
                # 发送数据报
                message = HandleMessage.generate(TYPE_REGISTER, username, password)
                UDPMessage.sendUDPMessage(self.dataSocket, self.address, message)
                # 接受数据报
                data, address = UDPMessage.receiveUDPMessage(self.dataSocket)
                ans = HandleMessage.read(data)
                if ans is False:
                    message = '该手机号已被注册'
                    title = '提示'
                    MessageBox.MessageBox(message, title).launch()
                else:
                    message = '注册成功'
                    title = '提示'
                    MessageBox.MessageBox(message, title).launch()
                    self.ui.close()


class ForgetPassword(Register):
    def __init__(self,dataSocket, address):
        super(ForgetPassword, self).__init__(dataSocket, address)
        self.ui.setWindowTitle('忘记密码')


    def handleRegister(self):
        username = self.ui.username.text()
        password = self.ui.password.text()
        confirm_password = self.ui.confirm_password.text()
        if (len(password) < 8 or len(password) > 16) or (len(username) != 11):
            message = '手机号/密码长度不符合规范\n密码长度需大于8位小于16位'
            title = '警告'
            MessageBox.MessageBox(message, title).launch()
        else:
            if password != confirm_password:
                message = '两次密码输入不匹配！'
                title = '警告'
                MessageBox.MessageBox(message, title).launch()
            else:
                # 发送数据报
                message = HandleMessage.generate(TYPE_FORGET_PASSWORD, username, password)
                UDPMessage.sendUDPMessage(self.dataSocket, self.address, message)
                # 接收数据报
                data, address = UDPMessage.receiveUDPMessage(self.dataSocket)
                ans = HandleMessage.read(data)
                if ans is False:
                    message = '未找到该用户\n请检查输入或前往注册'
                    title = '警告'
                    MessageBox.MessageBox(message, title).launch()
                else:
                    message = '密码修改成功'
                    title = '提示'
                    MessageBox.MessageBox(message, title).launch()
                    self.ui.close()
