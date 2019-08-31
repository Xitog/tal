# Whiteboard : for dynamic code
# Use reload(wb) to reload this script after having executed datamodel.py
import openpyxl
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import PatternFill, Font

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


def p_cs_de_inf(t):
    res = elem_cs_de_inf(t)
    print(*res, sep = ' -> ')

patterns = [
    PatternFill(start_color='00FFFF00', end_color='00FFFF00', fill_type='solid'), # yellow
    PatternFill(start_color='0087CEEB', end_color='0087CEEB', fill_type='solid'), # blue sky
    PatternFill(start_color='0000FF00', end_color='0000FF00', fill_type='solid'), # green
    PatternFill(start_color='00FF0000', end_color='00FF0000', fill_type='solid'), # red
]

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
    wb.save('out.xlsx')


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


# DEPRECATED
# 1ère version (trop large) : être 1269 que 496 vinf 14902
# 2nd version sur corpus    : cpt_n_etre_n 805 cpt_n_etre_que 68 cpt_n_de_vinf 153
# 3e version sur corpus (+n avant de_vinf) : cpt_n_etre_n 833 cpt_n_etre_que 85 cpt_de_vinf 153
# 1209231 Possibilités de réduire
out = None
def search_cs(data=None, display=None, title=None):
    global out, last_pattern
    if display is not None:
        out = open(display + '.txt', mode='w', encoding='utf8')
    def xprint(pattern, idt, t, i1=-1, i2=-1, i3=-1):
        global out
        out.write(f"{pattern:10} : {idt:6s} : ")
        for iw, w in enumerate(t.words):
            if iw in [i1, i2, i3]:
                out.write(f"[{iw}]")
            out.write(w.form + ' ')
        out.write('\n')
    cpt_n_etre_n = 0
    cpt_n_etre_que = 0
    cpt_n_de_vinf = 0
    if data is None and title is not None:
        data = {title.idt : title}
    for kt, t in data.items():
        etre = None
        que = None
        vinf = None
        de = None
        n1 = None
        n2 = None
        for iw, w in enumerate(t.words):
            if w.lemma == 'être' and w.pos == 'V':
                etre = iw
            elif w.form in ['que', "qu'"]:
                que = iw
            elif w.pos == 'VINF':
                vinf = iw
            elif w.form == 'de':
                if de is None: de = iw
            elif w.pos == 'NC':
                if etre is None:
                    n1 = iw
                else:
                    n2 = iw
        if n1 is not None and de is not None and vinf is not None and n1 < de < vinf:
            if display in ['cpt_n_de_vinf', 'all']: xprint('cpt_n_de_vinf', t.idt, t, n1, de, vinf)
            if etre is not None and n1 < etre < de and de < vinf:
                print(t.idt, t)
            cpt_n_de_vinf += 1
        elif n1 is not None and etre is not None and n2 is not None and n1 < etre < n2:
            if display in ['cpt_n_etre_n', 'all']: xprint('cpt_n_etre_n', t.idt, t, n1, etre, n2)
            cpt_n_etre_n += 1
        elif n1 is not None and que is not None:
            if etre is not None and n1 < etre < que or etre is None and n1 < que:
                if display in ['cpt_n_etre_que', 'all']: xprint('cpt_n_etre_que', t.idt, t, n1, etre, que)
                cpt_n_etre_que += 1
    if display is not None:
        out.close()
    print('cpt_n_etre_n', cpt_n_etre_n, 'cpt_n_etre_que', cpt_n_etre_que, 'cpt_n_de_vinf', cpt_n_de_vinf)


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
