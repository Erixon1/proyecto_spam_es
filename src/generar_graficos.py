"""Generador de gráficos y visualizaciones profesionales del proyecto.

Genera y exporta todas las figuras en alta resolución (300 DPI) a la carpeta docs/graficos/:
1. 01_distribucion_clases.png -> Proporción y conteo de Ham vs Spam
2. 02_distribucion_longitud.png -> Longitud de texto y palabras por categoría
3. 03_comparativa_metricas_modelos.png -> Comparativa de Accuracy, Precision, Recall, F1, ROC-AUC y PR-AUC
4. 04_matrices_confusion.png -> Matrices de confusión en Inglés y Español
5. 05_top_terminos_explicabilidad_xai.png -> Top palabras detonantes de Spam vs Ham (Log-Odds)
6. 06_curvas_roc_y_pr.png -> Curvas ROC y Precision-Recall comparativas
"""
import sys
from pathlib import Path

# Ajustar path al directorio raíz
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
    roc_curve, auc, precision_recall_curve, average_precision_score
)
from sklearn.model_selection import train_test_split
from config import DATA_LIMPIO, DATA_NLP, DATA_NEURAL, DATA_TRADUCIDO, MODELO_EN, MODELO_ES, METRICAS_CSV, RANDOM_STATE, TEST_SIZE
from modelo_wrapper import SpamClassifierWrapper

# Configurar estilo visual profesional
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

CARPETA_GRAFICOS = ROOT / "docs" / "graficos"
CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)


def graficar_distribucion_clases(df_limpio):
    """01: Gráfico de barras de balance de clases con conteos y porcentajes."""
    plt.figure(figsize=(7, 5), dpi=300)
    colores = ["#2ecc71", "#e74c3c"]
    ax = sns.countplot(data=df_limpio, x="Category", order=["ham", "spam"], palette=colores, edgecolor="black", linewidth=0.6)
    
    total = len(df_limpio)
    for p in ax.patches:
        altura = p.get_height()
        porcentaje = (altura / total) * 100
        ax.annotate(f"{int(altura):,} ({porcentaje:.1f}%)",
                    (p.get_x() + p.get_width() / 2., altura),
                    ha="center", va="bottom", fontsize=11, fontweight="bold",
                    xytext=(0, 6), textcoords="offset points")
        
    plt.title("Distribución de Clases en el Dataset Limpio (Enron)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Categoría del Correo", fontsize=11, fontweight="bold")
    plt.ylabel("Cantidad de Correos", fontsize=11, fontweight="bold")
    plt.ylim(0, max([p.get_height() for p in ax.patches]) * 1.15)
    
    salida = CARPETA_GRAFICOS / "01_distribucion_clases.png"
    plt.tight_layout()
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[Graficos] Exportado -> {salida}")


def graficar_distribucion_longitud(df_limpio):
    """02: Histogramas y KDE de longitud de caracteres y palabras."""
    df = df_limpio.copy()
    df["num_palabras"] = df["Message"].astype(str).apply(lambda x: len(x.split()))
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    colores = {"ham": "#2ecc71", "spam": "#e74c3c"}
    
    # Longitud de caracteres
    sns.histplot(data=df, x="longitud_correo", hue="Category", bins=60, kde=True,
                 palette=colores, ax=axes[0], alpha=0.5, log_scale=(True, False))
    axes[0].set_title("Distribución de Longitud de Caracteres (Log-Scale)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Caracteres por Correo (Escala Log)")
    axes[0].set_ylabel("Frecuencia")
    
    # Número de palabras
    sns.histplot(data=df, x="num_palabras", hue="Category", bins=60, kde=True,
                 palette=colores, ax=axes[1], alpha=0.5, log_scale=(True, False))
    axes[1].set_title("Distribución de Cantidad de Palabras (Log-Scale)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Palabras por Correo (Escala Log)")
    axes[1].set_ylabel("Frecuencia")
    
    salida = CARPETA_GRAFICOS / "02_distribucion_longitud.png"
    plt.tight_layout()
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[Graficos] Exportado -> {salida}")


def graficar_comparativa_modelos():
    """03: Comparativa de métricas clave entre modelos."""
    if not METRICAS_CSV.exists():
        print(f"[Graficos] Falta {METRICAS_CSV}, omitiendo comparativa.")
        return
        
    df_m = pd.read_csv(METRICAS_CSV)
    metricas = ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"]
    metricas_existentes = [m for m in metricas if m in df_m.columns]
    
    df_melt = df_m.melt(id_vars=["modelo"], value_vars=metricas_existentes,
                        var_name="Metrica", value_name="Puntaje")
    df_melt["Puntaje"] = df_melt["Puntaje"] * 100
    
    plt.figure(figsize=(12, 6), dpi=300)
    ax = sns.barplot(data=df_melt, x="modelo", y="Puntaje", hue="Metrica", palette="tab10", edgecolor="black", linewidth=0.5)
    
    plt.title("Comparativa de Rendimiento por Modelo y Corpus (Test Interno)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Modelo / Corpus", fontsize=11, fontweight="bold")
    plt.ylabel("Puntaje (%)", fontsize=11, fontweight="bold")
    plt.ylim(85, 101)
    plt.legend(title="Métrica", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=15, ha="right")
    
    salida = CARPETA_GRAFICOS / "03_comparativa_metricas_modelos.png"
    plt.tight_layout()
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[Graficos] Exportado -> {salida}")


def graficar_matrices_confusion():
    """04: Matrices de confusión para los modelos en inglés y español."""
    if not (MODELO_EN.exists() and MODELO_ES.exists()):
        print("[Graficos] Faltan archivos de modelos en models/, omitiendo matrices.")
        return
        
    df_en = pd.read_csv(DATA_NLP)
    df_es = pd.read_csv(DATA_NEURAL if DATA_NEURAL.exists() else DATA_TRADUCIDO)
    
    with open(MODELO_EN, "rb") as f:
        mod_en = pickle.load(f)
    with open(MODELO_ES, "rb") as f:
        mod_es = pickle.load(f)
        
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    
    # Evaluar EN
    X_en = df_en["clean_en"].astype(str)
    y_en = df_en["Label_Code"].astype(int)
    _, Xte_en, _, yte_en = train_test_split(X_en, y_en, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_en)
    pred_en = mod_en.predict(Xte_en)
    cm_en = confusion_matrix(yte_en, pred_en)
    
    disp_en = ConfusionMatrixDisplay(cm_en, display_labels=["Ham (0)", "Spam (1)"])
    disp_en.plot(ax=axes[0], cmap="Blues", values_format="d", colorbar=False)
    axes[0].set_title(f"Matriz de Confusión - Inglés (Umbral={mod_en.umbral})", fontsize=12, fontweight="bold")
    axes[0].grid(False)
    
    # Evaluar ES
    X_es = df_es["texto_es"].astype(str)
    y_es = df_es["Label_Code"].astype(int)
    _, Xte_es, _, yte_es = train_test_split(X_es, y_es, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_es)
    pred_es = mod_es.predict(Xte_es)
    cm_es = confusion_matrix(yte_es, pred_es)
    
    disp_es = ConfusionMatrixDisplay(cm_es, display_labels=["Ham (0)", "Spam (1)"])
    disp_es.plot(ax=axes[1], cmap="Oranges", values_format="d", colorbar=False)
    axes[1].set_title(f"Matriz de Confusión - Español (Umbral={mod_es.umbral})", fontsize=12, fontweight="bold")
    axes[1].grid(False)
    
    salida = CARPETA_GRAFICOS / "04_matrices_confusion.png"
    plt.tight_layout()
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[Graficos] Exportado -> {salida}")


def graficar_explicabilidad_xai():
    """05: Gráfico divergente de Top Palabras con mayor peso Log-Odds (Spam vs Ham)."""
    if not MODELO_ES.exists():
        return
    with open(MODELO_ES, "rb") as f:
        mod_es = pickle.load(f)
        
    top_spam = mod_es.top_spam[:12]
    top_ham = mod_es.top_ham[:12]
    
    palabras = [w for w, s in top_spam][::-1] + [w for w, s in top_ham]
    scores = [s for w, s in top_spam][::-1] + [-s for w, s in top_ham]
    colores = ["#e74c3c" if s > 0 else "#2ecc71" for s in scores]
    
    plt.figure(figsize=(10, 7), dpi=300)
    y_pos = np.arange(len(palabras))
    plt.barh(y_pos, scores, color=colores, edgecolor="black", linewidth=0.5)
    plt.yticks(y_pos, palabras, fontsize=10, fontweight="bold")
    plt.axvline(0, color="black", linewidth=1, linestyle="--")
    
    plt.title("Explicabilidad XAI: Términos con Mayor Impacto Discriminante (Log-Odds)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Log-Odds Ratio (Positivo = SPAM, Negativo = HAM)", fontsize=11, fontweight="bold")
    
    # Leyendas manuales
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#e74c3c', label='Gatillos de SPAM'),
                       Patch(facecolor='#2ecc71', label='Indicadores de HAM')]
    plt.legend(handles=legend_elements, loc="lower right", frameon=True)
    
    salida = CARPETA_GRAFICOS / "05_top_terminos_explicabilidad_xai.png"
    plt.tight_layout()
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[Graficos] Exportado -> {salida}")


def graficar_curvas_roc_pr():
    """06: Curvas ROC y Precision-Recall comparativas."""
    if not (MODELO_EN.exists() and MODELO_ES.exists()):
        return
    df_en = pd.read_csv(DATA_NLP)
    df_es = pd.read_csv(DATA_NEURAL if DATA_NEURAL.exists() else DATA_TRADUCIDO)
    
    with open(MODELO_EN, "rb") as f: mod_en = pickle.load(f)
    with open(MODELO_ES, "rb") as f: mod_es = pickle.load(f)
        
    _, Xte_en, _, yte_en = train_test_split(df_en["clean_en"].astype(str), df_en["Label_Code"].astype(int),
                                          test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=df_en["Label_Code"])
    _, Xte_es, _, yte_es = train_test_split(df_es["texto_es"].astype(str), df_es["Label_Code"].astype(int),
                                          test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=df_es["Label_Code"])
    
    prob_en = mod_en.predict_proba(Xte_en)[:, 1]
    prob_es = mod_es.predict_proba(Xte_es)[:, 1]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    
    # 1. Curva ROC
    fpr_en, tpr_en, _ = roc_curve(yte_en, prob_en)
    fpr_es, tpr_es, _ = roc_curve(yte_es, prob_es)
    axes[0].plot(fpr_en, tpr_en, color="#2980b9", lw=2, label=f"Modelo EN (AUC = {auc(fpr_en, tpr_en):.4f})")
    axes[0].plot(fpr_es, tpr_es, color="#e67e22", lw=2, label=f"Modelo ES (AUC = {auc(fpr_es, tpr_es):.4f})")
    axes[0].plot([0, 1], [0, 1], color="grey", linestyle="--")
    axes[0].set_title("Curva ROC Comparativa", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Tasa de Falsos Positivos (FPR)")
    axes[0].set_ylabel("Tasa de Verdaderos Positivos (Recall / TPR)")
    axes[0].legend(loc="lower right")
    
    # 2. Curva Precision-Recall
    prec_en, rec_en, _ = precision_recall_curve(yte_en, prob_en)
    prec_es, rec_es, _ = precision_recall_curve(yte_es, prob_es)
    axes[1].plot(rec_en, prec_en, color="#2980b9", lw=2, label=f"Modelo EN (PR-AUC = {average_precision_score(yte_en, prob_en):.4f})")
    axes[1].plot(rec_es, prec_es, color="#e67e22", lw=2, label=f"Modelo ES (PR-AUC = {average_precision_score(yte_es, prob_es):.4f})")
    axes[1].set_title("Curva Precision-Recall Comparativa", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].legend(loc="lower left")
    
    salida = CARPETA_GRAFICOS / "06_curvas_roc_y_pr.png"
    plt.tight_layout()
    plt.savefig(salida, dpi=300)
    plt.close()
    print(f"[Graficos] Exportado -> {salida}")


def main():
    print("=" * 60)
    print("      GENERANDO FIGURAS Y GRÁFICOS DEL PROYECTO       ")
    print("=" * 60)
    df_limpio = pd.read_csv(DATA_LIMPIO)
    
    graficar_distribucion_clases(df_limpio)
    graficar_distribucion_longitud(df_limpio)
    graficar_comparativa_modelos()
    graficar_matrices_confusion()
    graficar_explicabilidad_xai()
    graficar_curvas_roc_pr()
    
    print("\n[OK] Todos los graficos han sido exportados a:")
    print(f"   {CARPETA_GRAFICOS}")
    print("=" * 60)


if __name__ == "__main__":
    main()

