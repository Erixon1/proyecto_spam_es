@echo off
cd /d "%~dp0.."
title Etapa 04: Traduccion Neuronal MarianMT
cls

echo ==============================================================================
echo [ETAPA 04] TRADUCCION NEURONAL (MARIANMT EN GPU / CPU)
echo ==============================================================================
echo.
echo Este modo utiliza el modelo Helsinki-NLP/opus-mt-en-es.
echo Se recomienda contar con GPU NVIDIA (CUDA).
echo.
echo  [1] Iniciar traduccion neuronal completa (--marian)
echo  [2] Reanudar traduccion interrumpida (--marian --resume)
echo.
set /p opc_marian="Seleccione una opcion [1 o 2]: "

if "%opc_marian%"=="2" (
    echo.
    echo Reanudando desde checkpoint: python src/04_traducir_es.py --marian --resume
    python src/04_traducir_es.py --marian --resume
) else (
    echo.
    echo Iniciando traduccion: python src/04_traducir_es.py --marian
    python src/04_traducir_es.py --marian
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ocurrio un inconveniente en la traduccion neuronal.
    echo Si se guardo checkpoint, puedes reintentar con la opcion [2] (--resume).
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Traduccion neuronal completada exitosamente.
echo Archivo generado: data/04_traducido/enron_traducido_es_neural.csv
echo ==============================================================================
