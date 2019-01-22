
                  ____  _
                 / __ \| |                 
                | |  \/| |  ___   ____ ____
                | | __ | | / _ \ |_  /|_  /
                | |_\ \| || (_) | / /  / / 
                 \____/|_| \___/ /___|/___|


                             Titre du document : readme.txt
                                    Auteur : Damien Gouteux
                                    Version : 2019-01-22-1a
                                    Licence : CC3.0BY-SA-NC


           Grazie mille à Silvia pour la seconde annotation

-----------------------------------------------------------
Plan
-----------------------------------------------------------

Table des matières [MAT]
  1. Présentation du contenu de l'archive [ARC]
        1.1 Fichiers de l'archive
        1.2 Notes sur le code
        1.3 Script log.py
  2. Modèle d'annotation proposé [ANN]
        2.1 Type Mention
        2.2 Type Text
        2.3 Type Signature
        2.4 Relation MentionOfText
        2.5 Style
        2.6 Conversion de XML vers AA/AC
  3. Bilan de l'annotation [BIL]
        3.1 Comptage des annotations
        3.2 Comparaison des types
        3.3 Correspondance de positions
        3.4 Comparaison de feature
        3.5 Sorties
        3.6 Résultats
            3.6.1 Correspondance de positions
            3.6.2 Accord inter-annotateurs pour la feature fonction
            3.6.3 Accord inter-annotateurs pour la feature autoref
            3.6.4 Accord inter-annotateurs pour l'ensemble des features
    [FIN]

Ce document présente le travail effectué pour l'UE traitant de XML et de Glozz en Master 2 LITL à l'Université Jean-Jaurès.

Après une brève présentation du contenu de l'archive, nous présentons notre modèle d'annotation. Nous dressons ensuite un bilan de l'annotation en détaillant certains traitements opérés par le code.

Rechercher le code court entre crochets permet d'accéder directement à une partie.

Ce document utilise les conventions typographiques suivantes :
    o << Mention >> pour un type d'unités dans un modèle d'annotation Glozz (sauf dans les titres).
    o [[ feature ]] pour une feature d'une unité Glozz (sauf dans les titres).
    o < div > pour une balise XML.
    o [ attr ] pour un attribut de balise XML.
    o les guillemets doubles droits " " signalent un exemple.

-----------------------------------------------------------
1. Présentation du contenu de l'archive [ARC]
-----------------------------------------------------------

1.1 Fichiers de l'archive
-------------------------

Nous présentons dans cette partie le contenu de l'archive livrée sous la forme d'un tableau :

+====================+=======================+==============================================+
| Nom du fichier     | Type                  | Contenu                                      |
+====================+=======================+==============================================+
| readme.txt         | Fichier texte         | Ce fichier                                   |
+--------------------+-----------------------+----------------------------------------------+
| log.py             | Script Python         | Simple classe statique de logging            |
+--------------------+-----------------------+----------------------------------------------+
| script1.py         | Script Python         | Traduction XML TEI-P5 => GLOZZ AC + AA       |
+--------------------+-----------------------+----------------------------------------------+
| script2.py         | Script Python         | Comparaison de deux annotations GLOZZ AA     |
+--------------------+-----------------------+----------------------------------------------+
| talk.aam           | Modèle d'annotation   | Modèle d'annotation pour Glozz AAM           |
+--------------------+-----------------------+----------------------------------------------+
| talk.as            | Modèle de styles      | Modèle de styles pour modèle d'annotation    |
+--------------------+-----------------------+----------------------------------------------+
| 15075_dgx.aa       | Annotations de Damien | Annotations Glozz faites par Damien G.       |
+--------------------+-----------------------+----------------------------------------------+
| 15075_slv.aa       | Annotations de Silvia | Annotations Glozz faites par Silvia F.       |
+--------------------+-----------------------+----------------------------------------------+
| data (dossier)     | Fichiers AA + AC      | Tous les fichiers XML traduits en AA + AC    |
+--------------------+-----------------------+----------------------------------------------+
| fonction_diff.txt  | Fichier texte         | Fichier de résultats sur feature fonction    |
+--------------------+-----------------------+----------------------------------------------+
| autoref_diff.txt   | Fichier texte         | Fichier de résultats sur feature autoref     |
+--------------------+-----------------------+----------------------------------------------+
| all_diff.txt       | Fichier texte         | Fichier de résultats sur toutes les features |
+--------------------+-----------------------+----------------------------------------------+
| fonction_diff.xlsx | Fichier Excel 2007    | Fichier de résultats sur feature fonction    |
+--------------------+-----------------------+----------------------------------------------+
| autoref_diff.xlsx  | Fichier Excel 2007    | Fichier de résultats sur feature autoref     |
+--------------------+-----------------------+----------------------------------------------+
| all_diff.xlsx      | Fichier Excel 2007    | Fichier de résultats sur toutes les features |
+--------------------+-----------------------+----------------------------------------------+

1.2 Notes sur le code
---------------------

Notre code dépend des modules suivants :
    o LXML (obligatoire pour script1.py et script2.py)
    o NLTK (seulement pour le calcul du Kappa dans script2.py, optionnel)
    o openpyxl (seulement pour la sortie Excel dans script2.py, optionnel)

L'ensemble des scripts a été exécuté avec succès sous Windows avec Python 3.6.1 en version 32 bits et Python 3.7.0 en version 64 bits.

Les scripts utilisent la PEP 498, formatted string literals, introduite par la version 3.6.0. Ils ne fonctionneront donc pas avec une version antérieure.

Nous n'avons pas cherché à optimiser le code mais avons essayé de le maintenir clair et concis.

1.3 Script log.py
-----------------

Une classe statique simple pour logguer les différentes actions du programme.

Étant très périphérique, nous l'avons volontairement laissée très simple.

*******************
*** Commentaire ***
*******************

Une évolution possible serait d'en faire une classe non statique pour avoir plusieurs instances de logs qui loggueraient des choses différentes, voir sur des flux différents : sortie console, sortie fichier ou sortie réseau.

-----------------------------------------------------------
2. Modèle d'annotation proposé [ANN]
-----------------------------------------------------------

2.1 Type Mention
----------------

Le type central d'unité de notre annotation est le type << Mention >>.
Il possède 5 features :
    o [[ fonction ]] est une énumération de 12 valeurs possibles. 
      Nous fournissons de nombreuses possibilités à l'annotateur pour qu'il puisse exprimer finement son choix. Les 12 valeurs sont :
        + autorisation
            - le locuteur donne une autorisation à un autre
        + expression d'accord
            - le locuteur exprime son accord sur la production d'un autre locuteur
        + expression de désaccord
            - le locuteur exprime son désaccord sur la production d'un autre locuteur
        + demande d'intervention
            - le locuteur demande à un autre d'intervenir sur la page
        + demande de pardon
            - le locuteur demande pardon à un autre : "pardonnez-moi"
        + demande de politesse
            - utilisée pour les productions comme "s'il vous plaît"
        + question (par défaut)
            - le locuteur pose une question à un autre
        + citation
            - le locuteur en cite un autre
        + félicitation
            - le locuteur en félicite un autre
        + remerciement
            - le locuteur en remercie un autre
        + salutation
            - le locuteur salue un autre
        + affirmation
            - le locuteur affirme une information
    o [[ contexte ]] : le contexte général de la mention qui apporte une nuance à la fonction. 
      À choisir entre trois contextes larges :
        + positif (laudateur)
        + neutre
        + négatif (ironie, sarcasme, agressif)
      Une félicitation dans un contexte ironique n'a pas la même valeur sémantique qu'une félicitation dans un contexte positif.
    o [[ repriseID ]] : booléen (oui/non) indiquant si la mention d'un locuteur reprend directement son identifiant comme "Cher Crainquebille". Par défaut non.
    o [[ autoref ]] : si l'utilisateur se mentionne lui-même (oui / non), cela correspond à l'utilisation de la première personne. Par défaut non.
    o [[ commentaire ]] : pour rajouter une indication libre sur l'annotation comme exprimer un doute ou une nuance.

********************
*** Commentaires ***
********************

o La présentation de Mme Ludivine Crible nous a donné l'idée que peut-être la notion d'opposition et d'accord aurait dû être pensée comme une dimension orthogonale à la fonction même. Cela donnerait de nouvelles combinaisons dont il faudrait vérifier l'existence en corpus. Cette idée nous étant venue tardivement, nous n'avons pas pu la mettre en œuvre.
o Le texte "si je ne m'abuse" nous a posé problème. Une solution aurait été d'élargir la valeur "demande de politesse" à "formules de politesse" pour l'y placer aux côtés de "s'il vous plaît". Cette réflexion arrivant après les annotations, nous n'avons pas modifié notre modèle et l'avons placé dans "question", même si cette classification ne nous satisfait pas entièrement.
o En plus des mentions directes, "Cher Crainquebille", nous considérons tous les mots porteurs d'une marque de personne comme une mention, directe dans le cas des pronoms sujets et compléments, indirecte dans le cas des pronoms et adjectifs possessifs : on mentionne un intervenant via un de ses objets possédés.

2.2 Type Text
-------------

Une portion de texte. Le type << Text >> n'est pas utilisé.

2.3 Type Signature
------------------

Le type << Signature >> indique simplement une signature de post. Elles sont automatiquement créées par le script de conversion de XML vers AA/AC mais l'annotateur peut en rajouter manuellement.

*******************
*** Commentaire ***
*******************

o Il aurait été intéressant d'ajouter une feature [[ automatique ]] pour garder en mémoire si l'unité de type << Signature >> avait été générée automatiquement ou non.

2.4 Relation MentionOfText
--------------------------

Une relation qui relie une mention à une partie de texte. Cette relation n'est pas utilisée.
Notre idée était de pouvoir relier certaines mentions à une portion de texte concernée mais nous avons abandonné cette idée car elle ne semblait pas assez pertinente.

Si on prend comme exemple le remerciement, un intervenant A sur la page de discussion remercie un intervenant B pour une action. Cette action pour laquelle B est remerciée n'a que rarement une traduction textuelle ou celle-ci est trop diffuse pour que sa localisation soit intéressante.

*******************
*** Commentaire ***
*******************

o Nous avons remarqué que Glozz ne semble pas permettre de typer les deux extrémités d'une relation. Nous aurions aimé pouvoir dire qu'une extrémité devait être forcément d'un type donné d'unité comme dans << Mention >> -------MentionOfText-----------> << Texte >>

2.5 Style
---------

Nous proposons un style dans le fichier talk.as pour notre modèle d'annotation.

Nous avons joué sur les couleurs pour distinguer les différents types d'unités.

+=================+=========+
|      Type       | Couleur |
+=================+=========+
| << Mention >>   |  vert   |
+-----------------+---------+
| << Signature >> |  rouge  |
+-----------------+---------+
| << Text >>      |  bleu   |
+-----------------+---------+

********************
*** Commentaires ***
********************

o Il ne semble pas possible de modifier la couleur de la bordure d'un type, ni sa police.
o Il ne semble pas possible de modifier le style d'un type en fonction de la valeur de ses features. On aurait pu imaginer des couleurs différentes selon la [[ fonction ]] de la mention.

2.6 Conversion de XML vers AA/AC
--------------------------------

Le fichier script1.py contient le code de traduction de l'XML TEI-P5 vers un fichier corpus Glozz (AC) et un fichier annotation Glozz (AA). Ce script est un travail original.

Pour effectuer cette conversion, on désérialise le fichier XML à la norme TEI-P5. Les discussions sont une suite de balises < div >. Chaque < div > possède une tête < head > et une suite de < post > ou de sous < div >. Un < post > est écrit par un locuteur et contient une suite de paragraphes < p> et/ou de < list >. Une < list > possède à son tour des < item >.

Le script essaye d'obtenir pour chaque < post > une signature. Pour cela, il regarde à plusieurs endroits :
    o S'il existe dans le post un élément dont le chemin relatif est : .//signed/ref/name (il ne regarde que le premier élément correspondant à ce chemin)
    o Si rien n'est trouvé et si l'attribut [ who ] du post est renseigné, il prend la valeur de celui-ci.

Cette systématicité permet de mieux comprendre l'enchaînement des discussions dans le rendu du document final Glozz. Nous utilisons les unités typographiques par défaut de Glozz pour produire un document plus lisible. Un mode debug permet de rajouter des lignes dans le document produit pour encore mieux visualiser les différentes parties de la page de discussion.

Nous n'avons pas utilisé l'attribut [ indentLevel ] pour cette fonctionnalité car le résultat obtenu par notre méthode - en nous fondant sur la structure de l'arbre XML - nous semblait suffisant, mais il serait plus rigoureux d'utiliser les deux, ne serait-ce que pour vérifier.

-----------------------------------------------------------
3. Bilan de l'annotation [BIL]
-----------------------------------------------------------

Nous avons demandé à notre camarade de Master 2, Mme Silvia Federzoni, d'annoter le texte choisi, la discussion à propos de l'article sur le philosophe Friedrich Nietzsche (fichier original 15075.xml), et elle a aimablement bien voulu se prêter à l'exercice. Nous l'avons également annoté de notre côté pour obtenir une paire d'annotations, soit deux fichiers AA nommés 15075_dgx.aa et 15075_silvia.aa.

Le script2.py a été conçu pour traiter automatiquement les deux annotations, constituées d'unités, et en faire la comparaison.

3.1 Comptage des annotations
----------------------------

Il compte le nombre d'unités dans chaque annotation, en différenciant :
    o les unités typographiques qui sont générées automatiquement
    o les unités de type << Signature >> qui peuvent avoir été générées automatiquement ou non
    o les unités de type << Mention >>

3.2 Comparaison des types
-------------------------

    o Nous ne comparons automatiquement que les unités du type << Mention >>.
    o Les unités typographiques sont les mêmes, car générées automatiquement, nous ne les comparons donc pas. 
    o Nous avons rajouté dans notre annotation deux unités << Signature >> que le script de transformation de XML vers AA/AC n'avait pas trouvées, Silvia ne l'a pas fait, nous ne les comparons donc pas.

3.3 Correspondance de positions
-------------------------------

Pour savoir quoi comparer ensemble, il faut constituer des paires d'unités et pour cela nous utilisons la position des unités. Nous considérons qu'il existe une marge d'erreur entre les positions de deux unités. La sélection des limites se faisant à la souris, de manière peu précise, l'utilisateur peut toujours déborder d'un caractère ou deux. Nous considérons ainsi deux unités en correspondance de positions si les différences absolues entre leurs bornes de départ et leurs bornes de fin sont inférieures à une précision donnée, que nous avons mis empiriquement à deux. Nous ne testons pas le contenu des chaînes délimitées par les bornes car ces positions se réfèrent à un même fichier de corpus. Prenons un exemple :

"J'adore"

L'utilisateur 1 annote J, l'utilisateur 2 annote J'.
La différence entre les bornes de départ est de 0.
La différence entre les bornes de fin est de 1, donc inférieure à notre précision de 2.
Donc nous considérons les unités en correspondance de positions pour cet exercice même si leurs contenus est différent ("J" contre "J'").

Nous pouvons donc diviser les unités des annotations 1 et 2 en deux groupes :
    o celles en correspondance de positions, se trouvant donc dans les deux annotations,
    o celles sans correspondance de positions, se trouvant uniquement dans une des deux annotations.

On peut ensuite comparer les valeurs des features de celles en correspondance de positions.

********************
*** Commentaires ***
********************

o La précision est réglable via la variable statique Unit.PRECISION. Nous pensons qu'elle ne devrait pas excéder trois pour ne avoir de problème avec deux annotations se suivant de façon très proche comme dans "Je me".  
o Il est très facile de développer un mode strict qui considérerait toute différence de bornes comme une inégalité. Il nous a semblé que cela n'allait pas dans le sens de l'exercice. 

3.4 Comparaison de feature
--------------------------

On peut ensuite, pour les unités en correspondance de positions, évaluer l'accord inter-annotateurs sur les différentes features définies pour les unités. La partie bilan [BIL] dresse un tableau de nos résultats.

3.5 Sorties
-----------

Le script script2.py produit une sortie dans un fichier texte simple ainsi que dans un fichier Excel XLSX. Le contenu est autodescriptif, nous préciserons simplement que :
    o '=' signifie un couple d'unité en correspondance de positions et ayant la même valeur pour la feature considérée,
    o '!' signifie un couple d'unité en correspondance de positions n'ayant pas la même valeur pour la feature considérée,
    o '?' signifie une unité sans correspondance de positions dans l'autre annotation
    o DGX est le code utilisé pour désigner les unités provenant de l'annotation de Damien
    o SLV est le code utilisé pour désigner les unités provenant de l'annotation de Silvia

Le script script2.py produit également une sortie Excel si le module openpyxl est présent. Cette présentation reprend les informations du fichier texte mais dans une autre présentation :
    o Le premier onglet décrit les unités avec pour chacune son contexte dans une fenêtre de 10 caractères avant et après, dans la limite du texte disponible.
    o Le deuxième onglet décrit les unités en correspondance de positions et dont la valeur pour la feature sélectionnée est égale.
    o Le troisième onglet décrit les unités en correspondance de positions et dont la valeur pour la feature sélectionnée est différente.
    o Le quatrième onglet décrit les unités sans correspondance de positions.
    o Le cinquième onglet donne la valeur du Kappa de Cohen.
    
La valeur du Kappa de Cohen est calculée grâce à la bibliothèque NTLK si elle est disponible. Pour l'interpréter, nous nous fondons sur l'échelle de Landis, J. R., Koch, G. G., The measurement of observer agreement for categorical data. Biometrics, 33, 159-174. 

3.6 Résultats
-------------

3.6.1 Correspondance de positions
---------------------------------

Tableaux des unités dans chaque annotation :

    +========================+=====+=====+
    | Annotation             | DGX | SLV |
    +========================+=====+=====+
    | Unités typographiques  | 214 | 214 |
    +------------------------+-----+-----+
    | Unités << Signature >> |  47 |  45 |
    +------------------------+-----+-----+
    | Unités << Mention >>   |  73 |  59 |
    +========================+=====+=====+
    | Total                  | 334 | 318 |
    +========================+=====+=====+

Les unités typographiques étant générées automatiquement par le script de conversion (script1.py), il est normal qu'elles soient identiques et qu'on en compte le même nombre. J'ai rajouté manuellement deux << Signature >> comme indiqué plus haut. J'ai étiqueté 73 unités de type << Mention >> contre 59 pour Silvia.

Sur celles-ci, 35 sont en correspondance de positions : c'est-à-dire qu'il y a une correspondance directe entre une unité dans mon annotation et une autre dans l'annotation de Silvia. Par contre, 62 unités ne sont pas en correspondance : 38 ne sont présentes que dans mon annotation et 24 ne sont présentes que dans l'annotation de Silvia.

Tableau récapitulatif :

    +=======================================+=====+=====+=======+
    | Annotation                            | DGX | SLV | Total |
    +=======================================+=====+=====+=======+
    | Unités en correspondance de positions |  35 |  35 |    35*|
    +---------------------------------------+-----+-----+-------+
    | Unités sans correspondance            |  38 |  24 |    62 |
    +=======================================+=====+=====+=======+
    | Total                                 |  73 |  59 |    97 |
    +=======================================+=====+=====+=======+

* Nous ne les additionnons pas car il s'agit des mêmes unités.

On peut déjà voir dans ces chiffres un niveau d'accord entre les annotateurs sur la définition même des unités à étiqueter. Sur les 97 unités définies par les deux annotateurs, seulement 35 sont communes soit 36%.

En regardant les textes des différentes unités sans correspondance, il s'agit toujours de pronoms ou d'identifiants d'utilisateurs, donc des unités qui sont valides, mais qui n'ont pas été repérées par un des deux annotateurs. De plus, il y a sûrement des unités qui n'ont été repérées par aucun des annotateurs et qui sont donc parfaitement invisibles pour nos traitements.

3.6.2 Accord inter-annotateurs pour la feature fonction
-------------------------------------------------------

Nous avons d'abord testé l'accord inter-annotateurs sur les 35 unités en correspondance pour la feature [[ fonction ]]. Cette feature indique la fonction de la mention.

Nous constatons que 19 unités sur 35, soit 54%, ont la même valeur pour leur feature [[ fonction ]]. Il reste 16 unités n'ayant pas la même valeur. Nous avons un Kappa de Cohen de 0.40. Selon l'échelle de Landis et Koch, nous sommes à l'extrême limite de la plage définissant un accord faible (de 0.21 à 0.40) pour les unités en correspondance de positions.

Les résultats sont consignés dans le fichier fonction_diff.txt.

3.6.3 Accord inter-annotateurs pour la feature autoref
------------------------------------------------------

Nous avons ensuite testé l'accord inter-annotateurs sur les 35 unités en correspondance pour la feature [[ autoref ]]. Cette feature indique si l'utilisateur s'implique dans la mention, qu'il s'auto-implique, cela se traduisant par l'utilisation de la première personne (je, me, mon, nous, nos).

Nous constations que 35 unités sur 35, soit 100%, ont la même valeur pour leur feature [[ autoref ]]. Nous avons donc un Kappa de Cohen de 1.0. Selon l'échelle de Landis et Koch, nous avons un accord parfait pour les unités en correspondance de positions.

Les résultats sont consignés dans le fichier autoref_diff.txt.

3.6.4 Accord inter-annotateurs pour l'ensemble des features
-----------------------------------------------------------

Au lieu de considérer l'accord feature par feature, on peut également considérer l'accord "total", c'est-à-dire qu'il y a accord sur deux unités entre deux annotateurs si et seulement si toutes les valeurs des features des deux unités sont les mêmes.

Nous constatons que 12 unités sur 35, soit 34%, ont les mêmes valeurs pour toutes les features. Nous avons un Kappa de Cohen de 0.30. Selon l'échelle de Landis et Koch, nous acons un accord inter-annotateurs faible. Pour calculer ce Kappa, nous construisons une valeur en agrégeant toutes les valeurs des features par simple concaténation.

Les résultats sont consignés dans le fichier all_diff.txt.

-----------------------------------------------------------

                           [FIN]
