# Graph Report - proyecto_spam_es  (2026-10-26)

## Corpus Check
- 32 files · ~104,473 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 44 file(s) not represented in the graph (top: .bat 18, .csv 12, (none) 6)

## Summary
- 332 nodes · 505 edges · 18 communities (13 shown, 5 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 35 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d7bcabf5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Traducción y Preprocesamiento NLP
- Ingesta de Datos y Entrenamiento
- Predicción y Feedback en Vivo
- Catálogo de Correos de Prueba
- Traducción EN-ES y Pruebas
- Gráficos y Explicabilidad del Modelo
- servidor_web.py
- Entrenamiento del Corpus y Umbral
- Documentación del Pipeline de Datos
- Guía de Comandos para Terminal
- Instrucciones del Agente Graphify
- app.js
- SpamClassifierWrapper
- SpamClassifierWrapper

## God Nodes (most connected - your core abstractions)
1. `SpamClassifierWrapper` - 12 edges
2. `traducir_lote()` - 10 edges
3. `predecir()` - 9 edges
4. `traducir_texto_completo()` - 9 edges
5. `Procesamiento y Tratamiento de Datos en el Pipeline de Clasificación de Spam` - 9 edges
6. `🛑 Correos de SPAM en Español (IDs 1 al 8)` - 9 edges
7. `✅ Correos Legítimos (HAM) en Español (IDs 9 al 16)` - 9 edges
8. `expandir_abreviaturas()` - 8 edges
9. `traducir_lexico()` - 8 edges
10. `main()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `1. Lo que está BIEN en el Proyecto (Fortalezas Técnicas)` --references--> `SpamClassifierWrapper`  [INFERRED]
  docs/PLAN_ENTRENAMIENTO_Y_VISUAL.md → src/modelo_wrapper.py
- `Novedades y Mejoras Implementadas` --references--> `SpamClassifierWrapper`  [INFERRED]
  README.md → src/modelo_wrapper.py
- `ejecutar_banco_pruebas()` --calls--> `predecir()`  [INFERRED]
  scripts/probar_banco_correos.py → src/06_predecir.py
- `test_modo_lexico_completo()` --calls--> `modo_lexico()`  [INFERRED]
  tests/test_traduccion.py → src/04_traducir_es.py
- `test_muestra_estratificada_casos_borde()` --calls--> `muestra_estratificada()`  [INFERRED]
  tests/test_traduccion.py → src/04_traducir_es.py

## Import Cycles
- None detected.

## Communities (18 total, 5 thin omitted)

### Community 0 - "Traducción y Preprocesamiento NLP"
Cohesion: 0.09
Nodes (17): detectar_idiomas(), guardar_grafico_etapa03(), limpiar_texto_en(), main(), corregir_typos(), expandir_abreviaturas(), _cargar_marian(), normalizar_tokens_post_traduccion() (+9 more)

### Community 1 - "Ingesta de Datos y Entrenamiento"
Cohesion: 0.11
Nodes (9): empaquetar(), extraer_desde_hf(), guardar_grafico_etapa01(), main(), guardar_grafico_etapa02(), main(), cargar_datos(), entrenar_transformer() (+1 more)

### Community 2 - "Predicción y Feedback en Vivo"
Cohesion: 0.15
Nodes (13): aplicar_aprendizaje_incremental(), cargar_modelo(), cargar_pool(), detectar_idioma(), evaluar_y_mostrar(), gestionar_feedback(), guardar_caso_incierto(), limpiar_rapido() (+5 more)

### Community 3 - "Catálogo de Correos de Prueba"
Cohesion: 0.07
Nodes (29): Catálogo de Correos de Prueba (Testing Pool) - Detector de Spam, 🛑 Correos de SPAM en Español (IDs 1 al 8), 🌐 Correos de SPAM en Inglés (IDs 17 al 20), ✅ Correos Legítimos (HAM) en Español (IDs 9 al 16), 🏢 Correos Legítimos (HAM) en Inglés - Estilo Enron (IDs 21 al 24), ID 10: Contrato Comercial de Suministro, ID 11: Finanzas Corporativas y Presupuesto, ID 12: Auditoría Interna y Cumplimiento (+21 more)

### Community 4 - "Traducción EN-ES y Pruebas"
Cohesion: 0.15
Nodes (9): finalizar(), guardar_diccionario(), guardar_grafico_etapa04(), main(), modo_lexico(), modo_marian(), muestra_estratificada(), sanear_textos() (+1 more)

### Community 5 - "Gráficos y Explicabilidad del Modelo"
Cohesion: 0.08
Nodes (14): graficar_comparativa_modelos(), graficar_curvas_roc_pr(), graficar_distribucion_clases(), graficar_distribucion_longitud(), graficar_explicabilidad_xai(), graficar_matrices_confusion(), main(), test_modo_lexico_completo() (+6 more)

### Community 6 - "servidor_web.py"
Cohesion: 0.16
Nodes (3): ejecutar_banco_pruebas(), iniciar_servidor(), SpamRequestHandler

### Community 7 - "Entrenamiento del Corpus y Umbral"
Cohesion: 0.23
Nodes (9): analisis_errores(), cv_repetida(), entrenar_corpus(), evaluar(), extraer_top_features(), guardar_grafico_etapa05(), main(), mejor_umbral() (+1 more)

### Community 11 - "Documentación del Pipeline de Datos"
Cohesion: 0.13
Nodes (14): 1. Arquitectura General del Pipeline de Datos, 2. Etapa 01: Extracción e Ingesta de Datos (`src/01_extraer_hf.py`), 3. Etapa 02: Limpieza y Saneamiento Estructural (`src/02_limpiar.py`), 4.1. Meta-Tokens de Dominio, 4.2. Normalización de Texto, 4.3. Normalización Léxica y Jerga (`src/abreviaturas.py`), 4.4. Detección y Censo Lingüístico (`langdetect`), 4. Etapa 03: Preprocesamiento NLP e Inyección de Meta-Tokens (`src/03_preprocesar_nlp.py`) (+6 more)

### Community 12 - "Guía de Comandos para Terminal"
Cohesion: 0.17
Nodes (11): 1. Instalación de Dependencias, 2. Ejecución Automatizada del Pipeline Completo, 3. Ejecución Paso a Paso (Modular), 4. Clasificación e Inferencia en Vivo, 5. Panel Visual Interactivo y Servidor Web, 6. Ejecución de Pruebas Unitarias (Testing), Detector de Spam Enron, Estructura del Proyecto (+3 more)

### Community 14 - "app.js"
Cohesion: 0.05
Nodes (48): allHistoryGroups, btnClear, btnClearSearch, btnNextPage, btnPredict, btnPrevPage, btnRandomSample, btnTeachHam (+40 more)

### Community 15 - "SpamClassifierWrapper"
Cohesion: 0.18
Nodes (5): cargar_test_hf(), guardar_grafico_etapa07(), limpiar_y_nlp(), main(), SpamClassifierWrapper

### Community 16 - "SpamClassifierWrapper"
Cohesion: 0.09
Nodes (19): ❌ 1. Dependencia de Traducción Lenta en Tiempo Real para Correos en Inglés, 1. Lo que está BIEN en el Proyecto (Fortalezas Técnicas), ❌ 2. El Pipeline de Entrenamiento Entrena Modelos Separados pero no un Ensamble / Router Unificado, 2. Lo que está MAL o Requiere Corrección Crítica (Áreas de Mejora), 3. Plan de Acción: Entrenamiento Final Bilingüe (EN / ES), ❌ 3. Riesgo de Falsos Positivos en Correos Corporativos Legítimos (Ham), 4. Banco de Pruebas de Correos (Test Suite), ❌ 4. Falta un Banco de Pruebas Estandarizado de Correos (+11 more)

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpamClassifierWrapper` connect `SpamClassifierWrapper` to `Predicción y Feedback en Vivo`, `Gráficos y Explicabilidad del Modelo`, `Entrenamiento del Corpus y Umbral`, `Guía de Comandos para Terminal`, `SpamClassifierWrapper`?**
  _High betweenness centrality (0.203) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `SpamClassifierWrapper` (e.g. with `1. Lo que está BIEN en el Proyecto (Fortalezas Técnicas)` and `Novedades y Mejoras Implementadas`) actually correct?**
  _`SpamClassifierWrapper` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Traducción y Preprocesamiento NLP` be split into smaller, more focused modules?**
  _Cohesion score 0.08961593172119488 - nodes in this community are weakly interconnected._
- **Why does `7. Aprendizaje Continuo y Retroalimentación Incremental (Online Learning)` connect `SpamClassifierWrapper` to `Documentación del Pipeline de Datos`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `traducir_lote()` (e.g. with `modo_marian()` and `main()`) actually correct?**
  _`traducir_lote()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Ingesta de Datos y Entrenamiento` be split into smaller, more focused modules?**
  _Cohesion score 0.10837438423645321 - nodes in this community are weakly interconnected._
- **Why does `Procesamiento y Tratamiento de Datos en el Pipeline de Clasificación de Spam` connect `Documentación del Pipeline de Datos` to `SpamClassifierWrapper`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._