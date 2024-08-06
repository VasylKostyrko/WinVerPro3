"""Модуль функцій над типами значень змінних анотованої програми."""
from exprlib.treelib.tree import Tree


def conv_var_types_to_dict(vartypes):
    """Список типів змінних перетворює на словник.
    Також видає множину типів даних змінних."""
    vardict = {}
    type_set = set()
    group_list = vartypes.split(";")
    for group in group_list:
        grlist = group.strip().split(":")
        varlist = grlist[0].split(", ")
        vartype = grlist[1].strip()
        for var in varlist:
            vardict[var] = vartype
        type_set.add(vartype)
    return vardict, type_set


def build_dict_set_var_cp(cpdictctrees, dicttermtrees):
    """На базі словників cpdictctrees, dicttermtrees з деревами умов  та варіантів
    будує словник множин змінних в контрольних точках програми."""
    dict_set_var_cp = {}
    cplist = list(cpdictctrees.keys())
    for cp in cplist:
        exp_tree = cpdictctrees[cp]
        varset = build_set_var(exp_tree)
        exp_tree = dicttermtrees.get(cp, "")
        if exp_tree != "":
            vset = build_set_var(exp_tree)
            varset.update(vset)
        dict_set_var_cp[cp] = varset
    return dict_set_var_cp


def build_set_var(exp_tree):
    """На базі дерева виразу exp_tree будує множину його змінних.
    Рекурсивна функція."""
    if type(exp_tree) is Tree:
        if exp_tree.binary():
            ltree = exp_tree.getleft()
            rtree = exp_tree.getright()
            lvarset = build_set_var(ltree)
            rvarset = build_set_var(rtree)
            varset = lvarset | rvarset
            return varset
        else:
            # unary
            rtree = exp_tree.getright()
            rvarset = build_set_var(rtree)
            return rvarset
    elif type(exp_tree) is str:
        return set(exp_tree)
    else:
        return set()


def test_types_var(area, dict_var_types_cp, dict_set_var_cp):
    """Порівнюючи множину dict_set_var_cp всіх змінних в кожній КТ
    з множиною dict_var_types_cp всіх типізованих змінних в цій КТ,
    перевіряє, чи типізовано всі змінні в КТ.
    Якщо визначено область даних area,
    тоді відносить до неї всі нетипізовані змінні."""
    dict_non_type_var = {}
    listcp = list(dict_set_var_cp.keys())
    for cp in listcp:
        non_typed_var_set = set()
        varset = dict_set_var_cp[cp]
        dict_var_types = dict_var_types_cp.get(cp, "")
        if dict_var_types == "":
            if area == "":
                dict_non_type_var[cp] = varset.copy()
            else:
                # Формуємо типи значень всіх змінних на базі area
                dict_var_type = {}
                for var in varset:
                    dict_var_type[var] = area
                dict_var_types_cp[cp] = dict_var_type
        else:
            typed_var_set = set(dict_var_types.keys())
            for var in varset:
                if var not in typed_var_set:
                    if area == "":
                        non_typed_var_set.add(var)
                        if len(non_typed_var_set) > 0:
                            dict_non_type_var[cp] = non_typed_var_set
                    else:
                        dict_var_types[var] = area
    return dict_non_type_var


def compact_types(dict_var_types_cp):
    """Об'єднує описи змінних однакового типу."""
    dict_type_vars_cp = {}
    for cp in dict_var_types_cp:
        el = dict_var_types_cp[cp]
        dict_type = {}
        typeset = set(el.values())
        for curtype in typeset:
            var_list = []
            for var in el:
                if el[var] == curtype:
                    var_list.append(var)
            var_list.sort()
            dict_type[curtype] = var_list
        dict_type_vars_cp[cp] = dict_type
    return dict_type_vars_cp


def form_param_types(initvartrees, tracks, dict_type_vars_cp):
    """Формує словник типів параметрів умов."""
    dict_param_types_cp = {}
    for cp in dict_type_vars_cp:
        dict_par_type = {}
        # знайдемо список маршрутів, які починаються в КТ cp
        cp_tracks = []
        ntrack = 0
        for track in tracks:
            if track[0] == cp:
                cp_tracks.append(ntrack)
            ntrack += 1
        # знайдемо змінні, від яких залежить умова в КТ cp
        el = dict_type_vars_cp[cp]
        for curtype in el:
            paramset = set()
            varlist = el[curtype]
            for var in varlist:
                for ntrack in cp_tracks:
                    inittrack = initvartrees[ntrack]
                    param = inittrack.get(var, "")
                    if param == "":
                        paramset.add(var)
                    else:
                        paramset.add(inittrack[var])
            paramlist = list(paramset)
            paramlist.sort()
            dict_par_type[curtype] = paramlist
        dict_param_types_cp[cp] = dict_par_type
    return dict_param_types_cp


def type_z3(curtype):
    """Конвертує типи даних в z3."""
    if curtype == "Int":
        return ["Int", "Ints"]
    elif curtype == "Real":
        return ["Real", "Reals"]
    elif curtype == "Char":
        return ["Char", "Chars"]
    elif curtype == "Bool":
        return ["Bool", "Bools"]
    # elif curtype == "Array(Int)":
    #     return True
    # elif curtype == "Array(Real)":
    #     return True
    # elif curtype == "Array(Char)":
    #     return True
    else:
        return ""


def param_types_str(dict_param_types):
    """Будує текстове представлення словника типів параметрів dict_param_types."""
    params_types = ""
    types = dict_param_types.keys()
    for curtype in types:
        paramlist = dict_param_types[curtype]
        params_type = ""
        for curparam in paramlist:
            if params_type != "":
                params_type += ", "
            params_type += curparam
        if params_types != "":
            params_types += "; "
        params_types += params_type + ": " + curtype
    return params_types
