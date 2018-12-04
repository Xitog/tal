<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" version="1.0" encoding="utf-8"/>
<xsl:template match="/glawi">
	<html>
		<!--Méta-données de la page Web-->
		<head>
			<!--Titre de la page Web-->
			<title>
				Aperçu de la ressource Glawi
			</title>
			<style type="text/css">
				body {
				  padding: 1em 1em 1em 1em;
				  margin: 0;
				  font-family: sans-serif;
				  font-size: normal;
				  color: black;
				  background: white;
				  background-position: top left;
				  background-attachment: fixed;
				  background-repeat: no-repeat;
				  text-align: justify;
				}
			</style>
		</head>
		<!--Texte de la page Web-->
		<body>
			<!--Titre de la page Web et petit texte en préambule-->
			<h1>Aperçu de la ressource Glawi</h1>
			<p>Référence : Franck Sajous and Nabil Hathout (2015). GLAWI, a free XML-encoded Machine-Readable Dictionary built from the French Wiktionary. Proceedings of the eLex 2015 conference, pp. 405-426, Herstmonceux, England.</p>
			<p>
				<!--Insertion d'un lien vers la page sur le site redac-->
				<xsl:element name="a">
					<xsl:attribute name="href">
						<xsl:text>http://redac.univ-tlse2.fr/lexiques/glawi.html</xsl:text>
					</xsl:attribute> 
					<xsl:attribute name="target">
							<xsl:text>_blank</xsl:text>
					</xsl:attribute>
					Disponible sur redac				
				</xsl:element>			
			</p>
			<!--Création d'une table qui contientra toutes les entrées-->
			<table>
				<!--Une entrée correspond ici à une entrée associée à un POS-->
				<xsl:for-each select="article/text/pos">
				<tr>
					<td style="background: #F5F6CE">
						<!--La première colonne indique la valeur du titre de l'article (le mot de l'entrée) avec entre parenthèses le POS, indiqué dans l'attribut type de l'élémenyt pos-->
						<b><xsl:value-of select="../../title"/></b> (<xsl:value-of select="@type"/>)</td>
					<td style="background: #CEE3F6">
						<ul>
							<!--La deuxième colonne indique toutes les définitions associées à cette entrée (mot+pos). Les définitions sont contenues dans l'élément definition. Elle seront présentées sous forme de liste non numérotée-->
							<xsl:for-each select="definitions/definition">
								<!--Le texte de la définition est contenu dans l'élément gloss/txt-->
								<li><xsl:value-of select="gloss/txt"/></li>
							</xsl:for-each>
						</ul>
					</td>
				</tr>
				</xsl:for-each>
			</table>
		</body>
	</html>
</xsl:template>
	
</xsl:stylesheet>
