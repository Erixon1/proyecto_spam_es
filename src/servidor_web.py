"""Servidor API HTTP nativo para la interfaz visual de clasificación de spam."""
import http.server
import importlib.util
import json
import socketserver
import sys
from pathlib import Path
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Importar función predecir de forma limpia
spec = importlib.util.spec_from_file_location("modulo_predecir", ROOT / "src" / "06_predecir.py")
modulo_predecir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo_predecir)
predecir = modulo_predecir.predecir

PORT = 8000
WEB_DIR = ROOT / "web"


class SpamRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        url_path = urllib.parse.urlparse(self.path).path
        if url_path == "/api/pruebas":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            ruta_pruebas = ROOT / "data" / "pruebas_correos.json"
            if ruta_pruebas.exists():
                with open(ruta_pruebas, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.wfile.write(b"[]")
            return
        if url_path == "/api/historial":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            historial_file = ROOT / "data" / "feedback" / "historial_entrenamiento.jsonl"
            historial = []
            if historial_file.exists():
                with open(historial_file, "r", encoding="utf-8") as f:
                    for linea in f:
                        if linea.strip():
                            try:
                                historial.append(json.loads(linea))
                            except Exception:
                                pass
            self.wfile.write(json.dumps(historial, ensure_ascii=False).encode("utf-8"))
            return

        # Servir archivos estáticos del frontend
        return super().do_GET()

    def do_POST(self):
        url_path = urllib.parse.urlparse(self.path).path
        if url_path == "/api/predecir":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode("utf-8"))
                texto = payload.get("texto", "")
                
                # Ejecutar predicción bilingüe en milisegundos
                resultado = predecir(texto)
                
                # Convertir a formato JSON serializable
                respuesta = {
                    "etiqueta": resultado["etiqueta"],
                    "etiqueta_tentativa": resultado["etiqueta_tentativa"],
                    "es_incierto": resultado["es_incierto"],
                    "motivo_incertidumbre": resultado["motivo_incertidumbre"],
                    "p_spam": round(resultado["p_spam"], 4),
                    "p_ham": round(resultado["p_ham"], 4),
                    "umbral": float(resultado["umbral"]),
                    "idioma_detectado": resultado["idioma_detectado"],
                    "idioma_modelo": resultado["idioma_modelo"],
                    "explicacion": resultado["explicacion"]
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(respuesta, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if url_path == "/api/feedback":
            import datetime
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode("utf-8"))
                texto = payload.get("texto", "").strip()
                etiqueta = int(payload.get("label", 0)) # 1 para spam, 0 para ham
                idioma = payload.get("idioma", "es").lower()
                p_spam_prev = float(payload.get("p_spam", 0.0))
                p_ham_prev = float(payload.get("p_ham", 0.0))
                pred_prev = payload.get("pred_prev", "DESCONOCIDO")
                umbral_actual = float(payload.get("umbral", 0.5))

                if not texto:
                    raise ValueError("El texto a entrenar está vacío.")

                # Crear registro detallado para el historial
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                etiqueta_humana = "SPAM" if etiqueta == 1 else "HAM"
                porcentaje_spam_prev = round(p_spam_prev * 100, 1)

                # Cargar el modelo wrapper correspondiente y ejecutar partial_fit
                import pickle
                from config import MODELO_ES, MODELO_EN
                modelo_path = MODELO_EN if idioma == "en" else MODELO_ES
                
                with open(modelo_path, "rb") as f:
                    wrapper = pickle.load(f)

                # Limpieza rápida del texto antes de entrenar
                texto_limpio = modulo_predecir.limpiar_rapido(texto)
                wrapper.partial_fit(texto_limpio, etiqueta)

                # Re-serializar el modelo actualizado
                with open(modelo_path, "wb") as f:
                    pickle.dump(wrapper, f)

                # Inferencia inmediata para medir el impacto directo del aprendizaje (Antes vs Después)
                proba_post = wrapper.predict_proba(texto_limpio)[0]
                p_spam_post = float(proba_post[1])
                pred_post_num = wrapper.predict(texto_limpio)[0]
                pred_post = "SPAM" if pred_post_num == 1 else "HAM"
                porcentaje_spam_post = round(p_spam_post * 100, 1)
                delta_spam = round(porcentaje_spam_post - porcentaje_spam_prev, 1)

                # Estructurar registro completo de antes y después
                registro_historial = {
                    "timestamp": timestamp_str,
                    "texto": texto,
                    "texto_resumen": (texto[:120] + "...") if len(texto) > 120 else texto,
                    "idioma": idioma.upper(),
                    "prediccion_previa": pred_prev,
                    "probabilidad_spam_previa": p_spam_prev,
                    "porcentaje_antes": f"{porcentaje_spam_prev}%",
                    "prediccion_posterior": pred_post,
                    "probabilidad_spam_posterior": p_spam_post,
                    "porcentaje_despues": f"{porcentaje_spam_post}%",
                    "cambio_delta": f"{'+' if delta_spam >= 0 else ''}{delta_spam}%",
                    "umbral": umbral_actual,
                    "etiqueta_ensenada": etiqueta_humana,
                    "era_correcto": (pred_prev == etiqueta_humana)
                }

                # Guardar en archivo persistente de historial de entrenamiento (jsonl)
                feedback_dir = ROOT / "data" / "feedback"
                feedback_dir.mkdir(parents=True, exist_ok=True)
                historial_file = feedback_dir / "historial_entrenamiento.jsonl"
                with open(historial_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(registro_historial, ensure_ascii=False) + "\n")

                # Sincronizar catálogo consolidado y ordenado en dataset_reentrenamiento.json
                dataset_json_file = feedback_dir / "dataset_reentrenamiento.json"
                try:
                    dataset_existente = []
                    if dataset_json_file.exists():
                        with open(dataset_json_file, "r", encoding="utf-8") as f:
                            dataset_existente = json.load(f)
                    
                    # Buscar si el texto ya existe para actualizarlo o insertarlo
                    item_encontrado = None
                    for item in dataset_existente:
                        if item.get("texto", "").strip() == texto:
                            item_encontrado = item
                            break
                    
                    if item_encontrado:
                        item_encontrado["etiqueta"] = etiqueta_humana
                        item_encontrado["label"] = etiqueta
                        item_encontrado["veces_entrenado"] = item_encontrado.get("veces_entrenado", 1) + 1
                        item_encontrado["ultima_fecha"] = timestamp_str
                        item_encontrado["ultima_probabilidad_spam"] = p_spam_post
                    else:
                        nuevo_id = f"fb_{len(dataset_existente) + 1:03d}"
                        dataset_existente.append({
                            "id": nuevo_id,
                            "fecha": timestamp_str,
                            "idioma": idioma.upper(),
                            "etiqueta": etiqueta_humana,
                            "label": etiqueta,
                            "texto": texto,
                            "veces_entrenado": 1,
                            "ultima_probabilidad_spam": p_spam_post
                        })
                    
                    with open(dataset_json_file, "w", encoding="utf-8") as f:
                        json.dump(dataset_existente, f, ensure_ascii=False, indent=2)
                except Exception as sync_err:
                    print(f"Aviso: No se pudo sincronizar dataset_reentrenamiento.json: {sync_err}")

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "mensaje": f"¡Entrenamiento asimilado! Spam: {porcentaje_spam_prev}% → {porcentaje_spam_post}% ({'+' if delta_spam >= 0 else ''}{delta_spam}%)",
                    "registro": registro_historial,
                    "total_muestras": wrapper.metricas.get("n", 0)
                }, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def iniciar_servidor():
    with socketserver.TCPServer(("", PORT), SpamRequestHandler) as httpd:
        print(f"\n========================================================")
        print(f"  PANEL VISUAL ACTIVO EN: http://localhost:{PORT}")
        print(f"  Servidor ligero sin dependencias externas.")
        print(f"  Presiona Ctrl+C para detener el servidor.")
        print(f"========================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == "__main__":
    iniciar_servidor()
