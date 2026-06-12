public class FindTitle {
    public static void main(String[] args) throws Exception {
        java.util.zip.ZipInputStream zip = new java.util.zip.ZipInputStream(new java.io.FileInputStream("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar"));
        java.util.zip.ZipEntry entry;
        while ((entry = zip.getNextEntry()) != null) {
            if (entry.getName().startsWith("com/fs/legacyapp/title/")) {
                System.out.println(entry.getName());
            }
        }
    }
}
