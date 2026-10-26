"""Script de auditoría automatizada contra el banco de pruebas de correos bilingües."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import importlib.util

spec = importlib.util.spec_from_file_location("modulo_predecir", ROOT / "src" / "06_predecir.py")
modulo_predecir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo_predecir)
predecir = modulo_predecir.predecir


def ejecutar_banco_pruebas():
    ruta_json = ROOT / "data" / "pruebas_correos.json"
    if not ruta_json.exists():
        print(f"[!] No se encontró el archivo de pruebas: {ruta_json}")
        return

    with open(ruta_json, "r", encoding="utf-8") as f:
        casos = json.load(f)

    print("\n" + "="*80)
    print("      AUDITORÍA DEL BANCO DE PRUEBAS DE CORREOS (BILINGÜE EN / ES)")
    print("="*80)

    aciertos = 0
    total = len(casos)

    for c in casos:
        cid = c["id"]
        cat = c["categoria"]
        esperada = c["etiqueta_esperada"].upper()
        texto = c["texto"]
        
        res = predecir(texto)
        pred = res["etiqueta_tentativa"].upper()
        p_spam = res["p_spam"]
        idioma = res["idioma_detectado"]
        flujo = res["idioma_modelo"]
        
        ok = (pred == esperada)
        if ok:
            aciertos += 1
            icono = "[PASS]"
        else:
            icono = "[FAIL]"

        print(f"\n{icono} ID: {cid} | Cat: {cat}")
        print(f"       Idioma Detectado: {idioma} | Flujo: {flujo}")
        print(f"       Esperado: {esperada} | Predicho: {pred} | P(Spam): {p_spam:.3f} (Umbral: {res['umbral']})")
        
        if res["explicacion"]["tokens_spam"]:
            print(f"       Tokens Spam: {res['explicacion']['tokens_spam'][:3]}")
        if res["explicacion"]["tokens_ham"]:
            print(f"       Tokens Ham:  {res['explicacion']['tokens_ham'][:3]}")

    tasa = (aciertos / total) * 100
    print("\n" + "="*80)
    print(f"  RESUMEN DE PRUEBAS: {aciertos}/{total} pruebas superadas ({tasa:.1f}%)")
    print("="*80 + "\n")


if __name__ == "__main__":
    ejecutar_banco_pruebas()
