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
    06_predecir.py        -> Clasificador bilingüe e inferencia en vivo con detección automática de idioma
    07_evaluacion_final.py-> Evaluación rigurosa en partición Held-Out (~2k muestras nunca vistas)
    08_transformer_es.py  -> Fine-tuning comparativo con BETO / DistilBERT multilingüe (Fase 4)
    servidor_web.py       -> Servidor HTTP nativo en Python (sin dependencias) con endpoints REST
    generar_graficos.py   -> Generador de figuras de alta resolución (300 DPI) para documentación
    pipeline.py           -> Orquestador del flujo 01 -> 05 (+07 opcional)
    abreviaturas.py       -> Normalización, expansión de abreviaturas y glosario
    modelo_wrapper.py     -> Contenedor serializable con pipeline, umbral óptimo, explicabilidad y partial_fit
    traductor.py          -> Motor de traducción MarianMT en GPU/CPU + léxico
    config.py             -> Parámetros de rutas, semillas y configuración global
  web/                    -> Interfaz visual moderna (HTML5, Vanilla CSS plano, JavaScript reactivo)
    index.html            -> Panel de control, entrada de correos, XAI, historial paginado y buscador
    style.css             -> Diseño en dark mode y colores
    app.js                -> Lógica frontend: agrupación por mensaje, acordeón y filtros
  notebooks/
    Proyecto_Spam_ES.ipynb-> Cuaderno interactivo con EDA, gráficos y soporte híbrido Local/Colab
  data/                   -> Almacenamiento versionado e inmutable por etapas
    01_original a 04_traducido -> Datasets por etapas del pipeline de datos
    pruebas_correos.json  -> Banco estructurado de correos de prueba bilingües clasificados
    feedback/             -> Almacén de aprendizaje continuo y auditoría
      dataset_reentrenamiento.json   -> Catálogo consolidado y ordenado para futuros reentrenamientos en lote
      historial_entrenamiento.jsonl  -> Registro cronológico detallado de eventos y métricas (% antes/después)
  models/                 -> Modelos serializados (spam_nb_en.pkl, spam_nb_es.pkl) y metricas.csv
  docs/
    graficos/             -> Figuras y gráficos diagnósticos en 300 DPI (distribución, ROC, PR, matrices)
    PLAN_ENTRENAMIENTO_Y_VISUAL.md -> Diagnóstico crítico, arquitectura bilingüe y especificación del sistema
    distribucion_idiomas.csv     -> Censo y proporciones de idiomas detectados en el dataset
    ejemplo_traducciones.csv     -> Muestras multilingües con idioma detectado y traducción al español
    diccionario_abreviaturas.csv -> Glosario de 67 abreviaturas y equivalencias documentadas
    evaluacion_heldout.csv       -> Resultados y métricas en partición de prueba inédita
    errores_*.csv                -> Auditoría detallada de errores (Falsos Positivos y Negativos)
```

---

## Novedades y Mejoras Implementadas

1. **Panel Web Visual Interactivo (Dark Mode Profesional)**:
   - Servidor HTTP ligero y nativo en Python ([`src/servidor_web.py`](src/servidor_web.py)) sin requerir frameworks pesados externos.
   - Frontend moderno ([`web/`](web/)) con estética limpia, tipografía *Outfit*, diseño sin iconos genéricos ni gradientes, medidor de probabilidad y explicabilidad en tiempo real (XAI - Log-Odds).
2. **Enrutamiento Directo Bilingüe (EN/ES) de Baja Latencia**:
   - Correos en inglés usan directamente `spam_nb_en.pkl` y correos en español usan `spam_nb_es.pkl`, eliminando la latencia innecesaria de traducción neuronal MarianMT para inferencia (<2 ms).
3. **Aprendizaje Continuo en Caliente (Online Learning / Feedback)**:
   - Botones *"Enseñar que es SPAM"* y *"Enseñar que es HAM"* para reentrenar los pesos del modelo incrementalmente con `partial_fit`.
   - Comparación instantánea del impacto del aprendizaje: probabilidad previa vs. probabilidad posterior y variación ($\Delta\%$).
4. **Historial Inteligente con Sub-registros, Paginación y Buscador**:
   - **Agrupación por mensaje**: Los correos repetidos no saturan la tabla; muestran su última iteración y un badge de evaluaciones (`X evals`).
   - **Acordeón cronológico**: Al hacer clic en un mensaje, se despliega la sub-tabla con la evolución histórica completa de todas sus pruebas.
   - **Ordenamiento cronológico dinámico**: Se reordena automáticamente según la fecha más reciente de su última iteración.
   - **Paginación configurable**: 10 correos por página por defecto (configurable a 5, 25, 50 o Todos).
   - **Buscador en tiempo real**: Filtrado instantáneo por texto completo, texto resumido o idioma.
5. **Catálogo Consolidado de Reentrenamiento**:
   - Generación automática de [`data/feedback/dataset_reentrenamiento.json`](data/feedback/dataset_reentrenamiento.json) estructurado y listo para reentrenar en lote.
6. **Tokenización Preservativa de Señales Spam**: Preservación de URLs (`tokenurl`), divisas (`tokendinero`), exclamaciones (`tokenexclam`), correos (`tokenemail`) y números (`tokennumero`).
7. **Serialización Integral (`SpamClassifierWrapper`)**: El pipeline de Scikit-Learn viaja empaquetado junto a su umbral óptimo de decisión calibrado ($\tau$) y el motor de explicabilidad.
8. **Métricas Avanzadas y Curvas**: Reporte de **PR-AUC** y **ROC-AUC** junto a Precision, Recall y F1 estratificado con validación cruzada repetida (`RepeatedStratifiedKFold`).

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

# Etapa 04: Traducción (Léxica o Neuronal MarianMT en GPU sin truncar)
python src/04_traducir_es.py --full
# Traducción neuronal completa sin truncar (Recomendado Patch acelerado):
python src/04_traducir_es.py --marian --full-chunks --patch-existing --resume
# O re-traducción completa total desde cero:
python src/04_traducir_es.py --marian --full-chunks --resume

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

### 5. Panel Visual Interactivo y Servidor Web
```powershell
# Iniciar servidor web local (sin dependencias externas, Python puro):
python src/servidor_web.py

# O ejecutar el acceso directo para Windows:
scripts\ejecutar_servidor_web.bat
# Abrirá la aplicación en: http://localhost:8000
```

### 6. Ejecución de Pruebas Unitarias (Testing)
```powershell
# Ejecuta la suite completa de pruebas unitarias y validación
pytest tests/ -v
```
## Imagen del Flujo
<img width="2576" height="1438" alt="image" src="https://github.com/user-attachments/assets/0b4cee8a-7c7d-44d7-8827-7ddfd14a1d5e" />



