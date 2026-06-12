import java.io.*;
import java.util.zip.*;
import java.nio.file.*;
import java.nio.file.attribute.*;

public class MakeJar {
    public static void main(String[] args) throws Exception {
        String sourceDir = "build/classes";
        String zipFile = "jars/japanese_localization.jar";
        
        Path sourcePath = Paths.get(sourceDir);
        try (ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(zipFile))) {
            // Write MANIFEST.MF
            zos.putNextEntry(new ZipEntry("META-INF/MANIFEST.MF"));
            String manifest = "Manifest-Version: 1.0\n" +
                              "Premain-Class: com.applicationjp.AgentMain\n" +
                              "Boot-Class-Path: javassist.jar\n" +
                              "Can-Redefine-Classes: true\n" +
                              "Can-Retransform-Classes: true\n\n";
            zos.write(manifest.getBytes("UTF-8"));
            zos.closeEntry();
            
            Files.walkFileTree(sourcePath, new SimpleFileVisitor<Path>() {
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                    String entryName = sourcePath.relativize(file).toString().replace("\\", "/");
                    zos.putNextEntry(new ZipEntry(entryName));
                    Files.copy(file, zos);
                    zos.closeEntry();
                    return FileVisitResult.CONTINUE;
                }
            });
        }
    }
}
