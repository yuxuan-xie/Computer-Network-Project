from PySide2.QtCore import Signal, QObject
from PySide2.QtWidgets import QTextBrowser


class mySignal(QObject):
    receivedMessage = Signal(QTextBrowser, str)
    command = Signal(QTextBrowser, str)
    update = Signal()