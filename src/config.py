"""Rutas y parámetros centrales del proyecto."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_ORIGINAL = ROOT / "data" / "01_original" / "enron_original.csv"
DATA_LIMPIO = ROOT / "data" / "02_limpio" / "enron_limpio.csv"
DATA_NLP = ROOT / "data" / "03_nlp" / "enron_nlp_en.csv"
DATA_TRADUCIDO = ROOT / "data" / "04_traducido" / "enron_traducido_es.csv"
DATA_NEURAL = ROOT / "data" / "04_traducido" / "enron_traducido_es_neural.csv"
TEST_EN = ROOT / "data" / "04_traducido" / "hf_test_en.csv"
TEST_ES = ROOT / "data" / "04_traducido" / "hf_test_es_neural.csv"
HELDOUT_CSV = ROOT / "docs" / "evaluacion_heldout.csv"
DICCIONARIO_CSV = ROOT / "docs" / "diccionario_abreviaturas.csv"
EJEMPLOS_CSV = ROOT / "docs" / "ejemplo_traducciones.csv"

MODELO_ES = ROOT / "models" / "spam_nb_es.pkl"
MODELO_EN = ROOT / "models" / "spam_nb_en.pkl"
METRICAS_CSV = ROOT / "models" / "metricas.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.20
# Usar --full en 04_traducir_es.py para traducir el dataset completo.
MUESTRA_TRADUCCION = 1500

# Hiperparámetros de traducción neuronal y checkpoints (04_traducir_es.py / traductor.py)
MARIAN_BATCH_SIZE = 64
MARIAN_MAX_LENGTH = 128
MARIAN_TRUNC_CHARS = 600
MARIAN_CHECKPOINT_INTERVAL = 2000

# Fallback al CSV ya existente en la carpeta padre (Grupo 5) si HF no está disponible.
CSV_FALLBACK = ROOT.parent / "enron_spam_cleaned.csv"
