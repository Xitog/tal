@echo off
set JAVADIR=C:\tools\jdk-11.0.2\bin
echo ------------------- CLEANING ---------------------
del .\saxo\DGXHandler.class
echo ------------------- END CLEANING -----------------
echo ------------------ COMPILING ---------------------
%JAVADIR%\javac.exe .\saxo\DGXHandler.java -Xlint
echo ------------------ END COMPILING ---------------------
pause
if exist .\saxo\DGXHandler.java (
    echo ------------------ EXECUTING ---------------------
    %JAVADIR%\java.exe saxo.DGXHandler
    echo ------------------ END EXECUTING ---------------------
    pause
)
if not exist .\saxo\DGXHandler.java (
    echo SOMETHING WENT WRONT WHILE COMPILING
)