@echo off
cd /d "%~dp0.."
title Etapa 02: Limpieza y Deduplicacion
cls

echo ==============================================================================
echo [ETAPA 02] LIMPIEZA, DEDUPLICACION Y TRUNCAMIENTO DE TEXTO
echo ==============================================================================
echo.
echo Ejecutando src/02_limpiar.py...
echo.
python src/02_limpiar.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo la etapa de limpieza de datos.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Etapa 02 completada exitosamente.
echo Archivo generado: data/02_limpio/enron_limpio.csv
echo ==============================================================================
