"""Модуль задає основну програму застосунку, призначеного для генерації
інваріантів циклів та функцій частково анотованих програм."""

import os.path
import ctypes
import json
import sys
import copy
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QHeaderView
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QTableWidgetItem
from verification.showintable import testLang, getTextLang, viewErrMsg
from verification.showintable import cleartable
from verification.showintable import showanprog, showerrlist
from verification.common import saveProgNameOpt
from z3py.typefun import test_types_var, compact_types
from verification.check_anfun import check_anfun, genstrprog
from verification.gentracks import gentracks
from verification.formcondcorr import forminit, forminitvartrees, formcpdictctrees, symbolicEx
from z3py.typefun import build_dict_set_var_cp
from verification.showintable import show_types_in_table, show_areas_in_table
from verification.showintable import show_cp, show_ps, show_ce, show_ct, show_iv
from exprlib.treelib.tree import treeexpr, Tree
from exprlib.arilib.polynom import treetopoly, polytotree
from exprlib.logilib.conjunct import treetocon, con_rel_list
from exprlib.logilib.conjunct import normconj, contotree
from exprlib.logilib.relation import reltoexpr
from archive.condsWindow import CondsWindow

mainWindow = None

class MainWindow(QMainWindow):
    """Реалізація вікон та діалогу на базі бібліотеки PyQT5"""
    def __init__(self):
        super(MainWindow, self).__init__()
        curdir = os.path.abspath(os.curdir)
        path = curdir + '/design/СonstrInv.ui'
        uic.loadUi(path, self)

        self.setWindowState(QtCore.Qt.WindowMaximized)
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        # Розташовуємо таблицю
        table = self.tableWidget
        hpanel = 140
        table.setGeometry(20, hpanel, width - 40, height - hpanel - 100)
        header = table.horizontalHeader()
        table.horizontalHeader().setStyleSheet("QHeaderView::section{font-weight:bold; color:#46647F}")
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        table.setRowCount(0)
        table.setHorizontalHeaderLabels([""])
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)   # Табличний віджет не буде редагуватися

        # Атрибути класу MainWindow
        self.language = "eng"
        self.anprog = ""            # Текст анотованої програми
        self.progstru = []          # Список операторів програми
        self.dictcppos = {}         # Словник контрольних точок
        self.cpdictctrees = {}      # Словник з деревами контрольних умов
        self.tracks = []            # Список трас анотованої програми
        self.initvartrees = []      # Список представлення значень параметрів трас деревами
        self.options = {}           # Словник параметрів системи
        self.messLang = {}          # Словик перекладів повідомлень
        self.area = ""                      # Область даних програми
        self.dict_type_vars_cp = {}         # Cписок змінних типів даних в контрольних точках
        self.init_dict_var_types_cp = {}    # Cписок типів даних в контрольних точках (окрім area)
        self.dicttermtrees = {}     # Словник з деревами виразів варіантів
        self.terman = False         # Ознака перевірки завершимості трас
        self.selReady = False       # Ознака здійсненого вибору траси
        self.selTrackNum = 0        # Номер вибраної траси
        self.vardict = {}           # Словник символьних значень змінних траси
        self.trackcond = ""         # Дерево виразу співвідношення параметрів траси
        self.primary = True         # Первинний вибір
        self.seltracks = []         # Траси, які починаються в поточній КТ
        self.dict_track = None      # Словник номерів вибраних трас
        self.tabColNum = 0          # Номер поточного стовпчика умов
        self.tabAllConds = []       # Таблиця кінцевих умов всіх трас
        self.tabAllTracks = []      # Таблиця всіх трас
        self.condProc = None        # Вікно обробки умов

        # Призначення обробників кнопкам
        self.btnFileDlg.clicked.connect(self.filedlg)       # вибір анотованої програми
        self.btnProgram.clicked.connect(self.anprogram)     # побудова внутрішнього представлення анотованої програми
        self.btnTracks.clicked.connect(self.buildtracks)    # побудова трас
        self.btnParams.clicked.connect(self.buildparams)    # ініціалізація змінних трас
        self.btnSymEx.clicked.connect(self.symbolExecute)   # символьне виконання вибраної траси
        self.btnNext.clicked.connect(self.chNextTr)         # вибрати трасу, яка починається в поточній КТ
        self.btnOptions.clicked.connect(self.viewOptions)   # показати параметри програми
        self.btnCP.clicked.connect(self.showcp)             # показати контрольні точки програми
        self.btnPS.clicked.connect(self.showps)             # показати структуру програми
        self.btnAreas.clicked.connect(self.show_areas)      # показати області даних анотації
        self.btnTypes.clicked.connect(self.show_types)      # показати типи значень змінних програми в КТ
        self.btnCE.clicked.connect(self.showce)             # показати умови в контрольних точках програми.
        self.btnCT.clicked.connect(self.showct)             # показати траси програми
        self.btnIV.clicked.connect(self.showiv)             # показати ініціалізацію змінних трас символьними параметрами
        self.btnSel.clicked.connect(self.prepare_seltrack)  # вибрати трасу в програмі
        self.btnSVL.clicked.connect(self.showSVL)           # показати символьні значення змінних
        self.btnETC.clicked.connect(self.showETC)           # показати кінцеву умову символьного виконання траси
        self.btnSympl.clicked.connect(self.simplCond)       # спростити кінцеву умову траси
        self.btnNTC.clicked.connect(self.showSCond)         # показати спрощену кінцеву умову символьного викон.траси
        self.btnNTV.clicked.connect(self.showSVal)          # показати спрощені кінцеві символьні значення змінних

        self.btnConds.clicked.connect(self.showCondsWindow)     # утворити вікно умов в контрольній точці
        # self.btnConds.setEnabled(True)
        self.btnConds.setVisible(False)
        self.btnSave.setVisible(False)

        self.getOptions()

        lang = self.language
        ok = testLang(self, lang)
        if not ok:
            self.btnFileDlg.setEnabled(False)
            self.btnProgram.setEnabled(False)
            self.btnOptions.setEnabled(False)
            return

        messLang = getTextLang(lang)
        if messLang == "":
            errMsg = "Error: no translation dictionary found!"
            viewErrMsg(self, errMsg)
            self.btnFileDlg.setEnabled(False)
            self.btnProgram.setEnabled(False)
            self.btnOptions.setEnabled(False)
            return

        self.messLang = messLang
        self.setTextMenu(messLang)
        table = self.tableWidget
        table.itemSelectionChanged.connect(self.on_selection)   # вибір клітинок таблиці
        self.setInit()

    def changeEvent(self, event):
        """Обробник подій зміни стану вікна: Максимізувати, Нормалізувати."""
        if event.type() == QtCore.QEvent.WindowStateChange:
            table = self.tableWidget
            # Змінені розміри вікна
            width = self.width()
            height = self.height()
            hpanel = 140        # Висота панелі
            table.setGeometry(20, hpanel, width - 40, height - hpanel - 40)
        super(QMainWindow, self).changeEvent(event)

    def getOptions(self):
        """Прочитати параметри програми."""
        curdir = os.path.abspath(os.curdir)
        fname = curdir + '\\..\\options.json'
        with open(fname, 'r', encoding='utf-8') as f:
            self.options = json.load(f)
        params = self.options
        self.language = params["language"]
        program = params["program"]  # Ім'я аналізованої програми
        exdir = params["exdir"]      # Ім'я каталогу аналізованих програм
        filename = curdir + "\\" + exdir + "\\" + program + ".py"
        self.ledFileName.setText(filename)
        check = os.path.exists(filename)
        if not check:
            errMsg = "Error: annotation program file does not exist!"
            viewErrMsg(self, errMsg)
        self.btnProgram.setEnabled(check)

    def filedlg(self):
        """Видати діалог для вибору файла анотованої програми."""
        messLang = self.messLang
        curdir = os.path.abspath(os.curdir)
        dirname = curdir + "/anprograms"
        wintitle = messLang["selPrFile"]
        qfilename = QFileDialog.getOpenFileName(self, wintitle, dirname, "Python (*.py)")
        filename = qfilename[0]
        cleartable(self)
        self.btnSave.setEnabled(False)
        self.setdisable()
        self.ledFileName.setText(filename)
        self.btnProgram.setEnabled(filename != "")
        table = self.tableWidget
        table.setEnabled(True)
        self.setInit(0)

    def anprogram(self):
        """Прочитати, проаналізувати анотовану програму та побудувати її внутрішнє представлення."""
        self.setdisable()
        filename = self.ledFileName.text()
        pos = str.rfind(filename, ".")
        if pos >= 0:
            fname = filename[:pos]
            fname = fname.replace("/", "\\")
            posbs = str.rfind(fname, "\\")
            if posbs >= 0:
                netname = fname[posbs + 1:]
                program = self.options["program"]
                if program != netname:
                    options = self.options
                    options = saveProgNameOpt(netname, options)
                    self.options = options

        table = self.tableWidget
        table.setColumnCount(1)
        messLang = self.messLang
        prState = messLang["prState"]
        table.setHorizontalHeaderLabels([prState])
        filename = self.ledFileName.text()
        if not os.path.isfile(filename):
            errNoPrF = messLang["errNoPrF"]
            viewErrMsg(self, errNoPrF)
            return 1

        anprog = showanprog(table, filename, self)
        self.anprog = anprog

        dictcppos = {}
        cpdictconds = {}
        progstru = []
        dicttermexpr = {}
        dict_var_types_cp = {}
        res = check_anfun(self, filename, dictcppos, cpdictconds, progstru, dicttermexpr, dict_var_types_cp)
        self.dictcppos = dictcppos
        self.progstru = progstru

        cpdictctrees = formcpdictctrees(cpdictconds)

        # Будуємо словник множин змінних в контрольних точках програми
        dicttermtrees = {}
        dict_set_var_cp = build_dict_set_var_cp(cpdictctrees, dicttermtrees)

        area = dict_var_types_cp.get("AREA", "")
        if area != "":
            dict_var_types_cp.pop("AREA")
        self.area = area
        self.init_dict_var_types_cp = copy.deepcopy(dict_var_types_cp)
        dict_non_type_var = test_types_var(area, dict_var_types_cp, dict_set_var_cp)
        if len(dict_non_type_var) > 0:
            # Не всі змінні типізовано
            for cp in dict_non_type_var.keys():
                varlist = list(dict_non_type_var[cp])
                varstr = ""
                nvar = 0
                for var in varlist:
                    nvar += 1
                    if nvar > 1:
                        varstr += ", "
                    varstr += var

                errNoType = messLang["errNoType"] + cp + ": " + varstr + " !"
                viewErrMsg(self, errNoType)
            return 1
        dict_type_vars_cp = compact_types(dict_var_types_cp)
        self.cpdictctrees = cpdictctrees
        self.dicttermtrees = dicttermtrees
        self.dict_type_vars_cp = dict_type_vars_cp

        numrows = table.rowCount() + 1
        table.setRowCount(numrows)
        showerrlist(self, table, res)
        self.tabColNum = 0

        self.setInit(1)
        self.btnTracks.setEnabled(res[0] == 0)
        self.btnSave.setEnabled(res[0] == 0)
        self.btnCP.setEnabled(res[0] == 0)
        self.btnPS.setEnabled(res[0] == 0)
        self.btnCE.setEnabled(res[0] == 0)
        self.btnTypes.setEnabled(res[0] == 0)
        self.btnAreas.setEnabled(res[0] == 0)
        if res[0] != 0:
            return 1
        table = self.tableWidget
        table.setEnabled(True)
        # Очищаємо панель статусу: починаємо все спочатку
        self.statusBar().setStyleSheet("color: black; background-color : white")
        self.statusBar().showMessage("")

    def buildtracks(self):
        """Побудувати траси (контрольні шляхи в програмі)."""
        progstru = self.progstru
        dictcppos = self.dictcppos
        genstrprog(progstru)
        tracks = gentracks(progstru, dictcppos)
        self.progstru = progstru
        self.tracks = tracks
        self.btnCT.setEnabled(True)
        self.btnParams.setEnabled(True)
        self.btnTracks.setEnabled(False)

    def buildparams(self):
        """Побудувати параметри для ініціалізації змінних трас."""
        tracks = self.tracks
        initvars = forminit(tracks)
        initvartrees = forminitvartrees(initvars)
        self.initvartrees = initvartrees
        self.btnIV.setEnabled(True)
        self.btnSel.setEnabled(True)
        self.btnParams.setEnabled(False)

    # методи перегляду таблиць
    def showcp(self):
        """Показати контрольні точки програми."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        progCP = messLang["progCP"]
        typeCP = messLang["typeCP"]
        table.setHorizontalHeaderLabels([progCP, typeCP])
        dictcppos = self.dictcppos
        show_cp(self, table, dictcppos)
        table.resizeColumnsToContents()

    # Обробка типів даних
    def show_areas(self):
        # Показати області даних програми
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrSt = messLang["hdrSt"]
        hdrType = messLang["hdrType"]
        table.setHorizontalHeaderLabels([hdrSt, hdrType])
        init_dict_var_types_cp = self.init_dict_var_types_cp
        area = self.area
        show_areas_in_table(table, init_dict_var_types_cp, area)
        table.resizeColumnsToContents()

    def show_types(self):
        # Показати типи даних змінних в КТ
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrCP = messLang["hdrCP"]
        hdrTypes = messLang["hdrTypes"]
        table.setHorizontalHeaderLabels([hdrCP, hdrTypes])
        dict_type_vars_cp = self.dict_type_vars_cp
        show_types_in_table(table, dict_type_vars_cp)
        table.resizeColumnsToContents()

    def showps(self):
        """Показати структуру програми."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(4)
        prState = messLang["prState"]
        typeCP = messLang["typeCP"]
        offset = messLang["offset"]
        level = messLang["level"]
        table.setHorizontalHeaderLabels([prState, typeCP, offset, level])
        progstru = self.progstru
        show_ps(table, progstru)
        table.resizeColumnsToContents()

    def showce(self):
        """Показати умови в контрольних точках програми."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrCP = messLang["hdrCP"]
        hdrCond = messLang["hdrCond"]
        table.setHorizontalHeaderLabels([hdrCP, hdrCond])
        dictcppos = self.dictcppos
        cpdictctrees = self.cpdictctrees
        show_ce(table, dictcppos, cpdictctrees)
        table.resizeColumnsToContents()

    def showct(self):
        """Показати траси в програмі."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrStat = messLang["hdrStat"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrStat])
        tracks = self.tracks
        show_ct(table, tracks)
        table.resizeColumnsToContents()

    def showiv(self):
        """Показати оператори ініціалізації змінних трас."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrVarIn = messLang["hdrVarIn"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrVarIn])
        initvartrees = self.initvartrees
        tracks = self.tracks
        show_iv(table, tracks, initvartrees)
        table.resizeColumnsToContents()

    def showSVL(self):
        """Показати символьні значення змінних в кінцевій КТ траси"""
        vardict = self.vardict
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Змінна", "Символьне значення"])
        numRow = 0
        for var in vardict.keys():
            numRow += 1
            etree = vardict[var]
            table.setRowCount(numRow)
            cell = QTableWidgetItem(var)
            table.setItem(numRow - 1, 0, cell)
            symval = treeexpr(etree)
            cell = QTableWidgetItem(symval)
            table.setItem(numRow - 1, 1, cell)
        table.resizeColumnsToContents()

    def showETC(self):
        """Показати поточну умову символьного виконання траси."""
        trackcond = self.trackcond
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Відношення"])
        condconj = treetocon(trackcond)
        rellist = con_rel_list(condconj)
        numRow = 0
        for rel in rellist:
            relexpr = reltoexpr(rel)
            numRow += 1
            table.setRowCount(numRow)
            cell = QTableWidgetItem(relexpr)
            table.setItem(numRow - 1, 0, cell)
        table.resizeColumnsToContents()

    def simplCond(self):
        """Спростити поточну умову символьного виконання траси,
        а також символьні значення змінних."""
        trackcond = self.trackcond
        conj = treetocon(trackcond)
        conjNorm = normconj(conj)
        treeNorm = contotree(conjNorm)
        self.trackcond = treeNorm
        vardict = self.vardict
        vlist = vardict.items()
        for varitem in vlist:
            var = varitem[0]
            val = varitem[1]
            if type(val) is Tree:
                poly = treetopoly(val)
                polyNorm = poly.combine()
                treeNorm = polytotree(polyNorm)
                vardict[var] = treeNorm
        self.vardict = vardict
        self.btnETC.setEnabled(False)
        self.btnSVL.setEnabled(False)
        self.btnSympl.setEnabled(False)
        self.btnNTV.setEnabled(True)
        self.btnNTC.setEnabled(True)

    def showSCond(self):
        """Показати спрощену кінцеву умову траси."""
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Нормалізовані"])
        treeNorm = self.trackcond
        conjNorm = treetocon(treeNorm)
        rellist = con_rel_list(conjNorm)
        numRow = 0
        for rel in rellist:
            relexpr = reltoexpr(rel)
            numRow += 1
            table.setRowCount(numRow)
            cell = QTableWidgetItem(relexpr)
            table.setItem(numRow - 1, 0, cell)
        table.resizeColumnsToContents()

    def showSVal(self):
        """Показати спрощені кінцеві символьні значення змінних"""
        vardict = self.vardict
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Змінна", "Символьне значення"])
        numRow = 0
        for var in vardict.keys():
            numRow += 1
            etree = vardict[var]
            table.setRowCount(numRow)
            cell = QTableWidgetItem(var)
            table.setItem(numRow - 1, 0, cell)
            symval = treeexpr(etree)
            cell = QTableWidgetItem(symval)
            table.setItem(numRow - 1, 1, cell)
        table.resizeColumnsToContents()

    # Вибір та символьне виконання трас
    def prepare_seltrack(self):
        """Підготувати вибір траси в програмі для першого символьного виконання."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrStat = messLang["hdrStat"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrStat])
        tracks = self.tracks
        show_ct(table, tracks)
        selTraceMsg = messLang["selTrack"]
        self.statusBar().setStyleSheet("color: black; background-color : pink")
        self.statusBar().showMessage(selTraceMsg)
        self.selReady = True
        self.primary = True
        table.resizeColumnsToContents()

    def on_selection(self):
        """Обробник подій вибору рядка таблиці трас.
        Вибрати трасу для її символьного виконання (поточну трасу).
        Первинний та вторинний вибір."""
        if not self.selReady:
            return
        table = self.tableWidget
        messLang = self.messLang
        selList = table.selectedItems()
        if len(selList) == 1:
            selItem = selList[0]
            selRow = selItem.row()
            selTrace_cps = table.item(selRow, 0).text()
            pos_icp = selTrace_cps.find(" -> ")
            selTrack_icp = selTrace_cps[0: pos_icp]
            selTrack = selTrace_cps[:-1]
            if self.cpdictctrees.get(selTrack_icp, "") != "":
                # Користувач вибрав трасу
                self.selTrackNum = selRow
                self.btnSymEx.setEnabled(True)
                self.statusBar().setStyleSheet("color: black; background-color : white")
                self.statusBar().showMessage("")
                self.lbCurCP.setText(selTrack_icp)
                self.lbCurTr.setText(selTrack)
                self.btnNext.setEnabled(False)
            else:
                selTr_UnIC = messLang["selTr_UnIC"]
                self.statusBar().setStyleSheet("color: black; background-color : pink")
                self.statusBar().showMessage(selTr_UnIC)
                self.selReady = False
                self.lbCurCP.setText("")
                self.lbCurTr.setText("")
        self.btnSel.setEnabled(False)
        table.setEnabled(False)

    def symbolExecute(self):
        """Символьним виконанням траси побудувати кінцеві
        символьні значення змінних програми на шляху
        та відношення між початковими параметрами шляху.
        Первинне та вторинне виконання."""
        selTrackNum = self.selTrackNum
        if self.primary:
            selTrack = self.tracks[selTrackNum]
            initvardict = self.initvartrees[selTrackNum]
            selTrack_icp = selTrack[0]
            initcondtree = self.cpdictctrees[selTrack_icp]
        else:
            dict_track = self.dict_track
            selTrackN = dict_track[selTrackNum]
            selTrack = self.tracks[selTrackN]
            initvardict = self.vardict
            initcondtree = self.trackcond
        sel_Track = selTrack[1: -1]
        res = symbolicEx(sel_Track, initvardict, initcondtree)          # Проблема тут! При повторному виконанні
        selTrack_ecp = selTrack[-1]
        self.lbCurCP.setText(selTrack_ecp)
        vardict = res[0]
        trackcond = res[1]
        self.vardict = vardict
        self.trackcond = trackcond
        self.btnSVL.setEnabled(True)
        self.btnETC.setEnabled(True)
        self.btnSymEx.setEnabled(False)
        self.btnSympl.setEnabled(True)
        if selTrack_ecp != "E":
            self.btnNext.setEnabled(True)

    def chNextTr(self):
        """Показати траси, які починаються в поточній КТ.
        Вибрати одну з них для продовження символьного виконання
        (вторинний вибір)."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrStat = messLang["hdrStat"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrStat])
        selTrack_icp = self.lbCurCP.text()
        tracks = self.tracks
        sel_tracks = []
        n = 0
        num = 0
        dict_track = dict()
        for track in tracks:
            if track[0] == selTrack_icp:
                sel_tracks.append(track)
                dict_track[num] = n
                num += 1
            else:
                sel_tracks.append(None)
            n += 1
        if num > 0:
            self.seltracks = sel_tracks
            self.dict_track = dict_track
            show_ct(table, sel_tracks)
            selTraceMsg = messLang["selTrack"]
            self.statusBar().setStyleSheet("color: black; background-color : pink")
            self.statusBar().showMessage(selTraceMsg)
            self.selReady = True
            self.primary = False
            table.setEnabled(True)
        else:
            self.btnNext.setEnabled(False)
        self.btnSVL.setEnabled(False)
        self.btnETC.setEnabled(False)
        self.btnSympl.setEnabled(False)
        table.resizeColumnsToContents()

    def setTextMenu(self, messLang):
        """Транслює меню на мову користувача."""
        textMenu = messLang["lblFileName"]
        self.lblFileName.setText(textMenu)
        textMenu = messLang["btnProgram"]
        self.btnProgram.setText(textMenu)
        textMenu = messLang["btnTracks"]
        self.btnTracks.setText(textMenu)
        textMenu = messLang["btnParams"]
        self.btnParams.setText(textMenu)
        textMenu = messLang["btnSave"]
        self.btnSave.setText(textMenu)
        textMenu = messLang["btnCP"]
        self.btnCP.setText(textMenu)
        textMenu = messLang["btnPS"]
        self.btnPS.setText(textMenu)
    def getOptions(self):
        curdir = os.path.abspath(os.curdir)
        fname = curdir + '/options.json'
        with open(fname, 'r', encoding='utf-8') as f:
            self.options = json.load(f)
        params = self.options
        self.language = params["language"]
        program = params["program"]  # Ім'я аналізованої програми
        exdir = params["exdir"]      # Ім'я каталогу аналізованих програм
        filename = curdir + "/" + exdir + "/" + program + ".py"
        self.ledFileName.setText(filename)
        check = os.path.exists(filename)
        if not check:
            errMsg = "Error: annotation program file does not exist!"
            viewErrMsg(self, errMsg)
        self.btnProgram.setEnabled(check)

    def viewOptions(self):
        """Переглянути параметри"""
        messLang = self.messLang
        options = self.options
        filename = self.ledFileName.text()
        pos = str.rfind(filename, ".")
        netname = ""
        if pos >= 0:
            fname = filename[:pos]
            fname = fname.replace("/", "\\")
            posbs = str.rfind(fname, "\\")
            if posbs >= 0:
                netname = fname[posbs + 1:]
        else:
            netname = filename
        options = saveProgNameOpt(netname, options)
        self.options = options

        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(3)
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

    def setdisable(self):
        """Зробити всі кнопки недоступними."""
        self.btnTracks.setEnabled(False)
        self.btnParams.setEnabled(False)
        self.btnCP.setEnabled(False)
        self.btnPS.setEnabled(False)
        self.btnCE.setEnabled(False)
        self.btnCT.setEnabled(False)
        self.btnIV.setEnabled(False)

    def setInit(self, state=0):
        """Ініціалізувати інтерфейс в стані state.
        0 - це стан після вибору анотованої програми
        1 - це стан після аналізу анотованої програми
        2 - це стан після визначення параметрів трас
        """
        table = self.tableWidget
        table.setEnabled(True)
        self.btnCP.setEnabled(state > 0)
        self.btnPS.setEnabled(state > 0)
        self.btnTracks.setEnabled(state > 0)
        self.btnCE.setEnabled(state > 1)
        self.btnCT.setEnabled(state > 1)
        self.btnParams.setEnabled(state > 1)
        self.btnAreas.setEnabled(state > 1)
        self.btnTypes.setEnabled(state > 1)
        self.btnIV.setEnabled(state > 2)
        self.btnSel.setEnabled(state > 2)
        self.btnSVL.setEnabled(False)
        self.btnETC.setEnabled(False)
        self.btnNext.setEnabled(False)
        self.btnSymEx.setEnabled(False)
        self.lbCurCP.setText("")
        self.lbCurTr.setText("")

    def showCondsWindow(self):
        """Утворити вікно умов в контрольній точці/"""
        self.condProc = CondsWindow()
        self.condProc.show()
        self.condProc.setMain(self)
        self.hide()
        # self.btnBuildNet.setEnabled(False)
        # self.btnReadNames.setEnabled(True)

    # def setMain(self, mainWindow):
    #     self.mainWindow = mainWindow


def invariant_constuct():
    # if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
