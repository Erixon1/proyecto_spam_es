# Procesamiento y Tratamiento de Datos en el Pipeline de Clasificación de Spam

Este documento describe detalladamente la metodología, transformaciones y decisiones de ingeniería aplicadas durante el ciclo de vida del procesamiento de datos en el proyecto **Detector de Spam Enron Bilingüe**.

---

## 1. Arquitectura General del Pipeline de Datos

El tratamiento de los datos sigue una arquitectura modular y versionada en carpetas inmutables dentro del directorio `data/`:

```
data/
 ├── 01_original/    -> Extracción del corpus crudo (Hugging Face / Fallback local)
 ├── 02_limpio/      -> Limpieza estructural, deduplicación y truncamiento
 ├── 03_nlp/         -> Tokenización de meta-señales, lematización/abreviaturas y censo lingüístico
 └── 04_traducido/   -> Adaptación al español (Léxica o Neuronal con MarianMT)
```

---

## 2. Etapa 01: Extracción e Ingesta de Datos (`src/01_extraer_hf.py`)

- **Fuente Principal:** Conjunto de datos `SetFit/enron_spam` proveniente del repositorio de Hugging Face.
- **Protocolo de Carga con Respaldo Jerárquico:**
  1. *Carga directa HTTP:* Vía `pandas.read_json("hf://datasets/SetFit/enron_spam/train.jsonl", lines=True)`.
  2. *API Hugging Face `datasets`:* Fallback usando `datasets.load_dataset("SetFit/enron_spam")`.
  3. *Fallback Local:* En caso de desconexión a la red, se lee automáticamente el respaldo local en disco.
- **Trazabilidad:** Se crea una columna `split` (train/test) y una columna `fuente` para auditar el origen exacto de cada muestra.

---

## 3. Etapa 02: Limpieza y Saneamiento Estructural (`src/02_limpiar.py`)

Esta fase asegura la integridad estructural y elimina ruido estadístico que podría distorsionar el aprendizaje:

1. **Gestión de Nulos y Mapeo de Etiquetas:**
   - Detección y eliminación de registros sin cuerpo de mensaje (`dropna` sobre el campo textual).
   - Homogeneización de etiquetas a formato binario y textual: `ham` (legítimo $\rightarrow$ 0) y `spam` (no deseado $\rightarrow$ 1).
2. **Deduplicación:**
   - Eliminación de correos duplicados exactos (`drop_duplicates(subset=["Message"])`). Los duplicados artificiales sesgan la validación cruzada y sobreestiman el rendimiento.
3. **Filtrado por Longitud Mínima:**
   - Exclusión de mensajes con longitud $\le 5$ caracteres (mensajes vacíos, errores de parsing o firmas rotas).
4. **Control de Longitud Máxima y Truncamiento:**
   - **Límite:** 10,000 caracteres.
   - **Estrategia conservadora:** En lugar de descartar los correos largos (lo cual introduce sesgo de clase, pues correos con cadenas corporativas legítimas o reportes suelen ser extensos), se truncan a 10,000 caracteres y se crea la bandera booleana `truncado = 1` para auditoría.

---

## 4. Etapa 03: Preprocesamiento NLP e Inyección de Meta-Tokens (`src/03_preprocesar_nlp.py`)

A diferencia de una limpieza tradicional que elimina puntuación y símbolos indiscriminadamente, se implementó una **estrategia de preservación de señales fuertes de Spam**:

### 4.1. Meta-Tokens de Dominio
Antes de pasar el texto a minúsculas o retirar caracteres no alfanuméricos, las entidades sospechosas se sustituyen por meta-tokens especiales que conservan la semántica:
- **Enlaces y URLs:** Expresiones `https?://\S+|www\.\S+` $\longrightarrow$ `tokenurl`
- **Direcciones de correo:** Patrón `\S+@\S+` $\longrightarrow$ `tokenemail`
- **Símbolos monetarios y divisas:** `[\$€£]|(?:\b(?:usd|eur|dolares|dollars|pesos)\b)` $\longrightarrow$ `tokendinero`
- **Exclamaciones repetidas:** Uno o más signos `!` $\longrightarrow$ `tokenexclam`
- **Cifras y cantidades:** Secuencias numéricas `\d+` $\longrightarrow$ `tokennumero`

### 4.2. Normalización de Texto
- Conversión a minúsculas (`lowercase`).
- Eliminación de caracteres especiales no alfanuméricos conservando tildes y caracteres hispanos: `[^a-z0-9áéíóúñü_ ]`.
- Colapso de espacios en blanco consecutivos.

### 4.3. Normalización Léxica y Jerga (`src/abreviaturas.py`)
- **Expansión de Abreviaturas:** Diccionario de más de 65 contracciones y abreviaturas comunes en correos corporativos y técnicos en inglés (p. ej. *fyi* $\rightarrow$ *for your information*, *asap* $\rightarrow$ *as soon as possible*, *w/* $\rightarrow$ *with*).
- **Corrección de Typos Frecuentes:** Limpieza de errores comunes de escritura que dispersan el vocabulario.

### 4.4. Detección y Censo Lingüístico (`langdetect`)
- Se aplica la librería `langdetect` sobre una ventana de texto inicial de cada correo para censar la composición idiomática del corpus (inglés predominante, muestras residuales en otros idiomas).
- Esta metadata se exporta a [`docs/distribucion_idiomas.csv`](distribucion_idiomas.csv) y permite enrutar dinámicamente el modelo adecuado durante la inferencia en vivo.

---

## 5. Etapa 04: Traducción y Adaptación Bilingüe (`src/04_traducir_es.py` y `src/traductor.py`)

Para permitir la detección efectiva de Spam en español, se procesaron los datos mediante dos enfoques complementarios:

### 5.1. Modo Neuronal (Deep Learning - MarianMT)
- **Modelo:** `Helsinki-NLP/opus-mt-en-es` ejecutado en GPU (CUDA con soporte FP16 en Google Colab / local) o CPU.
- **Segmentación Inteligente por Oraciones (`--full-chunks`):**
  - Para evitar sobrepasar el límite de atención del modelo y prevenir pérdidas de información en correos extensos, los textos se dividen en fragmentos lógicos mediante expresiones regulares (`(?<=[.!?\n;:])\s+`) con un tope de **500 caracteres por fragmento** (`MARIAN_CHUNK_MAX_CHARS = 500`).
  - Cada fragmento se procesa con un `max_length` de generación de hasta **256 tokens** (o **128 tokens** en corridas rápidas/Colab con `batch_size = 64`).
  - Tras la inferencia, los fragmentos traducidos se concatenan reconstruyendo el correo completo sin pérdida de contexto.
- **Persistencia por Checkpoints:** Se guarda el progreso en `.tmp_checkpoint_neural.csv` a intervalos regulares (cada 200 filas por defecto), permitiendo pausar y reanudar (`--resume`) el procesamiento masivo en Colab sin pérdida de cómputo ante desconexiones.
- **Protección de Meta-Tokens:** Los meta-tokens (`tokenurl`, `tokendinero`, `tokenexclam`, etc.) se preservan intactos durante la traducción para no desvirtuar las señales discriminantes de spam.

### 5.2. Modo Léxico y Determinista (Fallback Rápido)
- Traducción basada en reglas y diccionarios de términos y frases clave de spam/ham sin requerir aceleración por hardware o conexión a internet.

---

## 6. Vectorización y Preparación para Modelado (`src/05_entrenar.py`)

Para el entrenamiento de los clasificadores (Multinomial Naive Bayes y Regresión Logística), la etapa final de preparación de características incluye:

1. **TF-IDF (Term Frequency - Inverse Document Frequency):**
   - Rango de n-gramas: Optimizado mediante búsqueda en cuadrícula entre unigramas y bigramas `(1, 1)` o `(1, 2)` para capturar combinaciones léxicas como *"gana dinero"* o *"haga clic"*.
   - Límite de vocabulario (`max_features`): Evaluado entre 5,000 y 10,000 términos más representativos.
   - Lista de palabras vacías (*Stopwords*): Integración de stopwords en español de NLTK (con lista local de respaldo).
2. **Estratificación y Validación Cruzada Repetida:**
   - División de conjuntos manteniendo la proporción de clases mediante `train_test_split` estratificado y `RepeatedStratifiedKFold`.
3. **Calibración de Umbral de Decisión ($\tau$):**
   - Búsqueda del umbral $\tau \in [0.2, 0.8]$ que maximiza el $F_1\text{-score}$ en validación interna para balancear la precisión y la recuperación según el costo de los Falsos Positivos.

---

## 7. Aprendizaje Continuo y Retroalimentación Incremental (Online Learning)

A partir de la integración del panel visual interactivo y la API REST en `src/servidor_web.py`:

1. **Entrenamiento Incremental en Caliente (`partial_fit`):**
   - Cuando un usuario corrige o confirma una predicción mediante la interfaz web, el clasificador ejecuta `wrapper.partial_fit(texto_limpio, etiqueta)`.
   - No requiere reentrenar los 28,000 correos desde cero; actualiza los vectores de recuento de palabras en milisegundos y re-serializa el modelo en disco (`spam_nb_es.pkl` o `spam_nb_en.pkl`).
2. **Auditoría de Impacto ($\Delta\%$):**
   - Se evalúa inmediatamente el correo tras el aprendizaje para registrar el antes vs. después (`probabilidad_spam_previa` $\rightarrow$ `probabilidad_spam_posterior`).
3. **Consolidación en `data/feedback/`:**
   - `historial_entrenamiento.jsonl`: Bitácora cronológica completa para alimentar la tabla web con acordeón desplegable.
   - `dataset_reentrenamiento.json`: Catálogo unificado, estructurado y sin duplicados para futuros reentrenamientos en bloque.

---

## 8. Resumen de Artefactos de Diagnóstico Generados

El tratamiento de los datos produce automáticamente registros reproducibles y visualizaciones a 300 DPI:
- **`docs/graficos/02_limpieza_duplicados_y_truncamiento.png`:** Flujo de retención de muestras y distribución de longitudes.
- **`docs/graficos/03_nlp_tokens_preservados.png`:** Frecuencia de aparición de meta-tokens y distribución de palabras limpias.
- **`docs/distribucion_idiomas.csv`:** Censo de idiomas del dataset.
- **`docs/diccionario_abreviaturas.csv`:** Catálogo de 67 abreviaturas y sus equivalencias.
