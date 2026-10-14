"""Generador de paquete para Google Colab.

Empaqueta código fuente y datasets de entrada en 'colab_pack.zip' (~48 MB)
listo para subir a Google Drive o directamente a la sesión de Colab.
"""
import zipfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALIDA_ZIP = ROOT / "colab_pack.zip"

ARCHIVOS_REQUERIDOS = [
    ROOT / "data" / "03_nlp" / "enron_nlp_en.csv",
    ROOT / "data" / "04_traducido" / "enron_traducido_es_neural.csv",
    ROOT / "requirements.txt",
]

def empaquetar():
    print("[Colab Pack] Verificando archivos requeridos...")
    for f in ARCHIVOS_REQUERIDOS:
        if not f.exists():
            print(f"[ERROR] Archivo faltante: {f}")
            sys.exit(1)

    print(f"[Colab Pack] Creando '{SALIDA_ZIP.name}'...")
    with zipfile.ZipFile(SALIDA_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        # 1. Empaquetar todo el directorio src/
        for p in (ROOT / "src").rglob("*"):
            if p.is_file() and not p.name.endswith((".pyc", ".pyo")):
                rel = p.relative_to(ROOT)
                z.write(p, str(rel))
                
        # 2. Empaquetar archivos de datos y configuración
        for f in ARCHIVOS_REQUERIDOS:
            rel = f.relative_to(ROOT)
            print(f" -> Añadiendo: {rel} ({f.stat().st_size / (1024*1024):.1f} MB)")
            z.write(f, str(rel))

    tam_mb = SALIDA_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Paquete generado exitosamente: {SALIDA_ZIP} ({tam_mb:.1f} MB)")
    print("[Colab Pack] Listo para subir a Google Drive o Google Colab.")

if __name__ == "__main__":
    empaquetar()
