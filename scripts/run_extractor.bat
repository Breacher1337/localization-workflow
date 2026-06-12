@echo off
set CLASSPATH="%APPLICATION_CORE_DIR%\legacyapp.api.jar";"%APPLICATION_CORE_DIR%\log4j-1.2.9.jar";"libs\javassist.jar"
javac -cp %CLASSPATH% StringExtractor.java
java -cp %CLASSPATH%;. StringExtractor
