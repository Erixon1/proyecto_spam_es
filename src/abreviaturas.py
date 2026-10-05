"""Abreviaturas, correcciones y glosario EN -> ES.

Objetivo: el dataset Enron está en inglés con abreviaturas, slang y typos.
Aquí se (1) expanden a inglés formal y (2) se adaptan al español.
"""
import re

# Abreviatura EN (minúsculas) -> inglés formal expandido.
ABBR_EN_EXPANSION = {
    "u": "you", "ur": "your", "urs": "yours", "r": "are",
    "pls": "please", "plz": "please", "pl": "please",
    "asap": "as soon as possible", "btw": "by the way",
    "fyi": "for your information", "lol": "laughing out loud",
    "omg": "oh my god", "idk": "i do not know", "tbh": "to be honest",
    "imo": "in my opinion", "imho": "in my humble opinion",
    "fwd": "forward", "fw": "forward", "re": "regarding",
    "msg": "message", "msgs": "messages", "info": "information",
    "adv": "advertisement", "promo": "promotion",
    "dept": "department", "corp": "corporation", "inc": "incorporated",
    "ltd": "limited", "co": "company", "etc": "etcetera",
    "vs": "versus", "eg": "for example", "ie": "that is",
    "dont": "do not", "cant": "cannot", "wont": "will not",
    "im": "i am", "ive": "i have", "youve": "you have",
    "thx": "thanks", "tks": "thanks", "thankx": "thanks",
    "cuz": "because", "coz": "because", "bc": "because",
    "w": "with", "wo": "without", "b4": "before",
    "gr8": "great", "l8r": "later", "2morrow": "tomorrow",
    "2day": "today", "4u": "for you", "4": "for",
    "hrs": "hours", "hr": "hour", "min": "minute",
    "yr": "year", "yrs": "years", "tel": "telephone",
    "no": "number", "nr": "number", "acct": "account",
    "pwd": "password", "usr": "user", "svc": "service",
    "biz": "business", "corp": "corporation",
}

# Typos frecuentes en spam -> corrección inglesa.
CORRECCIONES_EN = {
    "recieve": "receive", "adress": "address", "seperate": "separate",
    "occured": "occurred", "guaranteeed": "guaranteed", "unbelivable": "unbelievable",
    "viagara": "viagra", "ciallis": "cialis", "monney": "money",
    "winnner": "winner", "congradulations": "congratulations",
    "oppurtunity": "opportunity", "busines": "business",
}

# Frases completas EN -> ES (se aplican antes que palabra por palabra).
FRASES_EN_ES = {
    "as soon as possible": "lo antes posible",
    "by the way": "por cierto",
    "for your information": "para tu información",
    "in my opinion": "en mi opinión",
    "to be honest": "para ser honesto",
    "free money": "dinero gratis",
    "click here": "haz clic aquí",
    "act now": "actúa ahora",
    "limited time": "tiempo limitado",
    "credit card": "tarjeta de crédito",
    "bank account": "cuenta bancaria",
}

# Glosario palabra EN -> ES (spam + corporativo Enron + general).
GLOSARIO_EN_ES = {
    # Spam clásico
    "free": "gratis", "money": "dinero", "cash": "efectivo", "prize": "premio",
    "winner": "ganador", "win": "ganar", "won": "ganó", "congratulations": "felicitaciones",
    "click": "clic", "offer": "oferta", "bonus": "bono", "discount": "descuento",
    "cheap": "barato", "buy": "comprar", "order": "pedido", "price": "precio",
    "urgent": "urgente", "account": "cuenta", "password": "contraseña",
    "verify": "verificar", "suspended": "suspendida", "limited": "limitado",
    "guaranteed": "garantizado", "opportunity": "oportunidad", "business": "negocio",
    "credit": "crédito", "loan": "préstamo", "debt": "deuda", "bank": "banco",
    "card": "tarjeta", "viagra": "viagra", "cialis": "cialis", "pharmacy": "farmacia",
    "pills": "pastillas", "weight": "peso", "loss": "pérdida",
    "please": "por favor", "thanks": "gracias", "hello": "hola", "hi": "hola",
    "dear": "estimado", "friend": "amigo", "team": "equipo",
    "message": "mensaje", "email": "correo", "mail": "correo",
    "information": "información", "promotion": "promoción",
    "advertisement": "anuncio", "company": "empresa", "service": "servicio",
    "customer": "cliente", "meeting": "reunión", "tomorrow": "mañana",
    "today": "hoy", "time": "tiempo", "day": "día", "week": "semana",
    "month": "mes", "year": "año", "hour": "hora", "minute": "minuto",
    "number": "número", "numero": "número", "telephone": "teléfono",
    "user": "usuario", "department": "departamento",
    # Corporativo Enron (se traducen, nombres propios se conservan)
    "energy": "energía", "power": "energía", "gas": "gas", "electricity": "electricidad",
    "contract": "contrato", "deal": "acuerdo", "trade": "comercio",
    "report": "informe", "attached": "adjunto", "forward": "reenviar",
    "regarding": "respecto a", "conference": "conferencia", "call": "llamada",
    "office": "oficina", "manager": "gerente", "president": "presidente",
    "you": "tú", "your": "tu", "are": "eres", "with": "con",
    "without": "sin", "before": "antes", "great": "genial", "later": "luego",
    "because": "porque", "thanks": "gracias",
    "software": "software", "computer": "computadora",
    "do": "haz", "not": "no", "know": "sé", "now": "ahora",
    "here": "aquí", "there": "allí", "this": "esto", "that": "eso",
    # Tokens especiales para señales fuertes de spam
    "tokenurl": "tokenurl", "tokenemail": "tokenemail",
    "tokendinero": "tokendinero", "tokencurrency": "tokendinero",
    "tokenexclam": "tokenexclam", "tokennumero": "tokennumero",
    "tokennumber": "tokennumero",
}

# Abreviatura EN -> equivalencia directa en español (para el diccionario docs/).
ABBR_EN_A_ES = {
    "pls": "por favor", "plz": "por favor", "asap": "lo antes posible",
    "btw": "por cierto", "fyi": "para tu información",
    "msg": "mensaje", "info": "información", "promo": "promoción",
    "acct": "cuenta", "pwd": "contraseña", "tel": "teléfono",
    "hrs": "horas", "u": "tú", "ur": "tu",
}


# Patrones precompilados de una sola pasada (optimización de alto rendimiento)
_PATRON_ABBR = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(ABBR_EN_EXPANSION.keys(), key=len, reverse=True)) + r")\b")
_PATRON_TYPOS = re.compile(r"\b(" + "|".join(re.escape(k) for k in sorted(CORRECCIONES_EN.keys(), key=len, reverse=True)) + r")\b")


def expandir_abreviaturas(texto: str) -> str:
    """Expande abreviaturas inglesas usando un solo pase de regex precompilado."""
    if not isinstance(texto, str) or not texto:
        return ""
    return _PATRON_ABBR.sub(lambda m: ABBR_EN_EXPANSION.get(m.group(0), m.group(0)), texto)


def corregir_typos(texto: str) -> str:
    """Corrige errores frecuentes de tipeo en una sola pasada."""
    if not isinstance(texto, str) or not texto:
        return ""
    return _PATRON_TYPOS.sub(lambda m: CORRECCIONES_EN.get(m.group(0), m.group(0)), texto)


