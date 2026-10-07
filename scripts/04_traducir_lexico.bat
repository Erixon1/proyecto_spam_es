@echo off
cd /d "%~dp0.."
title Etapa 04: Traduccion Lexica al Espanol
cls

echo ==============================================================================
echo [ETAPA 04] TRADUCCION LEXICA AL ESPANOL (DETERMINISTA Y RAPIDA)
echo ==============================================================================
echo.
echo  [1] Traducir muestra estratificada (1500 filas por defecto)
echo  [2] Traducir dataset completo (--full)
echo.
set /p opc_tr="Seleccione el alcance [1 o 2]: "

if "%opc_tr%"=="2" (
    echo.
    echo Ejecutando src/04_traducir_es.py --full...
    python src/04_traducir_es.py --full
) else (
    echo.
    echo Ejecutando src/04_traducir_es.py (muestra estratificada)...
    python src/04_traducir_es.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Fallo la etapa de traduccion lexica.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [OK] Etapa 04 (Lexica) completada exitosamente.
echo Archivos generados:
echo   - data/04_traducido/enron_traducido_es.csv
echo   - docs/diccionario_abreviaturas.csv
echo   - docs/ejemplo_traducciones.csv
echo   - docs/graficos/04_traduccion_comparativa_longitud.png
echo ==============================================================================
