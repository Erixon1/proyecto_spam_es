@echo off
cd /d "%~dp0.."
title Etapa 00: Instalacion de Dependencias
cls

echo ==============================================================================
echo [ETAPA 00] INSTALACION Y VERIFICACION DE DEPENDENCIAS
echo ==============================================================================
echo.
echo Instalando paquetes requeridos desde requirements.txt...
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Descargando recursos de NLTK (stopwords, punkt)...
python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)"

echo.
echo ==============================================================================
echo [OK] Verificacion de dependencias completada.
echo ==============================================================================
