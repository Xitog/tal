#=================================================
# Production d'un document XML
#=================================================
# L'output sera de la forme :
# <?xml version="1.0" encoding="utf-8"?>
# <glawi>
#    <entree>
#       <version lang="fr">couche d'ozone</version>
#       <version lang="en">ozone layer</version>
#       <version lang="fi">otsonikerros</version>
#    </entree>
# </glawi>
# Ce script travaille à partir d'un extrait de
# GLAWI.
# Le premier paramètre doit être le nom du fichier
# source. Si aucun n'est fourni, un nom par défaut
# est essayé.
#=================================================

#-------------------------------------------------
# Import
#-------------------------------------------------
from lxml import etree
import datetime
import sys

#-------------------------------------------------
# Data model
#-------------------------------------------------
class Word:
    """A simple Word with its lemma and multiple translations"""
    
    def __init__(self):
        self.lemma = None
        self.translations = {}

    def set_lemma(self, lem):
        self.lemma = lem
        self.translations['fr'] = self.lemma

    def set_translation(self, lang, val):
        self.translations[lang] = val

#-------------------------------------------------
# Fonctions
#-------------------------------------------------
def make(root, output_name):
    # Build the list of words
    words = []
    for element in root.iter():
        if element.tag == 'article':
            words.append(Word())
        elif element.tag == 'title':
            words[-1].set_lemma(element.text)
        elif element.tag == 'trans':
            words[-1].set_translation(element.attrib['lang'], element.text)
    # Produce output
    root = etree.Element("glawi")
    print(f"[INFO] --- Writing output for {len(words)} words in", output_name)
    for w in words:
        entree = etree.SubElement(root, "entree")
        nb_trad = 0
        for trans, val in w.translations.items():
            t = etree.SubElement(entree, "version", lang=trans)
            t.text = val
            nb_trad += 1
        t = etree.SubElement(entree, "traductions", num=str(nb_trad))
    out = etree.ElementTree(root)
    out.write(output_name, pretty_print=True, xml_declaration=True, encoding="utf-8")

#-------------------------------------------------
# Main fonction
#-------------------------------------------------
if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            input_name = 'exo_02_GLAWI_R2016-05-18_100009.xml'
        else:
            input_name = sys.argv[1]
        tree = etree.parse(input_name)
        root = tree.getroot()
        start_time = datetime.datetime.now()
        print("[INFO] --- Starting at", start_time, 'for tag', root.tag)
        make(root, 'exo_02_out_glawi2.xml')
        end_time = datetime.datetime.now()
        print('[INFO] --- Ending at', end_time)
        delta = end_time - start_time
        print(f"[INFO] --- Script has ended [{delta} elapsed].\n")
    except OSError:
        print("Can't find input file:", input_name)

