#!/usr/bin/python
# -*-coding:utf-8-*-
## Auteure : Mai Ho-Dac
## Date : 16/04/18
## Fonction : transformer un fichier XML en un fichier html en appliquant une feuille de style XSLT
## Distribution : Creative Commons-BY
## commande : python3 xslt4xml.py $fichier $xsltFile
## $fichier indique le chemin vers le fichier xml à transformer
## $xsltFile indique le chemin vers le fichier .xsl de transformation

## amélioration : intégrer une option pour indiquer si la transformation génère un txt, un html ou un xml selon ce qui est indiqué dans la feuille de style (qui est de l'XML)

import sys
import lxml.etree as ET
import lxml.html

fichier = 'exo_05_glawiExtrait.xml' #sys.argv[1]
xslFile= 'exo_05_trad.xsl' #sys.argv[2]
print("lecture du fichier "+fichier)
xml = ET.parse(fichier)
xslt = ET.parse(xslFile)
transform = ET.XSLT(xslt)
html = transform(xml)
htmlFile = fichier.replace(".xml", '') + "_pyprod.xml"
out = open(htmlFile,'w', encoding='utf8')
out.write(str(html))
print("htmlFile générée : "+htmlFile)
out.close()
