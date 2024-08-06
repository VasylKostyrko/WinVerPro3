from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWidgets import QHeaderView
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5 import uic
import sys
import os.path
import ctypes
import json
from verification.showintable import viewErrMsg, testLang, getTextLang
from z3py.z3counter import z3countP, z3counterEx


class Ui(QMainWindow):
    """Реалізація вікон та діалогу на базі бібліотеки PyQT5"""
    def __init__(self):
        super(Ui, self).__init__()
        curdir = os.path.abspath(os.curdir)
        path = curdir + '\\design\\counterEx.ui'
        uic.loadUi(path, self)

        self.setWindowState(QtCore.Qt.WindowMaximized)
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        # Розташовуємо таблицю
        table = self.tableWidget
        hpanel = 40
        table.setGeometry(20, hpanel, width - 40, height - hpanel - 100)
        header = table.horizontalHeader()
        table.horizontalHeader().setStyleSheet("QHeaderView::section{font-weight:bold; color:#46647F}")
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        table.setRowCount(4)
        table.setHorizontalHeaderLabels([""])
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)   # Табличний віджет не редагується

        self.options = {}   # Словник параметрів системи
        self.messLang = {}  # Словник повідомлень українською та англійською мовами
        self.program = ""
        self.language = "en"
        self.ctype = ""
        self.cnum = 0

        self.btnCond.clicked.connect(self.showCond)         # Відобразити умову
        self.btnBuild.clicked.connect(self.buildCE)         # Побудувати контрприклад
        self.btnOptions.clicked.connect(self.viewOptions)   # Перегляд системних параметрів

        self.getOptions()
        lang = self.language
        ok = testLang(self, lang)
        if not ok:
            self.setInvalid()
            return

        messLang = getTextLang(lang)
        if messLang == "":
            errMsg = "Error: no translation dictionary found!"
            viewErrMsg(self, errMsg)
            self.setInvalid()
            return

        self.messLang = messLang
        self.setTextMenu()
        bldCoEx = messLang["bldCoEx"]
        self.setWindowTitle(bldCoEx)

        self.showCond()

    def changeEvent(self, event):
        """Обробник подій зміни стану вікна: Максимізувати, Нормалізувати."""
        if event.type() == QtCore.QEvent.WindowStateChange:
            table = self.tableWidget
            # Змінені розміри вікна
            width = self.width()
            height = self.height()
            hpanel = 40        # Висота панелі
            table.setGeometry(20, hpanel, width - 40, height - hpanel - 40)
        super(QMainWindow, self).changeEvent(event)

    def getOptions(self):
        """Відображає в таблиці параметри системи."""
        messLang = self.messLang
        curdir = os.path.abspath(os.curdir)
        fname = curdir + '\\options.json'
        if not os.path.isfile(fname):
            errMsg = messLang["errOptFile"]
            viewErrMsg(self, errMsg)
            self.setInvalid()
            return

        with open(fname, 'r', encoding='utf-8') as file_object:
            params = json.load(file_object)
        self.options = params
        self.language = params["language"]
        self.program = params["program"]  # Ім'я аналізованої програми

    def viewOptions(self):
        """Показати системні параметри"""
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        messLang = self.messLang
        hdrOpt = messLang["hdrOpt"]
        hdrVal = messLang["hdrVal"]
        table.setHorizontalHeaderLabels([hdrOpt, hdrVal])
        params = self.options
        npar = 0
        parNames = params.keys()
        for parName in parNames:
            npar += 1
            table.setRowCount(npar)
            cell = QTableWidgetItem(parName)
            table.setItem(npar - 1, 0, cell)
            parVal = params[parName]
            if type(parVal) is not str:
                parVal = str(parVal)
            cell = QTableWidgetItem(parVal)
            table.setItem(npar - 1, 1, cell)
        table.resizeColumnsToContents()

    def setInvalid(self):
        """Робить недосткупними всі операції меню."""
        self.btnCond.setEnabled(False)
        self.btnBuild.setEnabled(False)
        self.btnOptions.setEnabled(False)

    def showCond(self):
        """Відобразити в таблиці сумнівну умову"""
        messLang = self.messLang
        curdir = os.path.abspath(os.curdir)
        condFile = curdir + "//z3py//z3counter.py"
        if not os.path.isfile(condFile):
            errMsg = messLang["errCEFile"]
            viewErrMsg(self, errMsg)
            self.setInvalid()
            return
        parList = z3countP()
        if len(parList) != 4:
            errMsg = messLang["errCEnum"]
            viewErrMsg(self, errMsg)
            self.setInvalid()
            return

        program = parList[0]
        trackNum = parList[1]
        condType = parList[2]
        cond = parList[3]

        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrOpt = messLang["hdrOpt"]
        hdrVal = messLang["hdrVal"]
        table.setHorizontalHeaderLabels([hdrOpt, hdrVal])
        table.setRowCount(4)
        btnProgram = messLang["btnProgram"]
        cell = QTableWidgetItem(btnProgram)
        table.setItem(0, 0, cell)
        cell = QTableWidgetItem(program)
        table.setItem(0, 1, cell)
        hdrTrack = messLang["hdrTrack"]
        cell = QTableWidgetItem(hdrTrack)
        table.setItem(1, 0, cell)
        cell = QTableWidgetItem(str(trackNum))
        table.setItem(1, 1, cell)
        condType = messLang["condType"]
        cell = QTableWidgetItem(condType)
        table.setItem(2, 0, cell)
        conditionType = findCondType(condType)
        cell = QTableWidgetItem(conditionType)
        table.setItem(2, 1, cell)
        btnCond = messLang["btnCond"]
        cell = QTableWidgetItem(btnCond)
        table.setItem(3, 0, cell)
        cell = QTableWidgetItem(cond)
        table.setItem(3, 1, cell)
        table.resizeColumnsToContents()

    def buildCE(self):
        """Побудувати контрприклад для вибраної умови."""
        messLang = self.messLang
        parList = z3counterEx()
        condVal = parList[0]
        parNameList = parList[1]
        parValList = parList[2]
        sVal = str(condVal)
        table = self.tableWidget
        table.clear()
        table.setColumnCount(2)
        hdrParam = messLang["hdrParam"]
        hdrVal = messLang["hdrVal"]
        table.setHorizontalHeaderLabels([hdrParam, hdrVal])
        table.setRowCount(1)

        table.setSpan(0, 0, 2, 1)
        if sVal == "sat":
            condRes = messLang["condNIT"]
        else:
            condRes = messLang["condIT"]
        table.setSpan(0, 0, 1, 2)
        cell = QTableWidgetItem(condRes)
        cell.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        table.setItem(0, 0, cell)
        if sVal == "sat":
            num = len(parNameList)
            table.setRowCount(1 + num)

            for n in range(num):
                parName = parNameList[n]
                parVal = parValList[n]
                cell = QTableWidgetItem(parName)
                table.setItem(n + 1, 0, cell)
                cell = QTableWidgetItem(str(parVal))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(n + 1, 1, cell)
        table.resizeColumnsToContents()

    def setTextMenu(self):
        """Транслює меню на мову користувача."""
        messLang = self.messLang
        textMenu = messLang["btnCond"]
        self.btnCond.setText(textMenu)
        tipCond = messLang["tipCond"]
        self.btnCond.setToolTip(tipCond)

        textMenu = messLang["btnBuild"]
        self.btnBuild.setText(textMenu)
        tipBuild = messLang["tipBuild"]
        self.btnBuild.setToolTip(tipBuild)

        textMenu = messLang["btnOptions"]
        self.btnOptions.setText(textMenu)
        tipOpt = messLang["tipOpt"]
        self.btnOptions.setToolTip(tipOpt)
        self.btnBuild.setEnabled(True)


def findCondType(condType):
    """Знаходить назву типу умови."""
    if condType == "c":
        return "Коректність"
    else:
        return "Завершимість"


# if __name__ == '__main__':
def constr_counter_example():
    app = QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
