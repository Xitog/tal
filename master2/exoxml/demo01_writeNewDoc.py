#!/usr/bin/python
# -*-coding:utf-8-*-
## Auteure : Mai Ho-Dac
## Date : 16/04/18
## Fonction : Générer le document xml suivant
## <?xml version="1.0" encoding="UTF-8"?>
## <racine>
##	 <element>
##		texte A
##		<subElement attribut="valeur">
##			texte B
##  	</subElement>
##   </element>
## </racine>

## Distribution : Creative Commons-BY
## commande : python3 writeNexDoc.py
## $dossier indique le chemin vers le dossier contenant tous les fichiers tei/xml
import sys
import glob
from lxml import etree

#fonction .Element pour créer l'élément racine
racine = etree.Element("racine")

#fonction .subElement pour créer un élément fils de l'élément <racine>
fils = etree.SubElement(racine, "element")

#fonction .text pour associer un contenu textuel à l'élément <element>
fils.text = "texte A"

#fonction .subElement pour créer un élément fils de l'élément <element>. Cet élément fils a un attribut.
petitFils = etree.SubElement(fils, "subElement", attribut="valeur")

petitFils.text = "texte B"

# attention ! ajouter ici la ligne : 
# element.text = "texte C"
# n'ajoutera pas de texte après l'élément <subElement> mais remplacera le texte de l'élément <element> !
# pour ajouter du texte après l'élément <subElement> il faut utiliser la fonction .tail qui ajoute du texte après un élément
petitFils.tail = "texte C"

# créer un objet out contenant l'arbre XML créé
out = etree.ElementTree(racine)

# pour associer une feuille de transformation XSLT, utiliser la fonction .addprevious pour insérer l'instruction avant la racine
# racine.addprevious(etree.PI('xml-stylesheet', 'type="text/xsl" href="my.xsl"'))

# écrire l'objet créé dans un fichier "outpu.xml" avec les options : 
# pretty_print="True" pour indenter le fichier
# xml_declaration="True" pour insérer la déclaration en début de fichier
# encoding="utf-8" pour déclarer l'encodage du fichier
out.write('demo01_output.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")

# pour indiquer la validation du fichier selon un DTD, ajouter l'information dans la création du fichier :
# out.write('output.xml', pretty_print=True, xml_declaration=True, encoding="utf-8", doctype="<!DOCTYPE racine SYSTEM 'my.dtd'>")


 
