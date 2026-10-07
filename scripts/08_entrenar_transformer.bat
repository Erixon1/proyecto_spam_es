@echo off
cd /d "%~dp0.."
title Etapa 08: Fine-Tuning de Transformer (BETO)
cls

echo ==============================================================================
echo [ETAPA 08] FINE-TUNING TRANSFORMER (BETO / DISTILBERT)
echo ==============================================================================
echo.
echo Este proceso entrena un modelo contextual BERT en espanol.
echo Requiere GPU (CUDA) con soporte PyTorch y Hugging Face Transformers.
echo.
echo Ejecutando src/08_transformer_es.py...
echo.
python src/08_transformer_es.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ocurrio un error al ejecutar el modelo Transformer.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Entrenamiento Transformer completado.
echo ==============================================================================
