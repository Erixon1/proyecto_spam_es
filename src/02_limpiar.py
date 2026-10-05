"""Etapa 02: limpieza. Entrada 01_original -> Salida 02_limpio/enron_limpio.csv."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import DATA_ORIGINAL, DATA_LIMPIO


def guardar_grafico_etapa02(stats: dict, df_clean: "pd.DataFrame", ruta_grafico: Path):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        ruta_grafico.parent.mkdir(parents=True, exist_ok=True)
        
        fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
        
        # Panel 1: Flujo de limpieza y retención de registros
        etapas = ["Inicial", "Sin Nulos", "Sin Duplicados", "Filtrado Final"]
        valores = [stats["inicial"], stats["sin_nulos"], stats["sin_dup"], stats["final"]]
        colores = ["#3498db", "#9b59b6", "#f39c12", "#2ecc71"]
        
        bars = axes[0].bar(etapas, valores, color=colores, edgecolor="black", linewidth=0.8)
        for b in bars:
            h = b.get_height()
            pct = (h / stats["inicial"]) * 100
            axes[0].annotate(f"{int(h):,}\n({pct:.1f}%)",
                             (b.get_x() + b.get_width() / 2., h),
                             ha="center", va="bottom", fontsize=9, fontweight="bold",
                             xytext=(0, 3), textcoords="offset points")
        axes[0].set_title("Flujo de Limpieza y Reducción de Muestras", fontsize=11, fontweight="bold")
        axes[0].set_ylabel("Cantidad de Correos", fontsize=10, fontweight="bold")
        axes[0].grid(axis="y", linestyle="--", alpha=0.5)
        
        # Panel 2: Distribución de longitudes y control de truncamiento
        sns.histplot(data=df_clean, x="longitud_correo", hue="Category",
                     palette={"ham": "#2ecc71", "spam": "#e74c3c"},
                     bins=40, log_scale=(True, False), ax=axes[1], kde=True, edgecolor="black", linewidth=0.5)
        axes[1].axvline(10000, color="purple", linestyle="--", linewidth=1.5,
                        label=f"Límite Truncamiento ({stats['truncados']} correos)")
        axes[1].set_title("Distribución de Longitud de Caracteres (Escala Log)", fontsize=11, fontweight="bold")
        axes[1].set_xlabel("Longitud del Correo (Caracteres)", fontsize=10, fontweight="bold")
        axes[1].set_ylabel("Frecuencia", fontsize=10, fontweight="bold")
        axes[1].legend(loc="upper right")
        axes[1].grid(True, linestyle="--", alpha=0.5)
        
        plt.suptitle("Etapa 02: Diagnóstico de Limpieza, Deduplicación y Truncamiento", fontsize=13, fontweight="bold", y=1.02)
        plt.tight_layout()
        plt.savefig(ruta_grafico, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"[02] Gráfico generado -> {ruta_grafico}")
    except Exception as e:
        print(f"[02] Advertencia al generar gráfico: {e}")


def main(entrada: Path = DATA_ORIGINAL, salida: Path = DATA_LIMPIO):
    import pandas as pd
    import numpy as np
    df = pd.read_csv(entrada)
    n_inicial = len(df)
    print(f"[02] Entrada: {n_inicial} filas")
    print(f"[02] Nulos:\n{df.isnull().sum()}")

    col_texto = "text" if "text" in df.columns else ("Message" if "Message" in df.columns else "message")
    df = df.dropna(subset=[col_texto]).copy()
    n_sin_nulos = len(df)
    print(f"[02] Tras eliminar nulos en texto: {n_sin_nulos} filas")
    df["Message"] = df[col_texto].astype(str)
    if "label_text" in df.columns:
        df["Category"] = df["label_text"].astype(str).str.lower().replace({"0": "ham", "1": "spam"})
        mask_mala = ~df["Category"].isin(["ham", "spam"])
        if "label" in df.columns:
            df.loc[mask_mala, "Category"] = df.loc[mask_mala, "label"].map({0: "ham", 1: "spam"})
    elif "Category" not in df.columns:
        df["Category"] = df["label"].map({0: "ham", 1: "spam"})
    df = df.dropna(subset=["Category"]).copy()
    df["Label_Code"] = df["Category"].map({"ham": 0, "spam": 1})

    df["longitud_correo"] = df["Message"].apply(lambda x: len(x) if isinstance(x, str) else 0)
    df_clean = df.copy()
    dup = int(df_clean.duplicated(subset=["Message"]).sum())
    print(f"[02] Duplicados por mensaje: {dup}")
    df_clean = df_clean.drop_duplicates(subset=["Message"]).copy()
    n_sin_dup = len(df_clean)
    antes = len(df_clean)
    df_clean = df_clean[df_clean["longitud_correo"] > 5].copy()
    print(f"[02] Eliminados por longitud<=5: {antes - len(df_clean)}")
    
    MAX_LEN = 10000
    largos = df_clean["longitud_correo"] > MAX_LEN
    n_out = int(largos.sum())
    print(f"[02] Correos >{MAX_LEN} caracteres (a truncar, no eliminar): {n_out}")
    if n_out:
        print("[02] Sesgo en largos (por clase, ANTES de truncar):")
        print(df_clean.loc[largos, "Category"].value_counts().to_dict())
        df_clean.loc[largos, "Message"] = df_clean.loc[largos, "Message"].apply(
            lambda x: x[:MAX_LEN] if isinstance(x, str) else x)
        df_clean.loc[largos, "longitud_correo"] = MAX_LEN
        df_clean["truncado"] = largos.astype(int).values
    else:
        df_clean["truncado"] = 0
    df_clean["Label_Code"] = df_clean["Category"].map({"ham": 0, "spam": 1}).astype(int)

    keep = [c for c in ["message_id", "Message", "Label_Code", "Category", "subject",
                        "message", "date", "split", "fuente", "longitud_correo",
                        "truncado"] if c in df_clean.columns]
    df_clean = df_clean[keep]
    salida.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(salida, index=False, encoding="utf-8")
    print(f"[02] OK: {len(df_clean)} filas -> {salida}")
    print(df_clean["Category"].value_counts().to_dict())

    # Generar gráfico respectivo de la Etapa 02
    stats = {
        "inicial": n_inicial,
        "sin_nulos": n_sin_nulos,
        "sin_dup": n_sin_dup,
        "final": len(df_clean),
        "truncados": n_out
    }
    grafico_path = salida.parents[2] / "docs" / "graficos" / "02_limpieza_duplicados_y_truncamiento.png"
    guardar_grafico_etapa02(stats, df_clean, grafico_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default=str(DATA_ORIGINAL))
    ap.add_argument("--salida", default=str(DATA_LIMPIO))
    a = ap.parse_args()
    main(Path(a.entrada), Path(a.salida))

