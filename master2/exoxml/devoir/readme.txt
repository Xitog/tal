
                  ____  _
                 / __ \| |                 
                | |  \/| |  ___   ____ ____
                | | __ | | / _ \ |_  /|_  /
                | |_\ \| || (_) | / /  / / 
                 \____/|_| \___/ /___|/___|


                             Titre du document : readme.txt
                                    Auteur : Damien Gouteux
                                    Version : 2019-01-19-2a
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

Apr�s une br�ve pr�sentation du contenu de l'archive, nous pr�sentons notre mod�le d'annotation.Nous dressons ensuite un bilan de l'annotation avant de terminer par des notes sur le code.

Rechercher le code court entre crochets pour acc�der directement � une partie.

Ce document utilise les conventions suivantes :
    o << Mention >> pour un type d'unit�s dans un mod�le d'annotation.
    o < div > pour une balise XML.
    o [ attr ] pour un attribut de balise XML. 
    
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
| kappa.py       | Script Python         | Calcul de Kappa bas� sur NLTK             |
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

L'unit� centrale de notre annotation est le type << Mention >>.
Il poss�de 5 attributs :
    o fonction est une �num�ration de 12 valeurs possibles. 
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
    o contexte : le contexte g�n�ral de la mention qui apporte une nuance � la fonction. 
      � choisir entre trois contextes larges :
        + positif (laudateur)
        + neutre
        + n�gatif (ironie, sarcasme, agressif)
      Une f�licitation dans un contexte ironique n'a pas la m�me valeur s�mantique qu'une f�licitation dans un contexte positif.
    o repriseID : bool�en (oui/non) indiquant si la mention d'un locuteur reprend directement son identifiant comme "Cher Crainquebille". Par d�faut non.
    o autoref : si l'utilisateur se mentionne lui m�me (oui / non), cela correspond � l'utilisation de la premi�re personne. Par d�faut non.
    o commentaire : pour rajouter une indication libre sur l'annotation comme exprimer un doute, une nuance.

2.2 Type Text
-------------

Une portion de texte. Le type << Text >> n'est pas utilis�.

2.3 Type Signature
------------------

Le type << Signature >> indique simplement une signature de post. Elles sont automatiquement cr��s par le script de conversion XML => AA/AC mais l'annotateur peut en rajouter manuellement.

2.4 Relation MentionOfText
--------------------------

Une relation qui relie une mention � une partie de texte. Cette relation n'est pas utilis�e.
Notre id�e �tait de pouvoir relier certaines mentions � une portion de texte concern�e mais nous avons abandonn� cette id�e car elle ne semblait pas assez pertinente.

Par exemple pour le remerciement, un intervenant A sur la page de discussion remercie un intervenant B pour une action. Cette action pour laquelle B est remerci� n'a que rarement une traduction textuelle ou celle-ci est trop diffuse pour �tre int�ressante.

*******************
*** Commentaire ***
*******************

Nous avons remarqu� que Glozz ne semble pas permettre de typer les deux extr�mit�s d'une relation. Nous aurions aim� pouvoir dire qu'une extr�mit� devait �tre forc�ment un type de mention donn�. Ex : << Mention >> -------MentionOfText-----------> << Texte >>

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

*******************
*** Commentaire ***
*******************

o Il ne semble pas possible de modifier la couleur de la bordure d'un type, ni sa police.
o Il ne semble pas possible de modifier le style d'un type en fonction de la valeur de ses features. On aurait pu imaginer des couleurs diff�rentes selon la fonction de la mention.

-----------------------------------------------------------
3. Bilan de l'annotation [BIL]
-----------------------------------------------------------

TODO

-----------------------------------------------------------
4. Notes sur le code [COD]
-----------------------------------------------------------

4.1 script1.py
--------------

Ce fichier contient le code de traduction de l'XML TEI-P5 vers AC + AA.

Pour cela, on d�s�rialise le fichier XML � la norme TEI-P5. Les discussions sont une suite de balises < div >. Chaque < div > poss�de une t�te < head > et une suite de < post > ou de sous < div >. Un < post > est �crit par un locuteur et contient une suite de paragraphes < p> et/ou de < list >. Une < list > poss�de � son tour des < item >.

Le script essaye d'obtenir pour chaque < post > une signature. Pour cela, il regarde � plusieurs endroits :
    o S'il existe dans le post un �l�ment dont le chemin relatif est : .//signed/ref/name (il ne regarde que le premier �l�ment correspondant � ce chemin)
    o Si rien n'est trouv� et si l'attribut [ who ] du post est renseign�, il prend la valeur de celui-ci.

Cette syst�maticit� permet de mieux comprendre l'encha�nement des discussions. Un mode debug permet de rajouter des lignes dans le document produit pour Glozz et visualiser mieux les diff�rentes parties de la page de discussion.

Nous avons pas utilis� l'attribut indentLevel pour cette fonctionnalit� car le r�sultat obtenu par notre m�thode - en nous basant sur la structure de l'arbre XML - nous semblait suffisant, mais ce serait plus rigoureux, ne serait-ce que pour v�rifier.

4.2 script.py
-------------

TODO

4.3 kappa.py
------------

TODO

4.4 log.py
----------

Une classe statique simple pour logguer les diff�rentes actions du programme.

Une �volution possible serait d'en faire une classe non statique pour avoir plusieurs instances de logs qui loggueraient des choses diff�rentes, voir sur des flux diff�rents (sortie console, fichier).

�tant tr�s p�riph�rique, nous l'avons volontairement laiss�e tr�s simple.
