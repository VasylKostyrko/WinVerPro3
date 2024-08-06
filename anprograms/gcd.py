# coding=CP1251
"""�������� ������ ��� ���������� ����������
�������� ������� ���� ����� ����'����� �����."""


def gcd(m, n):
    # CP_I: m > 0 and n > 0
    while m != n:
        # m > 0 and n > 0 and GCD(x, y) == GCD(m, n)
        if m > n:
            m = m - n
        else:
            n = n - m
    # CP_E: m > 0 and n > 0 and GCD(x, y) == GCD(m, n)
    return m


m = 6
n = 21
r = gcd(m, n)
print(r)
