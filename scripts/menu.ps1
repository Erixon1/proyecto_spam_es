# ==============================================================================
# DETECTOR DE SPAM ENRON - PANEL DE CONTROL INTERACTIVO (PowerShell)
# ==============================================================================

Set-Location (Join-Path $PSScriptRoot "..")

function Mostrar-Menu {
    Clear-Host
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host "       DETECTOR DE SPAM ENRON (NLP BILINGUE EN/ES) - PANEL DE CONTROL         " -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1] Ejecutar Pipeline Completo (Etapas 01 a 05 - Traduccion Completa)" -ForegroundColor Green
    Write-Host "  [2] Ejecutar Pipeline Completo con GPU (Traduccion Neuronal MarianMT)" -ForegroundColor Yellow
    Write-Host "  [3] Ejecutar Suite de Pruebas Unitarias (pytest tests/ -v)" -ForegroundColor Magenta
    Write-Host "  [4] Submenu Paso a Paso (Ejecutar etapas 01 a 08 individualmente)" -ForegroundColor White
    Write-Host "  [5] Probar Clasificador e Inferencia en Vivo (Texto / Correo)" -ForegroundColor Cyan
    Write-Host "  [6] Evaluacion Rigurosa en Particion Held-Out (Etapa 07)" -ForegroundColor White
    Write-Host "  [7] Generar Graficos e Informes Diagnosticos (300 DPI)" -ForegroundColor White
    Write-Host "  [8] Instalar / Verificar Dependencias (requirements.txt)" -ForegroundColor White
    Write-Host "  [9] Salir" -ForegroundColor Red
    Write-Host ""
    Write-Host "==============================================================================" -ForegroundColor Cyan
}

while ($true) {
    Mostrar-Menu
    $opcion = Read-Host "Seleccione una opcion [1-9]"
    
    switch ($opcion) {
        "1" {
            & "$PSScriptRoot\pipeline_completo.bat"
            Write-Host ""
            Read-Host "Presione Enter para regresar al menu principal..."
        }
        "2" {
            & "$PSScriptRoot\04_traducir_neural.bat"
            Write-Host ""
            Read-Host "Presione Enter para regresar al menu principal..."
        }
        "3" {
            & "$PSScriptRoot\09_ejecutar_pruebas_unitarias.bat"
            Write-Host ""
            Read-Host "Presione Enter para regresar al menu principal..."
        }
        "4" {
            & "$PSScriptRoot\submenu_pasos.bat"
        }
        "5" {
            & "$PSScriptRoot\06_probar_prediccion.bat"
        }
        "6" {
            & "$PSScriptRoot\07_evaluacion_heldout.bat"
            Write-Host ""
            Read-Host "Presione Enter para regresar al menu principal..."
        }
        "7" {
            & "$PSScriptRoot\10_generar_graficos.bat"
            Write-Host ""
            Read-Host "Presione Enter para regresar al menu principal..."
        }
        "8" {
            & "$PSScriptRoot\00_instalar_dependencias.bat"
            Write-Host ""
            Read-Host "Presione Enter para regresar al menu principal..."
        }
        "9" {
            exit
        }
        default {
            Write-Host "[ERROR] Opcion no valida." -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}
