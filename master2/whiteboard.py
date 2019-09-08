# Whiteboard : for dynamic code
# Use reload(wb) to reload this script after having executed datamodel.py
import openpyxl
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import PatternFill, Font
from openpyxl import load_workbook

#-----------------------------------------------------------
# Final
#-----------------------------------------------------------

def count(dic, key, val=1):
    if key in dic:
        dic[key] += val
    else:
        dic[key] = val


def output_list(wb, title, lst):
    ws = wb.create_sheet(title)
    for val in lst:
        row = []
        for elem in val:
            if type(elem) == tuple:
                for e in elem:
                    row.append(e)
            else:
                row.append(elem)
        ws.append(row)


def output(wb, title, dic):
    ws = wb.create_sheet(title)
    cumul = 0
    tt = sum(dic.values())
    for key in sorted(dic, key=dic.get, reverse=True):
        if type(key) == tuple:
            row = [*key]
        else:
            row = [key]
        row.append(dic[key])
        per = dic[key] / tt
        row.append(per)
        cumul += per
        row.append(cumul)
        ws.append(row)


def is_first_ddaa(t): # contraint de la prép à de + contraint de fin en -tion, -ment, -age, -sion
    tt    = None
    p     = None
    nc    = None
    # first pattern
    for i, w in enumerate(t.words):
        if i == 0:
            if w.pos == 'DET' and i + 1 < len(t.words):
                if t.words[i + 1].pos == 'NC' and t.words[i + 1].lemma in TRANS:
                    tt = t.words[i + 1]
            elif w.pos == 'NC' and w.lemma in TRANS:
                tt = w
        elif tt is not None and w.pos in ['P', 'P+D']:
            if w.lemma == 'de':
                p = w
            else:
                break # the prep must be de !
        elif p is not None and w.pos == 'NC': # and w.lemma not in TRANS:
            if w.lemma.endswith('tion') or w.lemma.endswith('ment') or w.lemma.endswith('age') or w.lemma.endswith('sion'):
                nc = w
            else:
                break # the first noun after the prep must be like this
        if tt is not None and p is not None and nc is not None:
            break
    return (tt, p, nc)


def is_first(t):
    tt    = None
    p     = None
    nc    = None
    # first pattern
    for i, w in enumerate(t.words):
        if i == 0:
            if w.pos == 'DET' and i + 1 < len(t.words):
                if t.words[i + 1].pos == 'NC' and t.words[i + 1].lemma in TRANS:
                    tt = t.words[i + 1]
            elif w.pos == 'NC' and w.lemma in TRANS:
                tt = w
        elif tt is not None and w.pos in ['P', 'P+D']:
            p = w
        elif p is not None and w.pos == 'NC': # and w.lemma not in TRANS:
            nc = w
        if tt is not None and p is not None and nc is not None:
            break
    return (tt, p, nc)


def is_second(t):
    nc1 = None
    ponct = None
    tt = None
    p = None
    nc2 = None
    for w in t.words:
        #print(nc1, ponct, tt, p, nc2)
        if ponct is None and w.pos == 'NC' and w.lemma not in TRANS:
            nc1 = w
        elif nc1 is not None and ponct is None and w.pos == 'PONCT':
            ponct = w
        elif ponct is not None and tt is None and w.pos == 'NC' and w.lemma in TRANS:
            tt = w
        elif tt is not None and w.pos in ['P', 'P+D']:
            p = w
        elif p is not None and w.pos == 'NC' and w.lemma not in TRANS:
            nc2 = w
            break
        if nc1 is not None and ponct is not None and tt is not None and p is not None and nc2 is not None:
            break
    return(nc1, ponct, tt, p, nc2)


class MockWord:
    def __init__(self, pos, lemma):
        self.pos = pos
        self.lemma = lemma
        
    def __str__(self):
        return f"({self.lemma} {self.pos})"
    
class MockTitle:
    def __init__(self, words):
        self.words = words

# reload(wb) ; wb.xxtest()
def xxtest():
    nc1 = MockWord('NC', 'nc1')
    ponct = MockWord('PONCT', ':')
    tt = MockWord('NC', 'problème')
    p = MockWord('P', 'de')
    nc2 = MockWord('NC', 'nc2')
    t = MockTitle([nc1, ponct, tt, p, nc2])
    r = is_second(t)
    print('Res:')
    for e in r:
        print("   " + str(e))


IS_HEAD = 0

# reload(wb) ; wb.final(titles)
# reload(wb) ; wb.final(titles, 'problème')
# reload(wb) ; wb.final(titles, 'problème', True) # contraint with ddaa
# reload(wb) ; wb.final(titles, 'problème', ddaa=True, save=False)
def final(data, target=None, ddaa=False, save=True):
    global IS_HEAD
    SCHEMA1 = {}
    SCHEMA1_TRANS = {}
    SCHEMA1_NC = {}
    SCHEMA1_P = {}
    SCHEMA1_TEXT = []
    SCHEMA2 = {}
    SCHEMA2_P1 = {}
    SCHEMA2_P2 = {}
    SCHEMA2_NC1 = {}
    SCHEMA2_TRANS = {}
    SCHEMA2_PONCT = {}
    SCHEMA2_P = {}
    SCHEMA2_NC2 = {}
    SCHEMA2_TEXT = []
    cpt = 0
    total = 0
    seuil = 10000
    for kt, t in data.items():
        if not ddaa:
            tt, p, nc = is_first(t)
        else:
            tt, p, nc = is_first_ddaa(t)
        if tt is not None and p is not None and nc is not None:
            if target is None or target == tt.lemma:
                key = (tt.lemma, nc.lemma)
                count(SCHEMA1, key)
                count(SCHEMA1_TRANS, tt.lemma)
                count(SCHEMA1_P, p.lemma)
                count(SCHEMA1_NC, nc.lemma)
                if t.roots[0] == index(t, tt.idw):
                    IS_HEAD += 1
                else:
                    print(kt, t)
                if target is not None:
                    SCHEMA1_TEXT.append([p.lemma, nc.lemma, t.idt, t.text])
        # second pattern
        nc1, ponct, tt, p, nc2 = is_second(t)
        if nc1 is not None and ponct is not None and tt is not None and p is not None and nc2 is not None:
            if target is None or target == tt.lemma:
                key = (nc1.lemma, tt.lemma, nc2.lemma)
                keyP1 = (nc1.lemma, tt.lemma)
                keyP2 = (tt.lemma, nc2.lemma)
                count(SCHEMA2, key)
                count(SCHEMA2_P1, keyP1)
                count(SCHEMA2_P2, keyP2)
                count(SCHEMA2_NC1, nc1.lemma)
                count(SCHEMA2_PONCT, ponct.lemma)
                count(SCHEMA2_TRANS, tt.lemma)
                count(SCHEMA2_P, p.lemma)
                count(SCHEMA2_NC2, nc2.lemma)
                if target is not None:
                    SCHEMA2_TEXT.append([nc1.lemma, ponct.lemma, nc2.lemma, t.idt, t.text])
        cpt += 1
        total += 1
        if cpt == seuil:
            print(f"{total:6d} / {len(data):6d}")
            cpt = 0
    print(f"{total:6d} / {len(data):6d}")
    # write results
    wb = openpyxl.Workbook(write_only=True)
    output(wb, "Schema INIT TT NC", SCHEMA1)
    output(wb, "TT", SCHEMA1_TRANS)
    output(wb, "NC", SCHEMA1_NC)
    output(wb, "P", SCHEMA1_P)
    output_list(wb, "TEXT1", SCHEMA1_TEXT)
    output(wb, "Schema NC PONCT TT NC", SCHEMA2)
    output(wb, "NC1 TT", SCHEMA2_P1)
    output(wb, "TT NC2", SCHEMA2_P2)
    output(wb, "NC1", SCHEMA2_NC1)
    output(wb, "TT", SCHEMA2_TRANS)
    output(wb, "PONCT", SCHEMA2_PONCT)
    output(wb, "P", SCHEMA2_P)
    output(wb, "BC2", SCHEMA2_NC2)
    output_list(wb, "TEXT2", SCHEMA2_TEXT)
    if save:
        if target is None:
            wb.save("trans_schema.xlsx")
        else:
            if not ddaa:
                wb.save("trans_" + target + "_schema.xlsx")
            else:
                wb.save("trans_" + target + "_schema_ddaa.xlsx")


#-----------------------------------------------------------
# Tools
#-----------------------------------------------------------

# Only first level children
def get_children(t, word):
    children = []
    for w in t.words:
        if w.gov == word.idw:
            children.append(w)
    return children


def idw(t, p_idw):
    for w in t.words:
        if w.idw == p_idw:
            return w


def index(t, p_idw):
    for i, w in enumerate(t.words):
        if w.idw == p_idw:
            return i


def is_int(w):
    try:
        int(w.form)
        if ',' in w.form: return False # French flotting number
        return True
    except ValueError:
        return False


patterns = [
    PatternFill(start_color='00FFFF00', end_color='00FFFF00', fill_type='solid'), # yellow
    PatternFill(start_color='0087CEEB', end_color='0087CEEB', fill_type='solid'), # blue sky
    PatternFill(start_color='0000FF00', end_color='0000FF00', fill_type='solid'), # green
    PatternFill(start_color='00FF0000', end_color='00FF0000', fill_type='solid'), # red
]


# elem pour retrouver les éléments dans le titre
# cs pour trouver les matchs dans tous les titres
# f_cs pour écrire un fichier de résultat

# count nc de nc
# reload(wb) ; wb.count_de(titles, 'all')
def count_de(data, typ='all'):
    TRANS = trans()
    tt = 0
    for kt, t in data.items():
        ok = False
        for w in t.words:
            if w.pos == 'NC':
                children1 = get_children(t, w)
                for w1 in children1:
                    if w1.lemma == 'de':
                        children2 = get_children(t, w1)
                        for w2 in children2:
                            if w2.pos == 'NC':
                                ok = True
                            if ok: break
                    if ok: break
            if ok: break
        if ok and typ == 'all': tt += 1
        elif ok and typ == 'trans' and w.lemma in TRANS: tt += 1
        elif ok and typ == '!trans' and w.lemma not in TRANS: tt += 1
    return tt


# reload(wb) ; wb.count_trans_occ(titles)
def count_trans_occ(data):
    tt_trans = 0
    tt_no_trans = 0
    TRANS = trans()
    for kt, t in data.items():
        for w in t.words:
            if w.pos == 'NC':
                if w.lemma in TRANS:
                    tt_trans += 1
                else:
                    tt_no_trans += 1
    return tt_trans, tt_no_trans


#-----------------------------------------------------------
# CS : NGSS [être] NC
#-----------------------------------------------------------

def elem_n_est_n(t):
    res  = None
    ngss = None
    etre = None
    nco  = None
    for w in t.words:
        if w.pos == 'V' and w.lemma == 'être':
            etre = w
            # il doit y avoir un nom sujet
            children_of_etre = get_children(t, w)
            for w2 in children_of_etre:
                if w2.dep == 'suj' and w2.pos == 'NC':
                    ngss = w2
                elif w2.dep == 'obj' and w2.pos == 'NC':
                    nco = w2
                if ngss is not None and nco is not None:
                    break
        if ngss is not None and nco is not None:
            break
    return (ngss, etre, nco)


# reload(wb) ; res = wb.cs_n_est_n(titles); wb.f_cs_n_est_n(res)
def f_cs_n_est_n(data):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Out')
    all_ngss = {}
    all_nco = {}
    all_cs = {}
    for kt, t in data.items():
        ngss = None
        row = [int(kt)]
        elem = elem_n_est_n(t)
        for w in t.words:
            if w in elem:
                cpt = elem.index(w)
                c = WriteOnlyCell(ws, value=w.form)
                c.fill = patterns[cpt]
                if cpt == 0:
                    ngss = w.lemma
                    if w.lemma not in all_ngss:
                        all_ngss[w.lemma] = 1
                    else:
                        all_ngss[w.lemma] += 1
                elif cpt == 1:
                    pass
                elif cpt == 2:
                    nco = w.lemma
                    if w.lemma not in all_nco:
                        all_nco[w.lemma] = 1
                    else:
                        all_nco[w.lemma] += 1 
                    cs = (ngss, nco)
                    if cs not in all_cs:
                        all_cs[cs] = 1
                    else:
                        all_cs[cs] += 1
                row.append(c)
            else:
                row.append(w.form)
        ws.append(row)
    ws = wb.create_sheet('NGSS')
    ngss_total = sum(all_ngss.values())
    for k in sorted(all_ngss, key=all_ngss.get, reverse=True):
        ws.append([k, all_ngss[k], all_ngss[k] / ngss_total])
    ws = wb.create_sheet('NCO')
    nco_total = sum(all_nco.values())
    for k in sorted(all_nco, key=all_nco.get, reverse=True):
        ws.append([k, all_nco[k], all_nco[k] / nco_total])
    ws = wb.create_sheet('CS')
    cs_total = sum(all_cs.values())
    for k in sorted(all_cs, key=all_cs.get, reverse=True):
        ws.append([*k, all_cs[k], all_cs[k] / cs_total])
    ws = wb.create_sheet('Info')
    ws.append(['Total occ NGSS', ngss_total])
    ws.append(['Total occ NCO', nco_total])
    ws.append(['Total diff CS', cs_total])
    ws.append(['Total res', len(data)])
    wb.save('CS-n_est_n.xlsx')


def cs_n_est_n(data):
    res = {}
    for kt, t in data.items():
        ok_suj = False
        ok_obj = False
        for w in t.words:
            if w.pos == 'V' and w.lemma == 'être':
                # il doit y avoir un nom sujet
                children_of_etre = get_children(t, w)
                for w2 in children_of_etre:
                    if w2.dep == 'suj' and w2.pos == 'NC':
                        ok_suj = True
                    elif w2.dep == 'obj' and w2.pos == 'NC':
                        ok_obj = True
                    if ok_suj and ok_obj:
                        break
            if ok_suj and ok_obj:
                res[kt] = t
                break
    return res


#-----------------------------------------------------------
# CS : NGSS [être] que
#-----------------------------------------------------------


def elem_que(t):
    res  = None
    ngss = None
    etre = None
    que  = None
    for w in t.words:
        # on a un que CS
        if w.pos == 'CS' and w.lemma == 'que':
            que = w
            i_que = index(t, w.idw)
            # il y a avant un verbe être conjugué à l'indicatif
            if i_que > 1 and t.words[i_que - 1].lemma == 'être' and t.words[i_que - 1].pos == 'V':
                etre = t.words[i_que - 1]
                # il doit y avoir un nom sujet
                children_of_etre = get_children(t, t.words[i_que - 1])
                for w2 in children_of_etre:
                    if w2.dep == 'suj' and w2.pos == 'NC':
                        ngss = w2
                        res = (ngss, que)
                        break
                    elif w2.form == "c'": # le problème, c'est que ...
                        i_c = index(t, w2.idw)
                        if i_c > 2 and t.words[i_c - 1].form == ',' and t.words[i_c - 2].pos == 'NC':
                            ngss = t.words[i_c - 2]
                            res = (ngss, que)
                            break
                        elif i_c > 1 and t.words[i_c - 1].pos == 'NC':
                            ngss = t.words[i_c - 1]
                            res = (ngss, que)
                            break
            # il y a un nom avant
            elif i_que > 1 and t.words[i_que - 1].pos == 'NC':
                ngss = t.words[i_que - 1]
                res = (ngss, que, etre)
                break
    return res


# reload(wb) ; res = wb.cs_que(titles); wb.f_cs_que(res)
def f_cs_que(data):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Out')
    all_ngss = {}
    for kt, t in data.items():
        ngss = None
        row = [int(kt)]
        elem = elem_que(t)
        for w in t.words:
            if w in elem:
                cpt = elem.index(w)
                c = WriteOnlyCell(ws, value=w.form)
                c.fill = patterns[cpt]
                if cpt == 0:
                    ngss = w.lemma
                    if w.lemma not in all_ngss:
                        all_ngss[w.lemma] = 1
                    else:
                        all_ngss[w.lemma] += 1
                row.append(c)
            else:
                row.append(w.form)
        ws.append(row)
    ws = wb.create_sheet('NGSS')
    ngss_total = sum(all_ngss.values())
    for k in sorted(all_ngss, key=all_ngss.get, reverse=True):
        ws.append([k, all_ngss[k], all_ngss[k] / ngss_total])
    ws = wb.create_sheet('Info')
    ws.append(['Total occ NGSS', ngss_total])
    ws.append(['Total res', len(data)])
    wb.save('CS-que.xlsx')


def cs_que(data):
    res = {}
    for kt, t in data.items():
        ok = False
        for w in t.words:
            # on a un que CS
            if w.pos == 'CS' and w.lemma == 'que':
                i_que = index(t, w.idw)
                # il y a avant un verbe être conjugué à l'indicatif
                if i_que > 1 and t.words[i_que - 1].lemma == 'être' and t.words[i_que - 1].pos == 'V':
                    # il doit y avoir un nom sujet
                    children_of_etre = get_children(t, t.words[i_que - 1])
                    for w2 in children_of_etre:
                        if w2.dep == 'suj' and w2.pos == 'NC':
                            ok = True
                        elif w2.form == "c'": # le problème, c'est que ...
                            i_c = index(t, w2.idw)
                            if i_c > 2 and t.words[i_c - 1].form == ',' and t.words[i_c - 2].pos == 'NC':
                                ngss = t.words[i_c - 2]
                                ok = True
                                break
                            elif i_c > 1 and t.words[i_c - 1].pos == 'NC':
                                ngss = t.words[i_c - 1]
                                ok = True
                                break
                # il y a un nom avant
                elif i_que > 1 and t.words[i_que - 1].pos == 'NC':
                    ok = True
            if ok:
                res[kt] = t
                break
    return res


#-----------------------------------------------------------
# CS : NGSS [être] de inf
#-----------------------------------------------------------
# cs_de_inf(data)   fait un filtrage sur les titres qui correspondent à ce pattern
# elem_cs_de_inf(t) récupère les mots clés de la CS dans un titre
# f_cs_de_inf(data) met les résultats filtrés dans un fichier Excel à l'aide de elem_

def elem_cs_de_inf(t):
    res  = None
    ngss = None
    etre = None
    de   = None
    inf  = None
    for w in t.words:
        if w.pos == 'VINF':
            inf = w
            parent1 = idw(t, w.gov)
            if parent1 is not None and parent1.lemma == 'de' and parent1.pos == 'P':
                de = parent1
                parent2 = idw(t, parent1.gov)
                if parent2 is not None and parent2.lemma == 'être' and parent2.pos == 'V':
                    etre = parent2
                    children2 = get_children(t, parent2)
                    for w2 in children2:
                        if w2.dep == 'suj' and w2.pos == 'NC':
                            ngss = w2
                            res = (ngss, de, inf, etre)
                            break
                elif parent2 is not None and parent2.pos == 'NC':
                    ngss = parent2
                    res = (ngss, de, inf)
                    break
    if res is not None:
        # voyons s'il y a un NC juste avant le de pour corriger les dépendances
        i_de = index(t, de.idw)
        if i_de > 0 and t.words[i_de - 1].pos == 'NC':
            if len(res) == 3:
                res = (t.words[i_de - 1], de, inf)
            elif len(res) == 4:
                print(t.idt)
                res = (t.words[i_de - 1], de, inf, etre)
    return res


# reload(wb) ; res = wb.cs_de_inf(titles); wb.f_cs_de_inf(res)
def f_cs_de_inf(data):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Out')
    all_ngss = {}
    all_inf = {}
    all_cs = {}
    for kt, t in data.items():
        ngss = None
        row = [int(kt)]
        elem = elem_cs_de_inf(t)
        for w in t.words:
            if w in elem:
                cpt = elem.index(w)
                c = WriteOnlyCell(ws, value=w.form)
                c.fill = patterns[cpt]
                if cpt == 0:
                    ngss = w.lemma
                    if w.lemma not in all_ngss:
                        all_ngss[w.lemma] = 1
                    else:
                        all_ngss[w.lemma] += 1
                elif cpt == 2: # on ne retient pas le "être" optionnel
                    cs = (ngss, 'de', w.lemma)
                    if w.lemma not in all_inf:
                        all_inf[w.lemma] = 1
                    else:
                        all_inf[w.lemma] += 1
                    if cs not in all_cs:
                        all_cs[cs] = 1
                    else:
                        all_cs[cs] += 1
                row.append(c)
            else:
                row.append(w.form)
        ws.append(row)
    ws = wb.create_sheet('NGSS')
    ngss_total = sum(all_ngss.values())
    for k in sorted(all_ngss, key=all_ngss.get, reverse=True):
        ws.append([k, all_ngss[k], all_ngss[k] / ngss_total])
    ws = wb.create_sheet('INF')
    inf_total = sum(all_inf.values())
    for k in sorted(all_inf, key=all_inf.get, reverse=True):
        ws.append([k, all_inf[k], all_inf[k] / inf_total])
    ws = wb.create_sheet('CS')
    cs_total = sum(all_cs.values())
    for k in sorted(all_cs, key=all_cs.get, reverse=True):
        ws.append([*k, all_cs[k], all_cs[k] / cs_total])
    ws = wb.create_sheet('Info')
    ws.append(['Total occ NGSS', ngss_total])
    ws.append(['Total occ CS', cs_total])
    ws.append(['Total res', len(data)])
    wb.save('CS-inf.xlsx')


# ne pas est un children du verbe
# le sujet est un children du verbe
def cs_de_inf(data):
    res = {}
    for kt, t in data.items():
        ok = False
        for w in t.words:
            # on a un infinitf
            if w.pos == 'VINF' and w.form not in ['Grégoire', 'Alexandre'] and not is_int(w):
                # suppression de bien-être
                if w.lemma == 'être':
                    i_etre = index(t, w.idw)
                    if i_etre > 1 and t.words[i_etre - 1].form == '-' and t.words[i_etre - 2].form == 'bien':
                        continue
                # a-t-il pour parent de ?
                parent1 = idw(t, w.gov)
                if parent1 is not None and parent1.lemma == 'de' and parent1.pos == 'P':
                    # en vue de est un no go
                    i_de = index(t, parent1.idw)
                    if i_de > 0 and t.words[i_de - 1].form == 'vue':
                        break
                    # a-t-il pour parent un être ?
                    parent2 = idw(t, parent1.gov)
                    if parent2 is not None and parent2.lemma == 'être' and parent2.pos == 'V':
                        # si oui, son sujet doit être un NC !
                        children2 = get_children(t, parent2)
                        for w2 in children2:
                            if w2.dep == 'suj' and w2.pos == 'NC':
                                ok = True
                    elif parent2 is not None and parent2.pos == 'NC':
                        # si non, son recteur doit être le NGSS
                        ok = True
            if ok:
                res[kt] = t
                break
    return res

#-----------------------------------------------------------
# MOTIFS
#-----------------------------------------------------------


# Un motif M est contenu dans un autre M' si on retrouve sa séquence dans le même ordre, même disjointe : (A, C) (A, B, C) => le 1er est contenu dans le second
# Le motif M' est alors une sous-séquence du motif M, M' étant plus longue ou plus générique
# De ce fait, une super-séquence M ne peut pas être plus courte ou moins générique qu'une de ces sous-séquences M'
# Attention : on part de l'hypothèse qu'on ne se supporte pas soit même
# reload(wb) ; motifs_ngss, motifs_nc, supports_ngss, supports_nc = wb.fouille(titles, 2, 5)
def fouille(data, min_length, max_length):
    print('MOTIFS')
    motifs_ngss, motifs_nc = fouille_motifs(data, min_length, max_length)
    print('Length motifs NGSS :', len(motifs_ngss))
    print('Length motifs NC   :', len(motifs_nc))
    print('SUPPORT')
    supports_ngss = fouille_supports(motifs_ngss)
    supports_nc = fouille_supports(motifs_nc)
    print('SAVE')
    fouille_output(motifs_ngss, motifs_nc, supports_ngss, supports_nc)
    return motifs_ngss, motifs_nc, supports_ngss, supports_nc


# reload(wb) ; wb.fouille_test()
def fouille_test():
    motifs_ngss = {
            ('INIT', 'NGSS') : 2,
            ('INIT', 'DET', 'NGSS') : 1
        }
    motifs_nc = {
            ('INIT', 'NC') : 1,
            ('INIT', 'NC', 'ADJ') : 1
        }
    supports_ngss = fouille_supports(motifs_ngss)
    supports_nc = fouille_supports(motifs_nc)
    fouille_output(motifs_ngss, motifs_nc, supports_ngss, supports_nc)


# motifs(titles, -1, +1) : on va chercher les motifs A head C
# on ne garde les lemmes que pour les classes fermées DET P P+D CS CC PROREL et être et avoir sinon POS
# reload(wb) ; test = { '62226' : titles['62226'] } ; ngss, nc = wb.motifs(test, 2, 2)
# lemma::pos
# ou pos (y compris INIT et END)
def fouille_motifs(data, min_length, max_length):
    motifs_ngss = {} # ('INIT', 'NGSS') : 2
    motifs_nc   = {} # ('INIT', 'NC') : 2
    TRANS = trans()
    # count
    seuil = 10000
    cpt = 0
    total = 0
    # Pour length = 2, si i_root = 5, start = 4 (i = 4-5), 5 (i = 5-6)
    # Pour length = 3, si i_root = 5, start = 3 (i = 3-4-5)...
    for kt, t in data.items():
        # For all roots
        for i_root in t.roots:
            for length in range(min_length, max_length + 1):
                for start in range(i_root - length + 1, i_root + 1):
                    val = []
                    is_trans = []
                    for i in range(start, start + length):
                        # Limits
                        if i < -1:
                            continue
                        elif i == -1:
                            val.append('INIT')
                            continue
                        elif i == len(t.words):
                            val.append('END')
                            break
                        #elif i > len(t.words):
                        #   break
                        # Making the motif
                        w = t.words[i]
                        if w.pos in ['P', 'P+D', 'CS', 'CC', 'PROREL']: # 'DET', 
                            val.append(w.lemma + '::' + w.pos)
                        elif w.lemma in ['être', 'lemma']:
                            val.append(w.lemma + '::' + w.pos)
                        elif w.lemma in TRANS and w.pos == 'NC':
                            val.append('NGSS') # instead of NC
                            is_trans.append(i) # save every NC turned to NGSS
                        else:
                            val.append(w.pos)
                    val = tuple(val)
                    if len(is_trans) > 0:
                        if val not in motifs_ngss:
                            motifs_ngss[val] = 1
                        else:
                            motifs_ngss[val] += 1
                    else:
                        if val not in motifs_nc:
                            motifs_nc[val] = 1
                        else:
                            motifs_nc[val] += 1
        cpt += 1
        total += 1
        if cpt == seuil:
            cpt = 0
            print(f'Motifs done : {total:10d} / {len(data):10d}')
    print(f'Motifs done : {total:10d} / {len(data):10d}')
    return motifs_ngss, motifs_nc


# ('INIT', 'NGSS') => ('INIT', 'NC')
def fouille_change(key):
    neo = []
    for item in key:
        if item == 'NGSS':
            neo.append('NC')
        else:
            neo.append(item)
    return tuple(neo)
    

# non used
def fouille_filter(mtfs, value):
    res = {}
    for key in mtfs:
        if mtfs[key] >= value:
            res[key] = value
    return res


# reload(wb) ; test = { '62226' : titles['62226'] } ; ngss, nc = wb.motifs(test, 2, 2) ; ngss[('DET', 'NGSS', 'V')] = 1 ; wb.support(ngss)
def fouille_supports(mtfs):
    # count
    seuil = 1000
    cpt = 0
    total = 0
    # go
    res = {}
    for key1 in mtfs:
        res[key1] = 0
        for key2 in mtfs:
            if key1 != key2 and is_contained(key1, key2):
                res[key1] += 1
        cpt += 1
        total += 1
        if cpt == seuil:
            cpt = 0
            print(f'Supports done : {total:10d} / {len(mtfs):10d}')
    print(f'Supports done : {total:10d} / {len(mtfs):10d}')
    return res


# reload(wb) ; wb.f_motifs_supports(ngss, nc, supports_ngss, supports_nc)
def fouille_output(motifs_ngss, motifs_nc, supports_ngss, supports_nc):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Motifs Supports NGSS')
    ws.append(['Len', '1', '2', '3', '4', '5', 'Count', 'Support', 'Croissance'])
    for motif in sorted(supports_ngss, key=supports_ngss.get, reverse=True):
        count = motifs_ngss[motif]
        support = supports_ngss[motif]
        row = [len(motif)]
        for item in range(0, 5):
            if item < len(motif):
                row.append(motif[item])
            else:
                row.append('_')
        row.append(count)
        row.append(support)
        # fetch growth rate
        nc = fouille_change(motif)
        if nc not in motifs_nc or supports_nc[nc] == 0:
            tc = '∞'
        else:
            tc = supports_ngss[motif] / supports_nc[nc]
        row.append(tc)
        ws.append(row)
    # Support NC
    ws = wb.create_sheet('Motifs Supports NC')
    for motif in sorted(supports_nc, key=supports_nc.get, reverse=True):
        count = motifs_nc[motif]
        support = supports_nc[motif]
        row = [len(motif)]
        for item in range(0, 5):
            if item < len(motif):
                row.append(motif[item])
            else:
                row.append('_')
        row.append(support)
        row.append(count)
        ws.append(row)
    wb.save('motifs_supports.xlsx')


def item2lem_pos(item):
    if len(item.split('::')) == 1: # pos
        lem = 'SPECIAL_ANY'
        pos = item
    else: # lemma::pos
        lem, pos = item.split('::')
    return lem, pos


# pos is stronger for PRIME ONLY! (if no lemma is defined for only one item1, no comparison is made on it)
def cmp_item(item1, item2):
    lem1, pos1 = item2lem_pos(item1)
    lem2, pos2 = item2lem_pos(item2)                      # séquence vs sous-séquence
    if lem1 == 'SPECIAL_ANY' and lem2 == 'SPECIAL_ANY':   #      (V) vs (V)
        return pos1 == pos2
    elif lem1 == 'SPECIAL_ANY' and lem2 != 'SPECIAL_ANY': #      (V) vs (être V)
        return True
    elif lem1 != 'SPECIAL_ANY' and lem2 == 'SPECIAL_ANY': # (être V) vs (V)
        return False
    else:                                                 # (être V) vs (être V)
        return lem1 == lem2 and pos1 == pos2


# L'égalité peut avoir des trous : (A, C) est contenue dans (A, B, C) <=> (A, B, C) est une sous-séquence de (A, B)
# Donc on n'utilise plus ça qui était une égalité stricte
#def cmp_seq(seq1, seq2):
#    maxx = min(len(seq1), len(seq2))
#    for i in range(0, maxx):
#        if not cmp_item(seq1[i], seq2[i]):
#            return False
#    return True


# S'est contenu dans S ? <=> S' est une FORME PLUS GENERIQUE de S
# S' = <(DET) (NC) ,(être V)>
# S = <(le DET) (solution NC) (être V) (de P)>
# S' est contenue dans S
# S est une sous-séquence de S'
# S <_ S'
def is_contained(prime, s):
    #print(prime, 'vs', s)
    if len(prime) > len(s): return False # S' doit avoir une longueur plus petite ou égale à S
    nb = 0
    for item in s:
        #print('   ', nb, prime[nb], 'vs', item, cmp_item(prime[nb], item))
        if cmp_item(prime[nb], item):
            nb += 1
            if nb == len(prime): # tu restarts pas à 0 !!! c mauvais... voir def count_suite
                return True
    return False

    #first_prime = prime[0]
    #for i, item in enumerate(s):
    #    if cmp_item(first_prime, item):
    #        if cmp_seq(prime, s[i:]):
    #            return True
    #return False


import sys
def ptest(expr, val):
    if expr != val:
        sys.stderr.write(str(expr) + ' vs expected ' + str(val) + '\n')
    else:
        print(expr, ' (expected ', val, ')', sep='')


# reload(wb) ; wb.test_motifs()
def test_motifs():
    s1 = ('DET', 'ADJ', 'NGSS')
    prime1 = ('DET', 'NGSS')
    ptest(is_contained(prime1, s1), True)
    s2 = ('de::DET', 'ADJ', 'évolution::NGSS')
    prime2 = ('DET', 'NGSS')
    ptest(is_contained(prime2, s2), True)
    s3 = ('DET', 'NC', 'être::V')
    prime3 = ('DET', 'NC', 'V')
    ptest(is_contained(prime3, s3), True)
    s4 = ('DET', 'NC', 'V')
    prime4 = ('DET', 'NC', 'être::V') # False : prime4 is more precise than s4!
    ptest(is_contained(prime4, s4), False)


#---------------------------------------------------

# Check support
# reload(wb) ; wb.count_one('PONCT')
def count_one(val):
    wb = load_workbook(r".\output\motifs_supports-2-7.xlsx", read_only=True)
    pct = 0
    for i, sn in enumerate(wb.sheetnames):
        ws = wb[sn]
        if i == 0:
            for row in ws.rows:
                for j in range(1, 6):
                    lem = row[j].value
                    if lem == val:
                        pct += 1
    return pct


def read(filename, sheet):
    wbin = load_workbook(filename, read_only=True)
    for i, sn in enumerate(wbin.sheetnames):
        ws = wbin[sn]
        if i == sheet:
            lines = []
            for row in ws.rows:
                line = []
                for cell in row:
                    line.append(cell.value)
                lines.append(line)
    return lines


# [ '', 'A', 'B', '_', '_', '_'] => ['A', 'B']
def grep_motif(line):
    motif = []
    for k in line[1:6]:
        if k != '_':
            motif.append(k)
        else:
            return motif
    return motif


# r".\output\motifs_supports-2-7.xlsx"
# reload(wb) ; r = wb.recalc_support(r".\output\motifs_supports-2-5.xlsx")
def recalc_support(filename):
    # read
    print('READING')
    ngss = read(filename, 0)
    nc = read(filename, 1)
    # recalc support nc
    correponding = {}
    print('RECALC NC')
    first = True
    # count
    cpt = 0
    seuil = 1000
    total = 0
    for line in nc:
        if first:
            first = False
        else:
            #print(line, grep_motif(line))
            try:
                nc[7] = count_suite(grep_motif(line), nc) / (len(nc) - 1)
                key = line[1].replace('NC', 'NGSS') + line[2].replace('NC', 'NGSS') + line[3].replace('NC', 'NGSS') + line[4].replace('NC', 'NGSS') + line[5].replace('NC', 'NGSS')
                corresponding[key] = cpt
            except AttributeError:
                pass
        cpt += 1
        total += 1
        if cpt == seuil:
            print(f"{total:10d} / {len(nc)-1:10d}")
            cpt = 0
    # recalc support ngss
    print('RECALC NGSS')
    first = True
    # count
    cpt = 0
    seuil = 1000
    total = 0
    for line in ngss:
        if first:
            first = False
        else:
            #print(line, grep_motif(line))
            try:
                ngss[7] = count_suite(grep_motif(line), ngss) / (len(ngss) - 1)
                key = line[1] + line[2]+ line[3] + line[4] + line[5]
                if key in corresponding:
                    ngss[8] = ngss[7] / nc[corresponding[key]][7]
                else:
                    ngss[8] = '∞'
            except AttributeError:
                pass
        cpt += 1
        total += 1
        if cpt == seuil:
            print(f"{total:10d} / {len(ngss)-1:10d}")
            cpt = 0
    # output
    wbout = openpyxl.Workbook(write_only=True)
    ws = wbout.create_sheet('Motifs Supports NGSS')
    #ws.append(['Len', '1', '2', '3', '4', '5', 'Count', 'Support', 'Croissance'])
    for line in ngss:
        ws.append(line)
    ws = wbout.create_sheet('Motifs Supports NC')
    ws.append(['Len', '1', '2', '3', '4', '5', 'Count', 'Support', 'Croissance'])
    for line in nc:
        ws.append(line)
    wbout.save('motifs_supports_c.xlsx')
    return ngss, nc


# reload(wb) ; wb.count_suite(['PONCT', 'NGSS', 'VINF'])
# reload(wb) ; wb.count_suite(['PONCT', 'VINF'])
# 3  PONCT  NGSS  VINF  _  _  1  8610  ∞  
# 4  VINF  PONCT  NGSS  VINF  _  1  774  ∞  
# 5  PONCT  VINF  PONCT  NGSS  VINF  1  42  ∞  
# 4  PONCT  NGSS  VINF  en::P  _  1  30  ∞  
# 5  VINF  PONCT  NGSS  VINF  en::P  1  0  ∞  
# 5  PONCT  NGSS  VINF  en::P  NPP  1  0  ∞  
# 6

# reload(wb) ; wb.test_count_suite()
def test_count_suite():
    data = [
            ['', 'PONCT', 'PIPO', 'VINF', '', ''], # PYTHON CONCAT LES STRINGS SANS RIEN !
            ['', 'PONCT', 'VINF', '', '', ''],
            ['', 'PONCT', 'ZORBA', 'DRACULA', 'VINF', ''],
            ['', 'VINF', 'PONCT', '', '', ''],
            ['', 'PONCT', 'PONCT', 'VINF', '', ''],
            ['', 'de::DET', 'NC', '', '', ''],
            ['', 'NC', 'V', '', '', '']
        ]
    motif = ['PONCT', 'VINF']
    print('Should be True :', strict_seq_eq(motif, motif))
    print('Motif:', motif)
    print('Should be 3 :', count_suite(motif, data))
    motif = ['DET', 'NC']
    print('Motif:', motif)
    print('Should be 1 :', count_suite(motif, data))
    motif = ['pipo::NC', 'V']
    print('Motif:', motif)
    print('Should be 0 :', count_suite(motif, data))


# LE MOTIF PEUT ETRE PLUS PETIT ET MOINS PRECIS, PAS L'INVERSE
# wb.exq('DET', 'de::DET')      True
# wb.exq('de::DET', 'DET')      False
# wb.exq('de::DET', 'de::DET')  True
# wb.exq('DET', 'DET')          True
# reload(wb) ; wb.exq('DET', 'de::DET')
def exq(emotif, b):
    # motif more precise
    if len(emotif.split('::')) > len(b.split('::')) :
        return False
    elif len(emotif.split('::')) == 2 and len(b.split('::')) == 2:
        lem1, pos1 = emotif.split('::')
        lem2, pos2 = b.split('::')
        return lem1 == lem2 and pos1 == pos2
    elif len(b.split('::')) == 2: # and motif is only 1
        lem, pos = b.split('::')
        return emotif == pos
    else: # 1 and 1
        return emotif == b


def strict_item_eq(a, b):
    #print('==', a, b)
    return a == b


def strict_seq_eq(motif, sb):
    ok = True
    #print(len(motif), len(sb))
    if len(motif) > len(sb): return False
    for i in range(0, len(motif)):
        #print('=', 'i', i, 'mot', motif[i], 'row', sb[i], '.')
        if not strict_item_eq(motif[i], sb[i]):
            return False
    return ok


# reload(wb) ; wb.test_count_suite()
def count_suite(motif, data, exclude_first=True):
    pct = 0
    for row in data:
        if exclude_first:
            exclude_first = False
            continue
        #print('INFO', len(row), row)
        good = 0
        for j in range(1, 6):
            #print(motif[0], j, row[j])
            if exq(motif[0], row[j]):
                good = 0
                for k in range(j, j + len(motif) + 2):
                    if k < len(row) and k < 6 and exq(motif[good], row[k]):
                        #print('k', k, 'D', row[k], 'M', motif[good], '+1')
                        good += 1
                        if good == len(motif):
                            break
                    #else:
                    #    print('k', k, 'D', row[k], 'M', motif[good])
                if good == len(motif):
                    break
        #print(row)
        if good == len(motif) and not strict_seq_eq(motif, row[1:6]): #(because of identity)
            pct += 1
            #print('good')
        #elif strict_seq_eq(motif, row):
        #    print('equal')
        #print()
    return pct


def count_suite_direct(vals):
    wb = load_workbook(r".\output\motifs_supports-2-7.xlsx", read_only=True)
    pct = 0
    for i, sn in enumerate(wb.sheetnames):
        ws = wb[sn]
        if i == 0:
            for row in ws.rows:
                for j in range(1, 6):
                    lem = row[j].value
                    if lem == vals[0]:
                        #good = True
                        good = 0
                        for k in range(j, j + len(vals) + 1):
                            # non disjoint
                            #if k >= len(row) or row[k].value != vals[k - j]:
                            #    good = False
                            #    break
                            # disjoint
                            #print(i, k, len(row), row[k].value, good, vals[good])
                            if k < len(row) and row[k].value == vals[good]:
                                good += 1
                                if good == len(vals):
                                    break
                        #if good:
                        if good == len(vals):
                            pct += 1
                            #for i in range(0, len(row)):
                            #    print(row[i].value, ' ', end='')
                            #print('good')
    return pct


#-----------------------------------------------------------
# DISC & TRANS
#-----------------------------------------------------------


def read_disc_from_output_xlsx(filename, debug=True):
    TRANS = trans()
    filename = filename + '.xlsx' if not filename.endswith('.xlsx') else filename
    wb = load_workbook(filename, read_only=True)
    disc_heads = {}
    for i, sn in enumerate(wb.sheetnames):
        if i >= 4: # disc
            disc = sn[sn.index('.') + 2:]
            disc_heads[disc] = []
            ws = wb[sn]
            for row in ws.rows:
                key = str(row[1].value) + '::' + str(row[2].value)
                disc_heads[disc].append(key)
    disc_filtered = {}
    all_lemma_filtered = []
    for disc in disc_heads:
        disc_filtered[disc] = []
        for key in disc_heads[disc]:
            lemma, pos = key.split('::') # place existe en NC et NPP pour '1.shs.infocom'
            if lemma in TRANS:
                print(f"{disc:15} {lemma}")
                break
            disc_filtered[disc].append(lemma)
            if lemma not in all_lemma_filtered: all_lemma_filtered.append(lemma)
    if debug:
        print('Discipline      NbHead Filter - Minus Kept %')
        for disc in disc_heads:
            ld = len(disc_heads[disc])
            lf = len(disc_filtered[disc])
            print(f"{disc:15} {ld:6d} {lf:6d} -{ld-lf:6d} {lf/ld*100:5.2f}%")
    return disc_heads, all_lemma_filtered
rdfo = read_disc_from_output_xlsx


def recouvrement(DISC=None, TRANS=None):
    if type(DISC) != list: DISC = disc(DISC)
    if type(TRANS) != list: TRANS = trans(TRANS)
    recouv = 0
    for t in TRANS:
        if t in DISC:
            recouv += 1
    print(f"Length of DISC = {len(DISC)} Length of TRANS = {len(TRANS)}")
    print(f"Recouv : {recouv} / {len(TRANS)} {recouv/len(TRANS)*100:5.2f}")


def disc():
    file = open(r'.\output\disc_heads.txt', mode='r', encoding='utf8')
    lines = file.readlines()
    file.close()
    res = []
    for lin in lines:
        res.append(lin.rstrip())
    return res


def trans():
    file = open(r'.\output\trans_heads.txt', mode='r', encoding='utf8')
    lines = file.readlines()
    file.close()
    res = []
    for lin in lines:
        res.append(lin.rstrip())
    return res
get_trans = trans
TRANS = get_trans()


def select_trans_t(data):
    res = {}
    TRANS = trans()
    for kt, t in data.items():
        root1 = t.words[t.roots[0]]
        if root1.lemma in TRANS:
            res[kt] = t
            continue
        elif len(t.roots) > 1:
            root2 = t.words[t.roots[1]]
            if root2.lemma in TRANS:
                res[kt] = t
    return res


#-----------------------------------------------------------

# wb.search(titles, 'problème', text='Le problème')
def search(data, root1, root2=None, nb=10, text=None):
    for kt, t in data.items():
        if root2 is not None and len(t.roots) < 2: continue
        if text is not None and text not in t.text: continue
        troot1 = t.words[t.roots[0]]
        if root2 is None:
            if root1 == troot1.lemma:
                print(t.idt, t)
                nb -= 1
        else:
            troot2 = t.words[t.roots[1]]
            if root1 == troot1.lemma and root2 == troot2.lemma:
                print(t.idt, t)
                nb -= 1
        if nb == 0: break

# no title with same root2 and 'problème' AND 'question' as root1
def xsearch(data):
    for kt, t in data.items():
        if len(t.roots) < 2: continue
        troot2 = t.words[t.roots[1]]
        tp = None
        tq = None
        for kkt, tt in data.items():
            troot1 = t.words[t.roots[0]]
            if troot1.lemma == 'problème':
                tp = tt
            if troot1.lemma == 'question':
                tq = tt
        if tp is not None and tq is not None:
            print(tp)
            print(tq)


# wb.on_each(t121, wb.find_sub_roots)
def on_each(titles, f):
    for kt, t in titles.items():
        f(t)


# show in which segment are the roots
# already in the attribute roots_by_segment
def root_in_seg(titles, with_subroots = False):
    res = {}
    for kt, t in titles.items():
        if len(t.segments) > 1:
            if len(t.segments) == 2:
                # if the second segmentator mark is a closing one it's ok
                if t.segments[-1] != t.len_with_ponct - 1:
                    raise Exception('Too many segmentors: ' + str(t.segments))
            else:
                raise Exception('Too many segments: ' + str(len(t.segments)))
        # everything is ok
        seg_mark = t.segments[0]
        if len(t.roots) == 0:
            raise Exception('No root')
        elif len(t.roots) > 2:
            raise Exception('Too many roots: ' + str(len(t.roots)))
        in_seg1 = 0
        in_seg2 = 0
        if with_subroots == True:
            roots = t.roots + t.subroots
        else:
            roots = t.roots
        for root in roots:
            if root < seg_mark:
                in_seg1 += 1
            elif root > seg_mark:
                in_seg2 += 1
            else:
                raise Exception('Root is segmentator!')
        key = (in_seg1, in_seg2)
        if key not in res:
            res[key] = 1
        else:
            res[key] += 1
    return res


def pprint(data, nb_max=None):
    total = 0
    for k, v in data.items():
        total += v
    nb = 0
    for key in sorted(data, key=data.get, reverse=True):
        val = data[key]
        print(f"{str(key):20} {val:10} {round(val/total * 100, 2):5.2f}")
        nb += 1
        if nb_max is not None and nb == nb_max:
            break


def deter_for(titles, domains, lem1, lem2, seg):
    xlem = {
        'le' : 'def',
        'la' : 'def',
        'les' : 'def',
        'un' : 'indef',
        'une' : 'indef',
    }
    dets = { 'none' : 0}
    for kt, t in titles.items():
        if t.domain not in domains: continue
        root1 = t.words[t.roots[0]]
        root2 = t.words[t.roots[1]]
        if root1.lemma != lem1 or root2.lemma != lem2: continue
        found = False
        if seg == 1:
            start = 0
            end = t.segments[0]
            r = root1
            ir = t.roots[0]
        elif seg == 2:
            start = t.segments[0] + 1
            end = len(t.words)
            r = root2
            ir = t.roots[1]
        else:
            raise Exception('Number of seg not handled')
        for iw in range(start, end):
            w = t.words[iw]
            #print(t.roots[seg], w.pos, w.gov, w.dep)
            if w.pos == 'DET' and w.gov == r.idw and w.dep == 'det':
                if iw < ir:
                    lem = w.lemma
                    if lem in xlem:
                        lem = xlem[lem]
                    if lem not in dets:
                        dets[lem] = 1
                    else:
                        dets[lem] += 1
                    found = True
                    break
        if not found:
            dets['none'] += 1
    return dets


def go_deter(data, dom): # OneSegNoun.DOMAINS
    print('rôle', deter_for(data, dom, 'rôle', 'cas', 1))
    print('cas', deter_for(data, dom, 'rôle', 'cas', 2))
    print('approche', deter_for(data, dom, 'approche', 'cas', 1))
    print('cas', deter_for(data, dom, 'approche', 'cas', 2))
    print('apport', deter_for(data, dom, 'apport', 'exemple', 1))
    print('exemple', deter_for(data, dom, 'apport', 'exemple', 2))
    print('effet', deter_for(data, dom, 'effet', 'cas', 1))
    print('cas', deter_for(data, dom, 'effet', 'cas', 2))


# deprecated
def deter(titles, domains):
    det = {}
    no_det = 0
    nb_found = {}
    for kt, t in titles.items():
        if t.domain not in domains: continue
        root = t.roots[0] + 1
        found = 0
        for iw, w in enumerate(t.words):
            if w.pos == 'DET' and w.gov == root and w.dep == 'det':
                if iw < root:
                    found +=1
                    if w.form in det:
                        det[w.form] += 1
                    else:
                        det[w.form] = 1
                else:
                    pass # Dîtes-le avec des cartes
                    #t.info()
                    #raise Exception("Deter AFTER root " + str(w))
        if found in nb_found:
            nb_found[found] += 1
        else:
            nb_found[found] = 1
            #print('-------------------')
            #print('Root :', root)
            #t.info()
    ordered_det = {}
    for key in sorted(det, key=det.get, reverse=True):
        val = det[key]
        ordered_det[key] = val
    return ordered_det, nb_found


def comple(titles):
    dep = {}
    no_dep = 0
    nb_found = {}
    for kt, t in titles.items():
        root = t.roots[0] + 1
        found = 0
        for iw, w in enumerate(t.words):
            if w.pos == 'P' and w.gov == root and w.dep == 'dep':
                if iw >= root:
                    found +=1
                    if w.form.lower() in dep:
                        dep[w.form.lower()] += 1
                    else:
                        dep[w.form.lower()] = 1
                else:
                    t.info()
                    raise Exception("Compl BEFORE root " + str(w))
        if found in nb_found:
            nb_found[found] += 1
        else:
            nb_found[found] = 1
            #print('-------------------')
            #print('Root :', root)
            #t.info()
    ordered_dep = {}
    for key in sorted(dep, key=dep.get, reverse=True):
        val = dep[key]
        ordered_dep[key] = val
    return ordered_dep, nb_found


def nb_seg_2_nb_restarts(titles):
    count = 0
    exceptions = []
    for kt, t in titles.items():
        if t.nb_seg >= (t.nb_restarts + 1):
            count += 1
        else:
            exceptions.append(t)
    return count, count / len(titles), len(exceptions), exceptions


def count(d, k):
    if k in d:
        d[k] += 1
    else:
        d[k] = 1

# reload(wb);t=wb.before_restart(titles)
def before_restart(titles):
    all_before_roots = {} 
    for kt, t in titles.items():
        if t.nb_restarts != 1:
            continue
        i = t.restarts[0]
        before = t.words[i - 1]
        key = before.form + ' : ' + before.pos + ' : ' + before.lemma
        count(all_before_roots, key)
    for k in sorted(all_before_roots, key=all_before_roots.get, reverse=True):
        print(f"{k:22} {all_before_roots[k]:10d}")
    return all_before_roots


def test(titles):
    maxt = 10
    cpt = 0
    tx = []
    for kt, t in titles.items():
        for w in t.words:
            if w.gov == 0 and w.dep in ['_', 'root'] and w.pos == 'NC':
                print(t.idt, t.text)
                cpt += 1
                tx.append(t)
        if cpt == maxt:
            break
    return tx


def test1(titles):
    governed = {}
    "On regarde si la root est un P ou P+D, on regarde qui dépend d'elle"
    for kt, t in titles.items():
        for w in t.words:
            if w.gov == 0 and w.dep in ['_', 'root'] and w.pos in ['P', 'P+D']:
                nbgov = 0
                for ww in t.words:
                    if w.gov == 1:
                        nbgov += 1
                if nbgov in governed:
                    governed[nbgov] += 1
                else:
                    governed[nbgov] = 1
    return governed
