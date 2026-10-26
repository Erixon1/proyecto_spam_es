@echo off
cd /d "%~dp0.."
title Detector de Spam Enron - Panel de Control Integral
cls

:MENU
cls
echo ==============================================================================
echo        DETECTOR DE SPAM ENRON (NLP BILINGUE EN/ES) - PANEL DE CONTROL
echo ==============================================================================
echo.
echo  [1] Iniciar Apartado Visual Web Interactivo (http://localhost:8000)
echo  [2] Probar Banco de Pruebas Automatizado (data/pruebas_correos.json)
echo  [3] Ejecutar Pipeline Completo (Etapas 01 a 05 - Traduccion Completa)
echo  [4] Ejecutar Suite de Pruebas Unitarias (pytest tests/ -v)
echo  [5] Submenu Paso a Paso (Ejecutar etapas 01 a 08 individualmente)
echo  [6] Probar Clasificador por Consola
echo  [7] Evaluacion Rigurosa en Particion Held-Out (Etapa 07)
echo  [8] Generar Graficos e Informes Diagnosticos (300 DPI)
echo  [9] Salir
echo.
echo ==============================================================================
set /p opcion="Seleccione una opcion [1-9]: "

if "%opcion%"=="1" (
    call scripts\iniciar_interfaz_web.bat
    goto PAUSA_MENU
) else if "%opcion%"=="2" (
    python scripts\probar_banco_correos.py
    goto PAUSA_MENU
) else if "%opcion%"=="3" (
    call scripts\pipeline_completo.bat
    goto PAUSA_MENU
) else if "%opcion%"=="4" (
    call scripts\09_ejecutar_pruebas_unitarias.bat
    goto PAUSA_MENU
) else if "%opcion%"=="5" (
    call scripts\submenu_pasos.bat
    goto MENU
) else if "%opcion%"=="6" (
    call scripts\06_probar_prediccion.bat
    goto MENU
) else if "%opcion%"=="7" (
    call scripts\07_evaluacion_heldout.bat
    goto PAUSA_MENU
) else if "%opcion%"=="8" (
    call scripts\10_generar_graficos.bat
    goto PAUSA_MENU
) else if "%opcion%"=="9" (
    exit /b
) else (
    echo.
    echo [ERROR] Opcion no valida. Por favor intente nuevamente.
    timeout /t 2 >nul
    goto MENU
)

:PAUSA_MENU
echo.
echo ==============================================================================
echo Presione cualquier tecla para regresar al menu principal...
pause >nul
goto MENU
