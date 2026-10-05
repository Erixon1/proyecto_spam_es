"""Etapa 01: extraer dataset original desde Hugging Face (SetFit/enron_spam).

Por defecto descarga SOLO el split train (31.716 filas), igual que la Celda 2
del notebook ProyectoIA.ipynb:
    pd.read_json("hf://datasets/SetFit/enron_spam/train.jsonl", lines=True)
    # respaldo: load_dataset("SetFit/enron_spam")["train"]

Salida: data/01_original/enron_original.csv (una fila = un correo, con columna split).
Con --with-test incluye también el split test.
Si HF no está disponible, usa como respaldo el CSV local de la carpeta padre
y lo marca como fuente 'local_fallback'.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import DATA_ORIGINAL, CSV_FALLBACK


def extraer_desde_hf(solo_train: bool = True) -> "pd.DataFrame":
    import pandas as pd
    # Intento 1: protocolo hf:// directo con pandas.
    try:
        df_tr = pd.read_json("hf://datasets/SetFit/enron_spam/train.jsonl", lines=True)
        df_tr["split"] = "train"
        if solo_train:
            df_tr["fuente"] = "hf_direct_train"
            return df_tr
        df_te = pd.read_json("hf://datasets/SetFit/enron_spam/test.jsonl", lines=True)
        df_te["split"] = "test"
        df = pd.concat([df_tr, df_te], ignore_index=True)
        df["fuente"] = "hf_direct"
        return df
    except Exception as e1:
        print(f"[01] hf:// falló: {e1}")
    # Intento 2: librería datasets.
    try:
        from datasets import load_dataset
        ds = load_dataset("SetFit/enron_spam")
        import pandas as pd
        if solo_train:
            df = pd.DataFrame(ds["train"])
            df["split"] = "train"
            df["fuente"] = "hf_datasets_api_train"
            return df
        partes = []
        for split in ds.keys():
            d = pd.DataFrame(ds[split])
            d["split"] = split
            partes.append(d)
        df = pd.concat(partes, ignore_index=True)
        df["fuente"] = "hf_datasets_api"
        return df
    except Exception as e2:
        print(f"[01] datasets API falló: {e2}")
        raise RuntimeError("No se pudo descargar desde HF") from e2


def guardar_grafico_etapa01(df: "pd.DataFrame", ruta_grafico: Path):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        ruta_grafico.parent.mkdir(parents=True, exist_ok=True)
        col_label = "label_text" if "label_text" in df.columns else "label"
        
        plt.figure(figsize=(7, 4.5), dpi=300)
        ax = sns.countplot(data=df, x=col_label, palette=["#2ecc71", "#e74c3c"], edgecolor="black", linewidth=0.6)
        total = len(df)
        for p in ax.patches:
            h = p.get_height()
            ax.annotate(f"{int(h):,} ({(h/total)*100:.1f}%)",
                        (p.get_x() + p.get_width() / 2., h),
                        ha="center", va="bottom", fontsize=10, fontweight="bold",
                        xytext=(0, 5), textcoords="offset points")
        plt.title("Etapa 01: Distribución Inicial de Clases (Dataset Crudo HF)", fontsize=12, fontweight="bold")
        plt.xlabel("Etiqueta Original", fontsize=10, fontweight="bold")
        plt.ylabel("Cantidad de Correos", fontsize=10, fontweight="bold")
        plt.tight_layout()
        plt.savefig(ruta_grafico, dpi=300)
        plt.close()
        print(f"[01] Gráfico generado -> {ruta_grafico}")
    except Exception as e:
        print(f"[01] Advertencia al generar gráfico: {e}")


def main(salida: Path = DATA_ORIGINAL, solo_train: bool = True):
    import pandas as pd
    try:
        df = extraer_desde_hf(solo_train=solo_train)
    except RuntimeError:
        print(f"[01] Usando respaldo local: {CSV_FALLBACK}")
        if not CSV_FALLBACK.exists():
            raise FileNotFoundError("Sin HF y sin respaldo local. No hay datos.")
        df = pd.read_csv(CSV_FALLBACK)
        if "split" not in df.columns:
            df["split"] = "local"
        df["fuente"] = "local_fallback"
    salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"[01] OK: {len(df)} filas x {len(df.columns)} cols -> {salida}")
    print(f"[01] Columnas: {list(df.columns)}")
    col_label = "label_text" if "label_text" in df.columns else "label"
    print(f"[01] Distribución {col_label}:\n{df[col_label].value_counts()}")
    
    # Generar gráfico respectivo de la Etapa 01
    grafico_path = salida.parents[2] / "docs" / "graficos" / "01_extraccion_distribucion_inicial.png"
    guardar_grafico_etapa01(df, grafico_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=str(DATA_ORIGINAL))
    ap.add_argument("--with-test", action="store_true",
                    help="Incluye el split test además de train")
    args = ap.parse_args()
    main(Path(args.salida), solo_train=not args.with_test)

