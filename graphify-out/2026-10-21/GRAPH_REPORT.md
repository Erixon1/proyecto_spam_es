# Graph Report - proyecto_spam_es  (2026-10-21)

## Corpus Check
- 24 files · ~96,624 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 38 file(s) not represented in the graph (top: .bat 17, .csv 11, (none) 5)

## Summary
- 244 nodes · 397 edges · 14 communities (10 shown, 4 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9b5fcd46`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- traductor.py
- pathlib
- 06_predecir.py
- 🛑 Correos de SPAM en Español (IDs 1 al 8)
- 04_traducir_es.py
- generar_graficos.py
- SpamClassifierWrapper
- 05_entrenar.py
- Procesamiento y Tratamiento de Datos en el Pipeline de Clasificación de Spam
- Guía de Comandos para Terminal
- AGENTS.md

## God Nodes (most connected - your core abstractions)
1. `SpamClassifierWrapper` - 11 edges
2. `traducir_lote()` - 10 edges
3. `traducir_texto_completo()` - 9 edges
4. `🛑 Correos de SPAM en Español (IDs 1 al 8)` - 9 edges
5. `✅ Correos Legítimos (HAM) en Español (IDs 9 al 16)` - 9 edges
6. `main()` - 8 edges
7. `expandir_abreviaturas()` - 8 edges
8. `main()` - 8 edges
9. `traducir_lexico()` - 8 edges
10. `Procesamiento y Tratamiento de Datos en el Pipeline de Clasificación de Spam` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Novedades y Mejoras Implementadas` --references--> `SpamClassifierWrapper`  [INFERRED]
  README.md → src/modelo_wrapper.py
- `test_traducir_lexico_entradas_vacias_y_nulas()` --calls--> `traducir_lexico()`  [INFERRED]
  tests/test_traduccion.py → src/traductor.py
- `test_validar_entrada_columnas_faltantes()` --calls--> `validar_entrada()`  [INFERRED]
  tests/test_traduccion.py → src/04_traducir_es.py
- `test_validar_entrada_dataframe_vacio()` --calls--> `validar_entrada()`  [INFERRED]
  tests/test_traduccion.py → src/04_traducir_es.py
- `test_validar_entrada_valida()` --calls--> `validar_entrada()`  [INFERRED]
  tests/test_traduccion.py → src/04_traducir_es.py

## Import Cycles
- None detected.

## Communities (14 total, 4 thin omitted)

### Community 0 - "traductor.py"
Cohesion: 0.10
Nodes (16): detectar_idiomas(), guardar_grafico_etapa03(), limpiar_texto_en(), main(), corregir_typos(), expandir_abreviaturas(), _cargar_marian(), normalizar_tokens_post_traduccion() (+8 more)

### Community 1 - "pathlib"
Cohesion: 0.11
Nodes (9): empaquetar(), extraer_desde_hf(), guardar_grafico_etapa01(), main(), guardar_grafico_etapa02(), main(), cargar_datos(), entrenar_transformer() (+1 more)

### Community 2 - "06_predecir.py"
Cohesion: 0.15
Nodes (13): aplicar_aprendizaje_incremental(), cargar_modelo(), cargar_pool(), detectar_idioma(), evaluar_y_mostrar(), gestionar_feedback(), guardar_caso_incierto(), limpiar_rapido() (+5 more)

### Community 3 - "🛑 Correos de SPAM en Español (IDs 1 al 8)"
Cohesion: 0.07
Nodes (29): Catálogo de Correos de Prueba (Testing Pool) - Detector de Spam, 🛑 Correos de SPAM en Español (IDs 1 al 8), 🌐 Correos de SPAM en Inglés (IDs 17 al 20), ✅ Correos Legítimos (HAM) en Español (IDs 9 al 16), 🏢 Correos Legítimos (HAM) en Inglés - Estilo Enron (IDs 21 al 24), ID 10: Contrato Comercial de Suministro, ID 11: Finanzas Corporativas y Presupuesto, ID 12: Auditoría Interna y Cumplimiento (+21 more)

### Community 4 - "04_traducir_es.py"
Cohesion: 0.07
Nodes (17): finalizar(), guardar_diccionario(), guardar_grafico_etapa04(), main(), modo_lexico(), modo_marian(), muestra_estratificada(), sanear_textos() (+9 more)

### Community 5 - "generar_graficos.py"
Cohesion: 0.15
Nodes (7): graficar_comparativa_modelos(), graficar_curvas_roc_pr(), graficar_distribucion_clases(), graficar_distribucion_longitud(), graficar_explicabilidad_xai(), graficar_matrices_confusion(), main()

### Community 6 - "SpamClassifierWrapper"
Cohesion: 0.15
Nodes (5): cargar_test_hf(), guardar_grafico_etapa07(), limpiar_y_nlp(), main(), SpamClassifierWrapper

### Community 7 - "05_entrenar.py"
Cohesion: 0.26
Nodes (9): analisis_errores(), cv_repetida(), entrenar_corpus(), evaluar(), extraer_top_features(), guardar_grafico_etapa05(), main(), mejor_umbral() (+1 more)

### Community 11 - "Procesamiento y Tratamiento de Datos en el Pipeline de Clasificación de Spam"
Cohesion: 0.13
Nodes (14): 1. Arquitectura General del Pipeline de Datos, 2. Etapa 01: Extracción e Ingesta de Datos (`src/01_extraer_hf.py`), 3. Etapa 02: Limpieza y Saneamiento Estructural (`src/02_limpiar.py`), 4.1. Meta-Tokens de Dominio, 4.2. Normalización de Texto, 4.3. Normalización Léxica y Jerga (`src/abreviaturas.py`), 4.4. Detección y Censo Lingüístico (`langdetect`), 4. Etapa 03: Preprocesamiento NLP e Inyección de Meta-Tokens (`src/03_preprocesar_nlp.py`) (+6 more)

### Community 12 - "Guía de Comandos para Terminal"
Cohesion: 0.18
Nodes (10): 1. Instalación de Dependencias, 2. Ejecución Automatizada del Pipeline Completo, 3. Ejecución Paso a Paso (Modular), 4. Clasificación e Inferencia en Vivo, 5. Ejecución de Pruebas Unitarias (Testing), Detector de Spam Enron, Estructura del Proyecto, Guía de Comandos para Terminal (+2 more)

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpamClassifierWrapper` connect `SpamClassifierWrapper` to `06_predecir.py`, `Guía de Comandos para Terminal`, `generar_graficos.py`, `05_entrenar.py`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `SpamClassifierWrapper` (e.g. with `Novedades y Mejoras Implementadas` and `entrenar_corpus()`) actually correct?**
  _`SpamClassifierWrapper` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `traductor.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09682539682539683 - nodes in this community are weakly interconnected._
- **Why does `Novedades y Mejoras Implementadas` connect `Guía de Comandos para Terminal` to `SpamClassifierWrapper`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `traducir_lote()` (e.g. with `modo_marian()` and `main()`) actually correct?**
  _`traducir_lote()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.10837438423645321 - nodes in this community are weakly interconnected._
- **Should `🛑 Correos de SPAM en Español (IDs 1 al 8)` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._