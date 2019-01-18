package saxo;

import org.xml.sax.helpers.DefaultHandler;
import org.xml.sax.*;
import javax.xml.parsers.*;
import java.io.File;

class DGXHandler extends DefaultHandler {
    
    public void startElement(String uri, String localName, String qName, Attributes attrs) {
        System.out.println(qName);
    }
    
    public static void main(String[] args) {
        DGXHandler handler = new DGXHandler();
        File fileToParse = new File ("15075_dgx_aa.xml");
        
        SAXParserFactory spf = SAXParserFactory.newInstance();

        try {
            SAXParser saxParser = spf.newSAXParser();
            saxParser.parse(fileToParse, handler);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}