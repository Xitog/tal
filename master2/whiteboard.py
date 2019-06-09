# res = stat(['roots.0.pos', 'domain'])
def agreg(data, max_pos=5):
    # Get total of key 2 (domain)
    domain_count = {}
    for k, v in data.items():
        dom = k[1]
        if dom not in domain_count:
            domain_count[dom] = v
        else:
            domain_count[dom] += v
    # Get the first 5 POS for each domain
    domain_stat = {}
    for k, v in data.items():
        pos = k[0]
        dom = k[1]
        if dom not in domain_stat:
            domain_stat[dom] = {}
        domain_stat[dom][pos] = round(v / domain_count[dom] * 100, 2)
    # Display
    for kdom in sorted(domain_count, key=domain_count.get, reverse=True):
        dom = domain_stat[kdom]
        print(f"{kdom:14}", end=' ')
        cpt = 0
        for pos in sorted(dom, key=dom.get, reverse=True):
            v = dom[pos]
            print(f"{pos:5} {v:5.2f}", end='  ')
            cpt += 1
            if cpt >= max_pos: break
        print(f"{domain_count[kdom]:6d}")


# Noun vs Verb
def aggregate(data):
    neo_data = {}
    for k, v in data.items():
        pos = k[0]
        dom = k[1]
        if pos in ['V', 'VIMP', 'VINF', 'VPP', 'VPR', 'VS']:
            key = ('VERB', dom)
        elif pos in ['NC', 'NPP']:
            key = ('NOUN', dom)
        else:
            key = (pos, dom)
        if key in neo_data:
            neo_data[key] += v
        else:
            neo_data[key] = v
    return neo_data


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

