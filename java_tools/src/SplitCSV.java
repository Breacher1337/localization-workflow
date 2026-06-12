import java.io.*;
import java.util.*;

public class SplitCSV {
    public static void main(String[] args) throws Exception {
        List<String> lines = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("master_english_ui.csv"), "UTF-8"))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (!line.trim().isEmpty() && !line.startsWith("key,value")) {
                    lines.add(line);
                }
            }
        }
        
        int chunks = 8;
        int chunkSize = (int) Math.ceil((double) lines.size() / chunks);
        
        for (int i = 0; i < chunks; i++) {
            int start = i * chunkSize;
            int end = Math.min(start + chunkSize, lines.size());
            if (start >= end) break;
            
            List<String> chunk = lines.subList(start, end);
            String filename = "chunk_" + (i+1) + ".csv";
            try (PrintWriter pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(filename), "UTF-8"))) {
                pw.println("key,value");
                for (String c : chunk) {
                    pw.println(c);
                }
            }
            System.out.println("Wrote " + chunk.size() + " lines to " + filename);
        }
    }
}
