@echo off
javac MergeCSV.java
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
java MergeCSV
