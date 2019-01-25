@echo off
set JAVADIR=C:\tools\jdk-11.0.2\bin
echo ------------------ CLEANING ----------------------
if exist .\saxo\DGXHandler.class (
    del .\saxo\DGXHandler.class
)
if exist .\saxo\Inspector.class (
    del .\saxo\Inspector.class
)
echo ------------------ END CLEANING ------------------
echo ------------------ COMPILING ---------------------
%JAVADIR%\javac.exe -encoding utf8 .\saxo\DGXHandler.java -Xlint
echo ------------------ END COMPILING -----------------
if exist .\saxo\DGXHandler.class (
    if exist .\saxo\Inspector.class (
        echo ------------------ EXECUTING ---------------------
        %JAVADIR%\java.exe saxo.DGXHandler
        echo ------------------ END EXECUTING -----------------
    )
    if not exist .\saxo\Inspector.class (
        echo SOMETHING WENT WRONT WHILE COMPILING Inspector.java
    )
)
if not exist .\saxo\DGXHandler.class (
    echo SOMETHING WENT WRONT WHILE COMPILING DGXHandler.java
)