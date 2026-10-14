@echo off
cd /d "%~dp0.."
title Etapa 04: Traduccion Neuronal MarianMT
cls

echo ==============================================================================
echo [ETAPA 04] TRADUCCION NEURONAL COMPLETA SIN TRUNCAR (MARIANMT EN GPU)
echo ==============================================================================
echo.
echo Este modo utiliza Helsinki-NLP/opus-mt-en-es con segmentacion por oraciones
echo para traducir el 100%% del texto sin importar su longitud.
echo.
echo  [1] Modo Patch Acelerado (Re-traduce solo correos >600 chars con fragmentacion) [Recomendado]
echo  [2] Modo Completo Total desde cero (Re-traduce todo el dataset sin truncar)
echo  [3] Reanudar traduccion interrumpida desde checkpoint (--resume)
echo.
set /p opc_marian="Seleccione una opcion [1, 2 o 3]: "

if "%opc_marian%"=="1" (
    echo.
    echo Iniciando patch acelerado: python src/04_traducir_es.py --marian --full-chunks --patch-existing --resume
    python src/04_traducir_es.py --marian --full-chunks --patch-existing --resume
) else if "%opc_marian%"=="3" (
    echo.
    echo Reanudando desde checkpoint: python src/04_traducir_es.py --marian --full-chunks --resume
    python src/04_traducir_es.py --marian --full-chunks --resume
) else (
    echo.
    echo Iniciando traduccion completa: python src/04_traducir_es.py --marian --full-chunks
    python src/04_traducir_es.py --marian --full-chunks
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ocurrio un inconveniente en la traduccion neuronal.
    echo Si se guardo checkpoint, puedes reintentar con la opcion [3] (--resume).
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Traduccion neuronal completada exitosamente.
echo Archivo generado: data/04_traducido/enron_traducido_es_neural_full.csv
echo ==============================================================================

