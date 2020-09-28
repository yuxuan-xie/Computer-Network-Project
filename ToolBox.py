from PySide2.QtUiTools import QUiLoader
import json

BUFFER_LENGTH = 1024

TYPE_LOGIN = 0x0  # 用户端登录请求
TYPE_REGISTER = 0x1  # 用户端注册请求
TYPE_FORGET_PASSWORD = 0x2  # 用户端忘记密码/修改密码请求
TYPE_QUIT = 0x3  # 用户端退出请求
TYPE_MESSAGE = 0x4  # 用户端发送消息（GroupMessage）请求
TYPE_BOOK = 0x5  # 用户端申请预约请求


TYPE_OK = 0x10  # 登陆通过响应
TYPE_FAIL = 0X20  # 登录失败（密码错误）响应
TYPE_REJECT = 0x30  # 登陆失败（重复登陆）响应
TYPE_LOGIN_SUCCESS = 0x40  # 登陆成功、每次更新行政区列表等核心数据结构时使用的消息头
TYPE_MESSAGE_BACK = 0x50  # 服务端发往客户端的消息
TYPE_BOOK_OK = 0x60  # 预约成功响应
TYPE_BOOK_FULL = 0x70  # 预约失败（预约名额已满）响应
TYPE_BOOK_REJECT = 0x80  # 预约失败（多次预约）响应
TYPE_BOOK_NOT_ACTIVATE = 0x90  # 预约失败（该行政区未启动预约）响应
TYPE_KICK = 0Xa0  # 用户被踢出预约队列通知


class Obj:
    def __init__(self, dataSocket, address, filepath):
        self.dataSocket = dataSocket
        self.address = address
        self.ui = QUiLoader().load(filepath)

    def launch(self):
        self.ui.show()
        self.ui.exec_()


class UDPMessage:
    @staticmethod
    def sendUDPMessage(dataSocket, address, message):
        message = json.dumps(message).encode()
        dataSocket.sendto(message, address)

    @staticmethod
    def receiveUDPMessage(dataSocket):
        data,address = dataSocket.recvfrom(BUFFER_LENGTH)
        return data, address


class HandleMessage:
    @staticmethod
    def read(message):
        message.decode()
        message = json.loads(message)
        print(message)
        switch ={
            TYPE_OK: HandleMessage.__readOK,
            TYPE_FAIL: HandleMessage.__readFAIL,
            TYPE_REJECT: HandleMessage.__readREJECT,
            TYPE_LOGIN_SUCCESS: HandleMessage.__readLoginSuccess,
            TYPE_MESSAGE_BACK: HandleMessage.__readMessageBack,
            TYPE_LOGIN: HandleMessage.__readLogin,
            TYPE_REGISTER: HandleMessage.__readRegister,
            TYPE_FORGET_PASSWORD: HandleMessage.__readForgetPassword,
            TYPE_QUIT: HandleMessage.__readQuit,
            TYPE_MESSAGE: HandleMessage.__readMessage,
            TYPE_BOOK_OK: HandleMessage.__readBookOK,
            TYPE_BOOK_FULL: HandleMessage.__readBookFull,
            TYPE_BOOK_REJECT: HandleMessage.__readBookReject,
            TYPE_KICK: HandleMessage.__readKick,
            TYPE_BOOK_NOT_ACTIVATE: HandleMessage.__readBookNotActivate
        }
        ans = switch.get(message['Type'], HandleMessage.__default)(message)
        return ans

    @staticmethod
    def __readBookNotActivate(message):
        return "book", False,  "Server Admin" + '\n' + '正文：\n' + "对 " + message['1'] + ' 的预约失败' + '\n' "原因：\n该区域未启动口罩预约\n"+ '------------------------------'

    @staticmethod
    def __readKick(message):
        return "kick", '来自：' + "Server Admin" + '\n' + '正文：\n' + "您已被踢出 " + message['1'] + ' 的预约队列' + '\n' + '------------------------------'

    @staticmethod
    def __readBookOK(message):
        return "book",True, '来自：' + "Server Admin" + '\n' + '正文：\n' + "恭喜您，您已成功参与 " + message['1'] + ' 的预约' + '\n' + '------------------------------'

    @staticmethod
    def __readBookReject(message):
        return "book",False, '来自：' + "Server Admin" + '\n' + '正文：\n' + "对 " + message['1'] + ' 的预约失败' + '\n' "原因：\n您已参与过预约\n"+ '------------------------------'

    @staticmethod
    def __readBookFull(message):
        return "book", False, '来自：' + "Server Admin" + '\n' + '正文：\n' + "对 " + message['1'] + ' 的预约失败' + '\n' "原因：\n预约名额已满\n"+ '------------------------------'

    @staticmethod
    def __readOK(message):
        return True


    @staticmethod
    def __readFAIL(message):
        return False

    @staticmethod
    def __readREJECT(message):
        return None

    @staticmethod
    def __readLoginSuccess(message):
        return 'update', message['1'], message['2']

    @staticmethod
    def __readMessageBack(message):
        str1 = 'MessageBox'
        str2 = '来自：' + message['1'] + '\n' + '正文：\n' + message['2'] + '\n' + '------------------------------'
        return str1, str2;


    @staticmethod
    def __readLogin(message):
        return message['1'], message['2']

    @staticmethod
    def __readRegister(message):
        return message['1'], message['2']

    @staticmethod
    def __readForgetPassword(message):
        return message['1'], message['2']

    @staticmethod
    def __readQuit(message):
        return message['1']

    @staticmethod
    def __readMessage(message):
        return message['1'], message['2']

    @staticmethod
    def __default():
        pass

    @staticmethod
    def generate(Type, str1=None, str2=None, str3=None, str4=None):
        switch = {
            TYPE_LOGIN: HandleMessage.__generateLogin,
            TYPE_REGISTER: HandleMessage.__generateRegister,
            TYPE_FORGET_PASSWORD: HandleMessage.__generateForgetPassword,
            TYPE_QUIT: HandleMessage.__generateQuit,
            TYPE_MESSAGE: HandleMessage.__generateMessage,
            TYPE_OK: HandleMessage.__generateOK,
            TYPE_FAIL: HandleMessage.__generateFAIL,
            TYPE_REJECT: HandleMessage.__generateREJECT,
            TYPE_LOGIN_SUCCESS: HandleMessage.__generateLoginSuccess,
            TYPE_MESSAGE_BACK: HandleMessage.__generateMessageBack,
            TYPE_BOOK: HandleMessage.__generateBook,
            TYPE_BOOK_OK: HandleMessage.__generateBookOK,
            TYPE_BOOK_FULL: HandleMessage.__generateBookFull,
            TYPE_BOOK_REJECT: HandleMessage.__generateBookReject,
            TYPE_KICK: HandleMessage.__generateKick,
            TYPE_BOOK_NOT_ACTIVATE: HandleMessage.__generateBookNotActivate
        }
        message = switch.get(Type, HandleMessage.__default)(str1, str2, str3, str4)
        print(message)
        return message

    @staticmethod
    def __generateBookNotActivate(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type':TYPE_BOOK_NOT_ACTIVATE,
            '1':str1
        }
        return message

    @staticmethod
    def __generateKick(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type':TYPE_KICK,
            '1':str1
        }
        return message

    @staticmethod
    def __generateBookOK(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type':TYPE_BOOK_OK,
            '1':str1
        }
        return message

    @staticmethod
    def __generateBookFull(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type':TYPE_BOOK_FULL,
            '1':str1
        }
        return message

    @staticmethod
    def __generateBookReject(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_BOOK_REJECT,
            '1': str1
        }
        return message

    @staticmethod
    def __generateBook(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type':TYPE_BOOK,
            '1':str1,
            '2':str2
        }
        return message

    @staticmethod
    def __generateLogin(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_LOGIN,
            '1': str1,
            '2': str2
        }
        return message


    @staticmethod
    def __generateRegister(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_REGISTER,
            '1': str1,
            '2': str2
        }
        return message


    @staticmethod
    def __generateForgetPassword(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_FORGET_PASSWORD,
            '1': str1,
            '2': str2
        }
        return message


    @staticmethod
    def __generateQuit(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_QUIT,
            '1': str1
        }
        return message


    @staticmethod
    def __generateMessage(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_MESSAGE,
            '1': str1,
            '2': str2
        }
        return message

    @staticmethod
    def __generateOK(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_OK
        }
        return message

    @staticmethod
    def __generateFAIL(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_FAIL
        }
        return message

    @staticmethod
    def __generateREJECT(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_REJECT
        }
        return message

    @staticmethod
    def __generateLoginSuccess(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_LOGIN_SUCCESS,
            '1': str1
        }
        return message

    @staticmethod
    def __generateMessageBack(str1=None, str2=None, str3=None, str4=None):
        message = {
            'Type': TYPE_MESSAGE_BACK,
            '1': str1,
            '2': str2
        }
        return message



