# XML in TAL
from lxml import etree

root = etree.Element("CepiDC")

#file = open('exo_01_in_cepidc.txt', mode='r', encoding='utf8')
file = open('exo_01_in_AlignedCauses_2006-2012.csv', mode='r', encoding='utf8')
content = file.readlines()
content = content[1:]
file.close()
for line in content:
    infos = line.rstrip('\n').split(';')
    DocID = infos[0]
    YearCoded = infos[1]
    Gender = infos[2]
    Age = infos[3]
    LocationOfDeath = infos[4]
    LineID = infos[5]
    RawText = infos[6]
    IntType = infos[7]
    IntValue = infos[8]
    CauseRank = infos[9]
    StandardText = infos[10]
    ICD10 = infos[11]
    cause = etree.SubElement(root, "cause", icd10=ICD10, docid=DocID)
    rt = etree.SubElement(cause, "rawtext")
    rt.text = RawText
    st = etree.SubElement(cause, "standardtext")
    st.text = StandardText

out = etree.ElementTree(root)
out.write('exo_01_out_cepidc.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")

print(root.tag)
