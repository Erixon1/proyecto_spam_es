"""Traductor EN -> ES con dos niveles: MarianMT (opcional) y léxico local (siempre disponible)."""
import re
from pathlib import Path
try:
    from abreviaturas import (
        FRASES_EN_ES, GLOSARIO_EN_ES, expandir_abreviaturas, corregir_typos,
    )
except ImportError:  # cuando se importa como paquete src.traductor
    from .abreviaturas import (
        FRASES_EN_ES, GLOSARIO_EN_ES, expandir_abreviaturas, corregir_typos,
    )

_MARIAN = None  # caché lazy (tokenizer, model, torch)


def _cargar_marian():
    global _MARIAN
    if _MARIAN is not None:
        return _MARIAN
    try:
        from transformers import MarianMTModel, MarianTokenizer
        import torch  # noqa
        nombre = "Helsinki-NLP/opus-mt-en-es"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tok = MarianTokenizer.from_pretrained(nombre)
        mod = MarianMTModel.from_pretrained(nombre).to(device).eval()
        print(f"[traductor] MarianMT en {device}.")
        _MARIAN = (tok, mod, device)
        return _MARIAN
    except Exception as e:
        print(f"[traductor] MarianMT no disponible ({e}); se usará léxico local.")
        _MARIAN = False
        return False


def traducir_con_marian(textos, batch_size=32, max_length=256):
    """Traduce lista de textos con Helsinki-NLP/opus-mt-en-es. Devuelve None si falla."""
    carga = _cargar_marian()
    if not carga:
        return None
    try:
        import torch
        tok, mod, device = carga
        salidas = []
        for i in range(0, len(textos), batch_size):
            lote = [t[:2000] for t in textos[i:i + batch_size]]
            enc = tok(lote, return_tensors="pt", padding=True, truncation=True,
                      max_length=max_length)
            enc = {k: v.to(device) for k, v in enc.items()}
            with torch.no_grad():
                gen = mod.generate(**enc, max_length=max_length)
            salidas.extend(tok.batch_decode(gen, skip_special_tokens=True))
        return salidas
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print("[traductor] OOM en GPU: reintenta con batch_size menor (16 u 8).")
        else:
            print(f"[traductor] Falló MarianMT en inferencia: {e}")
        return None
    except Exception as e:
        print(f"[traductor] Falló MarianMT en inferencia: {e}")
        return None


_PATRON_FRASES = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(FRASES_EN_ES.keys(), key=len, reverse=True)) + r")\b")


def traducir_lexico(texto_en: str) -> str:
    """Traducción determinista palabra por palabra (sin internet ni GPU)."""
    if not isinstance(texto_en, str) or not texto_en.strip():
        return ""
    t = _PATRON_FRASES.sub(lambda m: FRASES_EN_ES.get(m.group(0), m.group(0)), texto_en.lower())
    # Traducir token por token conservando acentos del glosario.
    tokens = re.findall(r"[a-záéíóúñü0-9_]+", t)
    traducidos = [GLOSARIO_EN_ES.get(tok, tok) for tok in tokens]
    return " ".join(traducidos)



def traducir_texto(texto_en: str, usar_marian=False) -> str:
    """Pipeline: expandir abreviaturas -> corregir typos -> traducir."""
    base = corregir_typos(expandir_abreviaturas(texto_en.lower() if isinstance(texto_en, str) else ""))
    if usar_marian:
        res = traducir_con_marian([base])
        if res:
            return res[0]
    return traducir_lexico(base)


def traducir_lote(textos, usar_marian=False, batch_size=64, max_length=128,
                  trunc_chars=600, progreso_cada=2000, checkpoint_csv=None):
    """Traduce lista completa.

    - usar_marian=True: MarianMT en GPU/CPU por lotes. Para hacerlo viable en
      28k correos largos, la entrada se pre-trunca a `trunc_chars` caracteres
      (la señal spam/ham está al inicio) y la salida a `max_length` tokens.
    - usar_marian=False: solo léxico (rápido, determinista).
    - checkpoint_csv: si se indica, tras cada bloque de `progreso_cada` filas
      se anexa lo avanzado (permite --resume aunque el proceso muera).
    """
    # Normalización previa común.
    bases = [corregir_typos(expandir_abreviaturas(t.lower() if isinstance(t, str) else ""))
             for t in textos]
    if usar_marian:
        recortados = [b[:trunc_chars] for b in bases]
        total = len(recortados)
        salidas = []
        for ini in range(0, total, progreso_cada):
            lote = recortados[ini:ini + progreso_cada]
            res = traducir_con_marian(lote, batch_size=batch_size, max_length=max_length)
            if res is None:
                print("[traductor] Falló MarianMT; el llamador decide (reintentar/lexico).")
                return None
            salidas.extend(res)
            print(f"[traductor] MarianMT: {min(ini + progreso_cada, total)}/{total}")
            if checkpoint_csv:
                import pandas as _pd
                _pd.DataFrame({"texto_es": res}).to_csv(
                    checkpoint_csv, mode="a", header=not Path(checkpoint_csv).exists(),
                    index=False, encoding="utf-8")
        return salidas
    return [traducir_lexico(b) for b in bases]
