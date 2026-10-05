"""Etapa 05: entrenamiento con optimización, comparativa y serialización completa.

- Para cada corpus (EN, ES-léxico, ES-neuronal si existe):
  - Naive Bayes con GridSearchCV (max_features, ngram_range, alpha).
  - Regresión Logística baseline (grid en C).
  - CV estratificada repetida: se reporta media ± std.
  - Umbral óptimo (máx F1) ajustado en partición de validación interna.
  - Métricas avanzadas: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC.
  - Explicabilidad: extracción de Top Log-Odds / Coeficientes discriminantes.
- Empaqueta el pipeline completo y el umbral calibrado en SpamClassifierWrapper.
- Guarda modelos en models/, metricas.csv y docs/errores_*.csv.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import (DATA_NLP, DATA_TRADUCIDO, DATA_NEURAL, MODELO_ES, MODELO_EN,
                    METRICAS_CSV, RANDOM_STATE, TEST_SIZE)
from modelo_wrapper import SpamClassifierWrapper

STOP_ES_FALLBACK = ["de", "la", "el", "en", "y", "a", "los", "del", "se", "las",
                    "por", "un", "para", "con", "no", "una", "su", "al", "es",
                    "lo", "como", "mas", "pero", "sus", "le", "ya", "o", "este",
                    "si", "porque", "esta", "entre", "cuando", "muy", "sin",
                    "sobre", "tambien", "me", "hasta", "hay", "donde", "quien",
                    "desde", "todo", "nos", "tu", "que", "esto", "eso"]


def stop_es():
    try:
        from nltk.corpus import stopwords
        return stopwords.words("spanish")
    except Exception:
        print("[05] NLTK stopwords no disponible; uso lista local.")
        return STOP_ES_FALLBACK


def mejor_umbral(y_true, proba):
    import numpy as np
    from sklearn.metrics import f1_score
    umbrales = np.arange(0.2, 0.81, 0.05)
    fs = [f1_score(y_true, (proba >= u).astype(int), zero_division=0) for u in umbrales]
    i = int(np.argmax(fs))
    return round(float(umbrales[i]), 2), round(float(fs[i]), 4)


def evaluar(nombre, modelo, Xte, yte, umbral=0.5):
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                 f1_score, roc_auc_score, average_precision_score)
    proba = modelo.predict_proba(Xte)[:, 1]
    pred = (proba >= umbral).astype(int)
    
    try:
        roc_auc = round(float(roc_auc_score(yte, proba)), 4)
        pr_auc = round(float(average_precision_score(yte, proba)), 4)
    except Exception:
        roc_auc, pr_auc = 0.0, 0.0
        
    return {
        "modelo": nombre,
        "accuracy": round(float(accuracy_score(yte, pred)), 4),
        "precision": round(float(precision_score(yte, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(yte, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(yte, pred, zero_division=0)), 4),
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "umbral": round(float(umbral), 2)
    }


def cv_repetida(modelo, X, y):
    from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
    cv = RepeatedStratifiedKFold(n_splits=3, n_repeats=2, random_state=RANDOM_STATE)
    s = cross_val_score(modelo, X, y, cv=cv, scoring="f1", n_jobs=-1)
    return round(float(s.mean()), 4), round(float(s.std()), 4)


def extraer_top_features(pipeline, top_n=60):
    """Calcula las características más discriminantes para Spam y Ham."""
    import numpy as np
    try:
        vectorizer = pipeline.named_steps["tfidf"]
        feature_names = np.array(vectorizer.get_feature_names_out())
        
        if "nb" in pipeline.named_steps:
            nb = pipeline.named_steps["nb"]
            log_prob = nb.feature_log_prob_
            diff = log_prob[1] - log_prob[0]
            top_spam_idx = np.argsort(diff)[-top_n:][::-1]
            top_ham_idx = np.argsort(diff)[:top_n]
            top_spam = [(feature_names[i], round(float(diff[i]), 3)) for i in top_spam_idx]
            top_ham = [(feature_names[i], round(float(-diff[i]), 3)) for i in top_ham_idx]
            return top_spam, top_ham
        elif "lr" in pipeline.named_steps:
            lr = pipeline.named_steps["lr"]
            coefs = lr.coef_[0]
            top_spam_idx = np.argsort(coefs)[-top_n:][::-1]
            top_ham_idx = np.argsort(coefs)[:top_n]
            top_spam = [(feature_names[i], round(float(coefs[i]), 3)) for i in top_spam_idx]
            top_ham = [(feature_names[i], round(float(-coefs[i]), 3)) for i in top_ham_idx]
            return top_spam, top_ham
    except Exception as e:
        print(f"[05] Error al extraer top features: {e}")
    return [], []


def entrenar_corpus(df, col, stop, nombre):
    from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    
    X = df[col].astype(str)
    y = df["Label_Code"].astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=TEST_SIZE,
                                          random_state=RANDOM_STATE, stratify=y)
    # Sub-split para calibrar umbral en validación interna
    Xtr2, Xval, ytr2, yval = train_test_split(Xtr, ytr, test_size=0.2,
                                              random_state=RANDOM_STATE, stratify=ytr)
    cv3 = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)

    # --- 1. Naive Bayes con GridSearch ---
    grid_nb = GridSearchCV(
        Pipeline([("tfidf", TfidfVectorizer(stop_words=stop, sublinear_tf=True)),
                  ("nb", MultinomialNB())]),
        {"tfidf__max_features": [10000, 15000, 20000],
         "tfidf__ngram_range": [(1, 1), (1, 2)],
         "nb__alpha": [0.1, 0.3, 0.5, 1.0]},
        cv=cv3, scoring="f1", n_jobs=-1)
    grid_nb.fit(Xtr, ytr)
    best_nb = grid_nb.best_estimator_
    print(f"[05] {nombre} NB best: {grid_nb.best_params_} (cv={grid_nb.best_score_:.4f})")

    # --- 2. Regresión Logística baseline / comparativa ---
    grid_lr = GridSearchCV(
        Pipeline([("tfidf", TfidfVectorizer(stop_words=stop, max_features=15000,
                                            ngram_range=(1, 2), sublinear_tf=True)),
                  ("lr", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE))]),
        {"lr__C": [0.5, 1.0, 2.0, 4.0]}, cv=cv3, scoring="f1", n_jobs=-1)
    grid_lr.fit(Xtr, ytr)
    best_lr = grid_lr.best_estimator_
    print(f"[05] {nombre} LR best: {grid_lr.best_params_} (cv={grid_lr.best_score_:.4f})")

    # Calibrar umbrales óptimos en validación
    best_nb.fit(Xtr2, ytr2)
    umbral_nb, _ = mejor_umbral(yval, best_nb.predict_proba(Xval)[:, 1])
    best_nb.fit(Xtr, ytr)

    best_lr.fit(Xtr2, ytr2)
    umbral_lr, _ = mejor_umbral(yval, best_lr.predict_proba(Xval)[:, 1])
    best_lr.fit(Xtr, ytr)

    # Extraer explicabilidad (top palabras de spam/ham)
    top_spam_nb, top_ham_nb = extraer_top_features(best_nb)
    top_spam_lr, top_ham_lr = extraer_top_features(best_lr)

    filas = []
    wrappers = {}
    for tag, mod, umb, top_s, top_h, grid in [
        ("nb", best_nb, umbral_nb, top_spam_nb, top_ham_nb, grid_nb),
        ("lr", best_lr, umbral_lr, top_spam_lr, top_ham_lr, grid_lr)
    ]:
        m = evaluar(f"{nombre}_{tag}", mod, Xte, yte, umbral=umb)
        mean_cv, std_cv = cv_repetida(mod, Xtr, ytr)
        m.update({"n": len(df), "corpus": nombre,
                  "f1_cv_mean": mean_cv, "f1_cv_std": std_cv,
                  "best_params": str(grid.best_params_)})
        filas.append(m)
        
        wrapper = SpamClassifierWrapper(pipeline=mod, umbral=umb, idioma=nombre,
                                        metricas=m, top_spam=top_s, top_ham=top_h)
        wrappers[tag] = wrapper

    return wrappers, filas, (Xte, yte)


def analisis_errores(df_test_texts, y_true, wrapper, salida_csv, nombre):
    import pandas as pd
    proba = wrapper.predict_proba(df_test_texts)[:, 1]
    pred = wrapper.predict(df_test_texts)
    mask_fp = (pred == 1) & (y_true == 0)
    mask_fn = (pred == 0) & (y_true == 1)
    err = pd.DataFrame({"texto": df_test_texts, "real": y_true, "p_spam": proba.round(3),
                        "pred": pred})
    err = err[mask_fp | mask_fn].copy()
    err["tipo"] = ["FP" if a else "FN" for a in (err["pred"] == 1)]
    salida_csv.parent.mkdir(parents=True, exist_ok=True)
    err.head(100).to_csv(salida_csv, index=False, encoding="utf-8")
    print(f"[05] Errores {nombre}: {int(mask_fp.sum())} FP + {int(mask_fn.sum())} FN -> {salida_csv}")


def guardar_grafico_etapa05(df_metricas: "pd.DataFrame", wrappers_dict: dict, ruta_grafico: Path):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        ruta_grafico.parent.mkdir(parents=True, exist_ok=True)
        
        fig = plt.figure(figsize=(16, 10), dpi=300)
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
        
        # Panel 1: Comparativa de Métricas de Modelos (F1, Precision, Recall, ROC-AUC)
        ax1 = fig.add_subplot(gs[0, :])
        metricas_cols = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        df_melt = df_metricas.melt(id_vars=["modelo"], value_vars=metricas_cols,
                                  var_name="Métrica", value_name="Valor")
        sns.barplot(data=df_melt, x="Métrica", y="Valor", hue="modelo",
                    palette="Blues_d", edgecolor="black", linewidth=0.6, ax=ax1)
        ax1.set_ylim(0.85, 1.01)
        ax1.set_title("Comparativa de Rendimiento por Modelo y Corpus (Validación)", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Puntuación (0.0 - 1.0)", fontsize=10, fontweight="bold")
        ax1.legend(loc="lower right")
        ax1.grid(axis="y", linestyle="--", alpha=0.5)
        
        # Panel 2: XAI - Top 10 Palabras Predictoras de Spam en Inglés
        ax2 = fig.add_subplot(gs[1, 0])
        if "en" in wrappers_dict and wrappers_dict["en"].top_spam:
            top_en = wrappers_dict["en"].top_spam[:10]
            words_en = [w for w, _ in top_en][::-1]
            scores_en = [s for _, s in top_en][::-1]
            ax2.barh(words_en, scores_en, color="#e74c3c", edgecolor="black", linewidth=0.6)
            ax2.set_title("Top 10 Términos Spam - Modelo Inglés (Log-Odds)", fontsize=11, fontweight="bold")
            ax2.set_xlabel("Log-Odds Ratio (Spam / Ham)", fontsize=9, fontweight="bold")
            ax2.grid(axis="x", linestyle="--", alpha=0.5)
            
        # Panel 3: XAI - Top 10 Palabras Predictoras de Spam en Español
        ax3 = fig.add_subplot(gs[1, 1])
        clave_es = "es_neural" if "es_neural" in wrappers_dict else ("es_lex" if "es_lex" in wrappers_dict else None)
        if clave_es and wrappers_dict[clave_es].top_spam:
            top_es = wrappers_dict[clave_es].top_spam[:10]
            words_es = [w for w, _ in top_es][::-1]
            scores_es = [s for _, s in top_es][::-1]
            ax3.barh(words_es, scores_es, color="#c0392b", edgecolor="black", linewidth=0.6)
            ax3.set_title(f"Top 10 Términos Spam - Modelo Español ({clave_es})", fontsize=11, fontweight="bold")
            ax3.set_xlabel("Log-Odds Ratio (Spam / Ham)", fontsize=9, fontweight="bold")
            ax3.grid(axis="x", linestyle="--", alpha=0.5)
            
        plt.suptitle("Etapa 05: Resultados de Entrenamiento y Explicabilidad (XAI)", fontsize=14, fontweight="bold", y=0.98)
        plt.savefig(ruta_grafico, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"[05] Gráfico generado -> {ruta_grafico}")
    except Exception as e:
        print(f"[05] Advertencia al generar gráfico: {e}")


def main():
    import pandas as pd
    import pickle
    stopwords_es = stop_es()
    print(f"[05] Stopwords ES cargadas: {len(stopwords_es)}")
    
    corpora = [("en", pd.read_csv(DATA_NLP), "clean_en", "english")]
    if DATA_TRADUCIDO.exists():
        corpora.append(("es_lex", pd.read_csv(DATA_TRADUCIDO), "texto_es", stopwords_es))
    if DATA_NEURAL.exists():
        corpora.append(("es_neural", pd.read_csv(DATA_NEURAL), "texto_es", stopwords_es))

    todas, wrappers_guardar = [], {}
    for nombre, df, col, stop in corpora:
        print(f"\n[05] === Entrenando Corpus: {nombre.upper()} ({len(df)} filas) ===")
        wrappers, filas, ev = entrenar_corpus(df, col, stop, nombre)
        todas.extend(filas)
        # Seleccionamos Naive Bayes como modelo principal por requerimiento de proyecto
        wrappers_guardar[nombre] = wrappers["nb"]
        
        Xte_texts = ev[0]
        analisis_errores(Xte_texts, ev[1].values if hasattr(ev[1], "values") else ev[1],
                         wrappers["nb"],
                         MODELO_EN.parent.parent / "docs" / f"errores_{nombre}.csv", nombre)

    MODELO_EN.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar modelo inglés serializado con Wrapper y umbral calibrado
    with open(MODELO_EN, "wb") as f:
        pickle.dump(wrappers_guardar["en"], f)
    print(f"[05] Guardado modelo EN: {MODELO_EN} (umbral={wrappers_guardar['en'].umbral})")
    
    # Guardar modelo español (prioriza neuronal si existe, si no léxico)
    clave_es = "es_neural" if "es_neural" in wrappers_guardar else ("es_lex" if "es_lex" in wrappers_guardar else None)
    if clave_es:
        with open(MODELO_ES, "wb") as f:
            pickle.dump(wrappers_guardar[clave_es], f)
        print(f"[05] Guardado modelo ES ({clave_es}): {MODELO_ES} (umbral={wrappers_guardar[clave_es].umbral})")
        
    df_metricas = pd.DataFrame(todas)
    df_metricas.to_csv(METRICAS_CSV, index=False, encoding="utf-8")
    print(f"[05] Métricas exportadas -> {METRICAS_CSV}")
    print("\n" + df_metricas[["modelo", "n", "accuracy", "precision", "recall",
                              "f1", "roc_auc", "pr_auc", "f1_cv_mean", "umbral"]].to_string(index=False))

    # Generar gráfico respectivo de la Etapa 05
    grafico_path = MODELO_EN.parent.parent / "docs" / "graficos" / "05_entrenamiento_matrices_y_xai.png"
    guardar_grafico_etapa05(df_metricas, wrappers_guardar, grafico_path)


if __name__ == "__main__":
    main()

