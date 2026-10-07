@echo off
cd /d "%~dp0.."
title Etapa 01: Extraccion de Datos
cls

echo ==============================================================================
echo [ETAPA 01] EXTRACCION DE DATOS (HUGGING FACE / FALLBACK LOCAL)
echo ==============================================================================
echo.
echo Ejecutando src/01_extraer_hf.py...
echo.
python src/01_extraer_hf.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo la extraccion de datos.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Etapa 01 completada exitosamente.
echo Archivo generado: data/01_original/enron_original.csv
echo ==============================================================================
