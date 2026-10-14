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
        if device == "cuda":
            try:
                mod = mod.half()
            except Exception:
                pass
        print(f"[traductor] MarianMT cargado en {device} (FP16={device == 'cuda'}).")
        _MARIAN = (tok, mod, device)
        return _MARIAN
    except Exception as e:
        print(f"[traductor] MarianMT no disponible ({e}); se usará léxico local.")
        _MARIAN = False
        return False


def traducir_con_marian(textos, batch_size=32, max_length=256, num_beams=1):
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
                gen = mod.generate(**enc, max_new_tokens=max_length, num_beams=num_beams)
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


def segmentar_en_oraciones(texto: str, max_chars_chunk: int = 500) -> list:
    """Divide un texto en fragmentos que preservan oraciones completas de hasta max_chars_chunk caracteres.
    
    Garantiza que ninguna oración quede truncada a mitad de frase ni se generen duplicaciones.
    """
    if not isinstance(texto, str) or not texto.strip():
        return []
    texto = texto.strip()
    if len(texto) <= max_chars_chunk:
        return [texto]

    # 1. Separar por límites de oración o saltos de línea sin perder puntuación
    oraciones_crudas = re.split(r'(?<=[.!?\n;:])\s+', texto)
    oraciones = []
    for orac in oraciones_crudas:
        orac = orac.strip()
        if not orac:
            continue
        if len(orac) <= max_chars_chunk:
            oraciones.append(orac)
        else:
            # Si una sola oración excede max_chars_chunk (ej. spam continuo sin puntuación), dividir por palabras
            palabras = orac.split()
            chunk_p = []
            len_p = 0
            for p in palabras:
                costo_p = len(p) + (1 if chunk_p else 0)
                if len_p + costo_p > max_chars_chunk and chunk_p:
                    oraciones.append(" ".join(chunk_p))
                    chunk_p = [p]
                    len_p = len(p)
                else:
                    chunk_p.append(p)
                    len_p += costo_p
            if chunk_p:
                oraciones.append(" ".join(chunk_p))

    # 2. Agrupar oraciones consecutivas en bloques contiguos de hasta max_chars_chunk
    bloques = []
    bloque_actual = []
    len_actual = 0
    for orac in oraciones:
        costo = len(orac) + (1 if bloque_actual else 0)
        if len_actual + costo > max_chars_chunk and bloque_actual:
            bloques.append(" ".join(bloque_actual))
            bloque_actual = [orac]
            len_actual = len(orac)
        else:
            bloque_actual.append(orac)
            len_actual += costo
    if bloque_actual:
        bloques.append(" ".join(bloque_actual))

    return bloques if bloques else [texto]


REZAGOS_FRASES_ES = {
    "original mail message": "mensaje de correo original",
    "original message": "mensaje original",
    "forwarded by": "reenviado por",
    "click here": "haga clic aquí",
    "act now": "actúe ahora",
    "as soon as possible": "lo antes posible",
    "for your information": "para su información",
    "by the way": "por cierto",
    "power trading": "comercio de energía",
    "energy services": "servicios de energía",
    "natural gas": "gas natural",
    "subject to": "sujeto a",
    "thank you": "gracias",
    "free money": "dinero gratis",
    "credit card": "tarjeta de crédito",
    "bank account": "cuenta bancaria",
}

REZAGOS_PALABRAS_ES = {
    # Cabeceras y metadatos de correo
    "subject": "asunto", "email": "correo", "emails": "correos",
    "mail": "correo", "mails": "correos", "message": "mensaje",
    "messages": "mensajes", "forward": "reenviar", "forwarded": "reenviado",
    "attached": "adjunto", "attachment": "archivo adjunto", "attn": "atención",
    "location": "ubicación",
    # Meses y días
    "january": "enero", "february": "febrero", "march": "marzo",
    "april": "abril", "may": "mayo", "june": "junio", "july": "julio",
    "august": "agosto", "september": "septiembre", "october": "octubre",
    "november": "noviembre", "december": "diciembre",
    "monday": "lunes", "tuesday": "martes", "wednesday": "miércoles",
    "thursday": "jueves", "friday": "viernes", "saturday": "sábado",
    "sunday": "domingo",
    # Términos corporativos y de Enron
    "office": "oficina", "offices": "oficinas", "energy": "energía",
    "power": "energía", "company": "empresa", "companies": "empresas",
    "business": "negocio", "businesses": "negocios", "deal": "acuerdo",
    "deals": "acuerdos", "trade": "comercio", "trades": "operaciones",
    "trading": "comercialización", "market": "mercado", "markets": "mercados",
    "price": "precio", "prices": "precios", "report": "informe",
    "reports": "informes", "meeting": "reunión", "meetings": "reuniones",
    "contract": "contrato", "contracts": "contratos", "department": "departamento",
    "manager": "gerente", "agreement": "acuerdo", "agreements": "acuerdos",
    "stock": "acciones", "stocks": "acciones", "customer": "cliente",
    "customers": "clientes", "client": "cliente", "clients": "clientes",
    "service": "servicio", "services": "servicios", "product": "producto",
    "products": "productos", "system": "sistema", "systems": "sistemas",
    "information": "información", "conference": "conferencia",
    # Términos de spam clásicos
    "free": "gratis", "click": "clic", "money": "dinero", "cash": "efectivo",
    "prize": "premio", "prizes": "premios", "winner": "ganador", "winners": "ganadores",
    "congratulations": "felicitaciones", "bonus": "bono", "discount": "descuento",
    "account": "cuenta", "accounts": "cuentas", "password": "contraseña",
    "passwords": "contraseñas", "urgent": "urgente", "verify": "verificar",
    "offer": "oferta", "offers": "ofertas", "order": "pedido", "orders": "pedidos",
    # Saludos y cortesía
    "dear": "estimado", "hello": "hola", "hi": "hola", "please": "por favor",
    "thanks": "gracias", "thank": "gracias", "welcome": "bienvenido",
    # Tiempo
    "today": "hoy", "tomorrow": "mañana", "yesterday": "ayer", "week": "semana",
    "weeks": "semanas", "month": "mes", "months": "meses", "year": "año",
    "years": "años", "hour": "hora", "hours": "horas", "minute": "minuto",
    "minutes": "minutos", "time": "tiempo", "daily": "diario",
    # Conectores y pronombres residuales
    "with": "con", "without": "sin", "for": "para", "from": "de",
    "you": "usted", "your": "su", "yours": "suyo", "we": "nosotros",
    "our": "nuestro", "ours": "nuestro", "they": "ellos", "their": "su",
    "theirs": "suyo", "have": "haber", "has": "ha", "had": "había",
    "can": "puede", "should": "debería", "would": "haría", "could": "podría",
    "phone": "teléfono", "call": "llamada", "number": "número",
    # Ofuscaciones típicas de spam (cambio de 'l' por 'i' o variantes fonéticas)
    "oniine": "en línea", "online": "en línea", "piease": "por favor",
    "soiutions": "soluciones", "soiution": "solución", "inciuding": "incluyendo",
    "resuits": "resultados", "resuit": "resultado", "resuiting": "resultando",
    "materialiy": "materialmente", "pubiisher": "editor", "circuiation": "circulación",
    "soiicitation": "solicitud", "teiecommunications": "telecomunicaciones",
    "revoiutioning": "revolucionando", "revoiution": "revolución",
    "buiiding": "construyendo", "chalienging": "desafiante",
    "caiils": "cialis", "cilais": "cialis", "spuer": "super", "suepr": "super",
    "vagira": "viagra", "viarga": "viagra", "virgaa": "viagra", "vigara": "viagra",
    "vairga": "viagra", "cilck": "clic", "intreseted": "interesado"
}


_PATRON_REZAGOS_FRASES = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(REZAGOS_FRASES_ES.keys(), key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE
)
_PATRON_REZAGOS_PALABRAS = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(REZAGOS_PALABRAS_ES.keys(), key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE
)


def normalizar_tokens_post_traduccion(texto: str) -> str:
    """Normaliza meta-tokens de spam preservados y corrige rezagos de traducción."""
    if not isinstance(texto, str) or not texto:
        return ""
    # 1. Pulir frases y palabras residuales en inglés que MarianMT omite
    t = _PATRON_REZAGOS_FRASES.sub(lambda m: REZAGOS_FRASES_ES[m.group(0).lower()], texto)
    t = _PATRON_REZAGOS_PALABRAS.sub(lambda m: REZAGOS_PALABRAS_ES[m.group(0).lower()], t)
    # 2. Evitar que subword tokenization separe los tokens estructurales de spam
    t = re.sub(r"\btoken\s*url\b", "tokenurl", t, flags=re.IGNORECASE)
    t = re.sub(r"\btoken\s*email\b", "tokenemail", t, flags=re.IGNORECASE)
    t = re.sub(r"\btoken\s*dinero\b", "tokendinero", t, flags=re.IGNORECASE)
    t = re.sub(r"\btoken\s*exclam\b", "tokenexclam", t, flags=re.IGNORECASE)
    t = re.sub(r"\btoken\s*n[uú]mero\b", "tokennumero", t, flags=re.IGNORECASE)
    t = re.sub(r"\bnumber\b", "número", t, flags=re.IGNORECASE)
    return t



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
    """Pipeline estándar de traducción para un único texto."""
    trad, _ = traducir_texto_completo(texto_en, usar_marian=usar_marian)
    return trad


def traducir_texto_completo(texto_en: str, usar_marian=True, max_chars_chunk=500, max_length=256) -> tuple:
    """Traduce un texto completo sin truncar, fragmentando en oraciones y reuniendo.
    
    Devuelve (texto_traducido, num_fragmentos).
    """
    if not isinstance(texto_en, str) or not texto_en.strip():
        return ("", 0)
    base = corregir_typos(expandir_abreviaturas(texto_en.lower()))
    if not usar_marian:
        return (traducir_lexico(base), 1)

    chunks = segmentar_en_oraciones(base, max_chars_chunk=max_chars_chunk)
    if not chunks:
        return ("", 0)

    res = traducir_con_marian(chunks, batch_size=len(chunks), max_length=max_length)
    if res is None:
        return (traducir_lexico(base), len(chunks))

    traducido = " ".join(res)
    traducido = normalizar_tokens_post_traduccion(traducido)
    return (traducido, len(chunks))


def traducir_lote(textos, usar_marian=False, batch_size=64, max_length=256,
                  trunc_chars=0, max_chars_chunk=500, progreso_cada=200,
                  checkpoint_csv=None, return_num_fragmentos=False,
                  num_beams=1):
    """Traduce lista completa de textos.
    
    - usar_marian=True:
        - Si trunc_chars > 0: modo recorte rápido (trunc_chars caracteres iniciales).
        - Si trunc_chars == 0 o None: modo completo sin truncar mediante segmentación por
          oraciones (sentence bundling), aplanamiento en GPU y reensamblado exacto.
    - usar_marian=False: solo léxico determinista.
    - checkpoint_csv: si se indica, tras cada bloque de progreso_cada filas se anexa
      el avance a disco con texto_es y num_fragmentos.
    """
    import pandas as _pd
    bases = [corregir_typos(expandir_abreviaturas(t.lower() if isinstance(t, str) else ""))
             for t in textos]
    
    if not usar_marian:
        res = [traducir_lexico(b) for b in bases]
        if return_num_fragmentos:
            return res, [1] * len(res)
        return res

    total = len(bases)
    salidas = []
    fragmentos_totales = []

    # 1. Modo legacy recortado (si trunc_chars > 0)
    if trunc_chars and trunc_chars > 0:
        recortados = [b[:trunc_chars] for b in bases]
        for ini in range(0, total, progreso_cada):
            fin = min(ini + progreso_cada, total)
            lote = recortados[ini:fin]
            res = traducir_con_marian(lote, batch_size=batch_size, max_length=max_length, num_beams=num_beams)
            if res is None:
                print("[traductor] Falló MarianMT; devolviendo None para reintento.")
                return None
            res = [normalizar_tokens_post_traduccion(t) for t in res]
            salidas.extend(res)
            fragmentos_totales.extend([1] * len(res))
            pct = (fin / total) * 100
            print(f"[traductor] MarianMT (recortado): {fin}/{total} ({pct:.1f}%)")
            if checkpoint_csv:
                df_ck = _pd.DataFrame({"texto_es": res, "num_fragmentos": [1] * len(res)})
                df_ck.to_csv(checkpoint_csv, mode="a",
                             header=not Path(checkpoint_csv).exists(),
                             index=False, encoding="utf-8")
        if return_num_fragmentos:
            return salidas, fragmentos_totales
        return salidas

    # 2. Modo Completo sin Truncar (A+B+C: Segmentación por oraciones y aplanamiento GPU)
    print(f"[traductor] Iniciando traducción completa sin truncar (max_chars_chunk={max_chars_chunk}, max_length={max_length}, num_beams={num_beams})...")
    for ini in range(0, total, progreso_cada):
        fin = min(ini + progreso_cada, total)
        lote_bases = bases[ini:fin]
        
        # Segmentar cada texto del bloque
        doc_chunks = [segmentar_en_oraciones(b, max_chars_chunk=max_chars_chunk) or [b]
                      for b in lote_bases]
        counts = [len(c) for c in doc_chunks]
        flat_chunks = [c for c_list in doc_chunks for c in c_list]
        
        # Traducir los fragmentos en lotes continuos en GPU
        flat_res = traducir_con_marian(flat_chunks, batch_size=batch_size, max_length=max_length, num_beams=num_beams)
        if flat_res is None:
            print("[traductor] Falló MarianMT en bloque de fragmentos.")
            return None
            
        # Reensamblar textos respetando sus fragmentos originales
        curr = 0
        lote_ensamblado = []
        for cnt in counts:
            piezas = flat_res[curr:curr + cnt]
            doc_es = normalizar_tokens_post_traduccion(" ".join(piezas))
            lote_ensamblado.append(doc_es)
            curr += cnt
            
        salidas.extend(lote_ensamblado)
        fragmentos_totales.extend(counts)
        pct = (fin / total) * 100
        print(f"[traductor] MarianMT (completo): {fin}/{total} correos ({pct:.1f}%) [{len(flat_chunks)} fragmentos GPU]")
        
        if checkpoint_csv:
            df_ck = _pd.DataFrame({"texto_es": lote_ensamblado, "num_fragmentos": counts})
            df_ck.to_csv(checkpoint_csv, mode="a",
                         header=not Path(checkpoint_csv).exists(),
                         index=False, encoding="utf-8")

    if return_num_fragmentos:
        return salidas, fragmentos_totales
    return salidas

