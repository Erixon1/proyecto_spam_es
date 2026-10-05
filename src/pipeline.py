"""Pipeline completo: ejecuta etapas 01 -> 05 en orden."""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
PY = sys.executable


def run(script, args=None):
    cmd = [PY, str(SRC / script)] + (args or [])
    print(f"\n===== {script} {' '.join(args or [])} =====")
    r = subprocess.run(cmd, cwd=str(SRC.parent))
    if r.returncode != 0:
        raise SystemExit(f"Falló {script}")
    return r


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--marian", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--heldout", action="store_true",
                    help="Evaluación final en split test de HF (07)")
    a = ap.parse_args()
    run("01_extraer_hf.py")
    run("02_limpiar.py")
    run("03_preprocesar_nlp.py")
    args4 = []
    if a.full:
        args4.append("--full")
    if a.marian:
        args4.append("--marian")
    run("04_traducir_es.py", args4)
    run("05_entrenar.py")
    if a.heldout:
        run("07_evaluacion_final.py")
    print("\nPipeline OK. Prueba: python src/06_predecir.py \"dinero gratis haz clic aquí\"")
