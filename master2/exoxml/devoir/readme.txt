
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


           Grazie mille � Silvia pour la seconde annotation

-----------------------------------------------------------
Plan
-----------------------------------------------------------

Table des mati�res [MAT]
  1. Pr�sentation du contenu de l'archive [ARC]
        1.1 Fichiers de l'archive
        1.2 Notes sur le code
        1.3 Script log.py
  2. Mod�le d'annotation propos� [ANN]
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
        3.6 R�sultats
            3.6.1 Correspondance de positions
            3.6.2 Accord inter-annotateurs pour la feature fonction
            3.6.3 Accord inter-annotateurs pour la feature autoref
            3.6.4 Accord inter-annotateurs pour l'ensemble des features
    [FIN]

Ce document pr�sente le travail effectu� pour l'UE traitant de XML et de Glozz en Master 2 LITL � l'Universit� Jean-Jaur�s.

Apr�s une br�ve pr�sentation du contenu de l'archive, nous pr�sentons notre mod�le d'annotation. Nous dressons ensuite un bilan de l'annotation en d�taillant certains traitements op�r�s par le code.

Rechercher le code court entre crochets permet d'acc�der directement � une partie.

Ce document utilise les conventions typographiques suivantes :
    o << Mention >> pour un type d'unit�s dans un mod�le d'annotation Glozz (sauf dans les titres).
    o [[ feature ]] pour une feature d'une unit� Glozz (sauf dans les titres).
    o < div > pour une balise XML.
    o [ attr ] pour un attribut de balise XML.
    o les guillemets doubles droits " " signalent un exemple.

-----------------------------------------------------------
1. Pr�sentation du contenu de l'archive [ARC]
-----------------------------------------------------------

1.1 Fichiers de l'archive
-------------------------

Nous pr�sentons dans cette partie le contenu de l'archive livr�e sous la forme d'un tableau :

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
| talk.aam           | Mod�le d'annotation   | Mod�le d'annotation pour Glozz AAM           |
+--------------------+-----------------------+----------------------------------------------+
| talk.as            | Mod�le de styles      | Mod�le de styles pour mod�le d'annotation    |
+--------------------+-----------------------+----------------------------------------------+
| 15075.ac           | Corpus Glozz          | Les annotations se fondent sur ce corpus     |
+--------------------+-----------------------+----------------------------------------------+
| 15075_dgx.aa       | Annotations de Damien | Annotations Glozz faites par Damien G.       |
+--------------------+-----------------------+----------------------------------------------+
| 15075_slv.aa       | Annotations de Silvia | Annotations Glozz faites par Silvia F.       |
+--------------------+-----------------------+----------------------------------------------+
| data (dossier)     | Fichiers AA + AC      | Tous les fichiers XML traduits en AA + AC    |
+--------------------+-----------------------+----------------------------------------------+
| fonction_diff.txt  | Fichier texte         | Fichier de r�sultats sur feature fonction    |
+--------------------+-----------------------+----------------------------------------------+
| autoref_diff.txt   | Fichier texte         | Fichier de r�sultats sur feature autoref     |
+--------------------+-----------------------+----------------------------------------------+
| all_diff.txt       | Fichier texte         | Fichier de r�sultats sur toutes les features |
+--------------------+-----------------------+----------------------------------------------+
| fonction_diff.xlsx | Fichier Excel 2007    | Fichier de r�sultats sur feature fonction    |
+--------------------+-----------------------+----------------------------------------------+
| autoref_diff.xlsx  | Fichier Excel 2007    | Fichier de r�sultats sur feature autoref     |
+--------------------+-----------------------+----------------------------------------------+
| all_diff.xlsx      | Fichier Excel 2007    | Fichier de r�sultats sur toutes les features |
+--------------------+-----------------------+----------------------------------------------+

1.2 Notes sur le code
---------------------

Notre code d�pend des modules suivants :
    o LXML (obligatoire pour script1.py et script2.py)
    o NLTK (seulement pour le calcul du Kappa dans script2.py, optionnel)
    o openpyxl (seulement pour la sortie Excel dans script2.py, optionnel)

L'ensemble des scripts a �t� ex�cut� avec succ�s sous Windows avec Python 3.6.1 en version 32 bits et Python 3.7.0 en version 64 bits.

Les scripts utilisent la PEP 498, formatted string literals, introduite par la version 3.6.0. Ils ne fonctionneront donc pas avec une version ant�rieure.

Nous n'avons pas cherch� � optimiser le code mais avons essay� de le maintenir clair et concis.

1.3 Script log.py
-----------------

Une classe statique simple pour logguer les diff�rentes actions du programme.

�tant tr�s p�riph�rique, nous l'avons volontairement laiss�e tr�s simple.

*******************
*** Commentaire ***
*******************

Une �volution possible serait d'en faire une classe non statique pour avoir plusieurs instances de logs qui loggueraient des choses diff�rentes, voir sur des flux diff�rents : sortie console, sortie fichier ou sortie r�seau.

-----------------------------------------------------------
2. Mod�le d'annotation propos� [ANN]
-----------------------------------------------------------

2.1 Type Mention
----------------

Le type central d'unit� de notre annotation est le type << Mention >>.
Il poss�de 5 features :
    o [[ fonction ]] est une �num�ration de 12 valeurs possibles. 
      Nous fournissons de nombreuses possibilit�s � l'annotateur pour qu'il puisse exprimer finement son choix. Les 12 valeurs sont :
        + autorisation
            - le locuteur donne une autorisation � un autre
        + expression d'accord
            - le locuteur exprime son accord sur la production d'un autre locuteur
        + expression de d�saccord
            - le locuteur exprime son d�saccord sur la production d'un autre locuteur
        + demande d'intervention
            - le locuteur demande � un autre d'intervenir sur la page
        + demande de pardon
            - le locuteur demande pardon � un autre : "pardonnez-moi"
        + demande de politesse
            - utilis�e pour les productions comme "s'il vous pla�t"
        + question (par d�faut)
            - le locuteur pose une question � un autre
        + citation
            - le locuteur en cite un autre
        + f�licitation
            - le locuteur en f�licite un autre
        + remerciement
            - le locuteur en remercie un autre
        + salutation
            - le locuteur salue un autre
        + affirmation
            - le locuteur affirme une information
    o [[ contexte ]] : le contexte g�n�ral de la mention qui apporte une nuance � la fonction. 
      � choisir entre trois contextes larges :
        + positif (laudateur)
        + neutre
        + n�gatif (ironie, sarcasme, agressif)
      Une f�licitation dans un contexte ironique n'a pas la m�me valeur s�mantique qu'une f�licitation dans un contexte positif.
    o [[ repriseID ]] : bool�en (oui/non) indiquant si la mention d'un locuteur reprend directement son identifiant comme "Cher Crainquebille". Par d�faut non.
    o [[ autoref ]] : si l'utilisateur se mentionne lui-m�me (oui / non), cela correspond � l'utilisation de la premi�re personne. Par d�faut non.
    o [[ commentaire ]] : pour rajouter une indication libre sur l'annotation comme exprimer un doute ou une nuance.

********************
*** Commentaires ***
********************

o La pr�sentation de Mme Ludivine Crible nous a donn� l'id�e que peut-�tre la notion d'opposition et d'accord aurait d� �tre pens�e comme une dimension orthogonale � la fonction m�me. Cela donnerait de nouvelles combinaisons dont il faudrait v�rifier l'existence en corpus. Cette id�e nous �tant venue tardivement, nous n'avons pas pu la mettre en �uvre.
o Le texte "si je ne m'abuse" nous a pos� probl�me. Une solution aurait �t� d'�largir la valeur "demande de politesse" � "formules de politesse" pour l'y placer aux c�t�s de "s'il vous pla�t". Cette r�flexion arrivant apr�s les annotations, nous n'avons pas modifi� notre mod�le et l'avons plac� dans "question", m�me si cette classification ne nous satisfait pas enti�rement.
o En plus des mentions directes, "Cher Crainquebille", nous consid�rons tous les mots porteurs d'une marque de personne comme une mention, directe dans le cas des pronoms sujets et compl�ments, indirecte dans le cas des pronoms et adjectifs possessifs : on mentionne un intervenant via un de ses objets poss�d�s.

2.2 Type Text
-------------

Une portion de texte. Le type << Text >> n'est pas utilis�.

2.3 Type Signature
------------------

Le type << Signature >> indique simplement une signature de post. Elles sont automatiquement cr��es par le script de conversion de XML vers AA/AC mais l'annotateur peut en rajouter manuellement.

*******************
*** Commentaire ***
*******************

o Il aurait �t� int�ressant d'ajouter une feature [[ automatique ]] pour garder en m�moire si l'unit� de type << Signature >> avait �t� g�n�r�e automatiquement ou non.

2.4 Relation MentionOfText
--------------------------

Une relation qui relie une mention � une partie de texte. Cette relation n'est pas utilis�e.
Notre id�e �tait de pouvoir relier certaines mentions � une portion de texte concern�e mais nous avons abandonn� cette id�e car elle ne semblait pas assez pertinente.

Si on prend comme exemple le remerciement, un intervenant A sur la page de discussion remercie un intervenant B pour une action. Cette action pour laquelle B est remerci�e n'a que rarement une traduction textuelle ou celle-ci est trop diffuse pour que sa localisation soit int�ressante.

*******************
*** Commentaire ***
*******************

o Nous avons remarqu� que Glozz ne semble pas permettre de typer les deux extr�mit�s d'une relation. Nous aurions aim� pouvoir dire qu'une extr�mit� devait �tre forc�ment d'un type donn� d'unit� comme dans << Mention >> -------MentionOfText-----------> << Texte >>

2.5 Style
---------

Nous proposons un style dans le fichier talk.as pour notre mod�le d'annotation.

Nous avons jou� sur les couleurs pour distinguer les diff�rents types d'unit�s.

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
o Il ne semble pas possible de modifier le style d'un type en fonction de la valeur de ses features. On aurait pu imaginer des couleurs diff�rentes selon la [[ fonction ]] de la mention.

2.6 Conversion de XML vers AA/AC
--------------------------------

Le fichier script1.py contient le code de traduction de l'XML TEI-P5 vers un fichier corpus Glozz (AC) et un fichier annotation Glozz (AA). Ce script est un travail original.

Pour effectuer cette conversion, on d�s�rialise le fichier XML � la norme TEI-P5. Les discussions sont une suite de balises < div >. Chaque < div > poss�de une t�te < head > et une suite de < post > ou de sous < div >. Un < post > est �crit par un locuteur et contient une suite de paragraphes < p> et/ou de < list >. Une < list > poss�de � son tour des < item >.

Le script essaye d'obtenir pour chaque < post > une signature. Pour cela, il regarde � plusieurs endroits :
    o S'il existe dans le post un �l�ment dont le chemin relatif est : .//signed/ref/name (il ne regarde que le premier �l�ment correspondant � ce chemin)
    o Si rien n'est trouv� et si l'attribut [ who ] du post est renseign�, il prend la valeur de celui-ci.

Cette syst�maticit� permet de mieux comprendre l'encha�nement des discussions dans le rendu du document final Glozz. Nous utilisons les unit�s typographiques par d�faut de Glozz pour produire un document plus lisible. Un mode debug permet de rajouter des lignes dans le document produit pour encore mieux visualiser les diff�rentes parties de la page de discussion.

Nous n'avons pas utilis� l'attribut [ indentLevel ] pour cette fonctionnalit� car le r�sultat obtenu par notre m�thode - en nous fondant sur la structure de l'arbre XML - nous semblait suffisant, mais il serait plus rigoureux d'utiliser les deux, ne serait-ce que pour v�rifier.

-----------------------------------------------------------
3. Bilan de l'annotation [BIL]
-----------------------------------------------------------

Nous avons demand� � notre camarade de Master 2, Mme Silvia Federzoni, d'annoter le texte choisi, la discussion � propos de l'article sur le philosophe Friedrich Nietzsche (fichier original 15075.xml), et elle a aimablement bien voulu se pr�ter � l'exercice. Nous l'avons �galement annot� de notre c�t� pour obtenir une paire d'annotations, soit deux fichiers AA nomm�s 15075_dgx.aa et 15075_silvia.aa.

Le script2.py a �t� con�u pour traiter automatiquement les deux annotations, constitu�es d'unit�s, et en faire la comparaison.

3.1 Comptage des annotations
----------------------------

Il compte le nombre d'unit�s dans chaque annotation, en diff�renciant :
    o les unit�s typographiques qui sont g�n�r�es automatiquement
    o les unit�s de type << Signature >> qui peuvent avoir �t� g�n�r�es automatiquement ou non
    o les unit�s de type << Mention >>

3.2 Comparaison des types
-------------------------

    o Nous ne comparons automatiquement que les unit�s du type << Mention >>.
    o Les unit�s typographiques sont les m�mes, car g�n�r�es automatiquement, nous ne les comparons donc pas. 
    o Nous avons rajout� dans notre annotation deux unit�s << Signature >> que le script de transformation de XML vers AA/AC n'avait pas trouv�es, Silvia ne l'a pas fait, nous ne les comparons donc pas.

3.3 Correspondance de positions
-------------------------------

Pour savoir quoi comparer ensemble, il faut constituer des paires d'unit�s et pour cela nous utilisons la position des unit�s. Nous consid�rons qu'il existe une marge d'erreur entre les positions de deux unit�s. La s�lection des limites se faisant � la souris, de mani�re peu pr�cise, l'utilisateur peut toujours d�border d'un caract�re ou deux. Nous consid�rons ainsi deux unit�s en correspondance de positions si les diff�rences absolues entre leurs bornes de d�part et leurs bornes de fin sont inf�rieures � une pr�cision donn�e, que nous avons mis empiriquement � deux. Nous ne testons pas le contenu des cha�nes d�limit�es par les bornes car ces positions se r�f�rent � un m�me fichier de corpus. Prenons un exemple :

"J'adore"

L'utilisateur 1 annote J, l'utilisateur 2 annote J'.
La diff�rence entre les bornes de d�part est de 0.
La diff�rence entre les bornes de fin est de 1, donc inf�rieure � notre pr�cision de 2.
Donc nous consid�rons les unit�s en correspondance de positions pour cet exercice m�me si leurs contenus est diff�rent ("J" contre "J'").

Nous pouvons donc diviser les unit�s des annotations 1 et 2 en deux groupes :
    o celles en correspondance de positions, se trouvant donc dans les deux annotations,
    o celles sans correspondance de positions, se trouvant uniquement dans une des deux annotations.

On peut ensuite comparer les valeurs des features de celles en correspondance de positions.

********************
*** Commentaires ***
********************

o La pr�cision est r�glable via la variable statique Unit.PRECISION. Nous pensons qu'elle ne devrait pas exc�der trois pour ne avoir de probl�me avec deux annotations se suivant de fa�on tr�s proche comme dans "Je me".  
o Il est tr�s facile de d�velopper un mode strict qui consid�rerait toute diff�rence de bornes comme une in�galit�. Il nous a sembl� que cela n'allait pas dans le sens de l'exercice. 

3.4 Comparaison de feature
--------------------------

On peut ensuite, pour les unit�s en correspondance de positions, �valuer l'accord inter-annotateurs sur les diff�rentes features d�finies pour les unit�s. La partie bilan [BIL] dresse un tableau de nos r�sultats.

3.5 Sorties
-----------

Le script script2.py produit une sortie dans un fichier texte simple ainsi que dans un fichier Excel XLSX. Le contenu est autodescriptif, nous pr�ciserons simplement que :
    o '=' signifie un couple d'unit� en correspondance de positions et ayant la m�me valeur pour la feature consid�r�e,
    o '!' signifie un couple d'unit� en correspondance de positions n'ayant pas la m�me valeur pour la feature consid�r�e,
    o '?' signifie une unit� sans correspondance de positions dans l'autre annotation
    o DGX est le code utilis� pour d�signer les unit�s provenant de l'annotation de Damien
    o SLV est le code utilis� pour d�signer les unit�s provenant de l'annotation de Silvia

Le script script2.py produit �galement une sortie Excel si le module openpyxl est pr�sent. Cette pr�sentation reprend les informations du fichier texte mais dans une autre pr�sentation :
    o Le premier onglet d�crit les unit�s avec pour chacune son contexte dans une fen�tre de 10 caract�res avant et apr�s, dans la limite du texte disponible.
    o Le deuxi�me onglet d�crit les unit�s en correspondance de positions et dont la valeur pour la feature s�lectionn�e est �gale.
    o Le troisi�me onglet d�crit les unit�s en correspondance de positions et dont la valeur pour la feature s�lectionn�e est diff�rente.
    o Le quatri�me onglet d�crit les unit�s sans correspondance de positions.
    o Le cinqui�me onglet donne la valeur du Kappa de Cohen.
    
La valeur du Kappa de Cohen est calcul�e gr�ce � la biblioth�que NTLK si elle est disponible. Pour l'interpr�ter, nous nous fondons sur l'�chelle de Landis, J. R., Koch, G. G., The measurement of observer agreement for categorical data. Biometrics, 33, 159-174. 

3.6 R�sultats
-------------

3.6.1 Correspondance de positions
---------------------------------

Tableaux des unit�s dans chaque annotation :

    +========================+=====+=====+
    | Annotation             | DGX | SLV |
    +========================+=====+=====+
    | Unit�s typographiques  | 214 | 214 |
    +------------------------+-----+-----+
    | Unit�s << Signature >> |  47 |  45 |
    +------------------------+-----+-----+
    | Unit�s << Mention >>   |  73 |  59 |
    +========================+=====+=====+
    | Total                  | 334 | 318 |
    +========================+=====+=====+

Les unit�s typographiques �tant g�n�r�es automatiquement par le script de conversion (script1.py), il est normal qu'elles soient identiques et qu'on en compte le m�me nombre. J'ai rajout� manuellement deux << Signature >> comme indiqu� plus haut. J'ai �tiquet� 73 unit�s de type << Mention >> contre 59 pour Silvia.

Sur celles-ci, 35 sont en correspondance de positions : c'est-�-dire qu'il y a une correspondance directe entre une unit� dans mon annotation et une autre dans l'annotation de Silvia. Par contre, 62 unit�s ne sont pas en correspondance : 38 ne sont pr�sentes que dans mon annotation et 24 ne sont pr�sentes que dans l'annotation de Silvia.

Tableau r�capitulatif :

    +=======================================+=====+=====+=======+
    | Annotation                            | DGX | SLV | Total |
    +=======================================+=====+=====+=======+
    | Unit�s en correspondance de positions |  35 |  35 |    35*|
    +---------------------------------------+-----+-----+-------+
    | Unit�s sans correspondance            |  38 |  24 |    62 |
    +=======================================+=====+=====+=======+
    | Total                                 |  73 |  59 |    97 |
    +=======================================+=====+=====+=======+

* Nous ne les additionnons pas car il s'agit des m�mes unit�s.

On peut d�j� voir dans ces chiffres un niveau d'accord entre les annotateurs sur la d�finition m�me des unit�s � �tiqueter. Sur les 97 unit�s d�finies par les deux annotateurs, seulement 35 sont communes soit 36%.

En regardant les textes des diff�rentes unit�s sans correspondance, il s'agit toujours de pronoms ou d'identifiants d'utilisateurs, donc des unit�s qui sont valides, mais qui n'ont pas �t� rep�r�es par un des deux annotateurs. De plus, il y a s�rement des unit�s qui n'ont �t� rep�r�es par aucun des annotateurs et qui sont donc parfaitement invisibles pour nos traitements.

3.6.2 Accord inter-annotateurs pour la feature fonction
-------------------------------------------------------

Nous avons d'abord test� l'accord inter-annotateurs sur les 35 unit�s en correspondance pour la feature [[ fonction ]]. Cette feature indique la fonction de la mention.

Nous constatons que 19 unit�s sur 35, soit 54%, ont la m�me valeur pour leur feature [[ fonction ]]. Il reste 16 unit�s n'ayant pas la m�me valeur. Nous avons un Kappa de Cohen de 0.40. Selon l'�chelle de Landis et Koch, nous sommes � l'extr�me limite de la plage d�finissant un accord faible (de 0.21 � 0.40) pour les unit�s en correspondance de positions.

Les r�sultats sont consign�s dans le fichier fonction_diff.txt.

3.6.3 Accord inter-annotateurs pour la feature autoref
------------------------------------------------------

Nous avons ensuite test� l'accord inter-annotateurs sur les 35 unit�s en correspondance pour la feature [[ autoref ]]. Cette feature indique si l'utilisateur s'implique dans la mention, qu'il s'auto-implique, cela se traduisant par l'utilisation de la premi�re personne (je, me, mon, nous, nos).

Nous constations que 35 unit�s sur 35, soit 100%, ont la m�me valeur pour leur feature [[ autoref ]]. Nous avons donc un Kappa de Cohen de 1.0. Selon l'�chelle de Landis et Koch, nous avons un accord parfait pour les unit�s en correspondance de positions.

Les r�sultats sont consign�s dans le fichier autoref_diff.txt.

3.6.4 Accord inter-annotateurs pour l'ensemble des features
-----------------------------------------------------------

Au lieu de consid�rer l'accord feature par feature, on peut �galement consid�rer l'accord "total", c'est-�-dire qu'il y a accord sur deux unit�s entre deux annotateurs si et seulement si toutes les valeurs des features des deux unit�s sont les m�mes.

Nous constatons que 12 unit�s sur 35, soit 34%, ont les m�mes valeurs pour toutes les features. Nous avons un Kappa de Cohen de 0.30. Selon l'�chelle de Landis et Koch, nous acons un accord inter-annotateurs faible. Pour calculer ce Kappa, nous construisons une valeur en agr�geant toutes les valeurs des features par simple concat�nation.

Les r�sultats sont consign�s dans le fichier all_diff.txt.

-----------------------------------------------------------

                           [FIN]
