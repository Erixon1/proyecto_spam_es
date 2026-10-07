"""Suite de pruebas unitarias para la etapa 04 de traducción y módulos de NLP."""
import sys
from pathlib import Path
import pytest
import pandas as pd

# Asegurar importación de src/
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from traductor import traducir_lexico, traducir_texto
from abreviaturas import expandir_abreviaturas, corregir_typos
from config import MUESTRA_TRADUCCION
from importlib import import_module

# Carga dinámica del módulo 04_traducir_es
etapa04 = import_module("04_traducir_es")
validar_entrada = etapa04.validar_entrada
sanear_textos = etapa04.sanear_textos
muestra_estratificada = etapa04.muestra_estratificada
modo_lexico = etapa04.modo_lexico


# ==========================================================
# 1. Pruebas de Traducción Léxica y Abreviaturas
# ==========================================================

def test_traducir_lexico_frases_y_palabras():
    """Verifica que el traductor léxico convierta frases y vocabulario clave a español."""
    texto = "free money click here"
    traducido = traducir_lexico(texto)
    assert "gratis" in traducido or "dinero" in traducido
    assert "haga clic" in traducido or "clic" in traducido


def test_traducir_lexico_abreviaturas():
    """Verifica la correcta expansión de abreviaturas comunes en correos electrónicos."""
    texto = "fyi please send the report asap"
    expandido = expandir_abreviaturas(texto)
    assert "for your information" in expandido
    assert "as soon as possible" in expandido
    
    traducido = traducir_texto(texto, usar_marian=False)
    assert isinstance(traducido, str)
    assert len(traducido) > 0


def test_traducir_lexico_entradas_vacias_y_nulas():
    """Verifica la robustez ante valores nulos, cadenas vacías y tipos no string."""
    assert traducir_lexico("") == ""
    assert traducir_lexico("   ") == ""
    assert traducir_lexico(None) == ""
    assert traducir_lexico(12345) == ""


# ==========================================================
# 2. Pruebas de Validación y Saneamiento de Datos
# ==========================================================

def test_validar_entrada_valida():
    """Verifica que un DataFrame con el esquema correcto pase la validación sin errores."""
    df_valido = pd.DataFrame({
        "clean_en": ["meeting tomorrow at office", "urgent win money click"],
        "Category": ["ham", "spam"],
        "Label_Code": [0, 1]
    })
    # No debe levantar excepción
    validar_entrada(df_valido, Path("dummy.csv"))


def test_validar_entrada_columnas_faltantes():
    """Verifica que falten columnas requeridas ('clean_en' o 'Category') levante ValueError descriptivo."""
    df_invalido = pd.DataFrame({
        "otro_texto": ["hello", "world"],
        "Category": ["ham", "spam"]
    })
    with pytest.raises(ValueError) as exc_info:
        validar_entrada(df_invalido, Path("dummy.csv"))
    assert "clean_en" in str(exc_info.value)


def test_validar_entrada_dataframe_vacio():
    """Verifica que un DataFrame vacío levante ValueError."""
    df_vacio = pd.DataFrame()
    with pytest.raises(ValueError) as exc_info:
        validar_entrada(df_vacio, Path("dummy_vacio.csv"))
    assert "vacío" in str(exc_info.value)


def test_sanear_textos_con_nulos():
    """Verifica que sanear_textos maneje correctamente NaNs sin generar cadenas 'nan'."""
    df_con_nulos = pd.DataFrame({
        "clean_en": ["valid text", None, "  spaced text  ", float("nan")],
        "Category": ["ham", "spam", "ham", "spam"]
    })
    df_limpio = sanear_textos(df_con_nulos)
    assert df_limpio["clean_en"].iloc[1] == ""
    assert df_limpio["clean_en"].iloc[2] == "spaced text"
    assert df_limpio["clean_en"].iloc[3] == ""
    assert df_limpio["clean_en"].isna().sum() == 0


# ==========================================================
# 3. Pruebas de Muestreo Estratificado
# ==========================================================

def test_muestra_estratificada_proporciones():
    """Verifica que el muestreo estratificado mantenga el ratio exacto entre clases."""
    # Dataset sintético de 100 filas: 80% ham, 20% spam
    df_sintetico = pd.DataFrame({
        "clean_en": [f"message {i}" for i in range(100)],
        "Category": ["ham"] * 80 + ["spam"] * 20,
        "Label_Code": [0] * 80 + [1] * 20
    })
    
    muestra_n = 20
    df_muestra = muestra_estratificada(df_sintetico, muestra=muestra_n, random_state=42)
    
    assert len(df_muestra) == muestra_n
    conteo = df_muestra["Category"].value_counts()
    # Debe ser exactamente 16 ham (80%) y 4 spam (20%)
    assert conteo["ham"] == 16
    assert conteo["spam"] == 4


def test_muestra_estratificada_casos_borde():
    """Verifica el comportamiento cuando la muestra pedida es mayor o igual al total."""
    df_sintetico = pd.DataFrame({
        "clean_en": ["msg1", "msg2", "msg3"],
        "Category": ["ham", "ham", "spam"]
    })
    
    # Muestra mayor o igual al total debe retornar copia completa
    assert len(muestra_estratificada(df_sintetico, muestra=10)) == 3
    assert len(muestra_estratificada(df_sintetico, muestra=0)) == 3
    assert len(muestra_estratificada(df_sintetico, muestra=-5)) == 3


def test_modo_lexico_completo():
    """Verifica la ejecución de modo_lexico devolviendo la columna 'texto_es' calculada."""
    df_test = pd.DataFrame({
        "clean_en": ["free money for everyone", "urgent meeting schedule"],
        "Category": ["spam", "ham"]
    })
    df_resultado = modo_lexico(df_test, muestra=0)
    assert "texto_es" in df_resultado.columns
    assert len(df_resultado["texto_es"]) == 2
    assert isinstance(df_resultado["texto_es"].iloc[0], str)
    assert len(df_resultado["texto_es"].iloc[0]) > 0
