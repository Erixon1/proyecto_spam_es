# Traducción y Preprocesamiento NLP

> 36 nodes · cohesion 0.10

## Key Concepts

- **traductor.py** (16 connections) — `src/traductor.py`
- **03_preprocesar_nlp.py** (11 connections) — `src/03_preprocesar_nlp.py`
- **traducir_lote()** (10 connections) — `src/traductor.py`
- **abreviaturas.py** (9 connections) — `src/abreviaturas.py`
- **traducir_texto_completo()** (9 connections) — `src/traductor.py`
- **expandir_abreviaturas()** (8 connections) — `src/abreviaturas.py`
- **traducir_lexico()** (8 connections) — `src/traductor.py`
- **corregir_typos()** (7 connections) — `src/abreviaturas.py`
- **re** (5 connections)
- **limpiar_texto_en()** (5 connections) — `src/03_preprocesar_nlp.py`
- **main()** (5 connections) — `src/03_preprocesar_nlp.py`
- **traducir_con_marian()** (5 connections) — `src/traductor.py`
- **traducir_texto()** (5 connections) — `src/traductor.py`
- **normalizar_tokens_post_traduccion()** (4 connections) — `src/traductor.py`
- **segmentar_en_oraciones()** (4 connections) — `src/traductor.py`
- **test_traducir_lexico_abreviaturas()** (4 connections) — `tests/test_traduccion.py`
- **detectar_idiomas()** (3 connections) — `src/03_preprocesar_nlp.py`
- **guardar_grafico_etapa03()** (3 connections) — `src/03_preprocesar_nlp.py`
- **test_traducir_lexico_frases_y_palabras()** (3 connections) — `tests/test_traduccion.py`
- **Path** (2 connections)
- **_cargar_marian()** (2 connections) — `src/traductor.py`
- **_detect()** (1 connections) — `src/03_preprocesar_nlp.py`
- **Etapa 03: preprocesamiento NLP en inglés. Entrada 02 -> Salida…** (1 connections) — `src/03_preprocesar_nlp.py`
- **Abreviaturas, correcciones y glosario EN -> ES. Objetivo: el dataset Enron está…** (1 connections) — `src/abreviaturas.py`
- **Expande abreviaturas inglesas usando un solo pase de regex precompilado.** (1 connections) — `src/abreviaturas.py`
- *... and 11 more nodes in this community*

## Relationships

- [Traducción EN-ES y Pruebas](Traducción_EN-ES_y_Pruebas.md) (9 shared connections)
- [Predicción y Feedback en Vivo](Predicción_y_Feedback_en_Vivo.md) (5 shared connections)
- [Ingesta de Datos y Entrenamiento](Ingesta_de_Datos_y_Entrenamiento.md) (4 shared connections)
- [Evaluación Final y Wrapper del Modelo](Evaluación_Final_y_Wrapper_del_Modelo.md) (2 shared connections)
- [Gráficos y Explicabilidad del Modelo](Gráficos_y_Explicabilidad_del_Modelo.md) (1 shared connections)

## Source Files

- `src/03_preprocesar_nlp.py`
- `src/abreviaturas.py`
- `src/traductor.py`
- `tests/test_traduccion.py`

## Audit Trail

- EXTRACTED: 68 (83%)
- INFERRED: 14 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*