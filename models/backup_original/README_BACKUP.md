# Registro de Copia de Seguridad (Backup)

**Fecha de creación:** 26 de Octubre de 2026  
**Propósito:** Preservar los artefactos originales de modelos y bancos de prueba antes de cualquier sesión de entrenamiento adicional o modificación.

---

## 1. Modelos Respaldados
Ubicación: `models/backup_original/`

- **`spam_nb_en.pkl`**: Modelo base en inglés entrenado con el corpus Enron NLP limpio (28,806 muestras), con pipeline TF-IDF y MultinomialNB con umbral óptimo calibrado.
- **`spam_nb_es.pkl`**: Modelo base en español entrenado sobre el corpus neuronal completo (`enron_traducido_es_neural_full.csv`), calibrado con métrica $F_{0.5}$.
- **`metricas.csv`**: Registro oficial de métricas de validación cruzada y evaluación Held-Out de los modelos originales.

> **Importante:** Estos archivos en `models/backup_original/` son de solo lectura conceptual. No serán modificados por `partial_fit()`, scripts de entrenamiento ni por la interfaz web.

---

## 2. Banco de Pruebas Respaldado
Ubicación: `data/backup_pruebas/`

- **`pruebas_correos_original.json`**: Copia intacta del catálogo de casos de prueba iniciales (correos de phishing bancario, lotería, finanzas corporativas, camuflados y verídicos).

---

## 3. Procedimiento de Restauración Rápida
Si en algún momento deseas revertir los modelos a su estado original previo a los entrenamientos de prueba, puedes ejecutar en PowerShell:

```powershell
Copy-Item -Path 'models\backup_original\*' -Destination 'models\' -Force
Copy-Item -Path 'data\backup_pruebas\pruebas_correos_original.json' -Destination 'data\pruebas_correos.json' -Force
```
