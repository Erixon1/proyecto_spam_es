@echo off
cd /d "%~dp0.."
title Detector de Spam Enron - Pipeline Completo (01 a 05)
cls

echo ==============================================================================
echo [PIPELINE COMPLETO] EJECUTANDO FLUJO INTEGRAL (ETAPAS 01 -> 05)
echo ==============================================================================
echo.
echo  [1] Pipeline Estandar con Traduccion Completa (--full)
echo  [2] Pipeline Estandar + Evaluacion Held-Out (--full --heldout)
echo.
set /p opc_pipe="Seleccione una opcion [1 o 2]: "

if "%opc_pipe%"=="2" (
    echo.
    echo Ejecutando: python src/pipeline.py --full --heldout
    python src/pipeline.py --full --heldout
) else (
    echo.
    echo Ejecutando: python src/pipeline.py --full
    python src/pipeline.py --full
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ocurrio un fallo durante la ejecucion del pipeline.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Pipeline completado con exito.
echo ==============================================================================
