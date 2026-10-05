"""Etapa 08 (Opcional - Fase 4): Comparativa con Transformer Preentrenado (BETO / Multilingual BERT).

Permite fine-tuning o evaluación rápida de un modelo Transformer para clasificación de texto en español.
Modelo por defecto: dccuchile/bert-base-spanish-wwm-cased (BETO) o distilbert-base-multilingual-cased.

Uso:
    python src/08_transformer_es.py --epochs 2 --sample 2000
    python src/08_transformer_es.py --eval-only
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from config import DATA_TRADUCIDO, DATA_NEURAL, ROOT, RANDOM_STATE

METRICAS_TRANSFORMER = ROOT / "docs" / "metricas_transformer.csv"


def cargar_datos(sample_n: int = 2000):
    import pandas as pd
    ruta = DATA_NEURAL if DATA_NEURAL.exists() else DATA_TRADUCIDO
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró dataset en español en {ruta}. Ejecuta 04_traducir_es.py primero.")
    
    df = pd.read_csv(ruta)
    df = df.dropna(subset=["texto_es", "Label_Code"]).copy()
    
    if sample_n and sample_n < len(df):
        # Muestra estratificada representativa
        df = df.groupby("Label_Code", group_keys=False).apply(
            lambda x: x.sample(min(len(x), sample_n // 2), random_state=RANDOM_STATE)
        ).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    return df


def entrenar_transformer(model_name="dccuchile/bert-base-spanish-wwm-cased",
                        epochs=2, batch_size=16, sample_n=2000, lr=2e-5):
    import torch
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
    from datasets import Dataset

    print(f"[08] Cargando datos (muestra={sample_n})...")
    df = cargar_datos(sample_n)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[08] Dispositivo de cómputo: {device.upper()}")
    print(f"[08] Cargando modelo y tokenizador: {model_name}")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2).to(device)
    except Exception as e:
        print(f"[08] No se pudo cargar {model_name} ({e}), intentando 'distilbert-base-multilingual-cased'...")
        model_name = "distilbert-base-multilingual-cased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2).to(device)

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=RANDOM_STATE, stratify=df["Label_Code"])
    
    def tokenize_func(batch):
        return tokenizer(batch["texto_es"], padding="max_length", truncation=True, max_length=128)

    train_ds = Dataset.from_pandas(train_df[["texto_es", "Label_Code"]].rename(columns={"Label_Code": "label"}))
    test_ds = Dataset.from_pandas(test_df[["texto_es", "Label_Code"]].rename(columns={"Label_Code": "label"}))

    train_ds = train_ds.map(tokenize_func, batched=True)
    test_ds = test_ds.map(tokenize_func, batched=True)

    def compute_metrics(eval_pred):
        import numpy as np
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        probs = torch.softmax(torch.tensor(logits), dim=-1)[:, 1].numpy()
        return {
            "accuracy": round(float(accuracy_score(labels, preds)), 4),
            "precision": round(float(precision_score(labels, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(labels, preds, zero_division=0)), 4),
            "f1": round(float(f1_score(labels, preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(labels, probs)), 4)
        }

    output_dir = ROOT / "models" / "transformer_checkpoints"
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        learning_rate=lr,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        logging_steps=50,
        save_strategy="no",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        compute_metrics=compute_metrics
    )

    print(f"[08] Iniciando entrenamiento ({epochs} épocas)...")
    trainer.train()

    print("\n[08] Evaluando en partición de prueba...")
    eval_results = trainer.evaluate()
    
    METRICAS_TRANSFORMER.parent.mkdir(parents=True, exist_ok=True)
    res_row = {
        "modelo": model_name,
        "n_samples": sample_n,
        "epochs": epochs,
        "accuracy": eval_results.get("eval_accuracy", 0.0),
        "precision": eval_results.get("eval_precision", 0.0),
        "recall": eval_results.get("eval_recall", 0.0),
        "f1": eval_results.get("eval_f1", 0.0),
        "roc_auc": eval_results.get("eval_roc_auc", 0.0)
    }
    
    pd.DataFrame([res_row]).to_csv(METRICAS_TRANSFORMER, index=False, encoding="utf-8")
    print(f"[08] Resultados guardados en: {METRICAS_TRANSFORMER}")
    print(pd.DataFrame([res_row]).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="dccuchile/bert-base-spanish-wwm-cased", help="Modelo transformer HF")
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--sample", type=int, default=2000, help="Tamaño de subconjunto para entrenamiento rápido")
    args = ap.parse_args()
    entrenar_transformer(model_name=args.model, epochs=args.epochs, batch_size=args.batch, sample_n=args.sample)
