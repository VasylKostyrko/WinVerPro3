from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWidgets import QHeaderView
from PyQt5 import QtCore
import ctypes
import sys
import os.path
import json
import copy

from verification.showintable import showanprog, showerrlist, cleartable, show_res, show_te, show_tc
from verification.showintable import show_cp, show_ce, show_ps, show_ct, show_iv, show_cc, show_sc, show_ts
from verification.showintable import buildAllCondsFile
from verification.check_anfun import check_anfun, genstrprog
from verification.gentracks import gentracks
from verification.formcondcorr import forminit, forminitvartrees, formcondcorr, istermcompl, formstconds
from verification.formcondcorr import formtermcond, formcpdictctrees, formdict_termtrees, copyvartrees
from verification.common import saveProgNameOpt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import uic
from z3py.z3pyFun import checkallconds, buildemptycond
from verification.showintable import testLang, getTextLang, viewErrMsg, testConds

from verification.showintable import show_types_in_table, show_areas_in_table
from z3py.typefun import build_dict_set_var_cp
from z3py.typefun import test_types_var, compact_types, form_param_types


class MainWindow(QMainWindow):
    """Реалізація вікон та діалогу на базі бібліотеки PyQT5"""
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        curdir = os.path.abspath(os.curdir)
        path = curdir + '/design/Verify.ui'
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

        # Атрибути класу MainWindow - тобто, застосування
        self.language = "eng"
        self.anprog = ""            # Текст анотованої програми
        self.progstru = []          # Список операторів програми
        self.dictcppos = {}         # Словник контрольних точок
        self.cpdictctrees = {}      # Словник з деревами контрольних умов
        self.dicttermtrees = {}     # Словник з деревами виразів завершення
        self.tracks = []            # Список трас анотованої програми
        self.initvartrees = []      # Список представлення значень параметрів трас деревами
        self.vcimps = []            # Список умов коректності (об'єктів класу Implication)
        self.tracktconds = []       # Список умов завершимості (об'єктів класу Implication)
        self.simplconds = []        # Список спрощених умов коректності (об'єктів класу Implication)
        self.stracktconds = []      # Список спрощених умов завершимості (об'єктів класу Implication)
        self.terman = False         # Ознака наявності в анотованій програмі виразів завершимості
        self.corran = False         # Ознака наявності умов коректності в усіх КТ анотованої програми
        self.options = {}           # Словник параметрів системи
        self.messLang = {}          # Словник перекладів повідомлень

        self.area = ""                      # Область даних програми
        self.dict_type_vars_cp = {}         # Cписок змінних типів даних в контрольних точках
        self.init_dict_var_types_cp = {}    # Cписок типів даних в контрольних точках (окрім area)

        # Обробники подій вікна застосування
        self.btnFileDlg.clicked.connect(self.filedlg)       # вибір анотованої програми
        self.btnProgram.clicked.connect(self.anprogram)     # побудова внутрішнього представлення анотованої програми
        self.btnTracks.clicked.connect(self.buildtracks)    # побудова трас
        self.btnParams.clicked.connect(self.buildparams)    # ініціалізація змінних трас
        self.btnCond.clicked.connect(self.buildconds)       # побудова умов коректності трас
        self.btnSimpl.clicked.connect(self.simplifyvcs)     # спрощення умов кор. трас еквівалентними перетвореннями

        self.btnOptions.clicked.connect(self.viewOptions)   # перегляд параметрів програми
        self.btnZ3.clicked.connect(self.genCondsZ3)         # генерація програми перевірки умов засобами Z3
        self.btnSave.clicked.connect(self.tabsave)          # збереження поточного змісту таблиці, наприклад,
                                                            #       умов коректності трас
        self.btnRes.clicked.connect(self.showresults)       # відображення результатів роботи програми
        self.btnAuto.clicked.connect(self.automatic)        # автоматизація процесу

        # Другий ряд кнопок
        self.btnCP.clicked.connect(self.showcp)             # відображення контрольних точок програми
        self.btnPS.clicked.connect(self.showps)             # показати структуру програми
        self.btnCE.clicked.connect(self.showce)             # показати умови в контрольних точках програми.
        self.btnTE.clicked.connect(self.showte)             # показати вирази завершимості трас
        self.btnCT.clicked.connect(self.showct)             # показати траси програми
        self.btnIV.clicked.connect(self.showiv)             # ініціалізація змінних трас
        self.btnCC.clicked.connect(self.showcc)             # показати умови коректності трас
        self.btnTC.clicked.connect(self.showtc)             # показати умови завершення трас
        self.btnSC.clicked.connect(self.showsc)             # показати спрощені умови коректності трас
        self.btnST.clicked.connect(self.showts)             # показати спрощені умови завершимості трас

        self.btnAreas.clicked.connect(self.show_areas)      # показати області даних анотації
        self.btnTypes.clicked.connect(self.show_types)      # показати типи значень змінних програми в КТ

        self.getOptions()

        lang = self.language
        ok = testLang(self, lang)
        if not ok:
            self.btnFileDlg.setEnabled(False)
            self.btnProgram.setEnabled(False)
            self.btnAuto.setEnabled(False)
            self.btnOptions.setEnabled(False)
            return

        messLang = getTextLang(lang)
        if messLang == "":
            errMsg = "Error: no translation dictionary found!"
            viewErrMsg(self, errMsg)
            self.btnFileDlg.setEnabled(False)
            self.btnFileDlg.setEnabled(False)
            self.btnProgram.setEnabled(False)
            self.btnOptions.setEnabled(False)
            return

        self.messLang = messLang
        self.setTextMenu(messLang)

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
        curdir = os.path.abspath(os.curdir)
        fname = curdir + '\\options.json'
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
        self.btnAuto.setEnabled(check)

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
        self.btnAuto.setEnabled(filename != "")

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
        terman = istermcompl(dicttermexpr)
        self.terman = terman
        self.dictcppos = dictcppos
        self.progstru = progstru
        self.terman = istermcompl(dicttermexpr)

        # Перевіряємо комплектність
        corran = True
        for cp in dictcppos:
            if cpdictconds.get(cp, -1) == -1:
                corran = False
                break
        self.corran = corran
        cpdictctrees = formcpdictctrees(cpdictconds)
        dicttermtrees = formdict_termtrees(dicttermexpr)

        # Будуємо словник множин змінних в контрольних точках програми
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

        # Перевірка умов в КТ
        for cp in cpdictctrees:
            cptree = cpdictctrees[cp]
            if type(cptree) is bool:
                res[0] += 1
                errCPCond = messLang["errCPCond"] + cp + "!"
                res[1].append(errCPCond)

        numrows = table.rowCount() + 1
        table.setRowCount(numrows)
        showerrlist(self, table, res)

        self.btnTracks.setEnabled(res[0] == 0)
        self.btnSave.setEnabled(res[0] == 0)
        self.btnCP.setEnabled(res[0] == 0)
        self.btnPS.setEnabled(res[0] == 0)
        self.btnCE.setEnabled(res[0] == 0)
        self.btnTE.setEnabled(res[0] == 0 and terman)
        self.btnTypes.setEnabled(res[0] == 0)
        self.btnAreas.setEnabled(res[0] == 0)
        self.btnTE.setEnabled(len(dicttermtrees) > 0)
        # self.btnCond.setEnabled(res[0] == 0 and corran)
        if res[0] != 0:
            return 1

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

    def buildparams(self):
        """Побудувати параметри для ініціалізації змінних трас."""
        tracks = self.tracks
        initvars = forminit(tracks)
        initvartrees = forminitvartrees(initvars)
        corran = self.corran
        self.initvartrees = initvartrees
        self.btnCond.setEnabled(corran)
        self.btnIV.setEnabled(True)

    def buildconds(self):
        """Побудувати умови коректності та завершимості трас."""
        tracks = self.tracks
        initvartrees = self.initvartrees
        cpdictctrees = self.cpdictctrees
        symvartrees = copyvartrees(initvartrees)
        vcimps = formcondcorr(tracks, symvartrees, cpdictctrees)     # Побудова умов коректності трас у вигляді дерев
        self.vcimps = vcimps
        self.btnCC.setEnabled(True)
        self.btnRes.setEnabled(True)
        params = self.options
        eqtrans = params["eqtrans"]  # Чи спрощувати умови коректності засобами VerPro? (True - спрощувати)
        if eqtrans == 1:
            self.btnSimpl.setEnabled(True)
        usez3py = params["usez3py"]  # Чи спрощувати умови коректності засобами Z3py? (True - спрощувати)
        if usez3py == 1:
            self.btnZ3.setEnabled(True)
        dicttermtrees = self.dicttermtrees
        if self.terman and len(dicttermtrees) > 0:
            tracktconds = formtermcond(tracks, vcimps, initvartrees, symvartrees, cpdictctrees, dicttermtrees)
            # Побудова умов завершення трас
            self.tracktconds = tracktconds
            self.btnTC.setEnabled(True)

    def simplifyvcs(self):
        """Спростити умови коректності трас
        і умови завершення трас."""
        simplconds = []
        vcimps = self.vcimps
        for imp in vcimps:
            simp = imp.simplimp()
            if type(simp) is not bool:
                cons = simp.cons
                if len(cons.con) == 0:
                    simp = True
            simplconds.append(simp)
        self.simplconds = simplconds
        self.btnSC.setEnabled(True)
        self.btnRes.setEnabled(True)
        dicttermtrees = self.dicttermtrees
        terman = self.terman
        if terman and len(dicttermtrees) > 0:
            tracktconds = self.tracktconds
            strtconds = formstconds(tracktconds)
            stracktconds = []
            for strtcond in strtconds:
                if strtcond != "":
                    if strtcond is not True:
                        cond = strtcond.cons
                        if len(cond.con) == 0:
                            strtcond = True
                stracktconds.append(strtcond)
            self.stracktconds = stracktconds
            self.btnST.setEnabled(True)

    def automatic(self):
        """Спробувати встановити коректність програми автоматично."""
        messLang = self.messLang
        cleartable(self)
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

        dictcppos = {}
        cpdictconds = {}
        progstru = []
        dicttermexpr = {}
        var_types = {}
        res = check_anfun(self, filename, dictcppos, cpdictconds, progstru, dicttermexpr, var_types)
        terman = istermcompl(dicttermexpr)
        self.terman = terman

        # Перевірка умов в КТ
        cpdictctrees = formcpdictctrees(cpdictconds)
        for cp in cpdictctrees:
            cptree = cpdictctrees[cp]
            if type(cptree) is bool:
                res[0] += 1
                errCPCond = messLang["errCPCond"] + cp
                res[1].append(errCPCond)

        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(1)
        if res[0] == 0:
            # Все ОК. Структура анотованої програми правильна.
            genstrprog(progstru)
            tracks = gentracks(progstru, dictcppos)
            initvars = forminit(tracks)
            initvartrees = forminitvartrees(initvars)
            symvartrees = copyvartrees(initvartrees)
            corran = True
            for cp in dictcppos:
                if cpdictconds.get(cp, -1) == -1:
                    corran = False
                    break
            self.corran = corran
            if not corran:
                hdrMess = messLang["hdrMess"]
                table.setHorizontalHeaderLabels([hdrMess])
                errANC = messLang["errANC"] + "."
                res = [1, [errANC]]
                showerrlist(self, table, res)
                return 1

            cpdictctrees = formcpdictctrees(cpdictconds)
            params = self.options
            eqtrans = params["eqtrans"]
            usez3py = params["usez3py"]
            tracktconds = []
            simplconds = []
            if corran:
                dicttermtrees = formdict_termtrees(dicttermexpr)
                vcimps = formcondcorr(tracks, symvartrees, cpdictctrees)
                tracktconds = formtermcond(tracks, vcimps, initvartrees, symvartrees, cpdictctrees, dicttermtrees)

                simplconds = vcimps
                if usez3py == 1:
                    self.btnZ3.setEnabled(True)
                if eqtrans == 1:
                    simplconds = []
                    for imp in vcimps:
                        simp = imp.simplimp()
                        if type(simp) is not bool:
                            cons = simp.cons
                            if len(cons.con) == 0:
                                simp = True
                        simplconds.append(simp)
                    self.simplconds = simplconds
            if terman:
                if eqtrans == 1:
                    tracktconds = self.tracktconds
                    strtconds = formstconds(tracktconds)
                    stracktconds = []
                    for strtcond in strtconds:
                        if strtcond != "":
                            if strtcond is not True:
                                cond = strtcond.cons
                                if len(cond.con) == 0:
                                    strtcond = True
                        stracktconds.append(strtcond)
                else:
                    stracktconds = tracktconds
            else:
                stracktconds = tracktconds
            self.stracktconds = stracktconds
            if corran:
                show_res(self, table, simplconds, terman, stracktconds)
                self.simplconds = simplconds
            self.btnRes.setEnabled(corran)
        else:
            # Знайдено помилки в структурі програми
            showanprog(table, filename, self)
            numrows = table.rowCount() + 1
            table.setRowCount(numrows)
            prState = messLang["prState"]
            table.setHorizontalHeaderLabels([prState])
            showerrlist(self, table, res)
        self.btnSave.setEnabled(True)

    def tabsave(self):
        """Виводить поточний вміст таблиці у файл."""
        messLang = self.messLang
        table = self.tableWidget
        nrows = table.rowCount()
        ncols = table.columnCount()
        filename = self.ledFileName.text()
        pos = str.rfind(filename, ".")
        if pos >= 0:
            fname = filename[:pos]
            posbs = str.rfind(fname, "\\")
            if posbs >= 0:
                netname = fname[posbs+1:]
                path = fname[:posbs]
                posmcat = str.rfind(path, "\\")
                if posmcat >= 0:
                    mpath = path[:posmcat + 1]
                    filename = mpath + "output\\" + netname + ".txt"
        saveFile = messLang["saveFile"]
        qfilename = QFileDialog.getSaveFileName(self, saveFile, filename, "TXT (*.txt)")
        filename = qfilename[0]
        if filename == "":
            return
        with open(filename, 'w') as file_object:
            row = ""
            for ncol in range(ncols):
                header = table.horizontalHeaderItem(ncol).text()
                if ncol < ncols - 1:
                    row += header + "\t"
                else:
                    row += header + "\n"
            file_object.write(row)

            for r in range(nrows):
                row = ""
                for c in range(ncols):
                    cell = table.item(r, c)
                    if cell is None:
                        val = ""
                    else:
                        val = cell.text()
                        if c < ncols - 1:
                            row += val + "\t"
                        else:
                            row += val
                file_object.write(row + "\n")
        tabSaved = messLang["tabSaved"]
        self.statusBar().showMessage(tabSaved)

    def clear(self):
        """Очистити таблицю."""
        cleartable(self)

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
        # table.setHorizontalHeaderLabels([hdrOpt, hdrVal])
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

    def genCondsZ3(self):
        # Згенерувати програму виклику Z3 для перевірки умов коректності та завершимості
        messLang = self.messLang
        table = self.tableWidget
        params = self.options
        usez3py = params["usez3py"]
        eqtrans = params["eqtrans"]
        curdir = os.path.abspath(os.curdir)
        progname = params["program"]
        if usez3py == 0:
            buildemptycond(curdir)
        else:
            terman = self.terman
            parms = [curdir, progname, terman]
            if eqtrans == 0:
                vcimps = self.vcimps
                tracktconds = self.tracktconds
            else:
                vcimps = self.simplconds
                tracktconds = self.stracktconds
            res = testConds(vcimps, tracktconds)
            if res:
                # Всі умови істинні або відсутні і не передаються Z3
                buildemptycond(curdir)
                msg = messLang["condsNZ3"]
                cell = QTableWidgetItem(msg)
                table.clear()
                table.setRowCount(1)
                table.setColumnCount(1)
                hdrMess = messLang["hdrMess"]
                table.setHorizontalHeaderLabels([hdrMess])
                table.setItem(0, 0, cell)
                table.resizeColumnsToContents()
            else:
                # Генеруємо програму виклику Z3 для перевірки умов коректності та завершимості
                scondlist = []
                n = 0
                for vcimp in vcimps:
                    n += 1
                    if not type(vcimp) is bool:
                        scondlist.append([n, vcimp])

                stcondlist = []
                n = 0
                for tracktcond in tracktconds:
                    n += 1
                    if tracktcond != "":
                        if type(tracktcond) is not bool:
                            stcondlist.append([n, tracktcond])
                # Будуємо модуль перевірки умов z3py/z3conds.py
                dict_type_vars_cp = self.dict_type_vars_cp
                initvartrees = self.initvartrees
                tracks = self.tracks
                dict_param_types_cp = form_param_types(initvartrees, tracks, dict_type_vars_cp)
                checkallconds(scondlist, stcondlist, dict_param_types_cp, tracks, parms)

                # В підкаталозі export будуємо файл <ім'я програми>_ct.json
                #    опису умов для їх перевірки програмою winCheckZ3
                table.clear()
                table.setRowCount(2)
                table.setColumnCount(1)
                z3Ext = messLang["z3Ext"]
                table.setHorizontalHeaderLabels([z3Ext])
                # msg = messLang["z3Cond"] + "z3py\\z3counter."
                msg = messLang["z3Cond"] + "z3py/z3conds."
                cell = QTableWidgetItem(msg)
                table.setItem(0, 0, cell)
                msg = messLang["z3Check"] + "winCheckZ3."
                cell = QTableWidgetItem(msg)
                table.setItem(1, 0, cell)
                table.resizeColumnsToContents()
                buildAllCondsFile(scondlist, stcondlist, progname, dict_param_types_cp, tracks)
        self.btnZ3.setEnabled(False)

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

    def showte(self):
        """Показати вирази завершимості в КТ."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrCP = messLang["hdrCP"]
        hdrTEx = messLang["hdrTEx"]
        table.setHorizontalHeaderLabels([hdrCP, hdrTEx])
        dicttermtrees = self.dicttermtrees
        show_te(table, dicttermtrees)

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

    def showcc(self):
        """Показати умови коректності трас."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrTrC = messLang["hdrTrC"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrTrC])
        tracks = self.tracks
        vctrees = self.vcimps
        show_cc(table, tracks, vctrees)

    def showsc(self):
        """Показати спрощені умови коректності трас."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrTrSC = messLang["hdrTrSC"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrTrSC])
        tracks = self.tracks
        simplconds = self.simplconds
        show_sc(table, tracks, simplconds)

    def showtc(self):
        """Показати умови завершимості трас."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrTrTC = messLang["hdrTrTC"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrTrTC])
        tracks = self.tracks
        trackterms = self.tracktconds
        show_tc(table, tracks, trackterms)

    def showts(self):
        """Показати спрощені умови завершимості трас."""
        messLang = self.messLang
        table = self.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        hdrTrack = messLang["hdrTrack"]
        hdrTrSTC = messLang["hdrTrSTC"]
        table.setHorizontalHeaderLabels([hdrTrack, hdrTrSTC])
        tracks = self.tracks
        stracktconds = self.stracktconds
        show_ts(table, tracks, stracktconds)

    def showresults(self):
        """Показати результати роботи програми."""
        table = self.tableWidget
        simplex = self.simplconds
        vcimps = self.vcimps
        params = self.options
        eqtrans = params["eqtrans"]
        stracktconds = self.stracktconds
        tracktconds = self.tracktconds
        if eqtrans == 0:
            simplex = vcimps
            stracktconds = tracktconds
        terman = self.terman
        show_res(self, table, simplex, terman, stracktconds)
        self.btnSave.setEnabled(True)

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

    def setdisable(self):
        """Зробити всі кнопки недоступними."""
        self.btnTracks.setEnabled(False)
        self.btnParams.setEnabled(False)
        self.btnCond.setEnabled(False)
        self.btnSimpl.setEnabled(False)
        self.btnRes.setEnabled(False)
        self.btnSave.setEnabled(False)
        self.btnCP.setEnabled(False)
        self.btnPS.setEnabled(False)
        self.btnCE.setEnabled(False)
        self.btnCT.setEnabled(False)
        self.btnIV.setEnabled(False)
        self.btnCC.setEnabled(False)
        self.btnSC.setEnabled(False)
        self.btnTE.setEnabled(False)
        self.btnTC.setEnabled(False)
        self.btnST.setEnabled(False)
        self.btnZ3.setEnabled(False)
        self.btnAreas.setEnabled(False)
        self.btnTypes.setEnabled(False)

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
        textMenu = messLang["btnCond"]
        self.btnCond.setText(textMenu)
        textMenu = messLang["btnSimpl"]
        self.btnSimpl.setText(textMenu)
        textMenu = messLang["btnZ3"]
        self.btnZ3.setText(textMenu)
        textMenu = messLang["btnOptions"]
        self.btnOptions.setText(textMenu)
        textMenu = messLang["btnAuto"]
        self.btnAuto.setText(textMenu)
        textMenu = messLang["btnRes"]
        self.btnRes.setText(textMenu)
        textMenu = messLang["btnSave"]
        self.btnSave.setText(textMenu)
        textMenu = messLang["btnCP"]
        self.btnCP.setText(textMenu)
        textMenu = messLang["btnPS"]
        self.btnPS.setText(textMenu)
        textMenu = messLang["btnCE"]
        self.btnCE.setText(textMenu)
        textMenu = messLang["btnTE"]
        self.btnTE.setText(textMenu)
        textMenu = messLang["btnCT"]
        self.btnCT.setText(textMenu)
        textMenu = messLang["btnIV"]
        self.btnIV.setText(textMenu)
        textMenu = messLang["btnCC"]
        self.btnCC.setText(textMenu)
        textMenu = messLang["btnTC"]
        self.btnTC.setText(textMenu)
        textMenu = messLang["btnSC"]
        self.btnSC.setText(textMenu)
        textMenu = messLang["btnST"]
        self.btnST.setText(textMenu)


def programverify():
    # if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
