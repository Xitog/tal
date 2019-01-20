
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


           Grazie mille à Silvia pour la seconde annotation

-----------------------------------------------------------
Plan
-----------------------------------------------------------

1. Présentation du contenu de l'archive [ARC]
2. Modèle d'annotation proposé [ANN]
3. Bilan de l'annotation [BIL]
4. Notes sur le code [COD]

Ce document présente le travail effectué pour l'UE traitant de XML et Glozz en Master 2 LITL.

Après une brève présentation du contenu de l'archive, nous présentons notre modèle d'annotation. Nous dressons ensuite un bilan de l'annotation avant de terminer par des notes sur le code.

Rechercher le code court entre crochets pour accéder directement à une partie.

Ce document utilise les conventions suivantes :
    o << Mention >> pour un type d'unités dans un modèle d'annotation.
    o < div > pour une balise XML.
    o [ attr ] pour un attribut de balise XML. 
    
-----------------------------------------------------------
1. Présentation du contenu de l'archive [ARC]
-----------------------------------------------------------

Nous présentons dans cette partie le contenu de l'archive livrée sous la forme d'un tableau :

+================+=======================+===========================================+
| Nom du fichier | Type                  | Contenu                                   |
+================+=======================+===========================================+
| readme.txt     | Fichier texte         | Ce fichier                                |
+----------------+-----------------------+-------------------------------------------+
| log.py         | Script Python         | Simple classe statique de logging         |
+----------------+-----------------------+-------------------------------------------+
| kappa.py       | Script Python         | Calcul de Kappa basé sur NLTK             |
+----------------+-----------------------+-------------------------------------------+
| script1.py     | Script Python         | Traduction XML TEI-P5 => GLOZZ AC + AA    |
+----------------+-----------------------+-------------------------------------------+
| script2.py     | Script Python         | Comparaison de deux annotations GLOZZ AA  |
+----------------+-----------------------+-------------------------------------------+
| talk.aam       | Modèle d'annotation   | Modèle d'annotation pour Glozz AAM        |
+----------------+-----------------------+-------------------------------------------+
| talk.as        | Modèle de styles      | Modèle de styles pour modèle d'annotation |
+----------------+-----------------------+-------------------------------------------+
| 15075_dgx.aa   | Annotations de Damien | Annotations Glozz faites par Damien G.    |
+----------------+-----------------------+-------------------------------------------+
| 15075_slv.aa   | Annotations de Silvia | Annotations Glozz faites par Silvia F.    |
+----------------+-----------------------+-------------------------------------------+
| data (dossier) | Fichiers AA + AC      | Tous les fichiers XML traduits en AA + AC |
+----------------+-----------------------+-------------------------------------------+

-----------------------------------------------------------
2. Modèle d'annotation proposé [ANN]
-----------------------------------------------------------

2.1 Type Mention
----------------

L'unité centrale de notre annotation est le type << Mention >>.
Il possède 5 attributs :
    o fonction est une énumération de 12 valeurs possibles. 
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
            - le locuteur pose une question à une autre
        + citation
            - le locuteur en cite un autre
        + félicitation
            - le locuteur en félicite un autre
        + remerciement
            - le locuteur en remercie un autre
        + salutation
            - le locuteur salut un autre
        + affirmation
            - le locuteur affirme une information
    o contexte : le contexte général de la mention qui apporte une nuance à la fonction. 
      À choisir entre trois contextes larges :
        + positif (laudateur)
        + neutre
        + négatif (ironie, sarcasme, agressif)
      Une félicitation dans un contexte ironique n'a pas la même valeur sémantique qu'une félicitation dans un contexte positif.
    o repriseID : booléen (oui/non) indiquant si la mention d'un locuteur reprend directement son identifiant comme "Cher Crainquebille". Par défaut non.
    o autoref : si l'utilisateur se mentionne lui-même (oui / non), cela correspond à l'utilisation de la première personne. Par défaut non.
    o commentaire : pour rajouter une indication libre sur l'annotation comme exprimer un doute, une nuance.

2.2 Type Text
-------------

Une portion de texte. Le type << Text >> n'est pas utilisé.

2.3 Type Signature
------------------

Le type << Signature >> indique simplement une signature de post. Elles sont automatiquement créées par le script de conversion XML => AA/AC mais l'annotateur peut en rajouter manuellement.

*******************
*** Commentaire ***
*******************

Il aurait été intéressant d'ajouter un attribut appelé automatique pour garder en mémoire si la balise avait été générée automatiquement ou non.

2.4 Relation MentionOfText
--------------------------

Une relation qui relie une mention à une partie de texte. Cette relation n'est pas utilisée.
Notre idée était de pouvoir relier certaines mentions à une portion de texte concernée mais nous avons abandonné cette idée car elle ne semblait pas assez pertinente.

Par exemple pour le remerciement, un intervenant A sur la page de discussion remercie un intervenant B pour une action. Cette action pour laquelle B est remerciée n'a que rarement une traduction textuelle ou celle-ci est trop diffuse pour être intéressante.

*******************
*** Commentaire ***
*******************

Nous avons remarqué que Glozz ne semble pas permettre de typer les deux extrémités d'une relation. Nous aurions aimé pouvoir dire qu'une extrémité devait être forcément un type de mention donné. Ex : << Mention >> -------MentionOfText-----------> << Texte >>

2.5 Style
---------

Nous proposons un style dans le fichier talk.as pour notre modèle d'annotation.

Nous avons joué sur les couleurs pour distinguer les différents types.

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
o Il ne semble pas possible de modifier le style d'un type en fonction de la valeur de ses features. On aurait pu imaginer des couleurs différentes selon la fonction de la mention.

-----------------------------------------------------------
3. Bilan de l'annotation [BIL]
-----------------------------------------------------------

Nous avons demandé à notre camarade Silvia Federzoni d'annoter le texte choisi, la discussion à propos de l'article sur le philosophe Friedrich Nietzsche (fichier original 15075.xml), et elle a aimablement bien voulu se prêter à l'exercice. Nous l'avons annoté de notre côté pour également pour obtenir une paire d'annotation (fichiers AA).

Le script2.py a été conçu pour traiter automatiquement deux annotations, constituées d'unités, et en faire la comparaison.

TODO

-----------------------------------------------------------
4. Notes sur le code [COD]
-----------------------------------------------------------

Notre code dépend des modules suivants :
    o LXML
    o NLTK (seulement pour le calcul du kappa)
    o openpyxl (seulement pour la sortie Excel)
Il a été compilé avec succès sous Windows avec Python 3.6 en version 32 bits.

4.1 script1.py
--------------

Ce fichier contient le code de traduction de l'XML TEI-P5 vers AC + AA.

Pour cela, on désérialise le fichier XML à la norme TEI-P5. Les discussions sont une suite de balises < div >. Chaque < div > possède une tête < head > et une suite de < post > ou de sous < div >. Un < post > est écrit par un locuteur et contient une suite de paragraphes < p> et/ou de < list >. Une < list > possède à son tour des < item >.

Le script essaye d'obtenir pour chaque < post > une signature. Pour cela, il regarde à plusieurs endroits :
    o S'il existe dans le post un élément dont le chemin relatif est : .//signed/ref/name (il ne regarde que le premier élément correspondant à ce chemin)
    o Si rien n'est trouvé et si l'attribut [ who ] du post est renseigné, il prend la valeur de celui-ci.

Cette systématicité permet de mieux comprendre l'enchaînement des discussions. Un mode debug permet de rajouter des lignes dans le document produit pour Glozz et visualiser mieux les différentes parties de la page de discussion.

Nous n'avons pas utilisé l'attribut [ indentLevel ] pour cette fonctionnalité car le résultat obtenu par notre méthode - en nous basant sur la structure de l'arbre XML - nous semblait suffisant, mais ce serait plus rigoureux, ne serait-ce que pour vérifier.

4.2 script2.py
--------------

TODO

4.3 kappa.py
------------

TODO

4.4 log.py
----------

Une classe statique simple pour logguer les différentes actions du programme.

Une évolution possible serait d'en faire une classe non statique pour avoir plusieurs instances de logs qui loggueraient des choses différentes, voir sur des flux différents (sortie console, fichier).

Étant très périphérique, nous l'avons volontairement laissée très simple.
