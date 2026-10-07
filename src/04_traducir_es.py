"""Etapa 04: traducción al español y adaptación bilingüe. Entrada 03 -> Salida 04_traducido/.

Modos de operación:
1. Modo léxico (por defecto): Rápido, determinista y sin dependencias de GPU ni conexión.
   - Sin flags: Traduce una muestra estratificada representativa (por defecto: 1500 filas, configurable vía MUESTRA_TRADUCCION en config.py).
   - Con flag `--full`: Traduce el dataset completo.
   - Salida: data/04_traducido/enron_traducido_es.csv

2. Modo neuronal (`--marian`): Modelo Helsinki-NLP/opus-mt-en-es sobre GPU (CUDA) o CPU.
   - Traduce siempre el dataset completo para entrenamiento profundo bilingüe.
   - Soporta `--resume` para reanudar desde checkpoints (.tmp_checkpoint_neural.csv) si el proceso se interrumpe.
   - Salida: data/04_traducido/enron_traducido_es_neural.csv

Artefactos adicionales generados:
- docs/diccionario_abreviaturas.csv: Glosario de abreviaturas normalizadas y equivalencias.
- docs/ejemplo_traducciones.csv: Muestra multilingüe estratificada con textos en inglés y español.
- docs/graficos/04_traduccion_comparativa_longitud.png: Diagnóstico visual comparativo (300 DPI).
"""
import argparse
import sys
from pathlib import Path

# Inclusión del directorio raíz de módulos
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import (DATA_NLP, DATA_TRADUCIDO, DATA_NEURAL, DICCIONARIO_CSV,
                    EJEMPLOS_CSV, MUESTRA_TRADUCCION, MARIAN_BATCH_SIZE,
                    MARIAN_MAX_LENGTH, MARIAN_TRUNC_CHARS,
                    MARIAN_CHECKPOINT_INTERVAL, RANDOM_STATE)
from abreviaturas import ABBR_EN_EXPANSION, ABBR_EN_A_ES
from traductor import traducir_lote, traducir_lexico

CHECKPOINT = DATA_TRADUCIDO.parent / ".tmp_checkpoint_neural.csv"


def validar_entrada(df, ruta_entrada: Path):
    """Valida la integridad y columnas requeridas del DataFrame de entrada."""
    if len(df) == 0:
        raise ValueError(f"[04] Error: El archivo de entrada '{ruta_entrada}' está vacío.")
    
    columnas_requeridas = ["clean_en", "Category"]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"[04] Error: Faltan columnas requeridas {faltantes} en '{ruta_entrada}'. "
            f"Columnas disponibles: {list(df.columns)}. "
            "Asegúrate de haber ejecutado 'src/03_preprocesar_nlp.py' previamente."
        )


def sanear_textos(df):
    """Sanea valores nulos o vacíos en la columna clean_en para prevenir errores de traducción."""
    nulos = df["clean_en"].isna().sum()
    if nulos > 0:
        print(f"[04] Advertencia: Se detectaron {nulos} valores nulos en 'clean_en'. Rellenando con cadena vacía.")
    
    df["clean_en"] = df["clean_en"].fillna("").astype(str).str.strip()
    return df


def guardar_diccionario():
    """Exporta el glosario de abreviaturas documentado a CSV."""
    import pandas as pd
    DICCIONARIO_CSV.parent.mkdir(parents=True, exist_ok=True)
    filas = [{"abreviatura_en": k, "expansion_en": v, "equivalente_es": ABBR_EN_A_ES.get(k, "")}
             for k, v in sorted(ABBR_EN_EXPANSION.items())]
    pd.DataFrame(filas).to_csv(DICCIONARIO_CSV, index=False, encoding="utf-8")
    print(f"[04] Diccionario: {len(filas)} abreviaturas documentadas -> {DICCIONARIO_CSV}")


def muestra_estratificada(df, muestra: int, random_state: int = RANDOM_STATE):
    """Extrae una muestra estratificada conservando fielmente las proporciones de las clases."""
    if not muestra or muestra <= 0 or muestra >= len(df):
        return df.copy()
    
    col_estrat = "Category" if "Category" in df.columns else ("Label_Code" if "Label_Code" in df.columns else None)
    if not col_estrat:
        import pandas as _pd
        return df.sample(n=muestra, random_state=random_state).reset_index(drop=True)
    
    partes = []
    for _, g in df.groupby(col_estrat):
        n = max(1, int(round(muestra * len(g) / len(df))))
        partes.append(g.sample(n=min(n, len(g)), random_state=random_state))
        
    import pandas as _pd
    out = _pd.concat(partes).sample(frac=1, random_state=random_state).reset_index(drop=True)
    print(f"[04] Muestra estratificada: {len(out)} filas seleccionadas (de {muestra} solicitadas)")
    return out


def modo_lexico(df, muestra: int):
    """Ejecuta traducción léxica con manejo granular de excepciones por registro."""
    if muestra and muestra > 0 and len(df) > muestra:
        df = muestra_estratificada(df, muestra)
    
    textos = df["clean_en"].tolist()
    traducidos = []
    errores = 0
    
    try:
        from tqdm import tqdm
        iterador = tqdm(textos, desc="[04] Traduciendo (Léxico)")
    except ImportError:
        iterador = textos
        print(f"[04] Traduciendo {len(textos)} registros con motor léxico...")
    
    for t in iterador:
        try:
            traducidos.append(traducir_lexico(t))
        except Exception:
            errores += 1
            traducidos.append(t if isinstance(t, str) else "")
            
    if errores > 0:
        print(f"[04] Advertencia: {errores} textos arrojaron anomalías léxicas y conservaron el texto original.")
    else:
        print(f"[04] Traducción léxica finalizada exitosamente: {len(traducidos)} textos procesados.")
        
    df["texto_es"] = traducidos
    return df


def modo_marian(df, batch_size: int, max_length: int, trunc_chars: int,
                progreso_cada: int, resume: bool):
    """Ejecuta traducción neuronal MarianMT con soporte de reanudación por checkpoints."""
    import pandas as pd
    textos = df["clean_en"].tolist()
    hechos = []
    inicio = 0
    
    if resume and CHECKPOINT.exists():
        try:
            ck = pd.read_csv(CHECKPOINT, usecols=["texto_es"])
            hechos = ck["texto_es"].fillna("").astype(str).tolist()
            inicio = len(hechos)
            print(f"[04] Reanudación (Resume): {inicio}/{len(textos)} registros ya procesados previamente.")
        except Exception as e:
            print(f"[04] Advertencia al leer checkpoint ({e}); se iniciará desde el principio.")
            hechos = []
            inicio = 0

    restantes = textos[inicio:]
    nuevos = traducir_lote(
        restantes,
        usar_marian=True,
        batch_size=batch_size,
        max_length=max_length,
        trunc_chars=trunc_chars,
        progreso_cada=progreso_cada,
        checkpoint_csv=str(CHECKPOINT)
    )
    
    if nuevos is None:
        if hechos:
            pd.DataFrame({"texto_es": hechos}).to_csv(CHECKPOINT, index=False)
        raise SystemExit("[04] Error en inferencia MarianMT; progreso guardado en checkpoint. Reintenta con '--resume'.")
    
    todos = hechos + nuevos
    import re as _re
    df["texto_es"] = [_re.sub(r"\bnumber\b", "número", str(t)) for t in todos]
    
    if CHECKPOINT.exists():
        try:
            CHECKPOINT.unlink()
        except OSError:
            pass
            
    return df


def guardar_grafico_etapa04(df, ruta_grafico: Path, etiqueta: str):
    """Genera y guarda el diagnóstico visual de longitudes y paridad bilingüe en alta resolución."""
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
        sample_size = min(1000, len(df_plot))
        sample_plot = df_plot.sample(n=sample_size, random_state=RANDOM_STATE)
        palette = {"ham": "#2ecc71", "spam": "#e74c3c"}
        
        sns.scatterplot(data=sample_plot, x="long_en", y="long_es", hue="Category",
                        palette=palette, alpha=0.6, edgecolor="none", s=25, ax=axes[1])
        
        max_val = max(10, min(sample_plot["long_en"].max(), sample_plot["long_es"].max()))
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


def finalizar(df, salida: Path, etiqueta: str):
    """Guarda el corpus traducido, genera ejemplos multilingües y el gráfico diagnóstico."""
    import pandas as pd
    df["longitud_es"] = df["texto_es"].astype(str).apply(len)
    
    # Preservar orden y columnas clave
    salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"[04] OK ({etiqueta}): {len(df)} filas guardadas -> {salida}")
    
    guardar_diccionario()
    
    # Muestra representativa para ejemplos multilingües
    cols_ejemplo = [c for c in ["message_id", "Message", "idioma_detectado", "clean_en", "texto_es", "Category"] if c in df.columns]
    if "idioma_detectado" in df.columns:
        ejemplos_partes = []
        for lang, g in df.groupby("idioma_detectado"):
            n = min(len(g), 3 if lang != "en" else 10)
            ejemplos_partes.append(g.head(n))
        df_ejemplos = pd.concat(ejemplos_partes, ignore_index=True)
    else:
        df_ejemplos = df.head(30)
        
    df_ejemplos[cols_ejemplo].to_csv(EJEMPLOS_CSV, index=False, encoding="utf-8")
    print(f"[04] Ejemplos multilingües -> {EJEMPLOS_CSV}")
    
    if len(df) > 0:
        ejemplo_txt = str(df['texto_es'].iloc[0])[:160]
        print(f"[04] Muestra ES: {ejemplo_txt}")
    
    # Generar gráfico diagnóstico
    grafico_path = salida.parents[2] / "docs" / "graficos" / "04_traduccion_comparativa_longitud.png"
    guardar_grafico_etapa04(df, grafico_path, etiqueta)


def main(entrada: Path = DATA_NLP, salida: Path = DATA_TRADUCIDO,
         muestra: int = MUESTRA_TRADUCCION, usar_marian: bool = False,
         batch_size: int = MARIAN_BATCH_SIZE, max_length: int = MARIAN_MAX_LENGTH,
         trunc_chars: int = MARIAN_TRUNC_CHARS, progreso_cada: int = MARIAN_CHECKPOINT_INTERVAL,
         resume: bool = False, salida_neural: Path = DATA_NEURAL):
    """Punto de entrada principal para la etapa 04."""
    import pandas as pd
    
    if not entrada.exists():
        raise FileNotFoundError(
            f"[04] Error: No se encontró el archivo de entrada '{entrada}'. "
            "Ejecuta 'src/03_preprocesar_nlp.py' o 'src/pipeline.py' para generarlo."
        )
        
    df = pd.read_csv(entrada)
    validar_entrada(df, entrada)
    df = sanear_textos(df)
    
    modo_str = "marian-neuronal" if usar_marian else "léxico"
    print(f"[04] Entrada NLP cargada: {len(df)} filas (Modo: {modo_str})")
    
    if usar_marian:
        df = modo_marian(
            df=df,
            batch_size=batch_size,
            max_length=max_length,
            trunc_chars=trunc_chars,
            progreso_cada=progreso_cada,
            resume=resume
        )
        finalizar(df, salida_neural, "marian-neuronal")
    else:
        df = modo_lexico(df, muestra=muestra)
        finalizar(df, salida, "lexico")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Etapa 04: Traducción EN -> ES del dataset de correos de Enron con soporte Léxico y Neuronal."
    )
    ap.add_argument("--entrada", default=str(DATA_NLP),
                    help=f"Ruta del CSV de entrada NLP (defecto: {DATA_NLP})")
    ap.add_argument("--salida", default=str(DATA_TRADUCIDO),
                    help=f"Ruta del CSV de salida traducido léxico (defecto: {DATA_TRADUCIDO})")
    ap.add_argument("--salida-neural", default=str(DATA_NEURAL),
                    help=f"Ruta del CSV de salida traducido neuronal (defecto: {DATA_NEURAL})")
    ap.add_argument("--muestra", type=int, default=MUESTRA_TRADUCCION,
                    help=f"Tamaño de muestra estratificada para traducción léxica (defecto: {MUESTRA_TRADUCCION}).")
    ap.add_argument("--full", action="store_true",
                    help="Traduce el dataset completo en modo léxico (ignora --muestra).")
    ap.add_argument("--marian", action="store_true",
                    help="Activa traducción neuronal MarianMT en GPU/CPU (siempre sobre dataset completo).")
    ap.add_argument("--batch", type=int, default=MARIAN_BATCH_SIZE,
                    help=f"Tamaño de lote (batch size) para MarianMT (defecto: {MARIAN_BATCH_SIZE}).")
    ap.add_argument("--max-len", type=int, default=MARIAN_MAX_LENGTH,
                    help=f"Longitud máxima de tokens en MarianMT (defecto: {MARIAN_MAX_LENGTH}).")
    ap.add_argument("--trunc-chars", type=int, default=MARIAN_TRUNC_CHARS,
                    help=f"Caracteres máximos de entrada por correo para MarianMT (defecto: {MARIAN_TRUNC_CHARS}).")
    ap.add_argument("--checkpoint-interval", type=int, default=MARIAN_CHECKPOINT_INTERVAL,
                    help=f"Frecuencia de guardado de checkpoints en filas (defecto: {MARIAN_CHECKPOINT_INTERVAL}).")
    ap.add_argument("--resume", action="store_true",
                    help="Reanuda la traducción neuronal desde el último checkpoint guardado.")
    
    a = ap.parse_args()
    muestra_final = 0 if (a.full or a.marian) else a.muestra
    
    main(
        entrada=Path(a.entrada),
        salida=Path(a.salida),
        salida_neural=Path(a.salida_neural),
        muestra=muestra_final,
        usar_marian=a.marian,
        batch_size=a.batch,
        max_length=a.max_len,
        trunc_chars=a.trunc_chars,
        progreso_cada=a.checkpoint_interval,
        resume=a.resume
    )
