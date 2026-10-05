"""Etapa 07: evaluación final en held-out (split test de HF, ~6k, nunca visto).

- Descarga SetFit/enron_spam[test], aplica la misma limpieza/NLP (02+03).
- Traduce a ES-neuronal con MarianMT (o utiliza caché si existe).
- Evalúa los modelos cargados desde models/ aplicando sus respectivos umbrales calibrados.
- Guarda docs/evaluacion_heldout.csv con métricas completas (Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import TEST_EN, TEST_ES, HELDOUT_CSV, MODELO_EN, MODELO_ES
from modelo_wrapper import SpamClassifierWrapper


def cargar_test_hf():
    import pandas as pd
    try:
        df = pd.read_json("hf://datasets/SetFit/enron_spam/test.jsonl", lines=True)
        df["fuente"] = "hf_direct_test"
    except Exception as e:
        print(f"[07] hf:// falló: {e}")
        from datasets import load_dataset
        ds = load_dataset("SetFit/enron_spam")
        df = pd.DataFrame(ds["test"])
        df["fuente"] = "hf_datasets_api_test"
    return df


def limpiar_y_nlp(df):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "m03", str(Path(__file__).resolve().parent / "03_preprocesar_nlp.py"))
    m03 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m03)
    
    col_texto = "text" if "text" in df.columns else ("Message" if "Message" in df.columns else "message")
    df = df.dropna(subset=[col_texto]).copy()
    df["Message"] = df[col_texto].astype(str)
    
    if "label" in df.columns:
        df["Category"] = df["label"].map({0: "ham", 1: "spam"})
        df["Label_Code"] = df["label"].astype(int)
    elif "label_text" in df.columns:
        df["Category"] = df["label_text"].astype(str).str.lower()
        df["Label_Code"] = df["Category"].map({"ham": 0, "spam": 1}).astype(int)
        
    df["longitud_correo"] = df["Message"].apply(len)
    df = df[df["longitud_correo"] > 5].copy()
    df.loc[df["longitud_correo"] > 10000, "Message"] = df.loc[
        df["longitud_correo"] > 10000, "Message"].apply(lambda x: x[:10000])
        
    if "subject" in df.columns and df["subject"].notna().any():
        mensaje_completo = df["subject"].fillna("").astype(str) + " " + df["Message"].astype(str)
    else:
        mensaje_completo = df["Message"].astype(str)
        
    df["clean_en"] = mensaje_completo.map(m03.limpiar_texto_en)
    df = df[df["clean_en"].str.len() > 5].copy()
    return df.reset_index(drop=True)


def guardar_grafico_etapa07(df_res: "pd.DataFrame", matrices_dict: dict, ruta_grafico: Path):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        ruta_grafico.parent.mkdir(parents=True, exist_ok=True)
        
        fig = plt.figure(figsize=(15, 5), dpi=300)
        gs = fig.add_gridspec(1, 3, width_ratios=[1.4, 1, 1], wspace=0.3)
        
        # Panel 1: Comparativa de Métricas en Held-Out
        ax1 = fig.add_subplot(gs[0, 0])
        metricas_cols = ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"]
        df_melt = df_res.melt(id_vars=["modelo"], value_vars=metricas_cols,
                              var_name="Métrica", value_name="Valor")
        sns.barplot(data=df_melt, x="Métrica", y="Valor", hue="modelo",
                    palette=["#3498db", "#2ecc71"], edgecolor="black", linewidth=0.6, ax=ax1)
        ax1.set_ylim(0.85, 1.02)
        ax1.set_title("Métricas de Generalización (Held-Out Test HF)", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Puntuación (0.0 - 1.0)", fontsize=9, fontweight="bold")
        ax1.legend(loc="lower right")
        ax1.grid(axis="y", linestyle="--", alpha=0.5)
        ax1.tick_params(axis="x", rotation=20)
        
        # Panel 2: Matriz Confusión EN
        if "nb_en_heldout" in matrices_dict:
            ax2 = fig.add_subplot(gs[0, 1])
            cm_en = matrices_dict["nb_en_heldout"]
            sns.heatmap(cm_en, annot=True, fmt="d", cmap="Blues", cbar=False,
                        xticklabels=["Ham", "Spam"], yticklabels=["Ham", "Spam"], ax=ax2)
            ax2.set_title("Matriz Held-Out: EN", fontsize=11, fontweight="bold")
            ax2.set_xlabel("Predicción", fontsize=9, fontweight="bold")
            ax2.set_ylabel("Real", fontsize=9, fontweight="bold")
            
        # Panel 3: Matriz Confusión ES
        if "nb_es_heldout" in matrices_dict:
            ax3 = fig.add_subplot(gs[0, 2])
            cm_es = matrices_dict["nb_es_heldout"]
            sns.heatmap(cm_es, annot=True, fmt="d", cmap="Greens", cbar=False,
                        xticklabels=["Ham", "Spam"], yticklabels=["Ham", "Spam"], ax=ax3)
            ax3.set_title("Matriz Held-Out: ES (Neuronal)", fontsize=11, fontweight="bold")
            ax3.set_xlabel("Predicción", fontsize=9, fontweight="bold")
            ax3.set_ylabel("Real", fontsize=9, fontweight="bold")
            
        plt.suptitle("Etapa 07: Evaluación Final en Datos Inéditos (Held-Out Test Split)", fontsize=13, fontweight="bold", y=1.03)
        plt.savefig(ruta_grafico, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"[07] Gráfico generado -> {ruta_grafico}")
    except Exception as e:
        print(f"[07] Advertencia al generar gráfico: {e}")


def main():
    import pandas as pd
    import pickle
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                 f1_score, roc_auc_score, average_precision_score,
                                 confusion_matrix)
    from traductor import traducir_lote
    
    df = cargar_test_hf()
    print(f"[07] Test HF crudo: {len(df)} filas")
    df = limpiar_y_nlp(df)
    print(f"[07] Tras limpieza + NLP: {len(df)} filas")
    TEST_EN.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(TEST_EN, index=False, encoding="utf-8")

    # Traducción si es requerida o si no existe TEST_ES
    regenerar = not TEST_ES.exists()
    if TEST_ES.exists():
        df_es_guardado = pd.read_csv(TEST_ES)
        if len(df_es_guardado) != len(df) or "texto_es" not in df_es_guardado.columns:
            regenerar = True
        else:
            df["texto_es"] = df_es_guardado["texto_es"].values
            
    if regenerar:
        print("[07] Generando traducción de test con MarianMT en GPU...")
        ckpt = TEST_ES.parent / ".tmp_checkpoint_test.csv"
        textos = df["clean_en"].astype(str).tolist()
        es = traducir_lote(textos, usar_marian=True,
                           batch_size=64, max_length=128, trunc_chars=600,
                           progreso_cada=500, checkpoint_csv=str(ckpt))
        if es is None:
            print("[07] Fallback: traduciendo test con léxico local...")
            from traductor import traducir_lexico
            es = [traducir_lexico(t) for t in textos]
            
        df["texto_es"] = es
        if ckpt.exists():
            ckpt.unlink()
        df.to_csv(TEST_ES, index=False, encoding="utf-8")
        print(f"[07] Test traducido guardado -> {TEST_ES}")

    filas = []
    matrices = {}
    for nombre, ruta, col in [("nb_en", MODELO_EN, "clean_en"), ("nb_es", MODELO_ES, "texto_es")]:
        if not ruta.exists():
            print(f"[07] Falta modelo en {ruta}, se omite {nombre}.")
            continue
        if col not in df.columns:
            print(f"[07] Falta columna {col} en dataset test, se omite {nombre}.")
            continue
            
        with open(ruta, "rb") as f:
            modelo = pickle.load(f)
            
        y = df["Label_Code"].astype(int)
        X = df[col].astype(str)
        
        if isinstance(modelo, SpamClassifierWrapper):
            proba = modelo.predict_proba(X)[:, 1]
            p = modelo.predict(X)
            umbral = modelo.umbral
        else:
            proba = modelo.predict_proba(X)[:, 1]
            umbral = 0.5
            p = (proba >= umbral).astype(int)
            
        try:
            roc_auc = round(float(roc_auc_score(y, proba)), 4)
            pr_auc = round(float(average_precision_score(y, proba)), 4)
        except Exception:
            roc_auc, pr_auc = 0.0, 0.0
            
        tag_modelo = nombre + "_heldout"
        filas.append({
            "modelo": tag_modelo,
            "n": len(df),
            "accuracy": round(float(accuracy_score(y, p)), 4),
            "precision": round(float(precision_score(y, p, zero_division=0)), 4),
            "recall": round(float(recall_score(y, p, zero_division=0)), 4),
            "f1": round(float(f1_score(y, p, zero_division=0)), 4),
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "umbral": round(float(umbral), 2)
        })
        matrices[tag_modelo] = confusion_matrix(y, p)

    HELDOUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_out = pd.DataFrame(filas)
    df_out.to_csv(HELDOUT_CSV, index=False, encoding="utf-8")
    print(f"\n[07] Evaluación en Held-Out exportada -> {HELDOUT_CSV}")
    print(df_out.to_string(index=False) + "\n")

    # Generar gráfico respectivo de la Etapa 07
    grafico_path = HELDOUT_CSV.parent / "graficos" / "07_evaluacion_heldout_metricas.png"
    guardar_grafico_etapa07(df_out, matrices, grafico_path)


if __name__ == "__main__":
    main()

