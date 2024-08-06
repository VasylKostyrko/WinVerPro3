"""Модуль приймає структуру анотованої програми,
і словник розташування її контрольних точок.
Видає список tracks трас програми."""

from verification.common import checkass, findoptype, negation


def opcond(netop):
    """Визначає тип оператора.
    Якщо це оператор присвоювання, то просто повертає список з ним же.
    Якщо це оператор умовний (if), тоді повертає його умову.
    Якщо це оператор циклу, тоді повертає умову продовження циклу."""
    typop = findoptype(netop)
    if typop == 2:
        sample = "while "
        lsample = len(sample)
        lop = len(netop)
        cond = netop[lsample: lop - 1]
        return [typop, cond]
    if typop == 3:
        sample = "if "
        lsample = len(sample)
        lop = len(netop)
        cond = netop[lsample: lop - 1]
        return [typop, cond]
    if typop == 4:
        sample = "elif "
        lsample = len(sample)
        lop = len(netop)
        cond = netop[lsample: lop - 1]
        return [typop, cond]
    if typop == 5:
        cond = ""
        return [typop, cond]
    if checkass(netop):
        return [6, netop]
    # Інші прості оператори, рядки опису контрольний точок та коментарі ігноруються
    return []


def generate(progstr, dictcp, cp):
    """Зі структури програми progstr в словник track додає основну трасу,
    яка починаються контрольною точкою cp.
    cpdict - це словник контрольних точок."""
    cptracks = []
    nopcp = dictcp[cp][0]
    el = progstr[nopcp]
    offprev = el["offset"]
    track = [cp]
    offcp = offprev  # Відступ КТ
    stackop = []
    staccond = []
    # Аналіз структури програми починаємо з наступного оператора після cp

    i = nopcp + 1
    fin = False
    numlist = dictcp[cp]
    cploop = (len(numlist) == 2)    # КТ знаходиться в циклі, отже, і поточний оператор теж в циклі

    while not fin:
        while True:
            el = progstr[i]
            if el["top"] == 13:
                # Продовження опису контрольної точки
                i += 1
                continue
            op = el["op"]
            netop = op.strip()
            # offset = op.find(netop)
            offset = el["offset"]
            if cp != "I":
                if offset < offcp:
                    if cploop:
                        # Вискочили з циклу, повертаємося на його початок
                        i = dictcp[cp][1]
                        el = progstr[i]
                        offprev = el["offset"]
                        cploop = False
                        continue
            # if netop.startswith("CP"):
            if el["top"] == 0:
                # Кінцева КТ траси
                pos = netop.find("(")
                if pos >=0:
                    cp_end = netop[pos + 1: -2]
                track.append(cp_end)
                break
            if offset < offprev:
                # Закінчився структурний оператор
                nstrop = stackop.pop()
                elstr = progstr[nstrop]
                typop = elstr["top"]
                if typop == 3:
                    nstrop = elstr["nextop"]
                    elstr = progstr[nstrop]
                    typop = elstr["top"]
                    if typop == 4:
                        nstrop = elstr["nextop"]
                        elstr = progstr[nstrop]
                        typop = elstr["top"]
                    if typop == 5:
                        nstrop = elstr["nextop"]
                        elstr = progstr[nstrop]
                    i = nstrop
                    continue

            # Накінець приступаємо до аналізу поточного оператора
            opc = opcond(netop)
            if len(opc) == 0:
                i += 1
                continue
            top = opc[0]
            expr = opc[1]
            if top == 6:
                # Присвоювання
                track.append(expr)
                offprev = offset
                i += 1
                continue
            if top == 2:
                # Цикл
                track.append(expr)
                stackop.append(i)
                offprev = offset
                ncond = len(track)
                staccond.append([i, ncond, track])
                i += 1
                continue
            elif top == 3:
                # Умовний, гілка if
                track.append(expr)
                stackop.append(i)
                offprev = offset
                ncond = len(track)
                staccond.append([i, ncond, track])
                i += 1
                continue
            elif top == 4:
                # Умовний, гілка elif
                track.append(expr)
                stackop.append(i)
                offprev = offset
                ncond = len(track)
                staccond.append([i, ncond, track])
                i += 1
                continue
            elif top == 5:
                # Умовний, гілка else
                track.append(expr)
                stackop.append(i)
                offprev = offset
                ncond = len(track)
                staccond.append([i, ncond, track])
                i += 1
                continue

        # Генеруємо решту траси
        cptracks.append(track)
        if len(staccond) == 0:
            fin = True
        else:
            el = staccond.pop()
            nop = el[0]
            elstr = progstr[nop]
            nextop = elstr["nextop"]
            track = el[2]
            ncond = el[1]
            track = track.copy()
            cond = ""
            while len(track) >= ncond:
                cond = track.pop()
            newcond = negation(cond)
            track.append(newcond)
            i = nextop
    return cptracks


def gentracks(progstr, dictcppos):
    """Утворює список tracklist трас програми зі структурою progstr.
    dictcppos - це словник КТ."""
    tracklist = []
    for cp in dictcppos:
        if cp == "E":
            continue
        cptracks = generate(progstr, dictcppos, cp)
        for tr in cptracks:
            tracklist.append(tr)
    return tracklist
