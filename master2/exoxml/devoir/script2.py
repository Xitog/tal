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
import openpyxl

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
        return self.features['fonction'] == self.features['fonction']
    
    def __eq__(self, other):
        if not isinstance(other, Unit):
            raise Exception('Impossible to compare Annotation to ' + str(type(other)))
        return self.author == other.author and self.date == other.date and \
               self.typ == other.typ and self.start == other.start and \
               self.end == other.end and self.features == other.features

    def get_function(self):
        return self.features['fonction'] if 'fonction' in self.features else None
    
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

    def get_nb_layout(self):
        return sum(1 for u in self.units if u.typ not in ['Signature', 'Mention'])
    
    def get_nb_signature(self):
        return sum(1 for u in self.units if u.typ == 'Signature')

    def get_nb_mention(self):
        return sum(1 for u in self.units if u.typ == 'Mention')

    def __len__(self):
        return len(self.units)


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
        # Output console
        #for p in range(len(ano)):
        #    print(f"{p}. {ano[p][0]} vs {ano[p][1]}")
        # Save
        self.ano1 = ano1
        self.ano2 = ano2
        self.ano = []
        self.eq = 0
        self.not_eq = 0
        # Calc
        for elem in ano:
            u1 = elem[0]
            u2 = elem[1]
            if u1 is not None and u2 is not None:
                self.ano.append([u1, u2, u1.fun_match(u2)])
                if u1.fun_match(u2): self.eq += 1
                else: self.not_eq += 1
            else:
                self.ano.append([u1, u2, 'missing annotation'])
                self.not_eq += 1

    def to_file(self):
        datafile = open('15075.ac', mode='r', encoding='utf8')
        data = datafile.read()
        datafile.close()
        out = open('out.txt', mode='w', encoding='utf8')
        out.write("Number of units by types\n")
        out.write("------------------------\n")
        out.write(f"Layout types : {self.ano1.get_nb_layout():3d} {self.ano2.get_nb_layout():3d}\n")
        out.write(f"Signature    : {self.ano1.get_nb_signature():3d} {self.ano2.get_nb_signature():3d}\n")
        out.write(f"Mention      : {self.ano1.get_nb_mention():3d} {self.ano2.get_nb_mention():3d}\n")
        out.write(f"-----------------------\n")
        out.write(f"Total        : {len(self.ano1)} {len(self.ano2)}\n")
        out.write("\n")
        out.write("Number of common Mentions\n")
        out.write("-------------------------\n")
        out.write(f"                      {self.eq:3d}\n\n")
        out.write("Number of different Mentions\n")
        out.write("----------------------------\n")
        out.write(f"                         {self.not_eq:3d}\n")
        out.write("Common mentions\n")
        out.write("---------------\n")
        for elem in self.ano:
            u1 = elem[0]
            u2 = elem[1]
            if u1 is not None and u2 is not None:
                if u1.fun_match(u2):
                    out.write(f"{u1.start:6d}, {u1.end:6d}, {data[u1.start : u1.end]:30s}, {u1.typ:10s}, {u1.get_function():10s}\n")
                    out.write(f"{u2.start:6d}, {u2.end:6d}, {data[u2.start : u2.end]:30s}, {u2.typ:10s}, {u2.get_function():10s}\n\n")
        out.write("Different mentions\n")
        out.write("------------------\n")
        for elem in self.ano:
            u1 = elem[0]
            u2 = elem[1]
            if u1 is None:
                out.write("No mention at this position.\n")
            else:
                out.write(f"{u1.start:6d}, {u1.end:6d}, {data[u1.start : u1.end]:30s}, {u1.typ:10s}, {u1.get_function():10s}\n")
            if u2 is None:
                out.write("No mention at this position.\n")
            else:
                out.write(f"{u2.start:6d}, {u2.end:6d}, {data[u2.start : u2.end]:30s}, {u2.typ:10s}, {u2.get_function():10s}\n\n")
        out.close()
    
    def to_excel(self):
        datafile = open('15075.ac', mode='r', encoding='utf8')
        data = datafile.read()
        datafile.close()
        wb = openpyxl.Workbook(write_only=True)
        ws = wb.active
        if ws is None:
            ws = wb.create_sheet("Results")
        else:
            ws.title = "Results"
        for a in self.ano:
            u1 = a[0]
            u2 = a[1]
            row_data = []
            if u1 is not None:
                row_data += [u1.start, u1.end, data[u1.start : u1.end], u1.typ]
            if u2 is not None:
                row_data += [u2.start, u2.end, data[u2.start : u2.end], u2.typ]
            row_data.append(a[2])
            ws.append(row_data)
        # If the excel is opened we will get an PermissionError.
        # To prevent the loss of our data, the add a modifier to the filename,
        # until finding one not already taken.
        done = False
        modifier = ''
        count = 0
        while not done:
            try:
                # We could add a datetime stamp to the filename
                wb.save(filename='out' + modifier + '.xlsx')
            except PermissionError:
                count += 1
                modifier = '_' + str(count)
            else:
                done = True
    
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
        Log.info(f'Length of annotation 1: {len(self.ano1.units)}')
        Log.info(f'Length of annotation 2: {len(self.ano2.units)}')
        Log.info(f'Length of fusion      : {len(self.ano)}')

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
        c = Comparison(dgx, slv)
        c.info()
        try:
            c.to_excel()
        except:
            Log.warn("Failed to produce Excel output.")
        try:
            c.to_file()
        except:
            Log.warn("Failed to produce file output.")
    Log.end()

