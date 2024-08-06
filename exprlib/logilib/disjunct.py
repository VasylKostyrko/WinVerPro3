"""Визначає клас Disjunct
для представлення диз'юнкції ряду стандартних кон'юнкцій.
Стандартна диз'юнкція - це диз'юнкція ряду об'єктів
класу Conjunct."""


class Disjunct:
    """Клас стандартних диз'юнкцій."""
    def __init__(self):
        self.dis = []

    def add(self, con):
        # додає в список dis стандартну кон'нкцію con
        ldis = self.dis
        ldis.append(con)

    def getdis(self):
        return self.dis


