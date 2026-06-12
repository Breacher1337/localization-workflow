import java.io.*;
import java.util.*;

public class MergeCSV {
    public static void main(String[] args) throws Exception {
        System.out.println("Merging translated chunks into ui.csv...");
        
        File outDir = new File("data/strings");
        if (!outDir.exists()) outDir.mkdirs();
        
        try (PrintWriter pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream("data/strings/ui.csv"), "UTF-8"))) {
            pw.println("key,value");
            
            for (int i = 1; i <= 3; i++) {
                File chunk = new File("chunk_" + i + "_translated.csv");
                if (chunk.exists()) {
                    try (BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(chunk), "UTF-8"))) {
                        String line;
                        while ((line = br.readLine()) != null) {
                            if (!line.trim().isEmpty() && !line.startsWith("key,value")) {
                                pw.println(line);
                            }
                        }
                    }
                    System.out.println("Merged chunk " + i);
                } else {
                    System.err.println("WARNING: chunk_" + i + "_translated.csv not found!");
                }
            }
        }
        System.out.println("Merge complete.");
    }
}
