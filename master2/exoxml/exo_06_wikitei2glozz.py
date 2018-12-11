# -*- coding: utf8 -*-
"""
#auteur : Lydia-Mai Ho-Dac
#date : 22 oct. 2018
#projet E:Calm
#fonction : transformation d'une discussion Wikipedia encodée selon la norme TEIP5 en fichier Glozz à annoter
#entrée : le fichier xml normé teiP5
#sortie deux fichiers : .ac et .aa
#commande : 
#python3 Wikitei2glozz.py $dir
#$dir = chemin du dossier contenant les XML TEI à transformer. 
 
#le modèle Glozz est le suivant : 
#<?xml version="1.0" encoding="UTF-8"?>
#<annotations>
#<unit id="transcription">
#<metadata>
#<author>layout</author>
#<creation-date>-1</creation-date>
#</metadata>
#<characterisation>
#<type>title</type>
#<featureSet/>
#</characterisation>
#<positioning>
#<start>
#<singlePosition index="###"/>
#</start>
#<end>
#<singlePosition index="###"/>
#</end>
#</positioning>
#</unit>

#Types de layout : 		<type name="title"/><type name="subTitle"/><type name="abstract"/><type name="sectionTitle"/><type name="subSectionTitle"/><type name="subSubSectionTitle"/><type name="subSubSubSectionTitle"/><type name="list"/><type name="numberedList"/><type name="listItem"/><type name="quote"/><type name="bold"/><type name="italic"/>

#import os
"""
import time
import sys
import glob
import re
from lxml import etree 

def generatedAA(fichier):
	outFile = fichier[0:(len(fichier)-4)]
	outAC=outFile+'.ac'
	outAA=outFile+'.aa'
	ac = open(outAC, 'w')
	tree = etree.parse(fichier)
	root = tree.getroot()
	ofsStart = 0
	ofsEnd = 0
	ofsStartPara = 0
	ofsEndPara = 0
	idUnit = 0
	embUnits = []
	rootAA = etree.Element("annotations")

	def addGlozzUnit(idUnit,unit,start,end):
	# Add the units subelements
		dateCreation = int(time.time()) #timestamp
		newUnit = etree.SubElement(rootAA, "unit", id=("layout_"+str(idUnit)))
		metadata = etree.SubElement(newUnit, "metadata")
		author = etree.SubElement(metadata, "author")
		author.text = "Wikitei2glozz"
		creation = etree.SubElement(metadata, "creation-date")
		creation.text = str(idUnit)
		characterisation = etree.SubElement(newUnit, "characterisation")
		charactType = etree.SubElement(characterisation, "type")
		charactType.text = unit
		featureSet = etree.SubElement(characterisation, "featureSet")
		positioning = etree.SubElement(newUnit, "positioning")
		posit = etree.SubElement(positioning, "start")
		index = etree.SubElement(posit, "singlePosition", index=str(start))
		posit = etree.SubElement(positioning, "end")
		index = etree.SubElement(posit, "singlePosition", index=str(end))

	body = root.find("text/body")
	memTail = ""
	mod = ""
	textDel = ""
	para = " "
	head = 0
	for elemt in body.getiterator():

		if isinstance(elemt.tag, str): #permet de ne pas prendre les commentaires

			textElemt = elemt.text #texte contenu dans l'élément (jusqu'au prochain élément, qqe soit sa hiérarchie) 
			tailElemt = elemt.tail #texte succédant à l'élément.
			tagElemt = elemt.tag
			typElemt = elemt.get("type")
			if textElemt is None:
				textElemt = ""
			else:
				textElemt = textElemt.replace("\n","")
				textElemt = textElemt.replace("\t","")
				textElemt = textElemt.replace("  "," ")

			if tailElemt is None:
				tailElemt = ""
			else:
				tailElemt = tailElemt.replace("\n","")
				tailElemt = tailElemt.replace("\t","")
				tailElemt = tailElemt.replace("  "," ")

			if typElemt is None:
				typElemt = ""
			if tagElemt is None:
				tagElemt = ""

#les éléments post ne contiennent pas de texte. Pour l'instant, on indique simplement le niveau et l'auteur du Post comme un soustitre de section. DOnc on ajoute du texte dans le .ac et on décale l'offset 
			if tagElemt == "post":
				textElemt = "Post niveau"+elemt.get("indentLevel")+" par "+elemt.get("who")
				ac.write(textElemt)
				ofsEnd = ofsStart+len(textElemt)
				idUnit = idUnit + 1
				addGlozzUnit(idUnit,"subSectionTitle",ofsStart,ofsEnd)
				ofsStartPara = ofsStartPara+len(textElemt)
				

#les éléments <signed></signed> contiennent la signature de l'auteur du post. 
			elif tagElemt == "signed":
#Il peut contenir des éléments <name> et <date> qui eux-mêmes contiennent du texte. ON fait donc un itertext() pour prendre tout élément textuel contenu dans la signature				
				for allText in elemt.itertext():
					allText = allText.replace("\n","")
					allText = allText.replace("\t","")
					allText = allText.replace("  "," ")
					
					textElemt = textElemt + allText
				para = para + textElemt
				ofsEnd = ofsStart+len(textElemt)
				print(tagElemt+": "+textElemt+" ("+str(ofsStart)+"-"+str(ofsEnd)+")")
				idUnit = idUnit + 1
				addGlozzUnit(idUnit,"bold",ofsStart,ofsEnd)
				para = para + tailElemt
				ofsEnd = ofsEnd + len(tailElemt)
				
			elif (tagElemt == "p" or tagElemt == "head" or tagElemt == "item") and (para == " " or para == ""):
				if tagElemt == "head":
					head = 1
				else:
					head = 0
				ofsEnd = ofsStart+len(textElemt)
				para = textElemt			

			elif tagElemt == "p" or tagElemt == "head" or tagElemt == "item":
				ofsEndPara = ofsStartPara+len(para)
				if head == 1:
					idUnit = idUnit + 1
					addGlozzUnit(idUnit,"sectionTitle",ofsStartPara,ofsEndPara)
				else: #pour l'instant on considère les items comme des paragraphes
					idUnit = idUnit + 1
					addGlozzUnit(idUnit,"paragraph",ofsStartPara,ofsEndPara)

				if tagElemt == "head":
					head = 1
				else:
					head = 0
				ac.write(para)
				ofsStartPara = ofsEndPara
				ofsStart = ofsStart
				ofsEnd = ofsStart+len(textElemt)
				para = textElemt			
			else:
				print(tagElemt+" elemt NOT DIRECTLY in AA : "+textElemt+" ("+str(ofsStart)+"-"+str(ofsEnd)+")")

			ofsStart = ofsEnd
	ofsEndPara = ofsStartPara+len(para)
	idUnit = idUnit + 1
	if head == 1:
		addGlozzUnit(idUnit,"sectionTitle",ofsStartPara,ofsEndPara)
	else:
		addGlozzUnit(idUnit,"paragraph",ofsStartPara,ofsEndPara)

	ac.write(para)
	ac.close()
	# Save annotations to aa file
	aa = etree.ElementTree(rootAA)
	aa.write(outAA, pretty_print=True, xml_declaration=True, encoding="utf-8")

dossier=sys.argv[1]
idUnit = 0
print("lecture du dossier "+dossier)
for xml in glob.glob(dossier+"/*.xml"):
	print(xml)
	generatedAA(xml)
