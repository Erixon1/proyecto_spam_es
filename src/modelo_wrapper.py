"""Módulo del contenedor y wrapper serializable para modelos de detección de spam."""
import re
import numpy as np


class SpamClassifierWrapper:
    """Contenedor serializable que acopla el pipeline de scikit-learn,
    el umbral calibrado de decisión, metadatos de entrenamiento y explicabilidad."""
    def __init__(self, pipeline, umbral=0.5, idioma="es", metricas=None,
                 top_spam=None, top_ham=None):
        self.pipeline = pipeline
        self.umbral = float(umbral)
        self.idioma = idioma
        self.metricas = metricas or {}
        self.top_spam = top_spam or []
        self.top_ham = top_ham or []

    def predict_proba(self, X):
        if isinstance(X, str):
            X = [X]
        return self.pipeline.predict_proba(X)

    def predict(self, X):
        if isinstance(X, str):
            X = [X]
        proba = self.pipeline.predict_proba(X)[:, 1]
        return (proba >= self.umbral).astype(int)

    def explicar(self, texto: str, top_k: int = 6):
        """Identifica palabras presentes en el texto que más empujan hacia Spam o Ham."""
        try:
            tfidf = self.pipeline.named_steps.get("tfidf")
            if not tfidf:
                return {"tokens_spam": [], "tokens_ham": []}
                
            feature_names = tfidf.get_feature_names_out()
            feature_map = {feat: idx for idx, feat in enumerate(feature_names)}
            
            words = re.findall(r"\b[a-záéíóúñü0-9_]+\b", texto.lower())
            
            if "nb" in self.pipeline.named_steps:
                nb = self.pipeline.named_steps["nb"]
                diff = nb.feature_log_prob_[1] - nb.feature_log_prob_[0]
            elif "lr" in self.pipeline.named_steps:
                lr = self.pipeline.named_steps["lr"]
                diff = lr.coef_[0]
            else:
                diff = None

            if diff is not None:
                candidatos = set(words)
                for i in range(len(words) - 1):
                    candidatos.add(f"{words[i]} {words[i+1]}")
                
                scores = []
                for c in candidatos:
                    if c in feature_map:
                        idx = feature_map[c]
                        scores.append((c, float(diff[idx])))
                
                scores_spam = sorted([s for s in scores if s[1] > 0], key=lambda x: x[1], reverse=True)[:top_k]
                scores_ham = sorted([s for s in scores if s[1] < 0], key=lambda x: x[1])[:top_k]
                
                return {
                    "tokens_spam": [f"{w} (+{s:.2f})" for w, s in scores_spam],
                    "tokens_ham": [f"{w} ({s:.2f})" for w, s in scores_ham]
                }
        except Exception:
            pass
        return {"tokens_spam": [], "tokens_ham": []}
