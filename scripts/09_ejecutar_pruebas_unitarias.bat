@echo off
cd /d "%~dp0.."
title Detector de Spam Enron - Suite de Pruebas Unitarias
cls

echo ==============================================================================
echo [TESTS] EJECUTANDO SUITE DE PRUEBAS UNITARIAS (PYTEST)
echo ==============================================================================
echo.
echo Evaluando calidad, saneamiento de nulos, traduccion y estratificacion...
echo Comando: pytest tests/ -v
echo.
python -m pytest tests/ -v
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==============================================================================
    echo [FALLO] Una o mas pruebas unitarias no pasaron. Revisa el log superior.
    echo ==============================================================================
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [EXITO] Todas las pruebas unitarias pasaron satisfactoriamente (10/10).
echo ==============================================================================
