import java.io.*;
import java.nio.file.*;
import java.util.zip.*;

public class PatchJar {
    public static void main(String[] args) throws Exception {
        System.out.println("[PatchJar] Patching legacyapp_obf.jar with injected classes...");
        File srcFile = new File("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar.bak");
        File destFile = new File("C:\\Program Files (x86)\\Acme Corp\\Application\\application-core\\legacyapp_obf.jar");
        File overrideDir = new File("build/classes");

        try (ZipInputStream zis = new ZipInputStream(new FileInputStream(srcFile));
             ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(destFile))) {
             
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                File overrideFile = new File(overrideDir, entry.getName());
                
                ZipEntry newEntry = new ZipEntry(entry.getName());
                zos.putNextEntry(newEntry);
                
                if (overrideFile.exists() && overrideFile.isFile()) {
                    Files.copy(overrideFile.toPath(), zos);
                    System.out.println("  Patched: " + entry.getName());
                } else {
                    byte[] buffer = new byte[1024];
                    int len;
                    while ((len = zis.read(buffer)) > 0) {
                        zos.write(buffer, 0, len);
                    }
                }
                zos.closeEntry();
            }
        }
        System.out.println("[PatchJar] Patching complete.");
    }
}
