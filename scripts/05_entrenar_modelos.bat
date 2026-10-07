@echo off
cd /d "%~dp0.."
title Etapa 05: Entrenamiento de Modelos
cls

echo ==============================================================================
echo [ETAPA 05] ENTRENAMIENTO DE MODELOS, GRIDSEARCH, UMBRALES Y XAI
echo ==============================================================================
echo.
echo Ejecutando src/05_entrenar.py...
echo.
python src/05_entrenar.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo el entrenamiento de modelos.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Etapa 05 completada exitosamente.
echo Modelos y metricas generados:
echo   - models/spam_nb_en.pkl (Modelo en Ingles con Wrapper)
echo   - models/spam_nb_es.pkl (Modelo en Espanol con Wrapper)
echo   - models/metricas.csv (Tabla comparativa de desempeno)
echo   - docs/graficos/05_entrenamiento_matrices_y_xai.png
echo ==============================================================================
