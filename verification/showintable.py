from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QColor, QBrush
from exprlib.logilib.implication import impexpr, Implication
from exprlib.treelib.tree import treeexpr
from verification.language import nounagree, plural
import os.path
import json
from z3py.typefun import param_types_str


def showanprog(table, filename, win):
    """З файла filename зчитує занотовану програму
    і відображає в таблиці table.
    Якщо при відкритті файлу виникає помилка,
    то помилку показує на панелі статусу вікна win."""
    annprog = ""
    numrows = 0
    try:
        with open(filename, 'r', encoding='utf-8') as file_object:
            for line in file_object:
                op = line.rstrip()
                numrows += 1
                table.setRowCount(numrows)
                cell = QTableWidgetItem(op)
                table.setItem(numrows - 1, 0, cell)
                annprog += line
            table.resizeColumnsToContents()
        return annprog
    except OSError:
        win.statusBar().showMessage('Помилка в імені файла!')


def showerrlist(win, table, res):
    """В таблицю table видає список помилок errlist."""
    messLang = win.messLang
    numrows = table.rowCount()
    nerr = res[0]
    errlist = res[1]
    numrows += 1
    if nerr > 0:
        message = messLang["errPrStr"]
        table.setRowCount(numrows)
        cell = QTableWidgetItem(message)
        table.setItem(numrows - 1, 0, cell)
        if nerr > 0:
            table.item(numrows - 1, 0).setForeground(QBrush(QColor(255, 0, 0)))

        for err in errlist:
            numrows += 1
            table.setRowCount(numrows)
            cell = QTableWidgetItem(err)
            table.setItem(numrows - 1, 0, cell)
            table.item(numrows - 1, 0).setForeground(QBrush(QColor(255, 0, 0)))
        table.resizeColumnsToContents()


def show_cp(win, table, dictcppos):
    """Відображає в таблиці контрольні точки програми."""
    messLang = win.messLang
    numrows = 0
    for cp in dictcppos:
        numrows += 1
        table.setRowCount(numrows)
        cell = QTableWidgetItem(cp)
        table.setItem(numrows - 1, 0, cell)
        if cp == "I":
            com = messLang["initCP"]
        elif cp == "E":
            com = messLang["endCP"]
        else:
            addr = dictcppos[cp]
            if len(addr) == 2:
                com = messLang["loopCP"]
            else:
                com = messLang["otherCP"]
        cell = QTableWidgetItem(com)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_ce(table, dictcppos, cpdictctrees):
    """Відображає в таблиці умови в контрольних точках програми
    зі словника cpdictctrees."""
    numrows = 0
    for cp in dictcppos:
        cpcond = ""
        cpctree = cpdictctrees.get(cp, -1)
        if cpctree != -1:
            cpcond = treeexpr(cpctree)
        numrows += 1
        table.setRowCount(numrows)
        cell = QTableWidgetItem(cp)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(cpcond)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_ps(table, progstru):
    """Відображає в таблиці структуру програми."""
    numrows = 0
    for opstru in progstru:
        numrows += 1
        table.setRowCount(numrows)
        op = opstru["op"]
        cell = QTableWidgetItem(op)
        table.setItem(numrows - 1, 0, cell)
        optype = opstru["top"]
        cell = QTableWidgetItem(str(optype))
        table.setItem(numrows - 1, 1, cell)
        offset = opstru["offset"]
        cell = QTableWidgetItem(str(offset))
        table.setItem(numrows - 1, 2, cell)
        level = opstru["level"]
        cell = QTableWidgetItem(str(level))
        table.setItem(numrows - 1, 3, cell)
    table.resizeColumnsToContents()


def show_ct(table, tracks):
    """Відображає в таблиці контрольні шляхи в програмі."""
    numrows = 0
    for track in tracks:
        if track is not None:
            numrows += 1
            table.setRowCount(numrows)
            strack = ""
            icp = ""
            ecp = 0
            nel = len(track)
            n = 0
            for op in track:
                n += 1
                if n == 1:
                    icp = op
                elif n == nel:
                    ecp = op
                else:
                    if strack == "":
                        strack = op
                    else:
                        strack += ", " + op
            cps = icp + " -> " + ecp + ":"
            cell = QTableWidgetItem(cps)
            table.setItem(numrows - 1, 0, cell)
            cell = QTableWidgetItem(strack)
            table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_iv(table, tracks, initvartrees):
    """Відображає в таблиці початкові значення змінних трас
    зі списку initvartrees."""
    numrows = 0
    for track in tracks:
        numrows += 1
        icp = track[0]
        nel = len(track)
        ecp = track[nel - 1]
        ivartree = initvartrees[numrows - 1]
        ivlist = ""
        n = 0
        for var in ivartree:
            el = ivartree[var]
            n += 1
            val = var + " = " + treeexpr(el)
            if n == 1:
                ivlist = val
            else:
                ivlist += ", " + val
        table.setRowCount(numrows)
        cps = icp + " -> " + ecp + ":"
        cell = QTableWidgetItem(cps)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(ivlist)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_cc(table, tracks, vctrees):
    """Відображає в таблиці умови коректності трас,
    представлені списком vctrees об'єктів класу Implication."""
    numrows = 0
    for track in tracks:
        numrows += 1
        icp = track[0]
        nel = len(track)
        ecp = track[nel - 1]
        cps = icp + " -> " + ecp + ":"
        imp = vctrees[numrows - 1]
        cond = imp.tostring()
        if type(cond) is bool:
            scond = str(cond)
        else:
            scond = cond
        table.setRowCount(numrows)
        cell = QTableWidgetItem(cps)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(scond)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_sc(table, tracks, simplconds):
    """Відображає в таблиці список simplconds
    спрощених умов коректності трас."""
    numrows = 0
    for track in tracks:
        numrows += 1
        icp = track[0]
        nel = len(track)
        ecp = track[nel - 1]
        cps = icp + " -> " + ecp + ":"
        imp = simplconds[numrows - 1]
        nOK = 0
        if type(imp) is bool:
            expr = str(imp)
            if imp is True:
                nOK += 1
        else:
            expr = impexpr(imp)
        table.setRowCount(numrows)
        cell = QTableWidgetItem(cps)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(expr)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def cleartable(win):
    """Очищає таблицю у вікні win."""
    table = win.tableWidget
    table.clear()
    table.setRowCount(0)
    table.setColumnCount(0)


def show_te(table, dicttermtrees):
    """Відображає в таблиці вирази завершення
    зі словника dicttermtrees."""
    numrows = 0
    for cp in dicttermtrees:
        numrows += 1
        termtree = dicttermtrees[cp]
        termexpr = treeexpr(termtree)
        table.setRowCount(numrows)
        cell = QTableWidgetItem(cp)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(termexpr)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_tc(table, tracks, trackterms):
    """Відображає в таблиці умови завершення трас.
    tracks - це список трас,
    trackterms - це список умов завершення трас."""
    numrows = 0
    for track in tracks:
        numrows += 1
        icp = track[0]
        tracklen = len(track)
        ecp = track[tracklen - 1]
        cps = icp + " -> " + ecp + ":"
        if icp == "I" or ecp == "E":
            expr = "---"
        else:
            trackterm = trackterms[numrows - 1]
            expr = impexpr(trackterm)
        table.setRowCount(numrows)
        cell = QTableWidgetItem(cps)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(expr)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_ts(table, tracks, stracktconds):
    """Відобразити в таблиці спрощені умови завершення трас.
    tracks - це список трас,
    trackterms - це список спрощених умов завершення трас."""
    numrows = 0
    for track in tracks:
        numrows += 1
        icp = track[0]
        tracklen = len(track)
        ecp = track[tracklen - 1]
        cps = icp + " -> " + ecp + ":"
        if icp == "I" or ecp == "E":
            expr = "---"
        else:
            stracktcond = stracktconds[numrows - 1]
            expr = impexpr(stracktcond)
            stracktconds[numrows - 1] = expr
            if type(expr) is bool:
                expr = str(expr)
        table.setRowCount(numrows)
        cell = QTableWidgetItem(cps)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(expr)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_res(win, table, simplex, terman, stracktconds):
    """Відображає в таблиці результати перевірки коректності програми."""
    messLang = win.messLang
    lang = win.language
    nok = 0
    ntermok = 0
    numrows = 0
    n = 0
    for cp in simplex:
        n += 1
        imp = simplex[n - 1]
        expr = impexpr(imp)
        if expr is True:
            nok += 1

    mes = ""
    if terman:
        for stracktcond in stracktconds:
            if stracktcond == "":
                ntermok += 1
            elif type(stracktcond) is bool:
                if stracktcond:
                    ntermok += 1
            elif type(stracktcond) is Implication:
                cons = stracktcond.getcons()
                if cons.len() == 0:
                    ntermok += 1
        if nok == n and ntermok == n:
            mes = messLang["resTCorr"]
        elif nok == n:
            mes = messLang["resCorr"]
    else:
        ntermok = n
        if nok == n:
            mes = messLang["resCorr"]
    table.clear()
    table.setColumnCount(1)
    table.setHorizontalHeaderLabels(["Результати"])
    if mes != "":
        numrows += 1
        table.setRowCount(numrows)
        cell = QTableWidgetItem(mes)
        table.setItem(numrows - 1, 0, cell)

    mes = ""
    if n - nok > 0 or n - ntermok > 0:
        mes = messLang["resCorr1"]
    mescond = messLang["hdrCond"].lower()
    mescorr = messLang["valCorrG"]
    mesand = messLang["and"]
    mesterm = messLang["valTermG"]
    if n - nok > 0:
        if lang == "uk":
            mes += " " + nounagree(n - nok, mescond) + " " + mescorr
        else:
            mes += " " + mescorr + " " + plural(n - nok, mescond)

    if n - nok > 0 and n - ntermok > 0:
        mes += " " + mesand
    if n - ntermok > 0:
        if lang == "uk":
            mes += " " + nounagree(n - ntermok, mescond) + " " + mesterm
        else:
            mes += " " + mesterm + " " + plural(n - ntermok, mescond)
    if n - nok > 0 or n - ntermok > 0:
        mes += " " + messLang["mesPrTr"].lower() + "."

    if mes != "":
        numrows += 1
        table.setRowCount(numrows)
        cell = QTableWidgetItem(mes)
        table.setItem(numrows - 1, 0, cell)
    table.resizeColumnsToContents()


def buildAllCondsFile(scondlist, stcondlist, program, dict_param_types_cp, tracks):
    """Будує текстовий файл формату JSON з усіми умовами.
    scondlist - це список умов коректності з номерами трас,
    stcondlist - це список умов завершимості з номерами трас.
    program - це ім'я аналізованої програми.
    dict_param_types_cp - це словник типів параметрів умов в КТ.
    tracks - це список трас програми."""
    jsonObj = {"program": program}
    arcs = []
    for elc in scondlist:
        ns = elc[0]
        scond = elc[1]
        exprc = impexpr(scond)
        track = tracks[ns]
        initcp = track[0]
        dict_param_types = dict_param_types_cp[initcp]
        param_types = param_types_str(dict_param_types)
        arc = [ns, exprc, param_types]
        arcs.append(arc)
    jsonObj["correctness"] = arcs
    arts = []
    for elt in stcondlist:
        nt = elt[0]
        tcond = elt[1]
        exprt = impexpr(tcond)
        track = tracks[nt]
        initcp = track[0]
        dict_param_types = dict_param_types_cp[initcp]
        param_types = param_types_str(dict_param_types)
        art = [nt, exprt, param_types]
        arts.append(art)
    jsonObj["termination"] = arts
    curdir = os.path.abspath(os.curdir)
    filename = curdir + "\\export\\" + program + "_ct.json"
    with open(filename, 'w') as file_object:
        json.dump(jsonObj, file_object, indent=4)


def viewErrMsg(win, errMsg):
    """Відображає таблицю з повідомленням про помилку!"""
    table = win.tableWidget
    if win.language == "en":
        hdrMsg = "Message"
    else:
        hdrMsg = "Повідомлення"
    table.setHorizontalHeaderLabels([hdrMsg])
    table.setColumnCount(1)
    numrows = 1
    table.setRowCount(numrows)
    cell = QTableWidgetItem(errMsg)
    table.setItem(numrows - 1, 0, cell)
    table.item(numrows - 1, 0).setForeground(QBrush(QColor(255, 0, 0)))
    table.resizeColumnsToContents()


def testLang(win, lang):
    """Перевіряє, чи lang = 'en' або 'uk'.
    інакше блокує дальшу роботу, видаючи помилку англійсьою мовою."""
    if lang == 'en' or lang == 'uk':
        return True
    else:
        errMsg = "Error: unexpected language symbol '" + lang + "'!"
        viewErrMsg(win, errMsg)
        return False


def getTextLang(lang):
    """Вибирає зі словника langMess повідомлення мовою lang і повертає словник з ними:
    en - англійською, uk - українською. """
    curdir = os.path.abspath(os.curdir)
    fname = curdir + '/verification/langMess.json'
    if not os.path.isfile(fname):
        return ""
    with open(fname, 'r', encoding='utf-8') as file_object:
        messTexts = json.load(file_object)
    textKeys = messTexts.keys()
    messLang = {}
    for key in textKeys:
        textLang = messTexts[key]
        text = textLang[lang]
        messLang[key] = text
    return messLang


def testConds(vcimps, tracktconds):
    """Перевіряє, чи потрібно щось робити з умовами."""
    res = True
    for vc in vcimps:
        if vc is not True:
            res = False
    for tc in tracktconds:
        if tc is not True and tc != "":
            res = False
    return res


def show_types_in_table(table, dict_type_vars_cp):
    """Показує типи даних змінних програми в КТ."""
    numrows = 0
    for cp in dict_type_vars_cp:
        cp_var_types = ""
        numrows += 1
        dict_types = dict_type_vars_cp[cp]
        ntype = 0
        for curtype in dict_types:
            ntype += 1
            if ntype > 1:
                cp_var_types += "; "
            varlist = dict_types[curtype]
            nvar = 0
            for var in varlist:
                nvar += 1
                if nvar > 1:
                    cp_var_types += ", "
                cp_var_types += var
            cp_var_types += ": " + curtype

        table.setRowCount(numrows)
        cell = QTableWidgetItem(cp)
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(cp_var_types)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()


def show_areas_in_table(table, init_dict_var_types, area):
    # Показати області даних програми
    numrows = 0
    if area != "":
        numrows += 1
        table.setRowCount(numrows)
        cell = QTableWidgetItem("AREA")
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(area)
        table.setItem(numrows - 1, 1, cell)
    var_type_list = list(init_dict_var_types.values())
    alltypes = set()
    for vardict in var_type_list:
        types = set(vardict.values())
        alltypes.update(types)
    for curtype in alltypes:
        numrows += 1
        table.setRowCount(numrows)
        cell = QTableWidgetItem("TYPE")
        table.setItem(numrows - 1, 0, cell)
        cell = QTableWidgetItem(curtype)
        table.setItem(numrows - 1, 1, cell)
    table.resizeColumnsToContents()
