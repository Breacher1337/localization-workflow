import javassist.*;
import java.util.zip.*;
import java.io.*;

public class BroadInjector {
    public static void main(String[] args) throws Exception {
        System.out.println("[BroadInjector] Running broad static bytecode injection...");
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp.api.jar");
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar");
        pool.insertClassPath("build/classes"); // for JPTranslationPlugin

        ZipInputStream zip = new ZipInputStream(new FileInputStream("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar"));
        ZipEntry entry;
        int injectedCount = 0;

        while ((entry = zip.getNextEntry()) != null) {
            if (entry.getName().startsWith("com/fs/legacyapp/ui/") && entry.getName().endsWith(".class")) {
                String className = entry.getName().replace("/", ".").replace(".class", "");
                try {
                    CtClass uiClass = pool.get(className);
                    boolean pluginified = false;

                    // 1. Hook any method named 'setText' taking a String
                    try {
                        CtMethod[] methods = uiClass.getDeclaredMethods();
                        for (CtMethod method : methods) {
                            if (method.getName().equals("setText")) {
                                CtClass[] params = method.getParameterTypes();
                                for (int i = 0; i < params.length; i++) {
                                    if (params[i].getName().equals("java.lang.String")) {
                                        int paramIndex = i + 1; // javassist params are 1-indexed
                                        String injectionCode = "{"
                                                + "  if ($" + paramIndex + " != null && com.applicationjp.JPTranslationPlugin.TR.containsKey($" + paramIndex + ")) {"
                                                + "      $" + paramIndex + " = (String) com.applicationjp.JPTranslationPlugin.TR.get($" + paramIndex + ");"
                                                + "  }"
                                                + "}";
                                        method.insertBefore(injectionCode);
                                        pluginified = true;
                                        System.out.println("  Hooked setText param " + paramIndex + " in: " + className);
                                    }
                                }
                            }
                        }
                    } catch (Exception e) {}

                    // 2. Hook constructors that take a String
                    try {
                        for (CtConstructor constructor : uiClass.getDeclaredConstructors()) {
                            CtClass[] params = constructor.getParameterTypes();
                            for (int i = 0; i < params.length; i++) {
                                if (params[i].getName().equals("java.lang.String")) {
                                    int paramIndex = i + 1;
                                    String injectionCode = "{"
                                            + "  if ($" + paramIndex + " != null && com.applicationjp.JPTranslationPlugin.TR.containsKey($" + paramIndex + ")) {"
                                            + "      $" + paramIndex + " = (String) com.applicationjp.JPTranslationPlugin.TR.get($" + paramIndex + ");"
                                            + "  }"
                                            + "}";
                                    constructor.insertBefore(injectionCode);
                                    pluginified = true;
                                    System.out.println("  Hooked constructor param " + paramIndex + " in: " + className);
                                }
                            }
                        }
                    } catch (Exception e) {}

                    if (pluginified) {
                        uiClass.writeFile("build/classes");
                        injectedCount++;
                    }
                } catch (Exception e) {
                    // System.out.println("Failed to process " + className + ": " + e.getMessage());
                }
            }
        }
        System.out.println("[BroadInjector] Total classes injected: " + injectedCount);
    }
}
