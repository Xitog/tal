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
