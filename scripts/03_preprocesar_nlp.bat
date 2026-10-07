@echo off
cd /d "%~dp0.."
title Etapa 03: Preprocesamiento NLP
cls

echo ==============================================================================
echo [ETAPA 03] PREPROCESAMIENTO NLP, TOKENS DE SPAM Y CENSO DE IDIOMAS
echo ==============================================================================
echo.
echo Ejecutando src/03_preprocesar_nlp.py...
echo.
python src/03_preprocesar_nlp.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo el preprocesamiento NLP.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Etapa 03 completada exitosamente.
echo Archivos generados:
echo   - data/03_nlp/enron_nlp_en.csv
echo   - docs/distribucion_idiomas.csv
echo   - docs/graficos/03_nlp_tokens_preservados.png
echo ==============================================================================
