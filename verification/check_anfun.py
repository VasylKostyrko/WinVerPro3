"""Модуль приймає модуль з анотованим описом одної функції і видає
структуру її тіла, список її контрольних точок
і словник з інформацією про їх розташування.
Початкова контрольна точка повинна розташовуватися
одразу після оператора def,
а кінцева контрольна точка повинна бути
в останньому рядку тіла функції.
Таким чином, описи початкової та кінцевої КТ
повинні мати однаковий відступ."""

from verification.common import findoptype, peek, opname, test_type
from z3py.typefun import conv_var_types_to_dict


def check_anfun(win, programfile, dictcppos, dictcpcond, progstru, dicttermexpr, dict_var_types_cp):
    """Зчиитує програму з файлу programfile.
    Перевіряє, чи правильна структура модуля programfile.
    Перевіряє, чи має вона правильно розставлені контрольні точки.
    Утворює словник dictcpcpnd контральних точок програми,
    словник dictcpcond з умовами в контрольнихз точках програми,
    список словників progstru зі структурою програми,
    dicttermexpr - список виразів для доведення завершимості програми.
    Словник dictcppos імені КТ співставляє список з одного чи двох чисел:
    перше число - це номер оператора з КТ, друге стосується
    лише КТ в операторі циклу (while) і задає номер цього оператора
    (I число буде більше від II).
    Повертає також словник dict_var_types_cp з типами змінних в контрольних точках
    (серед них ключ AREA визначає тип змінних за замовчуванням)."""
    messLang = win.messLang
    messlist = []
    standoff = 4
    stackop = []
    nop = 0         # номер оператора в програмі
    numop = -1      # номер оператора в програмі, починаючи від 0 і не рахуючи пустих
    nerr = 0
    offset = 0
    level = 0
    multyline_comment = False
    itisfunction = False
    # itismultycond = False
    defcp = False   # Область опису контрольної точки
    with open(programfile) as program:
        for line in program:
            operator = line.rstrip()
            if len(operator) > 0:
                netop = operator.strip()
                offset = operator.find(netop)
                bodyoff = offset + standoff
                test = checklevel(stackop, offset, numop)
                if not test:
                    # Помилка: Неправильний рівень оператора
                    nerr += 1
                    message = messLang["errStack"]
                    messlist.append(message)
                    res = [nerr, messlist]
                    return res

                if multyline_comment:
                    # Область багаторядкового коментара
                    optype = 10
                    offset = multyline_offset
                    opstru = {"top": optype, "op": netop, "offset": offset, "level": level}
                    progstru.append(opstru)
                    nop += 1
                    numop += 1
                    if netop.find('"""') >= 0:
                        # Завершення багаторядкового коментара
                        multyline_comment = False
                        continue

                optype = operatortype(operator, stackop, bodyoff, numop + 1)
                if defcp:
                    if optype != 1:
                        defcp = False
                if optype == 10:
                    # Початок багаторядкового коментара
                    offs = operator.find('"""')
                    operator_tail = operator[offs + 3:]
                    if operator_tail.find('"""') == -1:
                        multyline_comment = True
                        multyline_offset = offset
                elif optype == 11:
                    # Опис області даних програми
                    area = str.strip(netop[1:])
                    area_type = area[5: -1]
                    dict_var_types_cp["AREA"] = area_type
                    if not test_type(area_type):
                        # непередбачений тип даних
                        nerr += 1
                        message = messLang["errType"] + " " + netop + "!"
                        messlist.append(message)
                elif optype == 0:
                    # Опис контрольної точки
                    netop = str.strip(netop[1:])
                    pos = netop.find(":")
                    if pos == -1:
                        # Помилка: немає двокрапки
                        nerr += 1
                        netop += 1
                        message = messLang["errEmpCP1"] + netop + messLang["errEmpCP3"]
                        messlist.append(message)
                        cp = netop
                    else:
                        # Виділяємо ім'я контрольної точки
                        excp = netop[0:pos].strip()
                        n1 = netop.find("(")
                        cp = excp[n1 + 1: -1].strip()
                        defcp = True
                        cond = []
                    if dictcppos.get(cp, -1) > 0:
                        nerr += 1
                        message = messLang["errRepCP1"] + cp + messLang["errRepCP2"]
                        messlist.append(message)
                    if cp == "I":
                        if len(dictcppos) > 0:
                            nerr += 1
                            message = messLang["errInCPnf"]
                            messlist.append(message)
                        if not itisfunction:
                            if offset > 0:
                                nerr += 1
                                message = messLang["errInCPb"]
                                messlist.append(message)
                        dictcppos[cp] = [numop + 1]
                    elif cp == "E":
                        if itisfunction:
                            pass
                        elif offset > 0:
                            nerr += 1
                            message = messLang["errEndCPe"]
                            messlist.append(message)
                        dictcppos[cp] = [numop + 1]
                    else:
                        # Контрольна точка циклу
                        strop = peek(stackop)
                        typop = strop[1]
                        if typop == 2:
                            nloop = strop[0]
                            stackop.pop()
                            if len(strop) == 3:
                                strop.append(cp)
                            else:
                                nerr += 1
                                message = messLang["errLoop1"] + str(nloop) + messLang["errLoop2"] + strop[3] + ")!"
                                messlist.append(message)
                            stackop.append(strop)
                            dictcppos[cp] = [numop + 1, nloop]
                        elif typop > 0:
                            nerr += 1
                            message = messLang["errIfCP1"] + netop + messLang["errIfCP2"] + opname(typop) + ")!"
                            messlist.append(message)
                        else:
                            nerr += 1
                            message = messLang["errAnnStr"]
                            messlist.append(message)
                elif optype == 1:
                    # коментар або область опису контрольної точки
                    if defcp:
                        # область опису контрольної точки cp
                        linecp = netop[1:].strip()
                        if linecp == "ECP":
                            # Кінець області опису контрольної точки
                            defcp = False
                            dictcpcond[cp] = cond
                        else:
                            if linecp.startswith("VE("):
                                # Опис виразу варіанта
                                ve = linecp[3: -1]
                                # lenve = len(ve)
                                # ve = ve[0: lenve - 1]
                                dicttermexpr[cp] = ve
                            else:
                                if linecp.startswith("TYPE("):
                                    # Опис типів змінних
                                    vartypes = linecp[5: -1]
                                    dict_var, types_set = conv_var_types_to_dict(vartypes)
                                    dict_var_types_cp[cp] = dict_var
                                    for curtype in types_set:
                                        if not test_type(curtype):
                                            nerr += 1
                                            message = messLang["errType"] + " " + curtype + "!"
                                            messlist.append(message)
                                else:
                                    # відношення
                                    rel = linecp
                                    cond.append(rel)
                    opstru = {"top": 13, "op": netop, "offset": offset, "level": level}
                    progstru.append(opstru)
                    numop += 1
                    continue

                # інші структурні оператори
                elif optype == 2:
                    # Оператор while
                    if dictcppos.get("I", -1) == -1:
                        nerr += 1
                        message = messLang["errLoopCP1"] + str(nop) + messLang["errLoopCP2"]
                        messlist.append(message)
                elif optype == 8:
                    # Заголовок функції
                    itisfunction = True
                    if len(dictcppos) > 0:
                        nerr += 1
                        message = messLang["errFunCP"]
                        messlist.append(message)
                elif optype == 9:
                    # Оператор return
                    if dictcppos.get("E", -1) == -1:
                        nerr += 1
                        message = messLang["errRetCP"]
                        messlist.append(message)
                level = len(stackop) - 1

                # Структура програми
                if optype == 0:
                    op = operator.strip()
                else:
                    op = netop
                # opstru = {"top": optype, "op": netop, "offset": offset, "level": level}
                opstru = {"top": optype, "op": op, "offset": offset, "level": level}
                progstru.append(opstru)
                numop += 1
            nop += 1
        if nop == 0:
            nerr += 1
            message = messLang["errPrEmp"]
            messlist.append(message)
        if len(stackop) > 1:
            nerr += 1
            message = messLang["errPrStr"]
            messlist.append(message)
        if offset > 0:
            nerr += 1
            message = messLang["errPrStr"]
            messlist.append(message)
        if level > 0:
            nerr += 1
            message = messLang["errPrStr"]
            messlist.append(message)
        if len(dictcppos) == 0:
            nerr += 1
            message = messLang["errNoCP"]
            messlist.append(message)
        elif dictcppos.get("I", -1) == -1:
            nerr += 1
            message = messLang["errInitCP"]
            messlist.append(message)
        elif dictcppos.get("E", -1) == -1:
            nerr += 1
            message = messLang["errEndCP"]
            messlist.append(message)
        res = [nerr, messlist]
        return res


def checklevel(stackop, offset, nop):
    """"Функція перевіряє, чи поточний оператор не повертає виконання на нижчий рівень дерева тіла функції.
    Якщо повертає, то функція викидує зі stackop елементи, поки не вийде на той же рівень."""
    res = True
    if len(stackop) > 0:
        fstack = peek(stackop)
        # optype = fstack[1]
        if offset < fstack[2]:
            while offset < fstack[2]:
                stackop.pop()
                fstack = peek(stackop)
                optype = fstack[1]
                if optype == 2:
                    if len(fstack) == 3:
                        res = False
    else:
        # початок тіла функції
        stackop.append([nop, -1, offset])
    return res


def operatortype(operator, stackop, bodyoff, nop):
    """Аналізує оператор тіла функції. Визначає тип оператора.
    Якщо оператор структурний, то в stackop додає елемент
    з його типом, відступом bodyoff тіла оператора та
    його номером nop в програмі."""
    typop = findoptype(operator)
    if typop == 2:
        # Заголовок оператора циклу while
        stackop.append([nop, typop, bodyoff])
        return typop
    if typop == 3:
        # Заголовок if умовного оператора
        stackop.append([nop, typop, bodyoff])
        return typop
    if typop == 4:
        # Заголовок elif умовного оператора
        stackop.append([nop, typop, bodyoff])
        return typop
    if typop == 5:
        # Заголовок else умовного оператора
        stackop.append([nop, typop, bodyoff])
        return typop
    # Інакше оператор є звичайним коментарем (1), початком баторядкового коментара (10),
    #     початком опису контрольної точки програми (0), описом AREA області даних програми (11),
    #     заголовком функції (8), оператором return (9), оператором присвоювання (6)
    #     або оператором виводу (7).
    return typop


def readprog(programfile):
    """Зчитує файл програми programfile і будує список listop її операторів."""
    listop = []
    with open(programfile) as program:
        for line in program:
            operator = line.rstrip()
            typop = findoptype(operator)
            listop.append({"op": operator, "top": typop})
    return listop


def genstrprog(strprog):
    """У списку strprog зі структурою програми
    словник кожного структурного оператора доповнює
    елементом з ключем nextop, який задає
    номер останнього оператора його тіла."""
    strops = [2, 3, 4, 5, 8]    # Типи структурних операторів (функція findoptype)
    stackop = []
    loffso = 0
    i = 0
    for elstr in strprog:
        typop = elstr["top"]
        loffset = elstr["offset"]
        while loffset < loffso:
            # Вихід (підйом) зі структурного оператора в програму
            elstack = stackop.pop()
            nso = elstack[0]
            loffso = elstack[1]
            strop = strprog[nso]
            strop["nextop"] = i
        if typop in strops:
            # Початок структурного опратора
            stackop.append([i, loffset])
        elif typop == 0:
            # Контрольна точка
            pass
        else:
            loffso = loffset
        i += 1


def cplist(dictcp):
    """На базі словника dictcp КТ програми формує список listcp контрольних точок програми."""
    listcp = []
    for cp in dictcp:
        # if cp != "#CP_E":
        listcp.append(cp)
    return listcp


def istrack(expr):
    """Перевіряє, чи вираз expr задає трасу."""
    if type(expr) is str:
        pos = expr.find(" -> ")
        if pos == -1:
            return False
        icp = expr[:pos]
        ecp = expr[pos + 4:]
        if icp[:3] == "CP_" and ecp[:3] == "CP_":
            return True
        else:
            return False
    else:
        return False
