@echo off
cd /d "%~dp0.."
title Generar Paquete para Google Colab
cls

echo ==============================================================================
echo GENERANDO PAQUETE LIGERO PARA GOOGLE COLAB (colab_pack.zip)
echo ==============================================================================
echo.
python scripts/empaquetar_para_colab.py
echo.
pause
