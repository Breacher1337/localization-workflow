@echo off
javac SplitCSV.java
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
java SplitCSV
