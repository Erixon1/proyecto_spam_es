"""Etapa 03: preprocesamiento NLP en inglés. Entrada 02 -> Salida 03_nlp/enron_nlp_en.csv."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import DATA_LIMPIO, DATA_NLP
from abreviaturas import expandir_abreviaturas, corregir_typos


def limpiar_texto_en(s: str) -> str:
    if not isinstance(s, str):
        return ""
    # 1. Preservar señales fuertes antes de normalizar
    s = re.sub(r"https?://\S+|www\.\S+", " tokenurl ", s, flags=re.IGNORECASE)
    s = re.sub(r"\S+@\S+", " tokenemail ", s, flags=re.IGNORECASE)
    s = re.sub(r"[\$€£]|(?:\b(?:usd|eur|dolares|dollars|pesos)\b)", " tokendinero ", s, flags=re.IGNORECASE)
    s = re.sub(r"!{1,}", " tokenexclam ", s)
    s = re.sub(r"\d+", " tokennumero ", s)
    
    # 2. Minúsculas y limpieza de caracteres no alfanuméricos
    s = s.lower()
    s = re.sub(r"[^a-z0-9áéíóúñü_ ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    
    # 3. Expansión de abreviaturas y corrección de errores ortográficos
    s = expandir_abreviaturas(s)
    s = corregir_typos(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def guardar_grafico_etapa03(df: "pd.DataFrame", ruta_grafico: Path):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        ruta_grafico.parent.mkdir(parents=True, exist_ok=True)
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), dpi=300)
        
        # Panel 1: Detección de Meta-Tokens de Spam (Señales Estructuradas)
        tokens = ["tokenurl", "tokendinero", "tokenexclam", "tokenemail", "tokennumero"]
        nombres_amigables = ["URLs (web)", "Dinero ($/€/USD)", "Exclamaciones (!)", "Emails", "Números"]
        
        conteo_data = []
        for tok, nom in zip(tokens, nombres_amigables):
            spam_count = df[df["Category"] == "spam"]["clean_en"].str.count(tok).sum()
            ham_count = df[df["Category"] == "ham"]["clean_en"].str.count(tok).sum()
            conteo_data.append({"Señal": nom, "Clase": "Spam", "Ocurrencias": spam_count})
            conteo_data.append({"Señal": nom, "Clase": "Ham (Legítimo)", "Ocurrencias": ham_count})
            
        df_tokens = pd.DataFrame(conteo_data)
        sns.barplot(data=df_tokens, x="Señal", y="Ocurrencias", hue="Clase",
                    palette={"Spam": "#e74c3c", "Ham (Legítimo)": "#2ecc71"},
                    edgecolor="black", linewidth=0.7, ax=axes[0])
        axes[0].set_title("Ocurrencia de Meta-Tokens por Clase", fontsize=11, fontweight="bold")
        axes[0].set_xlabel("Meta-Token NLP", fontsize=10, fontweight="bold")
        axes[0].set_yscale("log")
        axes[0].set_ylabel("Frecuencia (Escala Log)", fontsize=10, fontweight="bold")
        axes[0].grid(axis="y", linestyle="--", alpha=0.5)
        axes[0].tick_params(axis="x", rotation=15)
        
        # Panel 2: Distribución de Idiomas Detectados (langdetect)
        if "idioma_detectado" in df.columns:
            top_langs = df["idioma_detectado"].value_counts().head(8)
            colores_langs = sns.color_palette("viridis", len(top_langs))
            bars = axes[1].bar(top_langs.index, top_langs.values, color=colores_langs, edgecolor="black", linewidth=0.7)
            axes[1].set_yscale("log")
            axes[1].set_title("Idiomas Detectados en Dataset (langdetect)", fontsize=11, fontweight="bold")
            axes[1].set_xlabel("Código ISO de Idioma", fontsize=10, fontweight="bold")
            axes[1].set_ylabel("Cantidad (Escala Log)", fontsize=10, fontweight="bold")
            axes[1].grid(axis="y", linestyle="--", alpha=0.5)
            for b in bars:
                h = b.get_height()
                axes[1].annotate(f"{int(h):,}", (b.get_x() + b.get_width() / 2., h),
                                 ha="center", va="bottom", fontsize=8, fontweight="bold",
                                 xytext=(0, 2), textcoords="offset points")
        
        # Panel 3: Distribución de Cantidad de Palabras Limpias
        sns.boxplot(data=df, x="Category", y="num_palabras_clean",
                    palette={"ham": "#2ecc71", "spam": "#e74c3c"},
                    showfliers=False, ax=axes[2], width=0.4, linewidth=1.2)
        axes[2].set_title("Longitud en Palabras Limpias", fontsize=11, fontweight="bold")
        axes[2].set_xlabel("Categoría", fontsize=10, fontweight="bold")
        axes[2].set_ylabel("Cantidad de Palabras", fontsize=10, fontweight="bold")
        axes[2].grid(axis="y", linestyle="--", alpha=0.5)
        
        plt.suptitle("Etapa 03: Diagnóstico NLP - Normalización, Idiomas (langdetect) y Meta-Tokens", fontsize=13, fontweight="bold", y=1.02)
        plt.tight_layout()
        plt.savefig(ruta_grafico, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"[03] Gráfico generado -> {ruta_grafico}")
    except Exception as e:
        print(f"[03] Advertencia al generar gráfico: {e}")


def detectar_idiomas(series_textos: "pd.Series") -> list:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    def _detect(s):
        if not isinstance(s, str): return "desconocido"
        t = s[:150].strip()
        if len(t) < 6: return "desconocido"
        try:
            return detect(t)
        except Exception:
            return "desconocido"
    return [_detect(t) for t in series_textos]


def main(entrada: Path = DATA_LIMPIO, salida: Path = DATA_NLP):
    import pandas as pd
    df = pd.read_csv(entrada)
    
    # 1. Detección de idioma con langdetect sobre el texto original
    print("[03] Detectando idiomas del corpus con langdetect...")
    df["idioma_detectado"] = detectar_idiomas(df["Message"])
    
    dist_idiomas = df["idioma_detectado"].value_counts().reset_index()
    dist_idiomas.columns = ["idioma_iso", "conteo"]
    dist_idiomas["porcentaje"] = ((dist_idiomas["conteo"] / len(df)) * 100).round(2)
    ruta_dist_csv = salida.parents[2] / "docs" / "distribucion_idiomas.csv"
    ruta_dist_csv.parent.mkdir(parents=True, exist_ok=True)
    dist_idiomas.to_csv(ruta_dist_csv, index=False, encoding="utf-8")
    print(f"[03] Distribución de idiomas guardada -> {ruta_dist_csv}")
    print(dist_idiomas.head(8).to_string(index=False))

    # 2. Si existe asunto (subject), se combina con el mensaje dando mayor contexto
    if "subject" in df.columns and df["subject"].notna().any():
        mensaje_completo = df["subject"].fillna("").astype(str) + " " + df["Message"].astype(str)
    else:
        mensaje_completo = df["Message"].astype(str)
        
    df["clean_en"] = mensaje_completo.map(limpiar_texto_en)
    df["long_clean"] = df["clean_en"].apply(len)
    df["num_palabras_clean"] = df["clean_en"].apply(lambda x: len(x.split()))
    
    antes = len(df)
    df = df[df["clean_en"].str.len() > 5].copy()
    print(f"[03] Filtrados por limpieza vacía: {antes - len(df)}")
    salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"[03] OK: {len(df)} filas -> {salida}")
    print(f"[03] Ejemplo: {df['clean_en'].iloc[0][:160]}")

    # 3. Generar gráfico respectivo de la Etapa 03
    grafico_path = salida.parents[2] / "docs" / "graficos" / "03_nlp_tokens_preservados.png"
    guardar_grafico_etapa03(df, grafico_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default=str(DATA_LIMPIO))
    ap.add_argument("--salida", default=str(DATA_NLP))
    a = ap.parse_args()
    main(Path(a.entrada), Path(a.salida))



