@echo off
cd /d "%~dp0.."
title Etapa 07: Evaluacion en Particion Held-Out
cls

echo ==============================================================================
echo [ETAPA 07] EVALUACION RIGUROSA EN TEST SET HELDOUT INEDITO
echo ==============================================================================
echo.
echo Ejecutando src/07_evaluacion_final.py...
echo.
python src/07_evaluacion_final.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo la evaluacion Held-Out.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Evaluacion Held-Out finalizada exitosamente.
echo Reportes generados:
echo   - docs/evaluacion_heldout.csv
echo   - docs/graficos/07_heldout_curvas_y_comparativa.png
echo ==============================================================================
