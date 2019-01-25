package saxo;

import org.xml.sax.helpers.DefaultHandler;
import org.xml.sax.*;
import javax.xml.parsers.*;
import java.io.File;
import java.util.*;
import java.io.*;

/**
 * Classe pour inspecter un extrait de GLAWI au format XML.
 * 
 * Master 2 LITL Université Jean Jaurès
 * @author Damien Gouteux
 */
class Inspector extends DefaultHandler {
    protected HashMap<String, Integer> all;
    protected ArrayList<String> encounterOrder;
    private ArrayList<String> level; // current level of exploration
    
    public Inspector(String filenameToParse) {
        this.level = new ArrayList<String>();
        this.encounterOrder = new ArrayList<String>();
        this.all = new HashMap<String, Integer>();
        File fileToParse = new File (filenameToParse);
        SAXParserFactory spf = SAXParserFactory.newInstance();
        try {
            SAXParser saxParser = spf.newSAXParser();
            saxParser.parse(fileToParse, this);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void inspect_alphabetical_order(String outFilename, boolean attributes) {
        try {
            FileWriter fileWriter = new FileWriter(outFilename);
            PrintWriter printWriter = new PrintWriter(fileWriter);
            ArrayList<String> alphabeticalOrder = new ArrayList<String>();
            alphabeticalOrder.addAll(this.encounterOrder);
            Collections.sort(alphabeticalOrder);
            for (String key : alphabeticalOrder) {
                if (key.contains("@") && !attributes) continue;
                String freq = String.format("%6s", String.valueOf(this.all.get(key)));
                printWriter.println(freq + "   " + key);
            }
            printWriter.close();
        } catch (IOException ioe) {
            System.out.println("[ERROR] Unable to write to file for " + outFilename);
        }
    }
    
    public void inspect_encounter_order(String outFilename, boolean attributes) {
        try {
            FileWriter fileWriter = new FileWriter(outFilename);
            PrintWriter printWriter = new PrintWriter(fileWriter);
            for (String key : this.encounterOrder) {
                if (key.contains("@") && !attributes) continue;
                String freq = String.format("%6s", String.valueOf(this.all.get(key)));
                printWriter.println(freq + "   " + key);
            }
            printWriter.close();
        } catch (IOException ioe) {
            System.out.println("[ERROR] Unable to write to file for " + outFilename);
        }
    }
    
    public void inspect_freq_order(String outFilename, boolean attributes) {
        try {
            List<Map.Entry<String, Integer>> list = new ArrayList<>(this.all.entrySet());
            list.sort(Collections.reverseOrder(Map.Entry.comparingByValue()));
            Iterator<Map.Entry<String, Integer>> iterator = list.iterator();
            FileWriter fileWriter = new FileWriter(outFilename);
            PrintWriter printWriter = new PrintWriter(fileWriter);
            while(iterator.hasNext()) {
                Map.Entry<String, Integer> entry = iterator.next();
                String key = entry.getKey();
                String freq = String.format("%6s", String.valueOf(entry.getValue()));
                if (key.contains("@") && !attributes) continue;
                printWriter.println(freq + "   " + key);
            }
            printWriter.close();
        } catch (IOException ioe) {
            System.out.println("[ERROR] Unable to write to file for " + outFilename);
        }
    }
    
    /**
     * Transforme la pile de niveau en une chaîne unique
     * [level1, level2, level3] => level1/level2/level3
     *
     * @return la clé sous la forme level1/level2/level3
     */
    public String refreshKey() {
        // Java 8 has String.join()
        // Make the key
        StringBuilder sb = new StringBuilder();
        boolean first = true;
        for (String s : this.level) {
            if (first) {
                sb.append(s);
                first = false;
            }
            else sb.append("/").append(s);
        }
        return sb.toString();
    }
    
    /**
     * La méthode startElement est appelée à chaque balise ouvrante.
     * Le texte entre balise ouvrante et balise fermante est gérée par la méthode characters
     * @param uri l'uri de l'élément
     * @param localName le nom local (vide)
     * @param qName le nom de la balise
     * @param attrs les attributs (on interroge avec getValue)
     */
    public void startElement(String uri, String localName, String qName, Attributes attrs) {
        this.level.add(qName);
        String key = this.refreshKey();
        if (!this.encounterOrder.contains(key)) {
            this.encounterOrder.add(key);
        }
        // Handle all attributes
        for (int i = 0; i < attrs.getLength(); i++) {
            String attrKey = key + "/@" + attrs.getQName(i);
            // Test if the key is inside the all
            if (!this.encounterOrder.contains(key)) {
                this.encounterOrder.add(key);
            }
            if (all.containsKey(attrKey)) {
                this.all.put(attrKey, this.all.get(attrKey) + 1);
            } else {
                this.encounterOrder.add(attrKey);
                this.all.put(attrKey, 1);
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
        String key = this.refreshKey();
        // Test if the key is inside the all
        if (this.all.containsKey(key)) {
            this.all.put(key, this.all.get(key) + 1);
        } else {
            this.all.put(key, 1);
        }
        this.level.remove(level.size() - 1);
    }
}
