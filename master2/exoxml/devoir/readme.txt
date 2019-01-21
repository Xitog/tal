
                  ____  _
                 / __ \| |                 
                | |  \/| |  ___   ____ ____
                | | __ | | / _ \ |_  /|_  /
                | |_\ \| || (_) | / /  / / 
                 \____/|_| \___/ /___|/___|


                             Titre du document : readme.txt
                                    Auteur : Damien Gouteux
                                    Version : 2019-01-21-3a
                                    Licence : CC3.0BY-SA-NC


           Grazie mille � Silvia pour la seconde annotation

-----------------------------------------------------------
Plan
-----------------------------------------------------------

1. Pr�sentation du contenu de l'archive [ARC]
2. Mod�le d'annotation propos� [ANN]
3. Bilan de l'annotation [BIL]
4. Notes sur le code [COD]

Ce document pr�sente le travail effectu� pour l'UE traitant de XML et Glozz en Master 2 LITL.

Apr�s une br�ve pr�sentation du contenu de l'archive, nous pr�sentons notre mod�le d'annotation. Nous dressons ensuite un bilan de l'annotation avant de terminer par des notes sur le code.

Rechercher le code court entre crochets pour acc�der directement � une partie.

Ce document utilise les conventions suivantes :
    o << Mention >> pour un type d'unit�s dans un mod�le d'annotation Glozz.
    o [[ feature ]] pour une feature d'une unit� Glozz.
    o < div > pour une balise XML.
    o [ attr ] pour un attribut de balise XML.
    o les guillemets doubles " " signalent un exemple.

-----------------------------------------------------------
1. Pr�sentation du contenu de l'archive [ARC]
-----------------------------------------------------------

Nous pr�sentons dans cette partie le contenu de l'archive livr�e sous la forme d'un tableau :

+================+=======================+===========================================+
| Nom du fichier | Type                  | Contenu                                   |
+================+=======================+===========================================+
| readme.txt     | Fichier texte         | Ce fichier                                |
+----------------+-----------------------+-------------------------------------------+
| log.py         | Script Python         | Simple classe statique de logging         |
+----------------+-----------------------+-------------------------------------------+
| kappa.py       | Script Python         | Calcul de Kappa en utilisant NLTK         |
+----------------+-----------------------+-------------------------------------------+
| script1.py     | Script Python         | Traduction XML TEI-P5 => GLOZZ AC + AA    |
+----------------+-----------------------+-------------------------------------------+
| script2.py     | Script Python         | Comparaison de deux annotations GLOZZ AA  |
+----------------+-----------------------+-------------------------------------------+
| talk.aam       | Mod�le d'annotation   | Mod�le d'annotation pour Glozz AAM        |
+----------------+-----------------------+-------------------------------------------+
| talk.as        | Mod�le de styles      | Mod�le de styles pour mod�le d'annotation |
+----------------+-----------------------+-------------------------------------------+
| 15075_dgx.aa   | Annotations de Damien | Annotations Glozz faites par Damien G.    |
+----------------+-----------------------+-------------------------------------------+
| 15075_slv.aa   | Annotations de Silvia | Annotations Glozz faites par Silvia F.    |
+----------------+-----------------------+-------------------------------------------+
| data (dossier) | Fichiers AA + AC      | Tous les fichiers XML traduits en AA + AC |
+----------------+-----------------------+-------------------------------------------+

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
            - le locuteur pose une question � une autre
        + citation
            - le locuteur en cite un autre
        + f�licitation
            - le locuteur en f�licite un autre
        + remerciement
            - le locuteur en remercie un autre
        + salutation
            - le locuteur salut un autre
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
    o [[ commentaire ]] : pour rajouter une indication libre sur l'annotation comme exprimer un doute, une nuance.

2.2 Type Text
-------------

Une portion de texte. Le type << Text >> n'est pas utilis�.

2.3 Type Signature
------------------

Le type << Signature >> indique simplement une signature de post. Elles sont automatiquement cr��es par le script de conversion XML => AA/AC mais l'annotateur peut en rajouter manuellement.

*******************
*** Commentaire ***
*******************

o Il aurait �t� int�ressant d'ajouter une feature [[ automatique ]] pour garder en m�moire si la balise avait �t� g�n�r�e automatiquement ou non.

2.4 Relation MentionOfText
--------------------------

Une relation qui relie une mention � une partie de texte. Cette relation n'est pas utilis�e.
Notre id�e �tait de pouvoir relier certaines mentions � une portion de texte concern�e mais nous avons abandonn� cette id�e car elle ne semblait pas assez pertinente.

Par exemple pour le remerciement, un intervenant A sur la page de discussion remercie un intervenant B pour une action. Cette action pour laquelle B est remerci�e n'a que rarement une traduction textuelle ou celle-ci est trop diffuse pour �tre int�ressante.

*******************
*** Commentaire ***
*******************

o Nous avons remarqu� que Glozz ne semble pas permettre de typer les deux extr�mit�s d'une relation. Nous aurions aim� pouvoir dire qu'une extr�mit� devait �tre forc�ment un type donn� d'unit� comme dans << Mention >> -------MentionOfText-----------> << Texte >>

2.5 Style
---------

Nous proposons un style dans le fichier talk.as pour notre mod�le d'annotation.

Nous avons jou� sur les couleurs pour distinguer les diff�rents types.

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
o Il ne semble pas possible de modifier le style d'un type en fonction de la valeur de ses features. On aurait pu imaginer des couleurs diff�rentes selon la fonction de la mention.

-----------------------------------------------------------
3. Bilan de l'annotation [BIL]
-----------------------------------------------------------

Nous avons demand� � notre camarade Silvia Federzoni d'annoter le texte choisi, la discussion � propos de l'article sur le philosophe Friedrich Nietzsche (fichier original 15075.xml), et elle a aimablement bien voulu se pr�ter � l'exercice. Nous l'avons annot� de notre c�t� pour obtenir une paire d'annotations, soit deux fichiers AA.

Le script2.py a �t� con�u pour traiter automatiquement les deux annotations, constitu�es d'unit�s, et en faire la comparaison.

Il compte le nombre d'annotations dans chaque jeu d'annotation, en diff�renciant :
- les annotations de mise en page qui sont g�n�r�es automatiquement
- les annotations de type << Signature >> qui peuvent avoir �t� g�n�r�es automatiquement ou non
- les annotations de type << Mention >>

Nous ne comparons que les annotations du type << Mention >>.

Nous consid�rons qu'il existe une marge d'erreur entre deux annotations. La s�lection des limites se faisant � la souris, l'utilisateur peut toujours d�border d'un caract�re ou deux. Nous consid�rons ainsi deux annotations �gales si les diff�rences absolues entre les bornes start et les bornes end sont inf�rieures � une pr�cision donn�e, que nous avons mis empiriquement � deux. Nous ne testons les cha�nes d�limit�es par les bornes car les bornes se r�f�rent au m�me corpus. Prenons un exemple :

"J'adore"

L'utilisateur 1 annote J, l'utilisateur 2 annote J'.
La diff�rence entre les bornes de d�part est de 0.
La diff�rence entre les bornes de fin est de 1, donc inf�rieure � notre pr�cision de 2.
Donc nous consid�rons les annotations comme �gales pour cet exercice mais si leurs contenus est diff�rent ("J" contre "J'").

********************
*** Commentaires ***
********************

o La pr�cision est r�glable via la variable statique Unit.PRECISION. Nous pensons qu'elle ne devrait pas exc�der trois pour ne avoir de probl�me avec deux annotations se suivant de fa�on tr�s proche comme dans "Je me".  
o Il est tr�s facile de d�velopper un mode strict qui consid�rerait toute diff�rence de borne comme une in�galit�. Il nous a sembl� que cela n'allait pas dans le sens de l'exercice. 

-----------------------------------------------------------
4. Notes sur le code [COD]
-----------------------------------------------------------

Notre code d�pend des modules suivants :
    o LXML (obligatoire)
    o NLTK (seulement pour le calcul du kappa, optionnel)
    o openpyxl (seulement pour la sortie Excel, optionnel)

Il a �t� ex�cut� avec succ�s sous Windows avec Python 3.6.1 en version 32 bits et Python 3.7.0 en version 64 bits.

Les scripts utilisent la PEP 498, formatted string literals introduite en version 3.6.0. Ils ne fonctionneront donc pas avec une version ant�rieure.

Nous n'avons pas cherch� � optimiser le code.

4.1 script1.py
--------------

Ce fichier contient le code de traduction de l'XML TEI-P5 vers AC + AA.

Pour cela, on d�s�rialise le fichier XML � la norme TEI-P5. Les discussions sont une suite de balises < div >. Chaque < div > poss�de une t�te < head > et une suite de < post > ou de sous < div >. Un < post > est �crit par un locuteur et contient une suite de paragraphes < p> et/ou de < list >. Une < list > poss�de � son tour des < item >.

Le script essaye d'obtenir pour chaque < post > une signature. Pour cela, il regarde � plusieurs endroits :
    o S'il existe dans le post un �l�ment dont le chemin relatif est : .//signed/ref/name (il ne regarde que le premier �l�ment correspondant � ce chemin)
    o Si rien n'est trouv� et si l'attribut [ who ] du post est renseign�, il prend la valeur de celui-ci.

Cette syst�maticit� permet de mieux comprendre l'encha�nement des discussions. Un mode debug permet de rajouter des lignes dans le document produit pour Glozz et visualiser mieux les diff�rentes parties de la page de discussion.

Nous n'avons pas utilis� l'attribut [ indentLevel ] pour cette fonctionnalit� car le r�sultat obtenu par notre m�thode - en nous basant sur la structure de l'arbre XML - nous semblait suffisant, mais ce serait plus rigoureux, ne serait-ce que pour v�rifier.

4.2 script2.py
--------------

TODO

4.3 kappa.py
------------

TODO

4.4 log.py
----------

Une classe statique simple pour logguer les diff�rentes actions du programme.

Une �volution possible serait d'en faire une classe non statique pour avoir plusieurs instances de logs qui loggueraient des choses diff�rentes, voir sur des flux diff�rents (sortie console, fichier).

�tant tr�s p�riph�rique, nous l'avons volontairement laiss�e tr�s simple.
