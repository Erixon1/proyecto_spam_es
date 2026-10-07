# Detector de Spam Enron
Sistema integral de Procesamiento de Lenguaje Natural (NLP) y clasificación de correo Spam vs. Ham (legítimo) con soporte bilingüe (inglés/español), traducción neuronal automática (`MarianMT`), detección de idiomas (`langdetect`), calibración de umbrales óptimos ($\tau$), explicabilidad en tiempo real (XAI) y evaluación comparativa con modelos clásicos y Transformers (BETO).

---

## Estructura del Proyecto

```text
proyecto_spam_es/
  ejecutar_menu.bat       -> Lanzador principal interactivo (Panel de control)
  scripts/                -> Scripts batch (.bat) y PowerShell (.ps1) para ejecución paso a paso
  tests/                  -> Suite de pruebas unitarias automatizadas (pytest)
  src/
    01_extraer_hf.py      -> Extracción desde Hugging Face (train/test) o fallback local
    02_limpiar.py         -> Limpieza, deduplicación y truncamiento controlado (10k chars)
    03_preprocesar_nlp.py -> Tokenización preservativa, abreviaturas y censo de idiomas (langdetect)
    04_traducir_es.py     -> Traducción neuronal MarianMT (GPU/CPU) / Léxica con checkpoints
    05_entrenar.py        -> GridSearchCV (NB + LR), calibración de umbrales y explicabilidad (Log-Odds)
    06_predecir.py        -> Clasificador e inferencia en vivo con detección automática de idioma
    07_evaluacion_final.py-> Evaluación rigurosa en partición Held-Out (~2k muestras nunca vistas)
    08_transformer_es.py  -> Fine-tuning comparativo con BETO / DistilBERT multilingüe (Fase 4)
    generar_graficos.py   -> Generador de figuras de alta resolución (300 DPI) para documentación
    pipeline.py           -> Orquestador del flujo 01 -> 05 (+07 opcional)
    abreviaturas.py       -> Normalización, expansión de abreviaturas y glosario
    modelo_wrapper.py     -> Contenedor serializable con pipeline, umbral óptimo y explicabilidad
    traductor.py          -> Motor de traducción MarianMT en GPU/CPU + léxico
    config.py             -> Parámetros de rutas, semillas y configuración global
  notebooks/
    Proyecto_Spam_ES.ipynb-> Cuaderno interactivo con EDA, gráficos y soporte híbrido Local/Colab
  data/                   -> Almacenamiento versionado e inmutable por etapas (01_original a 04_traducido)
  models/                 -> Modelos serializados (spam_nb_en.pkl, spam_nb_es.pkl) y metricas.csv
  docs/
    graficos/             -> Figuras y gráficos diagnósticos en 300 DPI (distribución, ROC, PR, matrices)
    distribucion_idiomas.csv     -> Censo y proporciones de idiomas detectados en el dataset
    ejemplo_traducciones.csv     -> Muestras multilingües con idioma detectado y traducción al español
    diccionario_abreviaturas.csv -> Glosario de 67 abreviaturas y equivalencias documentadas
    evaluacion_heldout.csv       -> Resultados y métricas en partición de prueba inédita
    errores_*.csv                -> Auditoría detallada de errores (Falsos Positivos y Negativos)
```

---

## Novedades y Mejoras Implementadas

1. **Generación Automática de Gráficos por Etapa**: Cada script del pipeline (`01` al `07`) genera y guarda automáticamente su propio gráfico diagnóstico de alta resolución (300 DPI) en [`docs/graficos/`](file:///c:/Users/Nox/Documents/Grupo%205-Proyecto%20IA/Grupo%205/proyecto_spam_es/docs/graficos).
2. **Detección y Censo Lingüístico (`langdetect`)**: Identificación automática de idiomas presentes en el corpus (`docs/distribucion_idiomas.csv`) y enrutamiento dinámico en inferencia.
3. **Tokenización Preservativa de Señales Spam**: Preservación de URLs (`tokenurl`), divisas (`tokendinero`), exclamaciones (`tokenexclam`), correos (`tokenemail`) y números (`tokennumero`).
4. **Serialización Integral (`SpamClassifierWrapper`)**: El pipeline de Scikit-Learn viaja empaquetado junto a su umbral óptimo de decisión calibrado ($\tau$) y el motor de explicabilidad.
5. **Métricas Avanzadas y Curvas**: Reporte de **PR-AUC** y **ROC-AUC** junto a Precision, Recall y F1 estratificado con validación cruzada repetida (`RepeatedStratifiedKFold`).
6. **Explicabilidad (XAI)**: Extracción de los términos con mayor razón logarítmica de probabilidades (*Log-Odds*) hacia spam y ham en tiempo real.
7. **Módulo de Visualización Global (300 DPI)**: Script `generar_graficos.py` para exportar todas las figuras consolidadas del proyecto a `docs/graficos/`.
8. **Comparativa Transformer (Fase 4)**: Inclusión del script `08_transformer_es.py` para fine-tuning con `dccuchile/bert-base-spanish-wwm-cased` (BETO) o DistilBERT multilingüe.

---

## Guía de Comandos para Terminal

Ejecuta los siguientes comandos directamente en tu terminal (PowerShell o Bash) dentro de la carpeta del proyecto:

### 1. Instalación de Dependencias
```powershell
pip install -r requirements.txt
```

### 2. Ejecución Automatizada del Pipeline Completo
```powershell
# Ejecuta de 01 a 05 con traducción completa y evaluación Held-Out (07):
python src/pipeline.py --full --heldout

# O usando GPU con MarianMT para traducción neuronal:
python src/pipeline.py --marian --heldout
```

### 3. Ejecución Paso a Paso (Modular)
```powershell
# Etapa 01: Extracción y gráfico de distribución inicial
python src/01_extraer_hf.py

# Etapa 02: Limpieza, deduplicación y control de truncamiento (10k chars)
python src/02_limpiar.py

# Etapa 03: Preprocesamiento NLP, tokens y censo de idiomas
python src/03_preprocesar_nlp.py

# Etapa 04: Traducción (Léxica o Neuronal MarianMT en GPU)
python src/04_traducir_es.py --full
# O en GPU: python src/04_traducir_es.py --marian --resume

# Etapa 05: Entrenamiento, optimización GridSearch, umbrales y XAI
python src/05_entrenar.py

# Etapa 07: Evaluación rigurosa en test set Held-Out inédito
python src/07_evaluacion_final.py

# Generación del informe gráfico consolidado (300 DPI)
python src/generar_graficos.py
```

### 4. Clasificación e Inferencia en Vivo
```powershell
# Prueba en español con detección de señales spam y explicabilidad:
python src/06_predecir.py "¡Felicidades! Has ganado un premio en efectivo de $5000 dólares. Haz clic aquí para reclamar tu bono"

# Prueba en inglés (detección automática de idioma y traducción en vivo):
python src/06_predecir.py "Free prize money and urgent discount offer click here to win"
```

### 5. Ejecución de Pruebas Unitarias (Testing)
```powershell
# Ejecuta la suite completa de pruebas unitarias y validación
pytest tests/ -v
```

