package saxo;

import org.xml.sax.helpers.DefaultHandler;
import org.xml.sax.*;
import javax.xml.parsers.*;
import java.io.File;
import java.util.*;
import java.io.*;

/**
 * Classe pour parser un extrait de GLAWI au format XML.
 * Cette classe propose une fonction main qui fait le travail sur GLAWI et le parsing SAX
 * Master 2 LITL Université Jean Jaurès
 * @author Damien Gouteux
 */
class DGXHandler extends DefaultHandler {
    
    protected ArrayList<String> nomenclature;               // For question 2.1
    protected ArrayList<String> entreeAtLeastOneBotanique;  // For question 2.5a
    protected ArrayList<String> entreeAllBotanique;         // For question 2.5b
    protected ArrayList<String> neologisms;                 // For questions 2.6 and 2.9
    protected ArrayList<String> neologismsOnlyOne;          // For question 2.7
    protected ArrayList<String> entreeFromLittre;           // For questions 2.8 and 2.9
    protected ArrayList<String> neologismsAll;              // For question 2.10
    
    protected HashMap<String, Integer> pos;                 // For question 2.2
    protected HashMap<String, Integer> labelTypes;          // For question 2.3
    protected HashMap<String, Integer> semValues;           // For question 2.3 bonus
    protected HashMap<String, Integer> domains;             // For question 2.4
    
    protected boolean inTitle;          // For question 2.1
    protected boolean inTxt;            // For question 2.5
    protected boolean inImport;         // For question 2.8
    
    protected boolean isNeologism;      // For questions 2.6 and 2.7 and 2.10
    protected boolean isFromLittre;     // For questions 2.8, 2.9 and 2.10
    
    protected String currentPosType;    // For questions 2.5 and 2.6
    protected String currentPosDefTxt;  // For question 2.6
    
    private int defCpt;                 // For questions 2.5 and 2.7 and 2.10
    private int posCpt;                 // For questions 2.7 and 2.10
    private int botCpt;                 // For question 2.5
    private int neoCpt;                 // For questions 2.7 and 2.10
    
    /**
     * Constructeur
     */
    public DGXHandler() {
        super();
        this.nomenclature = new ArrayList<String>();
        this.pos = new HashMap<String, Integer>();
        this.labelTypes = new HashMap<String, Integer>();
        this.semValues = new HashMap<String, Integer>();
        this.domains = new HashMap<String, Integer>();
        this.inTitle = false;
        this.entreeAtLeastOneBotanique = new ArrayList<String>();
        this.entreeAllBotanique = new ArrayList<String>();
        this.neologisms = new ArrayList<String>();
        this.neologismsOnlyOne = new ArrayList<String>();
        this.neologismsAll = new ArrayList<String>();
        this.entreeFromLittre = new ArrayList<String>();
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
            case "article":
                this.posCpt = 0;
                break;
            case "title":
                this.inTitle = true;
                break;
            case "pos":
                this.posCpt += 1;
                key = attrs.getValue("type");
                this.currentPosType = key;
                val = 1;
                if (this.pos.containsKey(key)) {
                    val = val + this.pos.get(key);
                }
                this.pos.put(key, val);
                // For questions 2.5a and 2.5b
                this.defCpt = 0;
                this.botCpt = 0;
                // For questions 2.7 and 2.10
                this.neoCpt = 0;
                break;
            case "definition":
                this.defCpt += 1;
                break;
            case "label":
                // <label type="xxx">
                String type = attrs.getValue("type");
                val = 1;
                if (labelTypes.containsKey(type)) {
                    val = val + this.labelTypes.get(type);
                }
                this.labelTypes.put(type, val);
                switch (type) {
                    case "sem":
                        value = attrs.getValue("value");
                        val = 1;
                        if (this.semValues.containsKey(value)) {
                            val = val + this.semValues.get(value);
                        }
                        this.semValues.put(value, val); 
                        break;
                    case "domain":
                        value = attrs.getValue("value");
                        val = 1;
                        if (this.domains.containsKey(value)) {
                            val = val + this.domains.get(value);
                        }
                        this.domains.put(value, val);
                        if (value.equals("botanique")) {
                            this.entreeAtLeastOneBotanique.add(this.nomenclature.get(this.nomenclature.size() - 1));
                            this.botCpt += 1;
                        }
                        break;
                    // For question 2.6
                    case "diachronic":
                        value = attrs.getValue("value");
                        if (value.equals("néologisme")) {
                            this.isNeologism = true;
                            this.neoCpt += 1; // For questions 2.7 and 2.10
                        }
                        break;
                }
                break;
            case "txt":
                this.inTxt = true;
                break;
            // For question 2.7
            case "import":
                this.isFromLittre = false;
                this.inImport = true;
                break;
        }
    }
    
    /**
     * La méthode endElement est appelée à chaque balise fermante.
     * @param uri l'uri de l'élément
     * @param localName le nom local (vide)
     * @param qName le nom de la balise
     */
    public void endElement(String uri, String localName, String qName) {
        String currentTitle = this.nomenclature.get(this.nomenclature.size() - 1);
        switch (qName) {
            case "title":
                this.inTitle = false;
                break;
            case "pos":
                // For questions 2.5a and 2.5b
                if (this.defCpt == this.botCpt && this.botCpt != 0) {
                    this.entreeAllBotanique.add(currentTitle);
                }
                // For question 2.7
                if (this.defCpt > 1 && this.neoCpt == 1) {
                    this.neologismsOnlyOne.add(currentTitle + "###" + 
                                               currentPosType + "###" + 
                                               String.valueOf(this.posCpt) + "###" +
                                               String.valueOf(this.defCpt) + "###" +
                                               String.valueOf(this.neoCpt));
                }
                // For question 2.10
                if (this.defCpt == this.neoCpt && this.neoCpt > 0) {
                    this.neologismsAll.add(currentTitle + "###" + 
                                           currentPosType + "###" + 
                                           String.valueOf(this.posCpt) + "###" +
                                           String.valueOf(this.defCpt) + "###" +
                                           String.valueOf(this.neoCpt));
                }
                break;
            // For question 2.6
            case "txt":
                this.inTxt = false;
                break;
            case "definition":
                if (this.isNeologism) {
                    this.neologisms.add(
                        currentTitle + "###" +
                        this.currentPosType + "###" +
                        this.currentPosDefTxt.replace("\n", " // ")
                    );
                    this.isNeologism = false;
                }
                break;
            // For question 2.8
            case "import":
                if (this.isFromLittre) {
                    this.entreeFromLittre.add(currentTitle);
                }
                this.inImport = false;
                break;
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
        } else if (this.inTxt) {
            this.currentPosDefTxt = new String(caracteres, debut, longueur);
        } else if (this.inImport) {
            String s = new String(caracteres, debut, longueur);
            if (s.equals("Littré")) {
                this.isFromLittre = true;
            }
        }
    }
    
    /**
     * Retourne la nomenclature
     *
     * @return les nomenclatures
     */
    public ArrayList<String> getTitles() {
        return this.nomenclature;
    }
    
    /**
     * Retourne les catégories du discours
     *
     * @return les catégories du discours
     */
    public HashMap<String, Integer> getPos() {
        return this.pos;
    }
        
    /**
     * Retourne les différents types des labels
     *
     * @return les différents types des labels
     */
    public HashMap<String, Integer> getLabelTypes() {
        return this.labelTypes;
    }

    /**
     * Retourne les valeurs pour les labels de type sem
     *
     * @return les valeurs pour les labels de type sem
     */
    public HashMap<String, Integer> getSemValues() {
        return this.semValues;
    }
    
    /**
     * Retourne les domaines
     *
     * @return les domaines
     */
    public HashMap<String, Integer> getDomains() {
        return this.domains;
    }
    
    /**
     * Retourne les entrées ayant au moins une définition d'une section POS en botanique
     *
     * @return les entrées ayant au moins une définition d'une section POS en botanique
     */
    public ArrayList<String> getAtLeastOneBotanique() {
        return this.entreeAtLeastOneBotanique;
    }
    
    /**
     * Retourne les entrées ayant toutes les définitions d'une section POS en botanique
     *
     * @return les entrées ayant toutes les définitions d'une section POS en botanique
     */
    public ArrayList<String> getAllOneBotanique() {
        return this.entreeAllBotanique;
    }
    
    /**
     * Retourne les néologismes
     *
     * @return les néologismes
     */
    public ArrayList<String> getNeologisms() {
        return this.neologisms;
    }
    
    /**
     * Retourne les entrées avec pos possédant plusieurs définitions dont une seule est marquée comme néologie
     *
     * @return les entrées avec pos possédant plusieurs définitions dont une seule est marquée comme néologie
     */
    public ArrayList<String> getNeologismsOnlyOne() {
        return this.neologismsOnlyOne;
    }
    
    /**
     * Retourne les entrées avec pos possédant dont toutes les définitions sont marquées comme néologie
     *
     * @return les entrées avec pos possédant dont toutes les définitions sont marquées comme néologie
     */
    public ArrayList<String> getNeologismsAll() {
        return this.neologismsAll;
    }
    
    /**
     * Retourne les entrées du Littré
     *
     * @return les entrées du Littré
     */
    public ArrayList<String> getEntreeFromLittre() {
        return this.entreeFromLittre;
    }
    
    /**
     * Output to file and console if console is true an Hashmap<String, Integer>
     *
     * @param title
     * @param hash
     * @param console
     */
    public static void output(String title, HashMap<String, Integer> hash, boolean console) {
        try {
            if (console) System.out.println("\n=== " + title + " ===\n");
            List<Map.Entry<String, Integer>> list = new ArrayList<>(hash.entrySet());
            list.sort(Collections.reverseOrder(Map.Entry.comparingByValue()));
            Iterator<Map.Entry<String, Integer>> iterator = list.iterator();
            FileWriter fileWriter = new FileWriter(title.replace(' ', '_') + ".txt");
            PrintWriter printWriter = new PrintWriter(fileWriter);
            while(iterator.hasNext()) {
                Map.Entry<String, Integer> entry = iterator.next();
                String key = String.format("%30s", entry.getKey());
                String val = String.format("%30s", String.valueOf(entry.getValue()));
                if (console) System.out.println("Key = " + key + " | Value = " + val);
                printWriter.println("Key = " + key + " | Value = " + val);
            }
            printWriter.close();
        } catch (IOException ioe) {
            System.out.println("[ERROR] Unable to write to file for " + title);
        }
    }
    
    /**
     * Output only to file
     */
    public static void output(String title, ArrayList<String> list) {
        output(title, list, false);
    }
    
    /**
     * Output to file and console if console is true
     */
    public static void output(String title, ArrayList<String> list, boolean console) {
        try {
            if (console) System.out.println("\n=== " + title + " ===\n");
            Collections.sort(list);
            FileWriter fileWriter = new FileWriter(title.replace(' ', '_') + ".txt");
            PrintWriter printWriter = new PrintWriter(fileWriter);
            for(String s : list) {
                if (console) System.out.println(s);
                printWriter.println(s);
            }
            printWriter.close();
        } catch (IOException ioe) {
            System.out.println("[ERROR] Unable to write to file for " + title);
        }
    }
    
    /**
     * Fonction principale
     *
     * @param args Paramètres d'entrées, non utilisés
     */
    public static void main(String[] args) {
        // Parcours de l'extrait de GLAWI
        DGXHandler handler = new DGXHandler();
        File fileToParse = new File ("glawiWork_1.xml");
        SAXParserFactory spf = SAXParserFactory.newInstance();
        try {
            SAXParser saxParser = spf.newSAXParser();
            saxParser.parse(fileToParse, handler);
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // 2.1 Extraction de la nomenclature (= les entrées)
        output("2_01_Nomenclature", handler.nomenclature);
        
        // 2.2 Table de fréquences des parties du discours
        output("2_02_Table of frequencies", handler.getPos(), false);
        
        // 2.3 Types de marques lexicographiques
        output("2_03_Table of label types", handler.getLabelTypes(), false);
        
        // Bonus : valeurs du type sem
        output("2_03b_Table values of sem types", handler.getSemValues(), false);
        
        // 2.4 Les 5 marques de domaine les plus fréquents
        try {
            FileWriter fileWriter = new FileWriter("2_04_Five most frequent domains.txt");
            PrintWriter printWriter = new PrintWriter(fileWriter);
            int old_max = -1;
            int max = 0; // pour remplir la condition du while la première fois
            int nb = 0;
            Set<Map.Entry<String, Integer>> set = handler.getDomains().entrySet();
            while (nb < 5 && max != -1) {
                printWriter.println(String.valueOf(nb + 1) + "]===================");
                max = -1;
                Iterator<Map.Entry<String, Integer>> iterator = set.iterator();
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
                            String key = String.format("%30s", entry.getKey());
                            String val = String.format("%30s", String.valueOf(entry.getValue()));
                            printWriter.println("Key = " + key + " | Value = " + val);
                        }
                    }
                    // Et on répète
                    old_max = max;
                    nb += 1;
                }
            }
            printWriter.close();
        } catch (IOException ioe) {
            System.out.println("[ERROR] Unable to write to file for 5 most frequent domains");
        }
        
        // 2.5a Entrées avec au moins une définition dans le domaine le plus fréquent
        output("2_05a_At least one definition in botanique", handler.getAtLeastOneBotanique());
        
        // 2.5b Entrées avec toutes les définitions dans le domaine le plus fréquent
        output("2_05b_All definitions in botanique", handler.getAllOneBotanique());
        
        // 2.6 Extraction des entrées avec leurs gloses qui sont des néologies
        output("2_06_Neologismes", handler.getNeologisms());

        // 2.7 Extraction des entrées avec plusieurs gloses dont une seule est une néologie
        output("2_07_Neologismes plusieurs def only one neo", handler.getNeologismsOnlyOne());
        
        // 2.8 Extraction des entrées importées du Littré
        output("2_08_From Littre", handler.getEntreeFromLittre());
        
        // 2.9 Extraction des entrées importées du Littré portant une marque de néologie
        // Il faut croiser neologisms & entreeFromLittre
        ArrayList<String> entreeFromLittreNeo = new ArrayList<String>();
        for (String s : handler.getNeologisms()) {
            String entree = s.split("###")[0];
            if (handler.getEntreeFromLittre().contains(entree)) {
                entreeFromLittreNeo.add(entree);
            }
        }
        output("2_09_Neologism from Littre", entreeFromLittreNeo);
        
        // 2.10 Extraction des entrées importées du Littré dont toutes les gloses sont des néologies
        output("2_10a_Entry with pos all neo", handler.getNeologismsAll());
        ArrayList<String> entreeFromLittreAllNeo = new ArrayList<String>();
        for (String s : handler.getNeologismsAll()) {
            String entree = s.split("###")[0];
            if (handler.getEntreeFromLittre().contains(entree) && !entreeFromLittreAllNeo.contains(entree)) {
                entreeFromLittreAllNeo.add(entree);
            }
        }
        output("2_10b_Entry from Littre with pos all neo", entreeFromLittreAllNeo);
        
        // 3. Inspecteur de structure 
        Inspector gadjet = new Inspector("glawiWork_1.xml");
        
        // 3.1 Les balises en les comptant par ordre alphabétique des niveaux, sans attributs
        gadjet.inspect_alphabetical_order("3_01_alpha no attr.txt", false);
        
        // 3.2 Les balises en les comptant par ordre de fréquences décroissantes, sans attributs
        gadjet.inspect_freq_order("3_02_freq no attr.txt", false);
        
        // 3.3 Les balises en les comptant par ordre alphabétique des niveaux, avec attributs
        gadjet.inspect_alphabetical_order("3_03_alpha attr.txt", true);
        
        // 3.4 Bonus : les balises en les comptant par ordre de rencontre, sans attributs
        gadjet.inspect_encounter_order("3_04_encounter no attr.txt", false);
    }

}