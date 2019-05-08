

# <title id="1559637"> dans 01
# verbe conjugué : c'est lui le root normalement.
# or, pour 75% c'est des noms ! Les titres sont principalement des
# constructions autour d'un SN.
def type_of_roots(titles):
    types = {}
    for _, t in titles.items():
        for w in t.words:
            if w.gov == '0' and w.dep in ['_', 'root']:
                if w.pos in types:
                    types[w.pos] += 1
                else:
                    types[w.pos] = 1
    total = 0
    for k, v in types.items():
        total += v
    return types, total, sorted(types, key=types.get, reverse=True)

                

