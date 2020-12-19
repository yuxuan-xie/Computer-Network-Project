####################################
# Author: Yuxuan Xie
# Version: 1.0 Alpha
####################################

from socket import *
from PySide2.QtWidgets import QApplication
import Welcome
from ToolBox import *

# 云服务器地址
# IP = '175.24.66.62'
# 测试地址
IP = '127.0.0.1'
SERVER_PORT = 4396
address = (IP, SERVER_PORT)
BUFFER_LENGTH = 1024
THREAD_FLAG = 1

dataSocket = socket(AF_INET, SOCK_DGRAM)

# 启动主界面（登陆界面）
app = QApplication([])
login = Welcome.Login(dataSocket, address)
login.ui.show()
app.exec_()

# 退出主界面后发送下线信息
username = login.username
message = HandleMessage.generate(TYPE_QUIT, username)
UDPMessage.sendUDPMessage(dataSocket, address, message)

dataSocket.close()
