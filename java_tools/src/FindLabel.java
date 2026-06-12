import javassist.*;

public class FindLabel {
    public static void main(String[] args) throws Exception {
        ClassPool pool = ClassPool.getDefault();
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp.api.jar");
        pool.insertClassPath("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar");

        java.util.zip.ZipInputStream zip = new java.util.zip.ZipInputStream(new java.io.FileInputStream("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar"));
        java.util.zip.ZipEntry entry;
        while ((entry = zip.getNextEntry()) != null) {
            if (entry.getName().endsWith(".class") && entry.getName().startsWith("com/fs/legacyapp/ui/")) {
                String className = entry.getName().replace("/", ".").replace(".class", "");
                try {
                    CtClass cc = pool.get(className);
                    for(CtMethod m : cc.getDeclaredMethods()) {
                        if (m.getName().equals("setText")) {
                            System.out.println("FOUND setText in: " + className);
                        }
                    }
                } catch(Exception e) {}
            }
        }
    }
}
