"""
XML Glozz Project
------------------------------------------------------------

Evaluating two set of annotation.

Damien Gouteux - 2019 - CC 3.0 BY-SA-NC
"""

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

# External library
from lxml import etree

# Project library
from log import Log
from kappa import kappa

#-------------------------------------------------------------------------------
# Object model
#-------------------------------------------------------------------------------

class Unit:
    """An annotation."""

    PRECISION = 2
    
    def __init__(self, author, date, typ, start, end, features = None):
        self.author = author
        self.date = date
        self.typ = typ
        self.start = start
        self.end = end
        self.features = features if features is not None else {}

    def is_before(self, other):
        if not isinstance(other, Unit):
            raise Exception('Impossible to compare Annotation to ' + str(type(other)))
        return self.start < other.start
    
    def pos_match(self, other):
        if not isinstance(other, Unit):
            raise Exception('Impossible to compare Annotation to ' + str(type(other)))
        return abs(self.start - other.start) <= Unit.PRECISION and \
            abs(self.end - other.end) <= Unit.PRECISION
    
    def fun_match(self, other):
        if not isinstance(other, Unit):
            raise Exception('Impossible to compare Annotation to ' + str(type(other)))
        return self.features['fonction'] != self.features['fonction']
    
    def __eq__(self, other):
        if not isinstance(other, Unit):
            raise Exception('Impossible to compare Annotation to ' + str(type(other)))
        return self.author == other.author and self.date == other.date and \
               self.typ == other.typ and self.start == other.start and \
               self.end == other.end and self.features == other.features
    
    def __str__(self):
        fun = self.features['fonction'] if 'fonction' in self.features else 'no'
        return f"{self.start}, {self.end}, {fun}"

    def __repr__(self):
        return str(self)


class Annotation:
    """A representation of a Glozz Annotation file (AA)."""

    def __init__(self, filepath : str):
        try:
            file = open(filepath, mode='r', encoding='utf8')
        except (FileNotFoundError, IOError) as e:
            Log.error(f'On opening {filepath} : ' + str(e))
        try:
            tree = etree.parse(file)
        except RuntimeError as e:
            Log.error(f'On decoding {filepath} : ' + str(e))
        else:
            file.close()
        root = tree.getroot()
        self.units = []
        for unit in root.iterfind('unit'):
            author = unit.find('metadata/author').text
            date = unit.find('metadata/creation-date').text
            typ = unit.find('characterisation/type').text
            start = int(unit.find('positioning/start/singlePosition').attrib['index'])
            end = int(unit.find('positioning/end/singlePosition').attrib['index'])
            fset = unit.find('characterisation/featureSet')
            features = {}
            for feat in list(fset):
                features[feat.attrib['name']] = feat.text
            self.units.append(Unit(author, date, typ, start, end, features))


class Comparison:
    """Comparison of two annotations."""
    
    def __init__(self, ano1 : Annotation, ano2 : Annotation):
        self.diff(ano1, ano2)

    def diff(self, ano1 : Annotation, ano2 : Annotation):
        # Doing a exact list, removing all standard unit (paragraph)
        # for example we have:
        # annotator1 : [1, 2, 'question'] [10, 12, 'remerciement']
        # annotator2 : [3, 4, 'félicitation'] [10, 12, 'remerciement']
        # results : ano = [
        #             [1, 2, 'question'] None
        #                           None [3, 4, 'félicitation']
        #       [10, 12, 'remerciement'] [10, 12, 'remerciement'] ]
        p1 = 0
        ano = []
        while p1 < len(ano1.units):
            u1 = ano1.units[p1]
            if 'fonction' not in u1.features:
                p1 += 1
                continue
            p2 = p1
            while p2 < len(ano2.units):
                u2 = ano2.units[p2]
                if u1.pos_match(u2):
                    ano.append([u1, u2])
                    break
                elif u2.is_before(u1):
                    ano.append([None, u2])
                else:
                    ano.append([u1, None])
                    break
                p2 += 1
            p1 += 1
        for p in range(len(ano)):
            print(f"{p}. {ano[p][0]} vs {ano[p][1]}")
        ### EQUALITY
        self.ano1 = ano1
        self.ano2 = ano2
        self.ano = ano
    
    def naive_diff(self):
        """Make a diff of two annotation"""
        p1 = 0
        self.eq = 0
        while p1 < len(ano1.units):
            u1 = ano1.units[p1]
            p2 = 0
            while p2 < len(ano2.units):
                u2 = ano2.units[p2]
                if u1 == u2:
                    self.eq += 1
                p2 += 1
            p1 += 1
        self.ano1 = ano1
        self.ano2 = ano2
    
    def info(self):
        print('Length of annotation 1:', len(self.ano1.units))
        print('Length of annotation 2:', len(self.ano2.units))
        print('Length of fusion      :', len(self.ano))
        print('Equality              :', self.eq)

#-------------------------------------------------------------------------------
# Main & tool function
#-------------------------------------------------------------------------------

mode = 'PROD' # TEST

if __name__ == '__main__':
    Log.start()
    if mode == 'PROD':
        Log.info('Production mode')
        dgx = Annotation('15075_dgx.aa')
        slv = Annotation('15075_dgx.aa')
        #slv = Annotation('15075_silvia.aa')
        Comparison(dgx, slv).info()
    Log.end()

