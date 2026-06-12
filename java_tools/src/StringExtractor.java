import javassist.*;
import javassist.bytecode.*;
import java.io.*;
import java.util.*;
import java.util.zip.*;

public class StringExtractor {
    public static void main(String[] args) throws Exception {
        System.out.println("[StringExtractor] Scanning legacyapp_obf.jar for UI strings...");
        
        File srcFile = new File("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar");
        if (!srcFile.exists()) {
            System.err.println("[StringExtractor] legacyapp_obf.jar not found!");
            return;
        }

        ClassPool pool = ClassPool.getDefault();
        Set<String> uniqueStrings = new HashSet<>();

        try (ZipInputStream zis = new ZipInputStream(new FileInputStream(srcFile))) {
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                String name = entry.getName();
                
                // Scan UI classes
                if (name.endsWith(".class")) {
                    byte[] bytes = readAllBytes(zis);
                    try {
                        CtClass uiClass = pool.makeClass(new ByteArrayInputStream(bytes));
                        ClassFile classFile = uiClass.getClassFile();
                        ConstPool constPool = classFile.getConstPool();
                        
                        for (int i = 1; i < constPool.getSize(); i++) {
                            int tag = constPool.getTag(i);
                            if (tag == ConstPool.CONST_String) {
                                String str = constPool.getStringInfo(i);
                                // Filter out empty, very short, or obviously non-UI strings
                                if (str != null && str.length() > 1 && !str.matches("^[a-zA-Z0-9_./\\\\]+$") && !str.matches("^\\d+$")) {
                                    uniqueStrings.add(str);
                                } else if (str != null && str.length() > 2) {
                                    // Catch CamelCase or sentence strings that might be missed
                                    if (str.contains(" ") || str.matches(".*[A-Z].*")) {
                                        uniqueStrings.add(str);
                                    }
                                }
                            }
                        }
                        uiClass.detach();
                    } catch (Exception e) {
                        // Ignore classes that fail to parse
                    }
                }
            }
        }
        
        System.out.println("[StringExtractor] Found " + uniqueStrings.size() + " unique UI strings.");
        
        File outFile = new File("master_english_ui.csv");
        try (PrintWriter pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(outFile), "UTF-8"))) {
            pw.println("key,value");
            List<String> sorted = new ArrayList<>(uniqueStrings);
            Collections.sort(sorted);
            for (String str : sorted) {
                // Escape quotes
                String escaped = str.replace("\"", "\"\"");
                pw.println("\"" + escaped + "\",\"\"");
            }
        }
        
        System.out.println("[StringExtractor] Wrote strings to master_english_ui.csv");
    }
    
    private static byte[] readAllBytes(InputStream is) throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        int nRead;
        byte[] data = new byte[16384];
        while ((nRead = is.read(data, 0, data.length)) != -1) {
            buffer.write(data, 0, nRead);
        }
        return buffer.toByteArray();
    }
}
