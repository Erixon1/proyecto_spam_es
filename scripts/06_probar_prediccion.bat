@echo off
cd /d "%~dp0.."
title Etapa 06: Clasificador e Inferencia en Vivo
cls

:BUCLE_PREDECIR
cls
echo ==============================================================================
echo [ETAPA 06] CLASIFICADOR E INFERENCIA EN VIVO (INGLES / ESPANOL)
echo ==============================================================================
echo.
echo Escriba el texto o cuerpo del correo que desea clasificar.
echo (O presione 'S' para salir y regresar).
echo.
set /p texto_correo="Ingrese el texto: "

if /i "%texto_correo%"=="S" (
    exit /b
)
if "%texto_correo%"=="" (
    echo.
    echo [ADVERTENCIA] No ingreso ningun texto.
    timeout /t 2 >nul
    goto BUCLE_PREDECIR
)

echo.
echo ------------------------------------------------------------------------------
echo Evaluando correo con modelo y explicabilidad (XAI)...
echo ------------------------------------------------------------------------------
python src/06_predecir.py "%texto_correo%"
echo ------------------------------------------------------------------------------
echo.
echo Presione cualquier tecla para clasificar otro texto...
pause >nul
goto BUCLE_PREDECIR
