# XML in TAL
from lxml import etree

class Word:

    def __init__(self):
        self.lemma = None
        self.translations = {}

    def set_lemma(self, lem):
        self.lemma = lem
        self.translations['fr'] = self.lemma

    def set_translation(self, lang, val):
        self.translations[lang] = val

def make(root):
    words = []
    for element in root.iter():
        if element.tag == 'article':
            words.append(Word())
        elif element.tag == 'title':
            words[-1].set_lemma(element.text)
        elif element.tag == 'trans':
            words[-1].set_translation(element.attrib['lang'], element.text)

    root = etree.Element("glawi")
    print(f"[INFO]  Output for {len(words)} words.")
    for w in words:
        entree = etree.SubElement(root, "entree")
        nb_trad = 0
        for trans, val in w.translations.items():
            t = etree.SubElement(entree, "version", lang=trans)
            t.text = val
            nb_trad += 1
        t = etree.SubElement(entree, "traductions", num=str(nb_trad))
    out = etree.ElementTree(root)
    out.write('exo_02_out_glawi.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")

if __name__ == '__main__':
    tree = etree.parse('exo_02_GLAWI_R2016-05-18_100009.xml')
    root = tree.getroot()
    print("[START]", root.tag)
    make(root)
    print("[DONE]")
