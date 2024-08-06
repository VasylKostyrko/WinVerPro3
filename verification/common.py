"""Модуль об'єднує відносно прості функції,
які застосвуються в багатьох інших модулях."""
import json
import os.path


def identifier(fragm):
    """Перевіряє, чи текст fragm є ідентифікатором."""
    for x in fragm:
        if not ('a' <= x.lower() <= 'z' or x == '_' or '0' <= x.lower() <= '9'):
            return False
    x = fragm[0]
    return 'a' <= x.lower() <= 'z' or x == '_'


def isnumber(fragm):
    """Перевіряє, чи текст fragm задає ціле число без знаку."""
    if len(fragm) == 0:
        return False
    for x in fragm:
        if not ('0' <= x <= '9'):
            return False
    return True


def signednumber(fragm):
    """Перевіряє, чи текст fragm задає ціле число зі знаком або без."""
    sym = fragm[0]
    if sym == "+" or sym == "-":
        num = fragm[1:]
    else:
        num = fragm
    res = isnumber(num)
    return res


def assignment(op):
    """Якщо текст op місить символи +=, -=, *= або просто =,
    тоді функція виділяє ліву частину оператора і перевіряє, чи вона є ідентифікатором.
    Якщо так, то функція розглядає op як оператор присвоювання
    і повертає список з непустих лівої та правої часин оператора.
    Інакше повертає пустий список."""
    n = op.find("=")
    if n == 0:
        return []
    left_ass = op[: n].strip()
    if len(left_ass) == 0:
        return[]
    accum = op[n - 1]
    if accum in ["+", "-", "*"]:
        left_ass = op[: n - 1].strip()
        right_ass = left_ass + " " + accum + " "
    else:
        accum = ""
        right_ass = ""
    if identifier(left_ass):
        right_ass = right_ass + op[n + 1:].strip()
        return [left_ass, right_ass]
    else:
        return []


def checkass(op):
    """Перевіряє, чи текст op є оператором присвоювання."""
    strass = assignment(op)
    if len(strass) == 0:
        return False
    return True


def findoptype(operator):
    """Визначає тип оператора operator."""
    op = operator.strip()
    # КТ або коментар
    if op.startswith("#"):
        # контрольна точка або коментар
        netop = str.strip(op[1:])
        if netop.startswith("CP("):
            # Контрольна точка
            return 0
        elif netop.startswith("AREA("):
            # Опис області даних програми
            return 11
        else:
            # Коментар
            return 1
    if op.startswith("while "):
        return 2
    if op.startswith("if "):
        return 3
    if op.startswith("elif "):
        return 4
    if op.startswith("else:"):
        return 5
    if checkass(op):
        # Оператор присвоювання
        return 6
    if op.startswith("print("):
        # Оператор виводу
        return 7
    if op.startswith("def"):
        # Заголовок опису функції
        return 8
    if op.startswith("return"):
        # Завершення виконання тіла
        return 9
    if op.startswith('"""'):
        # початок багаторядкового коментара
        return 10
    # Інші прості оператори: виводу, вводу
    return 12


def getoffset(op):
    """Виділяє відступ offset оператора op."""
    netop = op.strip()
    offset = op.find(netop)
    return offset


def negation(cond):
    """Будує заперечення заданої умови cond."""
    if cond == "True":
        return "False"
    if cond == "False":
        return "True"
    if cond.find(" and ") >= 0:
        return "not " + cond
    if cond.find(" or ") >= 0:
        return "not " + cond
    if cond.find("(not ") >= 0:
        return "not " + cond
    if cond.startswith("not "):
        return cond.replace("not ", "")
    if cond.find(" == ") >= 0:
        return cond.replace(" == ", " != ")
    if cond.find(" != ") >= 0:
        return cond.replace(" != ", " == ")
    if cond.find(" < ") >= 0:
        return cond.replace(" < ", " >= ")
    if cond.find(" <= ") >= 0:
        return cond.replace(" <= ", " > ")
    if cond.find(" > ") >= 0:
        return cond.replace(" > ", " <= ")
    if cond.find(" >= ") >= 0:
        return cond.replace(" >= ", " < ")
    return "not " + cond


def peek(stack):
    """Видає останній елемент непустого списку stack."""
    ns = len(stack) - 1
    fs = stack[ns]
    return fs


def fop(stack):
    """Видає останній елемент списку stack,
    видаляючи його зі списку."""
    nstack = len(stack) - 1
    fstack = stack[nstack]
    del stack[nstack]
    return fstack


def isletter(sym):
    """Визначає, чи символ sym є малою латинською літерою."""
    return "a" <= sym <= "z"


def isdigit(sym):
    """Визначає, чи символ sym є цифрою."""
    return "0" <= sym <= "9"


def operation(el):
    """Визначає, чи текст el є операцією."""
    if el == "+" or el == "-":
        return True
    elif el == "*":
        return True
    elif el == "==" or el == "!=" or el == "<" or el == "<=" or el == ">" or el == ">=":
        return True
    elif el == "and" or el == "or":
        return True
    elif el == "not":
        return True
    elif el == "->":
        # Імплікація
        return True
    elif el == "--":
        # Еквівалентність
        return True
    return False


def opname(optype):
    """Видає назву оператора за його типом."""
    optypes = ["Контрольна точка",          #0
               "Рядковий коментар",         #1
               "Цикл while",                #2
               "Гілка if",                  #3
               "Гілка elif",                #4
               "Гілка else",                #5
               "Присвоювання",              #6
               "Виводу",                    #7
               "Заголовок функції",         #8
               "Оператор return",           #9
               "Багаторядковий коментар",   #10
               ]
    res = optypes[optype]
    return res


def relopcod(op):
    """Визнає код операції для впорядування відношень у кон'юнкції."""
    if op == "==":
        return "1"
    elif op == "!=":
        return "2"
    elif op == ">":
        return "3"
    elif op == ">=":
        return "4"
    elif op == "<":
        return "5"
    elif op == "<=":
        return "6"
    else:
        return "7"


def saveProgNameOpt(netname, options):
    """Оновити файл параметрів, ваписавши в нього вибране ім'я netname анотованої програми.
    Повертає оновлеий список параметрів."""
    curdir = os.path.abspath(os.curdir)
    fname = curdir + '\\options.json'
    options["program"] = netname
    with open(fname, 'w', encoding='utf-8') as file_object:
        json.dump(options, file_object, indent=4)
    return options


def test_type(curtype):
    """Перевіряє, чи curtype є дозволеним типом даних."""
    if curtype == "Int":
        return True
    elif curtype == "Real":
        return True
    elif curtype == "Char":
        return True
    elif curtype == "Bool":
        return True
    elif curtype == "Array(Int)":
        return True
    elif curtype == "Array(Real)":
        return True
    elif curtype == "Array(Char)":
        return True
    else:
        return False
