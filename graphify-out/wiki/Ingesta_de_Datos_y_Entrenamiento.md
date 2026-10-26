# Ingesta de Datos y Entrenamiento

> 29 nodes · cohesion 0.11

## Key Concepts

- **pathlib** (14 connections)
- **sys** (13 connections)
- **config.py** (12 connections) — `src/config.py`
- **01_extraer_hf.py** (8 connections) — `src/01_extraer_hf.py`
- **02_limpiar.py** (7 connections) — `src/02_limpiar.py`
- **08_transformer_es.py** (7 connections) — `src/08_transformer_es.py`
- **pipeline.py** (6 connections) — `src/pipeline.py`
- **empaquetar_para_colab.py** (5 connections) — `scripts/empaquetar_para_colab.py`
- **main()** (4 connections) — `src/01_extraer_hf.py`
- **entrenar_transformer()** (4 connections) — `src/08_transformer_es.py`
- **empaquetar()** (3 connections) — `scripts/empaquetar_para_colab.py`
- **guardar_grafico_etapa01()** (3 connections) — `src/01_extraer_hf.py`
- **guardar_grafico_etapa02()** (3 connections) — `src/02_limpiar.py`
- **main()** (3 connections) — `src/02_limpiar.py`
- **extraer_desde_hf()** (2 connections) — `src/01_extraer_hf.py`
- **Path** (2 connections)
- **Path** (2 connections)
- **cargar_datos()** (2 connections) — `src/08_transformer_es.py`
- **run()** (2 connections) — `src/pipeline.py`
- **subprocess** (2 connections)
- **zipfile** (2 connections)
- **Generador de paquete para Google Colab. Empaqueta código fuente y datasets de…** (1 connections) — `scripts/empaquetar_para_colab.py`
- **Etapa 01: extraer dataset original desde Hugging Face (SetFit/enron_spam). Por…** (1 connections) — `src/01_extraer_hf.py`
- **Etapa 02: limpieza. Entrada 01_original -> Salida 02_limpio/enron_limpio.csv.** (1 connections) — `src/02_limpiar.py`
- **compute_metrics()** (1 connections) — `src/08_transformer_es.py`
- *... and 4 more nodes in this community*

## Relationships

- [Predicción y Feedback en Vivo](Predicción_y_Feedback_en_Vivo.md) (7 shared connections)
- [Traducción EN-ES y Pruebas](Traducción_EN-ES_y_Pruebas.md) (6 shared connections)
- [Traducción y Preprocesamiento NLP](Traducción_y_Preprocesamiento_NLP.md) (4 shared connections)
- [Entrenamiento del Corpus y Umbral](Entrenamiento_del_Corpus_y_Umbral.md) (3 shared connections)
- [Evaluación Final y Wrapper del Modelo](Evaluación_Final_y_Wrapper_del_Modelo.md) (3 shared connections)
- [Gráficos y Explicabilidad del Modelo](Gráficos_y_Explicabilidad_del_Modelo.md) (3 shared connections)

## Source Files

- `scripts/empaquetar_para_colab.py`
- `src/01_extraer_hf.py`
- `src/02_limpiar.py`
- `src/08_transformer_es.py`
- `src/config.py`
- `src/pipeline.py`

## Audit Trail

- EXTRACTED: 68 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*