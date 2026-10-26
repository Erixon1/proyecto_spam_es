@echo off
chcp 65001 > nul
title Detector de Spam Enron - Apartado Visual Interactivo

echo ========================================================
echo   INICIANDO INTERFAZ VISUAL BILINGÜE (EN / ES)
echo ========================================================
echo Abriendo servidor local en http://localhost:8000 ...
echo.

start "" "http://localhost:8000"
python "%~dp0..\src\servidor_web.py"

pause
