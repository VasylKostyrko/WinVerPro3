import os.path
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

class CondsWindow(QMainWindow):
    def __init__(self):
        super(CondsWindow, self).__init__()
        curdir = os.path.abspath(os.curdir)
        path = curdir + '/design/Conditions.ui'
        self.setWindowTitle("Conditions")
        uic.loadUi(path, self)

        self.btnBack.clicked.connect(self.openMain)

        self.mainWindow = None

    def openMain(self, window):
        window = self.mainWindow
        window.show()
        self.hide()

    def setMain(self, window):
        self.mainWindow = window
