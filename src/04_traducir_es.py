"""Etapa 04: traducción al español. Entrada 03 -> Salida 04_traducido/.

- Modo léxico (defecto): rápido y determinista. `--full` traduce todo,
  sin flag traduce muestra estratificada (MUESTRA_TRADUCCION).
  Salida: enron_traducido_es.csv
- Modo neuronal (--marian): Helsinki-NLP/opus-mt-en-es en GPU/CPU.
  Siempre traduce el dataset COMPLETO a enron_traducido_es_neural.csv
  (el léxico se conserva como baseline de comparación).
  Soporta --resume para continuar si se interrumpe (checkpoint cada
  --checkpoint filas en .tmp_checkpoint_neural.csv).
- Además genera docs/diccionario_abreviaturas.csv y docs/ejemplo_traducciones.csv
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import (DATA_NLP, DATA_TRADUCIDO, DICCIONARIO_CSV, EJEMPLOS_CSV,
                    MUESTRA_TRADUCCION)
from abreviaturas import ABBR_EN_EXPANSION, ABBR_EN_A_ES
from traductor import traducir_lote

DATA_NEURAL = DATA_TRADUCIDO.parent / "enron_traducido_es_neural.csv"
CHECKPOINT = DATA_TRADUCIDO.parent / ".tmp_checkpoint_neural.csv"


def guardar_diccionario():
    import pandas as pd
    DICCIONARIO_CSV.parent.mkdir(parents=True, exist_ok=True)
    filas = [{"abreviatura_en": k, "expansion_en": v, "equivalente_es": ABBR_EN_A_ES.get(k, "")}
             for k, v in sorted(ABBR_EN_EXPANSION.items())]
    pd.DataFrame(filas).to_csv(DICCIONARIO_CSV, index=False, encoding="utf-8")
    print(f"[04] Diccionario: {len(filas)} abreviaturas -> {DICCIONARIO_CSV}")


def muestra_estratificada(df, muestra):
    partes = []
    for cat, g in df.groupby("Category"):
        n = max(1, int(round(muestra * len(g) / len(df))))
        partes.append(g.sample(n=min(n, len(g)), random_state=42))
    import pandas as _pd
    out = _pd.concat(partes).sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"[04] Muestra estratificada: {len(out)} filas (de {muestra} pedidas)")
    return out


def modo_lexico(df, muestra):
    if muestra and muestra > 0 and len(df) > muestra:
        df = muestra_estratificada(df, muestra)
    textos = df["clean_en"].astype(str).tolist()
    try:
        from tqdm import tqdm
        from traductor import traducir_lexico
        traducidos = [traducir_lexico(t) for t in tqdm(textos, desc="[04] Traduciendo")]
    except ImportError:
        from traductor import traducir_lexico
        traducidos = [traducir_lexico(t) for t in textos]
        print(f"[04] Traducidos {len(traducidos)} textos con léxico.")
    df["texto_es"] = traducidos
    return df


def modo_marian(df, batch_size, max_length, trunc_chars, resume):
    import pandas as pd
    textos = df["clean_en"].astype(str).tolist()
    hechos = []
    inicio = 0
    if resume and CHECKPOINT.exists():
        ck = pd.read_csv(CHECKPOINT, usecols=["texto_es"])
        hechos = ck["texto_es"].astype(str).tolist()
        inicio = len(hechos)
        print(f"[04] Resume: {inicio}/{len(textos)} ya traducidos.")
    restantes = textos[inicio:]
    nuevos = traducir_lote(restantes, usar_marian=True, batch_size=batch_size,
                           max_length=max_length, trunc_chars=trunc_chars,
                           progreso_cada=2000, checkpoint_csv=str(CHECKPOINT))
    if nuevos is None:
        # Guardar lo avanzado como checkpoint aunque falle el resto.
        if hechos:
            pd.DataFrame({"texto_es": hechos}).to_csv(CHECKPOINT, index=False)
        raise SystemExit("[04] MarianMT falló; checkpoint guardado. Reintenta con --resume.")
    todos = hechos + nuevos
    import re as _re
    df["texto_es"] = [_re.sub(r"\bnumber\b", "número", t) for t in todos]
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()
    return df


def guardar_grafico_etapa04(df: "pd.DataFrame", ruta_grafico: Path, etiqueta: str):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        ruta_grafico.parent.mkdir(parents=True, exist_ok=True)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
        
        df_plot = df.copy()
        df_plot["long_en"] = df_plot["clean_en"].astype(str).apply(len)
        df_plot["long_es"] = df_plot["texto_es"].astype(str).apply(len)
        
        # Panel 1: Densidad comparativa de longitud EN vs ES
        sns.kdeplot(data=df_plot, x="long_en", label="Original (Inglés)", color="#2980b9",
                    fill=True, alpha=0.3, ax=axes[0], log_scale=True, linewidth=1.5)
        sns.kdeplot(data=df_plot, x="long_es", label="Traducido (Español)", color="#e67e22",
                    fill=True, alpha=0.3, ax=axes[0], log_scale=True, linewidth=1.5)
        axes[0].set_title("Distribución de Longitud: Inglés vs Español", fontsize=11, fontweight="bold")
        axes[0].set_xlabel("Longitud del Texto (Caracteres, Escala Log)", fontsize=10, fontweight="bold")
        axes[0].set_ylabel("Densidad", fontsize=10, fontweight="bold")
        axes[0].legend()
        axes[0].grid(True, linestyle="--", alpha=0.5)
        
        # Panel 2: Correlación y Preservación de Extensión
        sample_plot = df_plot.sample(n=min(1000, len(df_plot)), random_state=42)
        sns.scatterplot(data=sample_plot, x="long_en", y="long_es", hue="Category",
                        palette={"ham": "#2ecc71", "spam": "#e74c3c"},
                        alpha=0.6, edgecolor="none", s=25, ax=axes[1])
        # Línea de referencia identidad y = x
        max_val = min(sample_plot["long_en"].max(), sample_plot["long_es"].max())
        axes[1].plot([0, max_val], [0, max_val], color="gray", linestyle="--", linewidth=1.2, label="Paridad 1:1")
        axes[1].set_title(f"Correlación de Longitud EN vs ES ({etiqueta})", fontsize=11, fontweight="bold")
        axes[1].set_xlabel("Caracteres en Inglés", fontsize=10, fontweight="bold")
        axes[1].set_ylabel("Caracteres en Español", fontsize=10, fontweight="bold")
        axes[1].legend()
        axes[1].grid(True, linestyle="--", alpha=0.5)
        
        plt.suptitle(f"Etapa 04: Diagnóstico de Traducción al Español ({etiqueta.upper()})", fontsize=13, fontweight="bold", y=1.02)
        plt.tight_layout()
        plt.savefig(ruta_grafico, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"[04] Gráfico generado -> {ruta_grafico}")
    except Exception as e:
        print(f"[04] Advertencia al generar gráfico: {e}")


def finalizar(df, salida, etiqueta):
    import pandas as pd  # noqa
    df["longitud_es"] = df["texto_es"].apply(len)
    salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"[04] OK ({etiqueta}): {len(df)} filas -> {salida}")
    guardar_diccionario()
    
    cols = [c for c in ["Message", "idioma_detectado", "clean_en", "texto_es", "Category"] if c in df.columns]
    
    # Muestra representativa estratificada por idioma si existe idioma_detectado
    if "idioma_detectado" in df.columns:
        ejemplos_partes = []
        for lang, g in df.groupby("idioma_detectado"):
            n = min(len(g), 3 if lang != "en" else 10)
            ejemplos_partes.append(g.head(n))
        df_ejemplos = pd.concat(ejemplos_partes, ignore_index=True)
    else:
        df_ejemplos = df.head(30)
        
    df_ejemplos[cols].to_csv(EJEMPLOS_CSV, index=False, encoding="utf-8")
    print(f"[04] Ejemplos multilingües -> {EJEMPLOS_CSV}")
    print(f"[04] Muestra ES: {df['texto_es'].iloc[0][:160]}")
    
    # Generar gráfico respectivo de la Etapa 04
    grafico_path = salida.parents[2] / "docs" / "graficos" / "04_traduccion_comparativa_longitud.png"
    guardar_grafico_etapa04(df, grafico_path, etiqueta)




def main(entrada: Path = DATA_NLP, salida: Path = DATA_TRADUCIDO,
         muestra: int = MUESTRA_TRADUCCION, usar_marian: bool = False,
         batch_size: int = 64, max_length: int = 128, trunc_chars: int = 600,
         resume: bool = False, salida_neural: Path = DATA_NEURAL):
    import pandas as pd
    df = pd.read_csv(entrada)
    print(f"[04] Entrada NLP: {len(df)} filas (traductor={'marian' if usar_marian else 'lexico'})")
    if usar_marian:
        df = modo_marian(df, batch_size, max_length, trunc_chars, resume)
        finalizar(df, salida_neural, "marian-neuronal")
    else:
        df = modo_lexico(df, muestra)
        finalizar(df, salida, "lexico")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default=str(DATA_NLP))
    ap.add_argument("--salida", default=str(DATA_TRADUCIDO))
    ap.add_argument("--muestra", type=int, default=MUESTRA_TRADUCCION)
    ap.add_argument("--full", action="store_true", help="Traduce el dataset completo (léxico)")
    ap.add_argument("--marian", action="store_true", help="MarianMT neuronal GPU (siempre full)")
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--trunc-chars", type=int, default=600)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    muestra = 0 if (a.full or a.marian) else a.muestra
    main(Path(a.entrada), Path(a.salida), muestra=muestra, usar_marian=a.marian,
         batch_size=a.batch, max_length=a.max_len, trunc_chars=a.trunc_chars,
         resume=a.resume)
