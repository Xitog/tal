package saxo;

import org.xml.sax.helpers.DefaultHandler;
import org.xml.sax.*;
import javax.xml.parsers.*;
import java.io.File;
import java.util.*;

/**
 * Classe pour parser un extrait de GLAWI au format XML.
 * Cette classe propose une fonction main qui fait le travail sur GLAWI et le parsing SAX
 * Master 2 LITL Université Jean Jaurès
 * @author Damien Gouteux
 */
class DGXHandler extends DefaultHandler {
    
    protected ArrayList<String> nomenclature;
    protected HashMap<String, Integer> pos;
    protected HashMap<String, Integer> lexMarks;
    protected HashMap<String, Integer> domains;
    protected boolean inTitle;
    
    /**
     * Constructeur
     */
    public DGXHandler() {
        super();
        this.nomenclature = new ArrayList<String>();
        this.pos = new HashMap<String, Integer>();
        this.lexMarks = new HashMap<String, Integer>();
        this.domains = new HashMap<String, Integer>();
        this.inTitle = false;
    }
    
    /**
     * La méthode startElement est appelée à chaque balise ouvrante.
     * Le texte entre balise ouvrante et balise fermante est gérée par la méthode characters
     * @param uri l'uri de l'élément
     * @param localName le nom local (vide)
     * @param qName le nom de la balise
     * @param attrs les attributs (on interroge avec getValue)
     * @see DGXHandler#characters
     */
    public void startElement(String uri, String localName, String qName, Attributes attrs) {
        //System.out.println(qName);
        int val;
        String key;
        String value;
        switch (qName) {
            case "title":
                this.inTitle = true;
                break;
            case "pos":
                key = attrs.getValue("type");
                val = 1;
                if (this.pos.containsKey(key)) {
                    val = val + this.pos.get(key);
                }
                this.pos.put(key, val); 
                break;
            case "label":
                key = attrs.getValue("type");
                String typ = attrs.getValue("type");
                switch (typ) {
                    case "sem":
                        value = attrs.getValue("value");
                        val = 1;
                        if (this.lexMarks.containsKey(value)) {
                            val = val + this.lexMarks.get(value);
                        }
                        this.lexMarks.put(value, val); 
                        break;
                    case "domain":
                        value = attrs.getValue("value");
                        val = 1;
                        if (this.domains.containsKey(value)) {
                            val = val + this.domains.get(value);
                        }
                        this.domains.put(value, val);
                        break;
                }
        }
    }
    
    /**
     * La méthode endElement est appelée à chaque balise fermante.
     * @param uri l'uri de l'élément
     * @param localName le nom local (vide)
     * @param qName le nom de la balise
     */
    public void endElement(String uri, String localName, String qName) {
        if (qName.equals("title")) {
            this.inTitle = false;
        }
    }
    
    /**
     * La méthode characters gère ce qui est entre la balise ouvrante et la balise fermante.
     * Pour le caster en String, on peut utiliser le constructeur qui prend les mêmes paramètres.
     * StringBuffer serait mieux.
     * @param caracteres un tableau de tous les chars
     * @param debut début du contenu de la balise
     * @param longueur longueur du contenu de la balise
     */
    public void characters(char[] caracteres, int debut, int longueur) {
        if (this.inTitle) {
            String donnees = new String(caracteres, debut, longueur);
            this.nomenclature.add(donnees);
        }
    }
    
    /**
     *
     */
    public ArrayList<String> getTitles() {
        return this.nomenclature;
    }
    
    /**
     *
     */
    public HashMap<String, Integer> getPos() {
        return this.pos;
    }
    
    /**
     *
     */
    public HashMap<String, Integer> getLexicalMarks() {
        return this.lexMarks;
    }
    
    /**
     *
     */
    public HashMap<String, Integer> getDomains() {
        return this.domains;
    }
    
    /**
     *
     */
    public static void main(String[] args) {
        //-------------------------------------------------
        // Parcours de l'extrait de GLAWI
        //-------------------------------------------------
        DGXHandler handler = new DGXHandler();
        File fileToParse = new File ("glawiWork_1.xml");
        
        SAXParserFactory spf = SAXParserFactory.newInstance();

        try {
            SAXParser saxParser = spf.newSAXParser();
            saxParser.parse(fileToParse, handler);
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        //-------------------------------------------------
        // Afficher les nomenclature (= les entrées)
        //-------------------------------------------------
        System.out.println("\nNomenclature\n");
        for(String s : handler.nomenclature) {
            System.out.println(s);
        }
        
        //-------------------------------------------------
        // Afficher la table de fréquences des parties du discours
        //-------------------------------------------------
        System.out.println("\nTable of frequencies\n");
        Set<Map.Entry<String, Integer>> set = handler.getPos().entrySet();
        Iterator<Map.Entry<String, Integer>> iterator = set.iterator();
        while(iterator.hasNext()) {
            Map.Entry<String, Integer> entry = iterator.next();
            System.out.println("Key = " + entry.getKey() + " & Value = " + String.valueOf(entry.getValue()));
        }
        
        //-------------------------------------------------
        // Afficher la table de fréquences des marques lexicographiques
        //-------------------------------------------------
        System.out.println("\nTable of lexical marks\n");
        set = handler.getLexicalMarks().entrySet();
        iterator = set.iterator();
        while(iterator.hasNext()) {
            Map.Entry<String, Integer> entry = iterator.next();
            System.out.println("Key = " + entry.getKey() + " & Value = " + String.valueOf(entry.getValue()));
        }
        
        //-------------------------------------------------
        // Afficher les 5 domaines les plus fréquents
        //-------------------------------------------------
        // [1] Méthode une
        // Le problème est qu'on peut avoir plusieurs domaines avec le même nombre
        // d'éléments. Dans mon fichier texte, beaucoup n'en ont qu'un...
        // Or, si on veut les plus fréquents, il faut éliciter tous les domaines pour
        // un nombre d'éléments donnés.
        System.out.println("\nFive most frequent domains\n");
        ArrayList<Map.Entry<String,Integer>> list = new ArrayList<>(handler.getDomains().entrySet());
        list.sort(Map.Entry.comparingByValue());
        ListIterator<Map.Entry<String, Integer>> itelist = list.listIterator(list.size());
        int nb = 0;
        while (nb < 5 && itelist.hasPrevious()) {
            Map.Entry<String, Integer> entry = itelist.previous();
            System.out.println("Key = " + entry.getKey() + " & Value = " + String.valueOf(entry.getValue()));
            nb += 1;
        }
        
        // [2] Méthode deux
        // On va faire différemment donc : on repère la plus grande valeur
        System.out.println("\nFive most frequent domains, take 2\n");
        int old_max = -1;
        int max = 0; // pour remplir la condition du while la première fois
        nb = 0;
        set = handler.getDomains().entrySet();
        while (nb < 5 && max != -1) {
            System.out.println(String.valueOf(nb + 1) + "]=====================================");
            max = -1;
            iterator = set.iterator();
            while(iterator.hasNext()) {
                Map.Entry<String, Integer> entry = iterator.next();
                // Donc, on a un nouveau max si :
                // max < value < old_max
                // ou
                // max < value si old_max == 1 (cas initial)
                if (entry.getValue() > max && (entry.getValue() < old_max || old_max == -1)) {
                    max = entry.getValue();
                }
            }
            // Si on a trouvé un max
            // On finira par ne plus en trouver à cause de la condition sur old_max
            if (max != -1) {
                // Ok, on a un max. Quel(s) domaine(s) sont aussi fréquents ?
                iterator = set.iterator();
                while(iterator.hasNext()) {
                    Map.Entry<String, Integer> entry = iterator.next();
                    if (entry.getValue() == max) {
                        System.out.println("    Key = " + entry.getKey() + " & Value = " + String.valueOf(entry.getValue()));
                    }
                }
                // Et on répète
                old_max = max;
                nb += 1;
            }
        }
        
        
    }

}