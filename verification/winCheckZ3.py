from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import os.path
import json
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import uic
from z3py.z3conds import checkcondsz3
from verification.showintable import viewErrMsg, testLang, getTextLang
from exprlib.logilib.implication import exprimp
from z3py.z3pyFun import z3CouEx
from z3 import *


class MainWindow(QMainWindow):
    """Реалізація вікон та діалогу на базі бібліотеки PyQT5"""
    def __init__(self):
        super(MainWindow, self).__init__()
        curdir = os.path.abspath(os.curdir)
        path = curdir + '/design/CheckZ3.ui'
        uic.loadUi(path, self)

        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        # Розташовуємо таблицю
        table = self.tableWidget
        hpanel = 60
        table.setGeometry(20, hpanel, width - 40, height - hpanel - 100)
        header = table.horizontalHeader()
        table.horizontalHeader().setStyleSheet("QHeaderView::section{font-weight:bold; color:#46647F}")
        header.setStretchLastSection(True)
        table.setRowCount(4)
        table.setHorizontalHeaderLabels([""])

        self.options = {}   # Словник параметрів системи
        self.messLang = {}  # Словник повідомлень українською та англійською мовами
        self.program = ""
        self.language = "uk"
        self.checkRes = []
        self.tabConds = {}
        self.selReady = False
        self.dictCorr = {}
        self.dictTerm = {}

        self.btnConds.clicked.connect(self.readJson)        # переглядає JSON-файл з умовами коректності та завершимості
        self.btnCheck.clicked.connect(self.check)           # перевіряє умови коректності та завершимості маршрутів
        self.btnRes.clicked.connect(self.result)            # відображає результати перевірки умов
        self.btnCEx.clicked.connect(self.counterEx)         # знаходить контрприклад для невірної умови
        self.btnOptions.clicked.connect(self.viewOptions)   # переглядає системні параметри
        self.btnCEx.setEnabled(False)

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
        self.readJson()
        self.btnRes.setEnabled(False)
        table.itemSelectionChanged.connect(self.on_selection)   # вибір клітинок таблиці

    def changeEvent(self, event):
        """Обробник подій зміни стану вікна: Максимізувати, Нормалізувати."""
        if event.type() == QtCore.QEvent.WindowStateChange:
            table = self.tableWidget
            # Змінені розміри вікна
            width = self.width()
            height = self.height()
            hpanel = 100        # Висота панелі
            table.setGeometry(20, hpanel, width - 40, height - hpanel - 40)
        super(QMainWindow, self).changeEvent(event)

    def getOptions(self):
        """Відображає в таблиці параметри системи."""
        curdir = os.path.abspath(os.curdir)
        fname = curdir + '\\options.json'
        with open(fname, 'r', encoding='utf-8') as file_object:
            params = json.load(file_object)
        self.options = params
        self.language = params["language"]
        self.program = params["program"]  # Ім'я аналізованої програми

    def readJson(self):
        """Читає і відображає в таблиці JSON-файл імпорту умов. """
        messLang = self.messLang
        curdir = os.path.abspath(os.curdir)
        progName = self.program
        lang = self.language
        path = curdir + '/export/'
        netName = progName + "_ct.json"
        importJsonFile = path + netName

        if not os.path.isfile(importJsonFile):
            errMsg = messLang["errCondFile1"] + netName + messLang["errCondFile2"]
            viewErrMsg(self, errMsg)
            self.setInvalid()
            return

        with open(importJsonFile, 'r', encoding='utf-8') as file_object:
            importJson = json.load(file_object)
        impProgName = importJson["program"]
        if impProgName != progName:
            # Помилка: файл імпорту умов містить дані про іншу програму
            errMsg = messLang["errprog1"] + impProgName + messLang["errprog2"] + progName + "'!"
            viewErrMsg(self, errMsg)
            self.btnCheck.setEnabled(False)
            return False
        table = self.tableWidget
        table.setColumnCount(3)
        hdrTrNum = messLang["hdrTrNum"]
        hdrCType = messLang["hdrCType"]
        hdrCond = messLang["hdrCond"]
        table.setHorizontalHeaderLabels([hdrTrNum, hdrCType, hdrCond])
        condCorr = messLang["valCorr"]
        condTerm = messLang["valTerm"]
        corrConds = importJson["correctness"]
        dictCorr = {}
        for corrCond in corrConds:
            nc = corrCond[0]
            dictCorr[nc] = [corrCond[1], corrCond[2]]
        self.dictCorr = dictCorr
        termConds = importJson["termination"]
        dictTerm = {}
        for termCond in termConds:
            nt = termCond[0]
            dictTerm[nc] = [termCond[1], termCond[2]]
        self.dictTerm = dictTerm
        table.setRowCount(0)

        nconds = len(dictCorr) + len(dictTerm)
        if nconds == 0:
            progZ3 = messLang["progZ3_1"] + progName + ". " + messLang["progZ3_2"]
            table.setRowCount(1)
            table.setColumnCount(1)
            hdrMess = messLang["hdrMess"]
            table.setHorizontalHeaderLabels([hdrMess])
            cell = QTableWidgetItem(progZ3)
            table.setItem(0, 0, cell)
            table.resizeColumnsToContents()
            self.setInvalid()
        else:
            tabConds = []
            numRows = 0
            # for corrCond in corrConds:
            nCorr = dictCorr.keys()
            for nc in nCorr:
                numRows += 1
                # nc = corrCond[0]
                el = dictCorr[nc]
                cCond = el[0]
                elT = [nc, "c", cCond]
                table.setRowCount(numRows)
                cell = QTableWidgetItem(str(nc))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)
                table.setItem(numRows - 1, 0, cell)
                cell = QTableWidgetItem(condCorr)
                table.setItem(numRows - 1, 1, cell)
                cell = QTableWidgetItem(cCond)
                table.setItem(numRows - 1, 2, cell)
                tabConds.append(elT)

            # for termCond in termConds:
            nTerm = dictTerm.keys()
            for nt in nTerm:
                numRows += 1
                # nt = termCond[0]
                el = dictTerm[nt]
                tCond = el[0]
                table.setRowCount(numRows)
                cell = QTableWidgetItem(str(nt))
                elT = [nt, "t", tCond]
                cell.setTextAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)
                table.setItem(numRows - 1, 0, cell)
                cell = QTableWidgetItem(condTerm)
                table.setItem(numRows - 1, 1, cell)
                cell = QTableWidgetItem(tCond)
                table.setItem(numRows - 1, 2, cell)
                tabConds.append(elT)
            table.resizeColumnsToContents()
            self.tabConds = tabConds

    def check(self):
        """Запустити програму перевірки умов коректності та завершимості."""
        table = self.tableWidget
        table.setColumnCount(4)
        messLang = self.messLang
        hdrTrNum = messLang["hdrTrNum"]
        hdrCType = messLang["hdrCType"]
        hdrCond = messLang["hdrCond"]
        table.setHorizontalHeaderLabels([hdrTrNum, hdrCType, hdrCond])
        res = checkcondsz3()
        resList = res[2]
        numRow = 0
        allTrue = True
        numFalse = 0
        for resEl in resList:
            numRow += 1
            allTrue = allTrue and resEl
            table.setRowCount(numRow)
            nc = resEl[0]
            cell = QTableWidgetItem(str(nc))
            cell.setTextAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)
            table.setItem(numRow - 1, 0, cell)
            ctype = resEl[1]
            if ctype == 'c':
                condType = messLang["valCorr"]
                cond = self.dictCorr[nc]
            else:
                condType = messLang["valTerm"]
                cond = self.dictTerm[nc]
            cell = QTableWidgetItem(condType)
            table.setItem(numRow - 1, 1, cell)
            cell = QTableWidgetItem(str(cond))
            table.setItem(numRow - 1, 2, cell)
            valcond = resEl[2]
            if not valcond:
                numFalse += 1
            cell = QTableWidgetItem(str(valcond))
            table.setItem(numRow - 1, 3, cell)
        self.checkRes = [res[0], res[1]]
        if numFalse > 0:
            selCond = messLang["selCond"]
            self.statusBar().setStyleSheet("color: black; background-color : pink")
            self.statusBar().showMessage(selCond)
        self.btnRes.setEnabled(True)
        self.btnCEx.setEnabled(not allTrue)
        self.selReady = True
        table.resizeColumnsToContents()

    def on_selection(self):
        if not self.selReady:
            return
        table = self.tableWidget
        messLang = self.messLang
        selList = table.selectedItems()
        if len(selList) == 1:
            selItem = selList[0]
            selRow = selItem.row()
            condVal = table.item(selRow, 3).text()
            condVal = eval(condVal)
            if condVal:
                self.btnCEx.setEnabled(False)
                self.statusBar().setStyleSheet("color: red; background-color : white")
                tCondSel = messLang["tCondSel"]
                self.statusBar().showMessage(tCondSel)
            else:
                wCondSel = messLang["fCondSel"]
                self.statusBar().setStyleSheet("color: blue; background-color : pink")
                self.statusBar().showMessage(wCondSel)
                self.btnCEx.setEnabled(True)
            self.selReady = False

    def result(self):
        """Показати результат перевірки."""
        program = self.program
        table = self.tableWidget
        table.setColumnCount(1)
        messLang = self.messLang
        hdrMess = messLang["hdrMess"]
        table.setHorizontalHeaderLabels([hdrMess])
        resc = self.checkRes[0]
        rest = self.checkRes[1]
        messLang = self.messLang
        messAT = messLang["messAT"]
        messC = messLang["messC"]
        messNAT = messLang["messNAT"]
        messT = messLang["messT"]
        nRows = 0
        if resc is not None:
            nRows += 1
            if resc:
                textCorr = messAT + program + messC
            else:
                textCorr = messNAT + program + messC
            table.setRowCount(nRows)
            cell = QTableWidgetItem(textCorr)
            table.setItem(0, 0, cell)
        if rest is not None:
            nRows += 1
            if rest:
                textTerm = messAT + program + messT
            else:
                textTerm = messNAT + program + messT
            table.setRowCount(nRows)
            cell = QTableWidgetItem(textTerm)
            table.setItem(1, 0, cell)
        table.resizeColumnsToContents()

    def viewOptions(self):
        """Переглянути параметри"""
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(3)
        messLang = self.messLang
        hdrOpt = messLang["hdrOpt"]
        hdrVal = messLang["hdrVal"]
        hdrPur = messLang["hdrPur"]
        table.setHorizontalHeaderLabels([hdrOpt, hdrVal, hdrPur])

        curdir = os.path.abspath(os.curdir)
        fname = curdir + '\\options_mess.json'
        with open(fname, 'r', encoding='utf-8') as file_object:
            params_mess = json.load(file_object)

        params = self.options
        language = self.language
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
            par_mess = params_mess[parName]
            message = par_mess[language]
            cell = QTableWidgetItem(message)
            table.setItem(npar - 1, 2, cell)
        table.resizeColumnsToContents()

    def setTextMenu(self):
        """Транслює меню на мову користувача."""
        messLang = self.messLang
        textMenu = messLang["btnConds"]
        self.btnConds.setText(textMenu)
        tipZConds = messLang["tipZConds"]
        self.btnConds.setToolTip(tipZConds)
        textMenu = messLang["btnCheck"]
        self.btnCheck.setText(textMenu)
        tipZChk = messLang["tipZChk"]
        self.btnCheck.setToolTip(tipZChk)
        textMenu = messLang["btnRes"]
        self.btnRes.setText(textMenu)
        tipZRes = messLang["tipZRes"]
        self.btnRes.setToolTip(tipZRes)
        textMenu = messLang["btnOptions"]
        self.btnOptions.setText(textMenu)
        tipOpt = messLang["tipOpt"]
        self.btnOptions.setToolTip(tipOpt)

    def setInvalid(self):
        """Робить недоступними всі команди меню."""
        self.btnConds.setEnabled(False)
        self.btnCheck.setEnabled(False)
        self.btnRes.setEnabled(False)
        self.btnOptions.setEnabled(False)

    def counterEx(self):
        """Знаходить контрприклад для невірної умови."""
        table = self.tableWidget
        progName = self.program
        messLang = self.messLang
        sellist = table.selectedItems()
        if len(sellist) == 1:
            el = sellist[0]
            num = el.row()
            sel = self.tabConds[num]
            selNum = int(sel[0])
            selType = sel[1]
            selCond = sel[2]
            impl = exprimp(selCond)
            curdir = os.path.abspath(os.curdir)
            parms = [curdir, progName, selCond]
            z3CouEx(impl, selType, selNum, parms)
        self.statusBar().setStyleSheet("color:blue; background-color: white")
        exCouEx = messLang["exCouEx"]
        self.statusBar().showMessage(exCouEx)
        self.selReady = False
        self.setInvalid()


def checkz3():
    # if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())