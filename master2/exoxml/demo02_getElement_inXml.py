#!/usr/bin/python
# -*-coding:utf-8-*-
## Auteure : Mai Ho-Dac
## Date : 16/04/17
## Fonction : extraire des éléments spécifiques dans un fichier XML

## Distribution : Creative Commons-BY
## commande : python3 getElement_inXml.py $fichier
## $fichier indique le chemin vers le fichier xml dans lequel extraire l'information
## output : stdout
import sys
import glob
from lxml import etree

#fichier=sys.argv[1]
fichier = 'exo_01_out_cepidc.xml'

tree = etree.parse(fichier)
root = tree.getroot()

# la fonction .findall permet de ramener tous les éléments selon une requête xpath (ici tout élément <cause> descendant de la racine)
for element in root.findall('.//cause'):
# la fonction .iter permet de ramener tous les éléments répondant aux tags indiqués entre parenthèses
#	for element in root.iter('child1', 'child2'):
        code = element.attrib['icd10']
        if len(code) == 0:
                code = 'None'
        text = element.find('.//standardtext').text
        if text is not None and len(text) == 0:
                text = 'No text'
        if code == "R092":
                print(f"{code:5s}", text)
	#if element.attrib.get('Code') == "R092":
	#	cause = element.text
	#	if cause:
	#		print(cause)
