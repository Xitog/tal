f = open('de_X_a_Y_brut.csv', mode='r', encoding='utf-8')
content = f.readlines()
print(len(content))

cpt_nom1_eq_nom2 = 0
cpt_occ_nom1_eq_nom2 = 0
nom1_eq_nom2 = []

class Line:

    de = 0
    nom1 = 1
    a = 2
    nom2 = 3
    nb = 4

    def __init__(self, arr):
        arr = line.split(';')
        self.de = arr[Line.de]
        self.nom1 = arr[Line.nom1]
        self.a = arr[Line.a]
        self.nom2 = arr[Line.nom2]
        self.nb = int(arr[Line.nb])

origin = 'origin'
arrivee = 'arrivee'
data = {}
nb_jour = 0
for line in content:
    d = Line(line)
    if d.nom1 == 'jour' or d.nom2 == 'jour':
        nb_jour += d.nb
    if d.nom1 == d.nom2:
        cpt_nom1_eq_nom2 += 1
        cpt_occ_nom1_eq_nom2 += d.nb
        nom1_eq_nom2.append(d.nom1)
        #if d.nb > 1:
        #    print(d.nom1, d.nom2, d.nb)
    if d.nom1 not in data:
        data[d.nom1] = {origin: d.nb, arrivee: 0}
    else:
        data[d.nom1][origin] += d.nb
    if d.nom2 not in data:
        data[d.nom2] = {origin: 0, arrivee: d.nb}
    else:
        data[d.nom2][arrivee] += d.nb
    if d.nom2 == 'application':
        print('de', d.nom1, 'à application [', d.nb, ']')
    if d.nom2 == 'jour':
        print('de', d.nom1, 'à jour [', d.nb, ']')

print('nb jour:', nb_jour)
print('nb jour (data):', data['jour'][origin], data['jour'][arrivee])

print('------------------------------')
print('Results')
print('------------------------------')
f = open('out.csv', mode='w', encoding='utf-8')
for d in data:
    f.write(d + ';' + str(data[d][origin]) + ';' + str(data[d][arrivee]) + '\n')
f.close()

print('nom1 = nom2 [cas]', cpt_nom1_eq_nom2)
print('nom1 = nom2 [occ]', cpt_occ_nom1_eq_nom2)
#print(nom1_eq_nom2)
for n in nom1_eq_nom2:
    print(n, ', ', sep='', end='')
