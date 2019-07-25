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


def deter(titles):
    det = {}
    no_det = 0
    nb_found = {}
    for kt, t in titles.items():
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
