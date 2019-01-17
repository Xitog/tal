                  ____  _
                 / __ \| |                 
                | |  \/| |  ___   ____ ____
                | | __ | | / _ \ |_  /|_  /
                | |_\ \| || (_) | / /  / / 
                 \____/|_| \___/ /___|/___|


                             Titre du document : readme.txt
                                    Auteur : Damien Gouteux
                                     Version : 2019-01-19-1

-----------------------------------------------------------
Plan
-----------------------------------------------------------

1. Présentation du contenu de l'archive [ARC]
2. Modèle d'annotation proposé [MOD]
3. Bilan de l'annotation [BIL]

Rechercher le code court entre crochets pour accéder directement à une partie.

-----------------------------------------------------------
1. Présentation du contenu de l'archive [ARC]
-----------------------------------------------------------

Nous présentons dans cette partie le contenu de l'archive livrée sous la forme d'un tableau :

+================+===============+========================+
| Nom du fichier | Type          | Contenu                |
+================+===============+========================+
| readme.txt     | Fichier texte | Ce fichier             |
+----------------+---------------+------------------------+
| script1.py     | Script Python |                        |
+----------------+---------------+------------------------+
| script2.py     | Script Python |                        |
+----------------+---------------+------------------------+

-----------------------------------------------------------
2. Modèle d'annotation proposé [MOD]
-----------------------------------------------------------

2.1 Type Mention
----------------

L'unité centrale de notre annotation est le type Mention.
Il possède 5 attributs :
- fonction est une énumération de 12 valeurs possibles. Nous fournissons de nombreuses possibilités à l'annotateur pour qu'il puisse faire son choix. Les 12 valeurs sont :
    - autorisation
    - expression d'accord
    - expression de désaccord
    - demande d'intervention
    - demande de pardon
    - demande de politesse
    - question (défaut)
    - citation
    - félicitation
    - remerciement
    - salutation
    - affirmation
- contexte : le contexte général de la mention à choisir entre :
    - positif (laudateur)
    - neutre
    - négatif (ironie, sarcasme, agressif)
- repriseID : booléen (oui/non) indiquant si la mention reprend directement l'id de l'utilisateur. Par défaut non.
- autoref : si l'utilisateur se mentionne lui même (oui / non), cela correspond à l'utilisateur de la première personne. Par défaut non.
- commentaire : pour rajouter une indication libre sur l'annotation.

2.2 Text

Un texte. Ce type n'est pas utilisé.

2.3 Signature

Le type signature indique simplement une signature de post. Elles sont automatiquement créés par le script de conversion XML => AA/AC mais l'annotateur peut en rajouter.

    <relations>
        <type name="MentionOfText" oriented="true" groups="mention">
            <featureSet/>
        </type>
    </relations>

-----------------------------------------------------------
3. Bilan de l'annotation [BIL]
-----------------------------------------------------------

