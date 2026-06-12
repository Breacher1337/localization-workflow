import javassist.*;
import java.io.*;
import java.util.zip.*;
import java.util.*;

public class DirectJarPatcher {
    public static void main(String[] args) throws Exception {
        System.out.println("[DirectJarPatcher] Patching legacyapp_obf.jar in-memory...");
        
        File srcFile = new File("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar.bak");
        if (!srcFile.exists()) {
            System.out.println("[DirectJarPatcher] Backup not found. Assuming already patched or missing.");
            return;
        }
        
        File destFile = new File("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar");

        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp.api.jar");
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar.bak");

        // We inject our Translator class into the pool so the hook compiles
        CtClass translatorClass = pool.makeClass("com.fs.legacyapp.ui.JPTranslator");
        CtField mapField = CtField.make("public static java.util.HashMap TR = new java.util.HashMap();", translatorClass);
        translatorClass.addField(mapField);
        
        CtConstructor staticBlock = translatorClass.makeClassInitializer();
        staticBlock.insertAfter("{"
            + "  TR.put(\"Continue\", \"続きから\");"
            + "  TR.put(\"Tutorials\", \"チュートリアル\");"
            + "  TR.put(\"Missions\", \"ミッション\");"
            + "  TR.put(\"New Application\", \"新規アプリケーション\");"
            + "  TR.put(\"Load Application\", \"データ読み込み\");"
            + "  TR.put(\"Codex\", \"データベース\");"
            + "  TR.put(\"Settings\", \"設定\");"
            + "  TR.put(\"Credits\", \"クレジット\");"
            + "  TR.put(\"Quit\", \"システム停止\");"
            + "  TR.put(\"Tutorial\", \"チュートリアル\");"
            + "  TR.put(\"Campaign\", \"キャンペーン\");"
            + "}");

        try (ZipInputStream zis = new ZipInputStream(new FileInputStream(srcFile));
             ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(destFile))) {
             
            // Add the new Translator class to the jar
            ZipEntry trEntry = new ZipEntry("com/fs/legacyapp/ui/JPTranslator.class");
            zos.putNextEntry(trEntry);
            zos.write(translatorClass.toBytecode());
            zos.closeEntry();

            ZipEntry entry;
            int injectedCount = 0;
            while ((entry = zis.getNextEntry()) != null) {
                String name = entry.getName();
                
                // Only process UI classes
                if (name.startsWith("com/fs/legacyapp/ui/") && name.endsWith(".class")) {
                    String className = name.replace("/", ".").replace(".class", "");
                    byte[] bytes = readAllBytes(zis);
                    
                    try {
                        CtClass uiClass = pool.makeClass(new ByteArrayInputStream(bytes));
                        boolean pluginified = false;

                        // 1. Hook setText
                        try {
                            for (CtMethod method : uiClass.getDeclaredMethods()) {
                                if (method.getName().equals("setText")) {
                                    CtClass[] params = method.getParameterTypes();
                                    for (int i = 0; i < params.length; i++) {
                                        if (params[i].getName().equals("java.lang.String")) {
                                            int paramIndex = i + 1;
                                            String injectionCode = "{"
                                                    + "  if ($" + paramIndex + " != null && com.fs.legacyapp.ui.JPTranslator.TR.containsKey($" + paramIndex + ")) {"
                                                    + "      $" + paramIndex + " = (String) com.fs.legacyapp.ui.JPTranslator.TR.get($" + paramIndex + ");"
                                                    + "  }"
                                                    + "}";
                                            method.insertBefore(injectionCode);
                                            pluginified = true;
                                        }
                                    }
                                }
                            }
                        } catch (Exception e) {}

                        // 2. Hook constructors
                        try {
                            for (CtConstructor constructor : uiClass.getDeclaredConstructors()) {
                                CtClass[] params = constructor.getParameterTypes();
                                for (int i = 0; i < params.length; i++) {
                                    if (params[i].getName().equals("java.lang.String")) {
                                        int paramIndex = i + 1;
                                        String injectionCode = "{"
                                                + "  if ($" + paramIndex + " != null && com.fs.legacyapp.ui.JPTranslator.TR.containsKey($" + paramIndex + ")) {"
                                                + "      $" + paramIndex + " = (String) com.fs.legacyapp.ui.JPTranslator.TR.get($" + paramIndex + ");"
                                                + "  }"
                                                + "}";
                                        constructor.insertBefore(injectionCode);
                                        pluginified = true;
                                    }
                                }
                            }
                        } catch (Exception e) {}

                        ZipEntry newEntry = new ZipEntry(name);
                        zos.putNextEntry(newEntry);
                        if (pluginified) {
                            zos.write(uiClass.toBytecode());
                            injectedCount++;
                        } else {
                            zos.write(bytes);
                        }
                        zos.closeEntry();
                        
                        uiClass.detach(); // Free memory
                    } catch (Exception e) {
                        ZipEntry newEntry = new ZipEntry(name);
                        zos.putNextEntry(newEntry);
                        zos.write(bytes);
                        zos.closeEntry();
                    }
                } else {
                    ZipEntry newEntry = new ZipEntry(name);
                    zos.putNextEntry(newEntry);
                    byte[] bytes = readAllBytes(zis);
                    zos.write(bytes);
                    zos.closeEntry();
                }
            }
            System.out.println("[DirectJarPatcher] Successfully patched " + injectedCount + " classes in-memory.");
        }
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
