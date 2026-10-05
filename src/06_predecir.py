"""Etapa 06: predicción con detección automática de idioma, umbral calibrado y explicabilidad.

Uso:
    python src/06_predecir.py "¡Felicidades! Ganaste dinero gratis haz clic aquí"
    python src/06_predecir.py "Please review the attached contract for the meeting"
    python src/06_predecir.py "Please review the attached contract" --en
"""
import argparse
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import MODELO_ES, MODELO_EN
from abreviaturas import expandir_abreviaturas, corregir_typos
from modelo_wrapper import SpamClassifierWrapper


def detectar_idioma(texto: str) -> str:
    """Detecta el código ISO de idioma (es, en, fr, de, etc.) usando langdetect."""
    if not isinstance(texto, str) or not texto.strip():
        return "es"
    try:
        from langdetect import detect
        return detect(texto)
    except Exception:
        # Fallback heurístico simple si el texto es muy corto o ambiguo
        palabras_en = {"the", "and", "is", "for", "you", "deal", "meeting", "please", "click", "money"}
        tokens = set(texto.lower().split())
        if len(tokens.intersection(palabras_en)) >= 2:
            return "en"
        return "es"


def limpiar_rapido(s: str) -> str:
    import re
    if not isinstance(s, str):
        return ""
    s = re.sub(r"https?://\S+|www\.\S+", " tokenurl ", s, flags=re.IGNORECASE)
    s = re.sub(r"\S+@\S+", " tokenemail ", s, flags=re.IGNORECASE)
    s = re.sub(r"[\$€£]|(?:\b(?:usd|eur|dolares|dollars|pesos)\b)", " tokendinero ", s, flags=re.IGNORECASE)
    s = re.sub(r"!{1,}", " tokenexclam ", s)
    s = re.sub(r"\d+", " tokennumero ", s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9áéíóúñü_ ]", " ", s)
    s = expandir_abreviaturas(s)
    s = corregir_typos(s)
    return re.sub(r"\s+", " ", s).strip()


def cargar_modelo(modelo_path):
    if not modelo_path.exists():
        raise FileNotFoundError(f"No se encontró el modelo en {modelo_path}. Ejecuta 05_entrenar.py primero.")
    with open(modelo_path, "rb") as f:
        return pickle.load(f)


def traducir_entrada(texto: str) -> str:
    """Traduce texto EN->ES con MarianMT si está disponible o léxico local."""
    try:
        from traductor import traducir_texto
        return traducir_texto(texto, usar_marian=True)
    except Exception:
        from traductor import traducir_texto
        return traducir_texto(texto, usar_marian=False)


def predecir(texto: str, en_ingles: bool = False):
    idioma_detectado = "en" if en_ingles else detectar_idioma(texto)
    texto_limpio = limpiar_rapido(texto)
    
    # Enrutamiento inteligente según idioma detectado
    if idioma_detectado == "en":
        if en_ingles:
            modelo = cargar_modelo(MODELO_EN)
            idioma_modelo = "Inglés (Directo)"
            texto_evaluar = texto_limpio
        else:
            modelo = cargar_modelo(MODELO_ES)
            texto_trad = traducir_entrada(texto)
            texto_evaluar = limpiar_rapido(texto_trad)
            idioma_modelo = f"Español (Traducido de {idioma_detectado.upper()})"
    elif idioma_detectado == "es":
        modelo = cargar_modelo(MODELO_ES)
        idioma_modelo = "Español (Directo)"
        texto_evaluar = texto_limpio
    else:
        # Idioma terciario (ej. Francés, Alemán): traducir y clasificar en español
        modelo = cargar_modelo(MODELO_ES)
        texto_trad = traducir_entrada(texto)
        texto_evaluar = limpiar_rapido(texto_trad)
        idioma_modelo = f"Español (Detectado {idioma_detectado.upper()}, Traducido)"

    # Comprobar si es un wrapper o pipeline crudo
    if isinstance(modelo, SpamClassifierWrapper):
        proba = modelo.predict_proba(texto_evaluar)[0]
        p_spam = float(proba[1])
        p_ham = float(proba[0])
        pred = modelo.predict(texto_evaluar)[0]
        umbral = modelo.umbral
        explicacion = modelo.explicar(texto_evaluar)
    else:
        proba = modelo.predict_proba([texto_evaluar])[0]
        p_spam = float(proba[1])
        p_ham = float(proba[0])
        umbral = 0.5
        pred = 1 if p_spam >= umbral else 0
        explicacion = {"tokens_spam": [], "tokens_ham": []}

    etiqueta = "SPAM" if pred == 1 else "HAM"
    return {
        "etiqueta": etiqueta,
        "p_spam": p_spam,
        "p_ham": p_ham,
        "umbral": umbral,
        "idioma_detectado": idioma_detectado.upper(),
        "idioma_modelo": idioma_modelo,
        "texto_procesado": texto_evaluar,
        "explicacion": explicacion
    }


def main():
    ap = argparse.ArgumentParser(description="Detector de Spam con detección automática de idioma y explicabilidad")
    ap.add_argument("texto", help="Texto del correo a clasificar")
    ap.add_argument("--en", action="store_true", help="Forzar uso del modelo en inglés sin traducir")
    a = ap.parse_args()
    
    res = predecir(a.texto, en_ingles=a.en)
    
    print("\n" + "=" * 55)
    print("        RESULTADO DE CLASIFICACIÓN DE SPAM        ")
    print("=" * 55)
    print(f"Texto evaluado:   \"{a.texto}\"")
    print(f"Idioma detectado: {res['idioma_detectado']}")
    print(f"Flujo aplicado:   {res['idioma_modelo']}")
    print(f"Predicción:       >>> {res['etiqueta']} <<<")
    print(f"Probabilidad:     P(Spam) = {res['p_spam']:.3f} | P(Ham) = {res['p_ham']:.3f}")
    print(f"Umbral decisión:  {res['umbral']:.2f}")
    
    if res["explicacion"]["tokens_spam"]:
        print(f"[!] Senales SPAM detectadas: {res['explicacion']['tokens_spam']}")
    if res["explicacion"]["tokens_ham"]:
        print(f"[+] Senales HAM detectadas:  {res['explicacion']['tokens_ham']}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
