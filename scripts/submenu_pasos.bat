@echo off
cd /d "%~dp0.."
title Detector de Spam Enron - Ejecucion Paso a Paso
cls

:SUBMENU
cls
echo ==============================================================================
echo                 EJECUCION MODULAR PASO A PASO (ETAPAS 00 A 08)
echo ==============================================================================
echo.
echo  [0] Etapa 00: Instalar / Verificar Entorno y Dependencias
echo  [1] Etapa 01: Extraccion de Datos (Hugging Face / Fallback Local)
echo  [2] Etapa 02: Limpieza, Deduplicacion y Control de Longitud
echo  [3] Etapa 03: Preprocesamiento NLP, Tokens y Censo de Idiomas
echo  [4] Etapa 04: Traduccion Lexica al Espanol (Muestra o Full)
echo  [5] Etapa 04: Traduccion Neuronal MarianMT en GPU (--resume)
echo  [6] Etapa 05: Entrenamiento Naive Bayes + Regresion Logistica + XAI
echo  [7] Etapa 06: Probar Inferencia en Vivo
echo  [8] Etapa 07: Evaluacion Final en Test Set Held-Out
echo  [9] Etapa 08: Fine-Tuning Transformer (BETO / DistilBERT)
echo  [R] Regresar al Menu Principal
echo.
echo ==============================================================================
set /p subopcion="Seleccione una etapa [0-9 / R]: "

if /i "%subopcion%"=="0" (
    call scripts\00_instalar_dependencias.bat
) else if "%subopcion%"=="1" (
    call scripts\01_extraer_datos.bat
) else if "%subopcion%"=="2" (
    call scripts\02_limpiar_datos.bat
) else if "%subopcion%"=="3" (
    call scripts\03_preprocesar_nlp.bat
) else if "%subopcion%"=="4" (
    call scripts\04_traducir_lexico.bat
) else if "%subopcion%"=="5" (
    call scripts\04_traducir_neural.bat
) else if "%subopcion%"=="6" (
    call scripts\05_entrenar_modelos.bat
) else if "%subopcion%"=="7" (
    call scripts\06_probar_prediccion.bat
) else if "%subopcion%"=="8" (
    call scripts\07_evaluacion_heldout.bat
) else if "%subopcion%"=="9" (
    call scripts\08_entrenar_transformer.bat
) else if /i "%subopcion%"=="R" (
    exit /b
) else (
    echo.
    echo [ERROR] Opcion no valida.
    timeout /t 2 >nul
    goto SUBMENU
)

echo.
echo ==============================================================================
echo Presione cualquier tecla para continuar en el submenu paso a paso...
pause >nul
goto SUBMENU
