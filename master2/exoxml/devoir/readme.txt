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

1. Pr�sentation du contenu de l'archive [ARC]
2. Mod�le d'annotation propos� [MOD]
3. Bilan de l'annotation [BIL]

Rechercher le code court entre crochets pour acc�der directement � une partie.

-----------------------------------------------------------
1. Pr�sentation du contenu de l'archive [ARC]
-----------------------------------------------------------

Nous pr�sentons dans cette partie le contenu de l'archive livr�e sous la forme d'un tableau :

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
2. Mod�le d'annotation propos� [MOD]
-----------------------------------------------------------

2.1 Type Mention
----------------

L'unit� centrale de notre annotation est le type Mention.
Il poss�de 5 attributs :
- fonction est une �num�ration de 12 valeurs possibles. Nous fournissons de nombreuses possibilit�s � l'annotateur pour qu'il puisse faire son choix. Les 12 valeurs sont :
    - autorisation
    - expression d'accord
    - expression de d�saccord
    - demande d'intervention
    - demande de pardon
    - demande de politesse
    - question (d�faut)
    - citation
    - f�licitation
    - remerciement
    - salutation
    - affirmation
- contexte : le contexte g�n�ral de la mention � choisir entre :
    - positif (laudateur)
    - neutre
    - n�gatif (ironie, sarcasme, agressif)
- repriseID : bool�en (oui/non) indiquant si la mention reprend directement l'id de l'utilisateur. Par d�faut non.
- autoref : si l'utilisateur se mentionne lui m�me (oui / non), cela correspond � l'utilisateur de la premi�re personne. Par d�faut non.
- commentaire : pour rajouter une indication libre sur l'annotation.

2.2 Text

Un texte. Ce type n'est pas utilis�.

2.3 Signature

Le type signature indique simplement une signature de post. Elles sont automatiquement cr��s par le script de conversion XML => AA/AC mais l'annotateur peut en rajouter.

    <relations>
        <type name="MentionOfText" oriented="true" groups="mention">
            <featureSet/>
        </type>
    </relations>

-----------------------------------------------------------
3. Bilan de l'annotation [BIL]
-----------------------------------------------------------

