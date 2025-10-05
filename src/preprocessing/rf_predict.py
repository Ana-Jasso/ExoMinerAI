#!/usr/bin/env python3
"""rf_predict.py

Entrypoint para predecir la columna `disposition_norm` usando RandomForest.

Uso (desde la carpeta repo root o ejecutando el script):
python src/preprocessing/rf_predict.py \
  --ra 123.45 --dec -23.4 --pl_orbper 10.5 --pl_rade 2.3 --pl_insol 150.0 \
  --pl_eqt 500 --st_teff 5500 --st_logg 4.4 --st_rad 1.0 --st_tmag 12.3 --mission TESS

El script intentará cargar un modelo cacheado 'rf_model.joblib' en la misma carpeta
del script. Si no existe, entrenará un RandomForest usando
`../../data/processed/cleaned_datasets.csv` (ruta relativa al archivo).

Devuelve la predicción como texto (la etiqueta original de `disposition_norm`).
"""

from __future__ import annotations
import argparse
import os
import sys
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(HERE, "rf_model.joblib")
DEFAULT_CLEANED_CSV = os.path.join(HERE, "..", "..", "data", "processed", "cleaned_datasets.csv")

FEATURES = [
    "ra",
    "dec",
    "pl_orbper",
    "pl_rade",
    "pl_insol",
    "pl_eqt",
    "st_teff",
    "st_logg",
    "st_rad",
    "st_tmag",
    "mission",
]


def train_and_save_model(cleaned_csv_path: str, model_path: str) -> Dict[str, Any]:
    """Entrena un RandomForest sobre el CSV limpio y guarda el modelo + encoders.

    Retorna un dict con claves: model, encoders, le_y, features
    """
    if not os.path.exists(cleaned_csv_path):
        raise FileNotFoundError(f"CSV de entrada no encontrado: {cleaned_csv_path}")

    df = pd.read_csv(cleaned_csv_path)

    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas esperadas en el CSV: {missing}")

    X = df[FEATURES].copy()
    y = df["disposition_norm"].copy()

    encoders: Dict[str, LabelEncoder] = {}
    # Encodificar columnas categóricas presentes en X (como 'mission')
    for col in X.select_dtypes(include=[object]).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    # Y también puede ser texto; lo codificamos para el modelo
    le_y = LabelEncoder()
    y_enc = le_y.fit_transform(y.astype(str))

    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X.values, y_enc)

    payload = {"model": clf, "encoders": encoders, "le_y": le_y, "features": FEATURES}
    joblib.dump(payload, model_path)
    return payload


def load_or_train(model_path: str = MODEL_FILE, cleaned_csv: str = DEFAULT_CLEANED_CSV) -> Dict[str, Any]:
    if os.path.exists(model_path):
        try:
            payload = joblib.load(model_path)
            # Quick sanity check
            if not all(k in payload for k in ("model", "encoders", "le_y", "features")):
                raise ValueError("Modelo cargado incompleto, reentrenando...")
            return payload
        except Exception:
            print("Advertencia: no se pudo cargar el modelo cacheado, reentrenando...")

    print("Entrenando RandomForest (esto puede tardar unos segundos)...")
    return train_and_save_model(cleaned_csv, model_path)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Predecir disposition_norm usando RandomForest.")
    # Añadimos los 11 parámetros
    p.add_argument("--ra", required=True, type=float)
    p.add_argument("--dec", required=True, type=float)
    p.add_argument("--pl_orbper", required=True, type=float)
    p.add_argument("--pl_rade", required=True, type=float)
    p.add_argument("--pl_insol", required=True, type=float)
    p.add_argument("--pl_eqt", required=True, type=float)
    p.add_argument("--st_teff", required=True, type=float)
    p.add_argument("--st_logg", required=True, type=float)
    p.add_argument("--st_rad", required=True, type=float)
    p.add_argument("--st_tmag", required=True, type=float)
    p.add_argument("--mission", required=True, type=str, help="Ej: TESS, Kepler, K2")
    p.add_argument("--retrain", action="store_true", help="Forzar reentrenamiento del modelo")
    return p.parse_args(argv)


def build_input_row(args, encoders: Dict[str, LabelEncoder], features):
    vals = []
    for f in features:
        v = getattr(args, f)
        if isinstance(v, str):
            # columna categórica (ej. mission)
            if f in encoders:
                le = encoders[f]
                if v not in le.classes_:
                    raise ValueError(f"Valor '{v}' para '{f}' no apareció en los datos de entrenamiento. Clases: {list(le.classes_)}")
                vals.append(int(le.transform([v])[0]))
            else:
                # no tenemos encoder: intentar convertir a float
                try:
                    vals.append(float(v))
                except Exception:
                    raise ValueError(f"No hay encoder para '{f}' y no es numérico: {v}")
        else:
            # numérico
            vals.append(float(v))
    return np.array(vals, dtype=float)


def main(argv=None):
    args = parse_args(argv)

    # Load or train model
    if args.retrain and os.path.exists(MODEL_FILE):
        try:
            os.remove(MODEL_FILE)
        except Exception:
            pass

    payload = load_or_train(MODEL_FILE, DEFAULT_CLEANED_CSV)
    model: RandomForestClassifier = payload["model"]
    encoders: Dict[str, LabelEncoder] = payload["encoders"]
    le_y: LabelEncoder = payload["le_y"]
    features = payload.get("features", FEATURES)

    try:
        row = build_input_row(args, encoders, features)
    except Exception as e:
        print(f"Error preparando la fila de entrada: {e}")
        sys.exit(2)

    pred_idx = model.predict([row])[0]
    pred_label = le_y.inverse_transform([pred_idx])[0]
    print(pred_label)


if __name__ == "__main__":
    main()
