import javassist.*;
import java.util.zip.*;
import java.io.*;

public class BroadInjector {
    public static void main(String[] args) throws Exception {
        System.out.println("[BroadInjector] Running advanced broad static bytecode injection...");

        String coreDir = System.getProperty("APPLICATION_CORE_DIR");
        if (coreDir == null) {
            coreDir = "."; // Default to current dir or handle as error
        }

        ClassPool pool = ClassPool.getDefault();
        try {
            pool.insertClassPath(new File(coreDir, "legacyapp.api.jar").getAbsolutePath());
            pool.insertClassPath(new File(coreDir, "legacyapp_obf.jar").getAbsolutePath());
        } catch (NotFoundException e) {
            System.err.println("[BroadInjector] Failed to load core jars: " + e.getMessage());
        }
        pool.insertClassPath("build/classes");

        File obfJar = new File(coreDir, "legacyapp_obf.jar");
        if (!obfJar.exists()) {
            System.err.println("[BroadInjector] legacyapp_obf.jar not found at " + obfJar.getAbsolutePath());
            return;
        }

        ZipInputStream zip = new ZipInputStream(new FileInputStream(obfJar));
        ZipEntry entry;
        int injectedCount = 0;

        while ((entry = zip.getNextEntry()) != null) {
            String name = entry.getName();
            if (name.endsWith(".class") && (name.startsWith("com/fs/legacyapp/ui/") || name.startsWith("com/fs/legacyapp/api/"))) {
                String className = name.replace("/", ".").replace(".class", "");
                try {
                    CtClass cc = pool.get(className);
                    boolean pluginified = false;

                    for (CtMethod method : cc.getDeclaredMethods()) {
                        String mname = method.getName();
                        if (mname.equals("setText") || mname.equals("addPara") || mname.equals("addParagraph")) {
                            CtClass[] params = method.getParameterTypes();
                            if (params.length > 0 && params[0].getName().equals("java.lang.String")) {
                                method.insertBefore("{  = com.applicationjp.JPTranslationPlugin.translate(); }");
                                pluginified = true;
                            }
                        }
                    }

                    if (pluginified) {
                        cc.writeFile("build/classes");
                        injectedCount++;
                    }
                } catch (Exception e) {
                    // Log to stderr instead of silent failure
                    // System.err.println("Failed to process class " + className + ": " + e.getMessage());
                }
            }
        }
        System.out.println("[BroadInjector] Total classes injected: " + injectedCount);
    }
}
