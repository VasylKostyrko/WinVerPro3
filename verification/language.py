"""Модуль призначений для узгодження чисел
з іменниками в текстових повідомленнях."""

# Знахідний відмінок
nounscaselistz = [{"m": "тотожність", 1: "тотожність", 2: "тотожності", 5: "тотожностей"},
                 {"m": "повторення", 1: "повторення", 2: "повторення", 5: "повторень"},
                 {"m": "кон'юнкт", 1: "кон'юнкт", 2: "кон'юнкти", 5: "кон'юнктів"},
                 {"m": "умова", 1: "умову", 2: "умови", 5: "умов"},
                 {"m": "константа", 1: "константу", 2: "константи", 5: "констант"}]

# Родовий відмінок
nounscaselistr = [{"m": "тотожність", 1: "тотожності", 2: "тотожностей", 5: "тотожностей"},
                 {"m": "повторення", 1: "повторення", 2: "повторень", 5: "повторень"},
                 {"m": "кон'юнкт", 1: "кон'юнкта", 2: "кон'юнктів", 5: "кон'юнктів"},
                 {"m": "умова", 1: "умови", 2: "умов", 5: "умов"},
                 {"m": "константа", 1: "константи", 2: "констант", 5: "констант"}]


def nounagree(num, noun, case = "з", join = True):
    """Визначає, чи передбачений іменник noun в списку nounscaselist.
    Якщо так, то узгоджує число num з іменником noun у відмінку case.
    Інакше просто повертає іменник noun.
    За замовчуванням приймається знахідний відмінок."""
    if case == "з":
        nounscaselist = nounscaselistz
    else:
        # Родовий відмінок
        nounscaselist = nounscaselistr
    for nouncase in nounscaselist:
        main = nouncase["m"]
        if noun == main:
            nounform = nounagreecase(num, nouncase)
            if join:
                nounform = str(num) + " " + nounform
            return nounform
    return noun


def nounagreecase(num, nouncase):
    """Узгоджує число num з іменником noun у відмінку case,
    використовуючи список nouncase форм іменника.
    За замовчуванням приймається знахідний відмінок."""
    if num == 0:
        return nouncase[5]
    num10 = num % 10
    num100 = int(num % 100 / 10) * 10
    if num100 == 10:
        return nouncase[5]
    if num10 == 1:
        return nouncase[1]
    if num10 in range(2, 5):
        return nouncase[2]
    if num10 == 0 or num10 >= 5:
        return nouncase[5]


def plural(num, noun):
    """Узгоджує іменник noun (заданий в однині) з числом num."""
    if num == 1:
        res = "1 " + noun
    else:
        res = str(num) + " " + noun + "s"
    return res
