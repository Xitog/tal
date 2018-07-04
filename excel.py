#===============================================================================
# Code handling for handling data in Excel format XLSX
#-------------------------------------------------------------------------------
# Author : Damien Gouteux
# Last updated : 08 April 2018
# Technologies : Python, Excel XSLX
# Usage :
#     Write or read data in an Excel XLSX file.
#===============================================================================

#-------------------------------------------------------------------------------
# Import
#-------------------------------------------------------------------------------

# external
import openpyxl
#import xlwt

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class ExcelFile:

    def __init__(self, name, mode='r'):
        self.name = name
        self.mode = mode
        #self.wb = xlwt.Workbook()
        if mode == 'w':
            self.wb = openpyxl.Workbook() #write_only=True)
            ws = self.wb.active
            ws.title = 'Information'
            self.nb_sheet = 0
        elif mode == 'r':
            self.wb = openpyxl.load_workbook(name, read_only=True)
            self.nb_sheet = len(self.wb.sheetnames)
    
    def sheet(self, name):
        if name not in self.wb.sheetnames:
            raise Exception("Sheet unknown: ", name)
        return self.wb[name]
    
    # you must send a dict with :
    # { key : [key, v1, v2, v3] }
    # order => which column to use to order
    # percent => which column to use to percent
    def save_to_sheet_mul(self, name, values, order_col=0, reverse_order=True, percent_col=None, percent_val=None):
        # Handle if a new sheet is needed
        if self.nb_sheet > 0:
            ws = self.wb.create_sheet(name)
            self.nb_sheet += 1
        else:
            ws = self.wb.active
            ws.title = name
            self.nb_sheet += 1
        # Calculate the value to divide to have the percent
        if percent_col is not None and percent_val is None:
            percent_val = 0
            for _, val in values.items():
                try:
                    percent_val += val[percent_col]
                except TypeError as e:
                    print("An error has been encountered.")
                    print("val of percent_col is :", val[percent_col])
                    print("percent_col is:", percent_col)
                    print("data is:")
                    for v in val:
                        print("   ", v)
                    raise e
        # Process all the values
        row = 1
        if isinstance(values, dict):
            for sorted_values_with_key in sorted(values.items(), key=lambda t: t[1][order_col], reverse=reverse_order):
                # (key, [list of values])
                nb = 1
                for val in sorted_values_with_key[1]: # we iterate on [list of values]
                    ws.cell(column=nb, row=row, value=val)
                    nb += 1
                    if percent_col is not None and type(percent_col) == int:
                        if nb == percent_col + 2:
                            ws.cell(column=nb, row=row, value=val / percent_val)
                            nb += 1
                row += 1
        elif isinstance(values, list):
            for list_of_values in sorted(values, key=lambda t: t[order_col], reverse=reverse_order):
                nb = 1
                for val in list_of_values:
                    ws.cell(column=nb, row=row, value=val)
                    nb +=1
                row += 1

    
    def save_to_sheet(self, name, values, percent=None, test_val=None):
        # ws = wb.add_sheet(name)
        if self.nb_sheet > 0:
            ws = self.wb.create_sheet(name)
            self.nb_sheet += 1
        else:
            ws= self.wb.active
            ws.title = name
            self.nb_sheet += 1
        row = 1
        for val in sorted(values, key=values.get, reverse=True): #sorted(values.keys()):
            if test_val is None or test_val(values[val]):
                nb = 1
                if type(val) in [tuple, list]:
                    for v in val:
                        ws.cell(column=nb, row=row, value=v)
                        nb += 1
                else:
                    ws.cell(column=nb, row=row, value=val)
                    nb += 1
                #ws.write(row, 0, val)
                if type(values[val]) in [tuple, list]:
                    for v in values[val]:
                        ws.cell(column=nb, row=row, value=v)
                        #ws.write(row, nb, v)
                        nb += 1
                else:
                    ws.cell(column=nb, row=row, value=values[val])
                    #ws.write(row, nb, values[val])
                    nb += 1
                if percent is not None: # percent on last value
                    if type(values[val]) in [tuple, list]:
                        ws.cell(column=nb, row=row, value=values[val][-1] / percent)
                    else:
                        ws.cell(column=nb, row=row, value=values[val] / percent)
                    #ws.write(row, nb, values[val] / percent)
                row += 1

    def load_sheet(self, name,key=0, ignore=None):
        # load any sheet in dict with the choosen column as a key
        # ignoring specific column
        data = {}
        sheet = self.sheet(name)
        nb_row = 0
        for row in sheet.iter_rows(min_row=0):
            nb_cell = 0
            last_id = 0
            values = []
            for cell in row:
                if cell.value is not None:
                    if nb_cell == key:
                        last_id = cell.value
                    else:
                        if ignore is None or nb_cell not in ignore:
                            values.append(cell.value)
                nb_cell += 1
            data[last_id] = values
            nb_row += 1
        return data
    
    def load(self): # load the first sheet
        if self.mode != 'r':
            raise Exception('This ExcelFile should be on read mode.')
        wb = openpyxl.load_workbook(self.name + '.xlsx', keep_vba=True, read_only=True)
        ws = wb[wb.sheetnames[0]]
        table = {}
        for row in ws.rows:
            record = []
            for cell in row:
                record.append(cell.value)
            if len(record) > 1:
                table[record[0]] = record[1:]
        return table
    
    def save(self):
        if self.mode != 'w':
            raise Exception('This ExcelFile should be on write mode.')
        done = False
        modifier = ''
        count = 0
        while not done:
            try:
                self.wb.save(filename=self.name + modifier + '.xlsx')
                done = True
            except PermissionError:
                count += 1
                modifier = '_' + str(count)

#-------------------------------------------------------------------------------
# Test code if main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    excel = ExcelFile(name='test', mode='w')
    data = {
        "bordeaux" : ['Bordeaux', 'préfecture', 33, 'Gironde'],
        "toulouse" : ['Toulouse', 'préfecture', 31, 'Haute-Garonne'],
        "albi"     : ['Albi', 'préfecture', 81, 'Tarn-et-Garonne'],
        "castres"  : ['Castres', 'sous-préfecture', 81, 'Tarn-et-Garonne'],
    }
    excel.save_to_sheet_mul('VILLES', data, order_col = 2, reverse_order = False)
    excel.save()

