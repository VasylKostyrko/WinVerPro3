"""Цей модуль перетворює вираз з операціями,
заданими в інфіксній формі,
в обернений польский запис.
Обернений польський запис виразу -
це список елементів виразу,
у якому операнди передують операції."""


def operation(el):
    """Визначає, чи текст el є операцією."""
    if el == " -> " or el == " -- ":
        # Імплікація та еквівалентність
        return True
    if el == "+" or el == "-":
        # Унарні операції
        return True
    if el == " +" or el == " -":
        # Унарні операції
        return True
    elif el == " + " or el == " - ":
        # Бінарні операції
        return True
    elif el == " * ":
        return True
    elif el == " == " or el == " != " or el == " < " or el == " <= " or el == " > " or el == " >= ":
        return True
    elif el == " and " or el == " or ":
        return True
    elif el == "not ":
        return True
    return False


def unary(op):
    """Визначаж чи операція op є унарною."""
    if op == "-" or op == "+":
        return True
    if op == " -" or op == " +":
        return True
    elif op == "not ":
        return True
    return False


def is_letter(sym):
    """Визначає, чи символ sym є малою латинською літерою."""
    return "a" <= sym <= "z"


def is_digit(sym):
    """Визначає, чи символ sym є цифрою."""
    return "0" <= sym <= "9"


def peek(stack):
    """Видає останній елемент непустого списку stack."""
    ns = len(stack) - 1
    fs = stack[ns]
    return fs


def priority(op):
    """Визначає пріоритет операції op."""
    if op == "(":
        return 0
    if op == ")":
        return 1
    if op == " -- ":
        # Еквівалентність
        return 2
    if op == " -> ":
        # Імплікація
        return 3
    if op == " or ":
        return 4
    if op == " and ":
        return 5
    if op == "not ":
        return 6
    if op == " == ":
        return 7
    if op == " != ":
        return 7
    if op == " < ":
        return 7
    if op == " <= ":
        return 7
    if op == " > ":
        return 7
    if op == " >= ":
        return 7
    if op == " + ":
        return 8
    if op == " - ":
        return 8
    if op == " * ":
        return 9
    if op == "+":
        # Унарний +
        return 10
    if op == "-":
        # Унарний -
        return 10
    # Інша операція
    return 11


def dijkstra(mode, op, stackop, res):
    """Реалізує алгоритм Дейкстри.
    mode - це тип лексеми:
    u - унарна операція,
    b - бінарна операція,
    ( - дужка,
    v - змінна
    n - число
    e - заключна обробка стеку операцій.
    stackop - це стек операцій,
    res - це результуючий стек елементів виразу.
    Бінарні операції і в інфіксному,
    і в оберненому польському записах
    оточені пропусками."""
    if mode == "v":
        res.append(op)
    elif mode == "n":
        num = int(op)
        res.append(num)
    elif mode == "e":
        ops = stackop.pop()
        res.append(ops)
    else:
        # унарні, бінарні операції або дужки
        if len(stackop) == 0:
            stackop.append(op)
        elif op == "(":
            stackop.append(op)
        elif op == "-" or op == "+":
            # Унарна операція
            stackop.append(op)
        else:
            last = peek(stackop)
            prlast = priority(last)
            priop = priority(op)
            if priop == 0:
                stackop.append(op)
            elif op == ")" and last == "(":
                stackop.pop()
            elif priop > prlast:
                stackop.append(op)
            else:
                while len(stackop) > 0 and priop <= prlast:
                    ops = stackop.pop()
                    res.append(ops)
                    if len(stackop) > 0:
                        last = peek(stackop)
                        prlast = priority(last)
                if last == "(" and op == ")":
                    stackop.pop()
                else:
                    stackop.append(op)


def expr_polish(expr, mode="a"):
    """Функція здійснює лексичний розбір виразу expr,
    записаного в інфіксній формі.
    Бінарні операції оточуються пропусками.
    Перетворює вираз в обернений польський запис.
    Бінарні операції і в інфіксному,
    і в оберненому польському записах
    оточені пропусками.
    Якщо mode = a, тоді у виразі можуть
    бути лише арифметичні операції,
    якщо mode = r, тоді головною операцією виразу
    є операція відношення, а її аргументами -
    арифметичні вирази.
    Якщо mode = b, тоді у виразі
    допускаються також логічні операції."""
    if mode == "a":
        modemess = "арифметичному виразі"
    elif  mode == "r":
        modemess = "відношенні"
    else:
        modemess = ""
    stackop = []
    res = []
    ident = ""
    num = ""
    op = ""
    for sym in expr:
        if sym == "(":
            dijkstra("(", sym, stackop, res)
        elif sym == ")" or sym == " ":
            if len(ident) > 0:
                # Ідентифікатор
                if ident == "not":
                    # Унарна літерна операція
                    if mode in "ar":
                        raise Exception("Помилка: недопустима операція '" + op + "' у " + modemess + ".")
                    dijkstra("u", ident + " ", stackop, res)
                    ident = ""
                elif ident == "and" or ident == "or":
                    # Бінарна літерна операція
                    if mode in "ar":
                        raise Exception("Помилка: недопустима операція '" + op + "' у " + modemess + ".")
                    dijkstra("b", " " + ident + " ", stackop, res)
                    ident = ""
                else:
                    # Змінна
                    if len(op) > 0 and op != " ":
                        # Унарна операція
                        dijkstra("u", op, stackop, res)
                        op = ""
                    if sym == " ":
                        op = " "
                    dijkstra("v", ident, stackop, res)
                    ident = ""
            elif len(num) > 0 and op != " ":
                # Число
                if len(op) > 0:
                    # Унарна операція
                    dijkstra("u", op, stackop, res)
                    op = ""
                if sym == " ":
                    op = " "
                dijkstra("n", num, stackop, res)
                num = ""
            elif len(op) > 0:
                # Завершується бінарна операція
                if op[0] != " ":
                    raise Exception("Помилка: після унарної операції '" + op + "' у виразі йде пропуск.")
                dijkstra("b", op + " ", stackop, res)
                op = ""
            elif sym == " ":
                # Починається бінарна операція
                op = " "
            if sym == ")":
                dijkstra("(", sym, stackop, res)
                op = ""
        elif is_letter(sym):
            if len(num) > 0:
                raise Exception("Помилка: неочікувана поява літери в числі: '" + num + sym + "'.")
            # if len(op) > 0:
            #     raise Exception("Помилка: після бінарної операції : '" + op + "' у виразі немає пропуску.")
            ident += sym
            sym = ""
        elif is_digit(sym):
            # if len(op) > 0:
            #     raise Exception("Помилка: після бінарної операції : '" + str.strip(op) + "' у виразі немає пропуску.")
            if ident == "":
                num += sym
            else:
                ident += sym
            sym = ""
        elif sym == "+" or sym == "-" or sym == "*":
            if op == " ":
                # Бінарна операція
                op = " " + sym
            elif sym == "+" or sym == "-":
                # Унарна операція
                if len(op) > 0:
                    # Декілька унарних операцій підряд
                    dijkstra("u", op, stackop, res)
                if len(ident) !=0 or len(num) != 0:
                    raise Exception("Помилка: перед бінарною операцією '" + sym + "' у виразі немає пропусків.")
                op = sym
        elif sym == "=" or sym == "!" or sym == "<" or sym == ">":
            op += sym
            if mode == "a":
                raise Exception("Помилка: недопустима операція '" + op + "' у " + modemess + ".")
        else:
            raise Exception("Помилка: у виразі зустрівся непередбачуваний символ: '" + sym + "'.")
    # Прикінцева обробка
    if len(ident) > 0:
        dijkstra("v", ident, stackop, res)
        if len(op) > 0:
            # Унарна операція
            dijkstra("u", op, stackop, res)
    if len(num) > 0:
        dijkstra("n", num, stackop, res)
        if len(op) > 0:
            # Унарна операція
            dijkstra("u", op, stackop, res)
    while len(stackop) > 0:
        dijkstra("e", op, stackop, res)
    # if sym != "":
    #     raise Exception("Помилка: у виразі знайдено зайвий символ: '" + sym + "'.")
    return res
