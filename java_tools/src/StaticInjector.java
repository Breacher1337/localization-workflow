import javassist.*;

public class StaticInjector {
    public static void main(String[] args) throws Exception {
        System.out.println("[StaticInjector] Running static bytecode injection...");
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp.api.jar");
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar");
        pool.insertClassPath("build/classes");

        String[] uiClasses = {
            "com.fs.legacyapp.ui.d",
            "com.fs.legacyapp.ui.impl.if",
            "com.fs.legacyapp.ui.n",
            "com.fs.legacyapp.ui.new",
            "com.fs.legacyapp.ui.t"
        };

        for (String className : uiClasses) {
            try {
                CtClass uiClass = pool.get(className);
                String injectionCode = "{"
                        + "  if ($1 != null && com.applicationjp.JPTranslationPlugin.TR.containsKey($1)) {"
                        + "      $1 = (String) com.applicationjp.JPTranslationPlugin.TR.get($1);"
                        + "  }"
                        + "}";
                
                try {
                    CtMethod setTextMethod = uiClass.getDeclaredMethod("setText", new CtClass[]{pool.get("java.lang.String")});
                    setTextMethod.insertBefore(injectionCode);
                } catch(Exception e) {}

                try {
                    for (CtConstructor constructor : uiClass.getDeclaredConstructors()) {
                        CtClass[] params = constructor.getParameterTypes();
                        if (params.length > 0 && params[0].getName().equals("java.lang.String")) {
                            constructor.insertBefore(injectionCode);
                            System.out.println("  Hooked constructor taking String in: " + className);
                        }
                    }
                } catch(Exception e) {}

                uiClass.writeFile("build/classes");
                System.out.println("[StaticInjector] Successfully injected: " + className);
            } catch (Exception e) {
                System.out.println("[StaticInjector] Could not hook " + className + ": " + e.getMessage());
            }
        }
    }
}
