@echo off
cd /d "%~dp0.."
title Generador de Graficos Diagnosticos
cls

echo ==============================================================================
echo [GRAFICOS] GENERACION CONSOLIDADA DE FIGURAS DIAGNOSTICAS (300 DPI)
echo ==============================================================================
echo.
echo Ejecutando src/generar_graficos.py...
echo.
python src/generar_graficos.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo la generacion de graficos.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Graficos consolidados generados exitosamente en: docs/graficos/
echo ==============================================================================
