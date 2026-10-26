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
        modelo = cargar_modelo(MODELO_EN)
        idioma_modelo = "Inglés (Directo - Modelo Nativo EN)"
        texto_evaluar = texto_limpio
        modelo_path = MODELO_EN
    elif idioma_detectado == "es":
        modelo = cargar_modelo(MODELO_ES)
        idioma_modelo = "Español (Directo - Modelo Nativo ES)"
        texto_evaluar = texto_limpio
        modelo_path = MODELO_ES
    else:
        # Idioma terciario no soportado nativamente (ej. Francés, Alemán): traducir y clasificar en español
        modelo = cargar_modelo(MODELO_ES)
        texto_trad = traducir_entrada(texto)
        texto_evaluar = limpiar_rapido(texto_trad)
        idioma_modelo = f"Español (Detectado {idioma_detectado.upper()}, Traducido a ES)"
        modelo_path = MODELO_ES

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

    # Análisis de certidumbre / información disponible
    tokens_eval = [t for t in texto_evaluar.split() if len(t) > 1]
    num_tokens = len(tokens_eval)
    etiqueta_tentativa = "SPAM" if pred == 1 else "HAM"

    es_incierto = False
    motivo_incertidumbre = ""

    if num_tokens <= 4:
        es_incierto = True
        motivo_incertidumbre = f"Información insuficiente: correo muy escueto ({num_tokens} tokens tras limpieza)."
    elif abs(p_spam - umbral) < 0.15:
        es_incierto = True
        motivo_incertidumbre = f"Zona gris de incertidumbre: probabilidad P(Spam)={p_spam:.3f} muy cercana al umbral ({umbral:.2f})."

    etiqueta = "INCIERTO (Falta información)" if es_incierto else etiqueta_tentativa

    return {
        "etiqueta": etiqueta,
        "etiqueta_tentativa": etiqueta_tentativa,
        "es_incierto": es_incierto,
        "motivo_incertidumbre": motivo_incertidumbre,
        "p_spam": p_spam,
        "p_ham": p_ham,
        "umbral": umbral,
        "idioma_detectado": idioma_detectado.upper(),
        "idioma_modelo": idioma_modelo,
        "texto_procesado": texto_evaluar,
        "explicacion": explicacion,
        "modelo_path": modelo_path
    }


def cargar_pool():
    import json
    ruta_pool = Path(__file__).resolve().parents[1] / "docs" / "pool_correos_prueba.json"
    if ruta_pool.exists():
        with open(ruta_pool, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def listar_pool(pool):
    print("\n" + "=" * 70)
    print("         CATÁLOGO DE CORREOS DE PRUEBA (TESTING POOL)         ")
    print("=" * 70)
    print(f"{'ID':<4} | {'TIPO':<6} | {'IDIOMA':<6} | {'CATEGORÍA':<35} | {'ASUNTO'}")
    print("-" * 70)
    for it in pool:
        print(f"{it['id']:<4} | {it['tipo']:<6} | {it['idioma']:<6} | {it['categoria'][:35]:<35} | {it['asunto'][:35]}...")
    print("=" * 70)
    print("Para probar uno: python src/06_predecir.py <ID> (ejemplo: python src/06_predecir.py 2)")
    print("O para uno al azar: python src/06_predecir.py --azar\n")


def guardar_caso_incierto(texto_original, texto_procesado, idioma, p_spam, umbral, motivo):
    """Archiva un caso ambiguo o con información insuficiente para revisión sin tocar el modelo."""
    import csv
    from datetime import datetime
    ruta_csv = Path(__file__).resolve().parents[1] / "docs" / "casos_inciertos_revision.csv"
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    existe = ruta_csv.exists()
    with open(ruta_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["timestamp", "idioma", "p_spam", "umbral", "motivo", "texto_original", "texto_procesado"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), idioma, f"{p_spam:.3f}", f"{umbral:.2f}",
                    motivo, texto_original, texto_procesado])
    print(f"[i] Caso archivado con éxito en: docs/casos_inciertos_revision.csv")
    print("    (El modelo NO fue alterado para mantener protegida la estabilidad de sus pesos).")


def aplicar_aprendizaje_incremental(modelo_path, texto_procesado, label_code, texto_original, idioma, p_spam):
    """Aprende incrementalmente el nuevo patrón (Online Learning) y persiste el modelo."""
    import csv
    from datetime import datetime
    try:
        modelo = cargar_modelo(modelo_path)
        ok = modelo.partial_fit(texto_procesado, label_code)
        if not ok:
            print("[ERROR] El modelo cargado no soporta aprendizaje incremental (partial_fit).")
            return False

        with open(modelo_path, "wb") as f:
            pickle.dump(modelo, f)

        ruta_log = Path(__file__).resolve().parents[1] / "data" / "feedback" / "retroalimentacion_aprendizaje.csv"
        ruta_log.parent.mkdir(parents=True, exist_ok=True)
        existe = ruta_log.exists()
        etiqueta_txt = "SPAM" if label_code == 1 else "HAM"
        with open(ruta_log, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not existe:
                w.writerow(["timestamp", "idioma", "etiqueta_asignada", "p_spam_previa", "num_muestras_total", "texto_original", "texto_procesado"])
            w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), idioma, etiqueta_txt, f"{p_spam:.3f}",
                        modelo.metricas.get("n", "N/A"), texto_original, texto_procesado])

        print(f"[+] ¡APRENDIZAJE COMPLETADO! Modelo actualizado incrementalmente en {modelo_path.name}.")
        print(f"    Total de muestras integradas en el clasificador: {modelo.metricas.get('n', 'N/A')}")
        print(f"    Registro guardado en: data/feedback/retroalimentacion_aprendizaje.csv")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar el modelo: {e}")
        return False


def gestionar_feedback(res, texto_original):
    """Presenta el menú de retroalimentación interactiva con opción para casos inciertos."""
    print("-" * 65)
    print("¿Deseas retroalimentar al modelo con este caso para que aprenda?")
    print(" [1] Sí, clasificar y aprender como SPAM")
    print(" [2] Sí, clasificar y aprender como HAM (Legítimo)")
    print(" [3] Marcar como INCIERTO / DUDOSO (Falta información, archivar sin alterar modelo)")
    print(" [Enter] Omitir y continuar sin modificar nada")
    print("-" * 65)

    try:
        opc = input("Seleccione opción [1/2/3/Enter]: ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if opc == "1":
        aplicar_aprendizaje_incremental(res["modelo_path"], res["texto_procesado"], 1,
                                       texto_original, res["idioma_detectado"], res["p_spam"])
    elif opc == "2":
        aplicar_aprendizaje_incremental(res["modelo_path"], res["texto_procesado"], 0,
                                       texto_original, res["idioma_detectado"], res["p_spam"])
    elif opc == "3":
        motivo = res["motivo_incertidumbre"] if res["es_incierto"] else "Marcado manualmente como ambiguo por el usuario."
        guardar_caso_incierto(texto_original, res["texto_procesado"], res["idioma_detectado"],
                             res["p_spam"], res["umbral"], motivo)
    else:
        print("[i] Muestra omitida (no se realizaron cambios).")


def evaluar_y_mostrar(texto_a_evaluar, en_ingles=False, pool_item=None, permitir_feedback=True):
    res = predecir(texto_a_evaluar, en_ingles=en_ingles)

    print("\n" + "=" * 65)
    print("        RESULTADO DE CLASIFICACIÓN DE SPAM        ")
    print("=" * 65)
    if pool_item:
        print(f"[Pool #{pool_item['id']}] Categoría: {pool_item['categoria']} (Esperado: {pool_item['esperado']})")
        print(f"Asunto:           \"{pool_item['asunto']}\"")
    print(f"Texto evaluado:   \"{texto_a_evaluar}\"")
    print(f"Idioma detectado: {res['idioma_detectado']}")
    print(f"Flujo aplicado:   {res['idioma_modelo']}")
    print(f"Predicción:       >>> {res['etiqueta']} <<<")

    if res["es_incierto"]:
        print(f"[?] Diagnóstico:   {res['motivo_incertidumbre']}")
        print(f"[~] Tendencia:     {res['etiqueta_tentativa']} (Baja confianza, requiere confirmación).")

    if pool_item:
        if res["es_incierto"]:
            print(f"Validación Pool:  [ZONA GRIS - Inclinación coincide con {res['etiqueta_tentativa']}]")
        else:
            acierto = "ACIERTO (OK)" if res["etiqueta"] == pool_item["esperado"] else "FALLO (DISCORDANCIA)"
            print(f"Validación Pool:  [{acierto}]")

    print(f"Probabilidad:     P(Spam) = {res['p_spam']:.3f} | P(Ham) = {res['p_ham']:.3f}")
    print(f"Umbral decisión:  {res['umbral']:.2f}")

    if res["explicacion"]["tokens_spam"]:
        print(f"[!] Señales SPAM detectadas: {res['explicacion']['tokens_spam']}")
    if res["explicacion"]["tokens_ham"]:
        print(f"[+] Señales HAM detectadas:  {res['explicacion']['tokens_ham']}")
    print("=" * 65)

    if permitir_feedback:
        gestionar_feedback(res, texto_a_evaluar)
    else:
        print()



def resolver_texto(entrada, pool):
    """Determina si la entrada es un ID del pool o un texto personalizado."""
    entrada = entrada.strip()
    if entrada.isdigit() and pool:
        num = int(entrada)
        for it in pool:
            if it["id"] == num:
                return it["texto"], it
        print(f"[Aviso] No existe ID {num} en el pool. Evaluando como texto directo.")
    return entrada, None


def main():
    import random
    ap = argparse.ArgumentParser(description="Detector de Spam con detección automática de idioma, explicabilidad y pool de pruebas")
    ap.add_argument("texto", nargs="*", default=[], help="Texto del correo a clasificar, ID del pool (1-24) o 'listar'")
    ap.add_argument("--en", action="store_true", help="Forzar uso del modelo en inglés sin traducir")
    ap.add_argument("--pool", nargs="?", const="listar", default=None, help="Listar o seleccionar correo del pool por ID")
    ap.add_argument("--azar", action="store_true", help="Elegir y clasificar un correo al azar del pool de pruebas")
    ap.add_argument("--feedback", action="store_true", help="Habilitar menú de retroalimentación en ejecuciones por argumento")
    a = ap.parse_args()

    pool = cargar_pool()
    raw_texto = " ".join(a.texto).strip()

    # 1. Flag explícito --pool
    if a.pool:
        if a.pool == "listar":
            listar_pool(pool)
            return
        elif a.pool.isdigit():
            texto_eval, pool_item = resolver_texto(a.pool, pool)
            evaluar_y_mostrar(texto_eval, en_ingles=a.en, pool_item=pool_item, permitir_feedback=a.feedback)
            return

    # 2. Flag explícito --azar
    if a.azar:
        if not pool:
            print("[ERROR] No se encontró el pool de pruebas.")
            return
        item = random.choice(pool)
        evaluar_y_mostrar(item["texto"], en_ingles=a.en, pool_item=item, permitir_feedback=a.feedback)
        return

    # 3. Argumento pasado por línea de comandos
    if raw_texto:
        if raw_texto.lower() in ("listar", "pool", "p", "--pool"):
            listar_pool(pool)
            return
        texto_eval, pool_item = resolver_texto(raw_texto, pool)
        evaluar_y_mostrar(texto_eval, en_ingles=a.en, pool_item=pool_item, permitir_feedback=a.feedback)
        return

    # 4. Modo interactivo en vivo (si se ejecuta sin argumentos)
    print("\n" + "=" * 65)
    print("   DETECTOR DE SPAM EN VIVO - INGRESO DE TEXTO O POOL   ")
    print("=" * 65)
    print(" - Puedes escribir o pegar cualquier texto libre que desees.")
    print(" - O ingresar un número [1-24] para seleccionar del pool.")
    print(" - O escribir 'P' para ver el catálogo del pool.")
    print(" - O escribir 'A' para un correo al azar.")
    print(" - O escribir 'S' para salir y regresar al menú.\n")

    while True:
        try:
            entrada = input("Ingrese texto o ID: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo...")
            break

        if not entrada:
            continue
        if entrada.lower() in ("s", "salir", "exit", "quit"):
            print("Regresando al menú principal...")
            break
        if entrada.lower() in ("p", "pool", "listar"):
            listar_pool(pool)
            continue
        if entrada.lower() in ("a", "azar", "random"):
            item = random.choice(pool)
            evaluar_y_mostrar(item["texto"], en_ingles=a.en, pool_item=item, permitir_feedback=True)
            continue

        texto_eval, pool_item = resolver_texto(entrada, pool)
        evaluar_y_mostrar(texto_eval, en_ingles=a.en, pool_item=pool_item, permitir_feedback=True)


if __name__ == "__main__":
    main()

