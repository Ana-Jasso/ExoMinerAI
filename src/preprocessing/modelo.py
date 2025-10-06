# --- Librerías ---
import os
import glob
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier

# --- Utilidad ---
def normalize_disposition(x):
    val = str(x).strip().upper()
    if val in {'CONFIRMED', 'CP', 'KP'}:
        return 'CONFIRMED'
    elif val in {'CANDIDATE', 'PC', 'APC'}:
        return 'CANDIDATE'
    elif val in {'FALSE POSITIVE', 'FP', 'FA', 'REFUTED'}:
        return 'FALSE'
    else:
        return 'UNKNOWN'

def safe_read_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        print(f"⚠️ Archivo no encontrado: {path}")
        return pd.DataFrame()

def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getctime) if files else None

# --- Cargar catálogos ---
tess_path = latest_file("../../data/raw/TESS_TOI_*.csv")
kepler_path = latest_file("../../data/raw/Kepler_cumulative_*.csv")
k2_path = latest_file("../../data/raw/k2pandc_*.csv")

tess = safe_read_csv(tess_path)
kepler = safe_read_csv(kepler_path)
k2 = safe_read_csv(k2_path)

# --- Renombrar/homogeneizar ---
if not tess.empty:
    tess = tess.rename(columns={
        'tfopwg_disp': 'disposition_raw',
        'pl_orbper': 'pl_orbper',
        'pl_rade': 'pl_rade',
        'pl_insol': 'pl_insol',
        'pl_eqt': 'pl_eqt',
        'st_teff': 'st_teff',
        'st_logg': 'st_logg',
        'st_rad': 'st_rad',
        'st_tmag': 'st_tmag',
    })
    tess['mission'] = 'TESS'
    tess_reduced_df = tess[['disposition_raw','ra','dec','pl_orbper','pl_rade','pl_insol','pl_eqt','st_teff','st_logg','st_rad','st_tmag','mission']]
else:
    tess_reduced_df = pd.DataFrame()

if not kepler.empty:
    kepler = kepler.rename(columns={
        'koi_disposition': 'disposition_raw',
        'koi_period': 'pl_orbper',
        'koi_prad': 'pl_rade',
        'koi_insol': 'pl_insol',
        'koi_teq': 'pl_eqt',
        'koi_steff': 'st_teff',
        'koi_slogg': 'st_logg',
        'koi_srad': 'st_rad',
        'koi_kepmag': 'st_tmag',
    })
    kepler['mission'] = 'Kepler'
    kepler_reduced_df = kepler[['disposition_raw','ra','dec','pl_orbper','pl_rade','pl_insol','pl_eqt','st_teff','st_logg','st_rad','st_tmag','mission']]
else:
    kepler_reduced_df = pd.DataFrame()

if not k2.empty:
    k2 = k2.rename(columns={
        'disposition': 'disposition_raw',
        'pl_orbper': 'pl_orbper',
        'pl_rade': 'pl_rade',
        'pl_insol': 'pl_insol',
        'pl_eqt': 'pl_eqt',
        'st_teff': 'st_teff',
        'st_logg': 'st_logg',
        'st_rad': 'st_rad',
        'sy_vmag': 'st_tmag',
    })
    k2['mission'] = 'K2'
    k2_reduced_df = k2[['disposition_raw','ra','dec','pl_orbper','pl_rade','pl_insol','pl_eqt','st_teff','st_logg','st_rad','st_tmag','mission']]
else:
    k2_reduced_df = pd.DataFrame()

# --- Unir ---
frames = [df for df in [tess_reduced_df, kepler_reduced_df, k2_reduced_df] if not df.empty]
combined = pd.concat(frames, ignore_index=True)

# --- Normalizar etiqueta ---
combined['disposition_norm'] = combined['disposition_raw'].apply(normalize_disposition)

# --- Limpieza ---
cleaned_df = combined.dropna().drop(columns=['disposition_raw']).reset_index(drop=True)

# --- Codificación ---
encoded_df = cleaned_df.copy()
label_encoders = {}
encoding_maps = {}

for col in encoded_df.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    encoded_df.loc[:, col] = le.fit_transform(encoded_df[col])
    label_encoders[col] = le
    encoding_maps[col] = dict(zip(le.classes_, le.transform(le.classes_)))

# --- Guardar datasets y mapas ---
os.makedirs("../../data/processed", exist_ok=True)
encoded_df.to_csv("../../data/processed/encoded_datasets.csv", index=False)
cleaned_df.to_csv("../../data/processed/cleaned_datasets.csv", index=False)
with open("../../data/processed/encoding_maps.json", "w") as f:
    json.dump(encoding_maps, f, indent=2)

# --- Variables ---
data = encoded_df.copy()
X = data.drop('disposition_norm', axis=1)
y = data['disposition_norm']

# --- Escalado ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- Split ---
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# --- Etiquetas legibles ---
le_status = label_encoders['disposition_norm']
disposition_norm_classes = le_status.classes_
class_labels = list(range(len(disposition_norm_classes)))

# --- Modelo ---
name = 'Random Forest'
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

print(f"🔹 {name}")
print(f"   Exactitud: {acc:.4f}")
print("   Reporte:")
print(classification_report(
    y_test, preds,
    labels=class_labels,
    target_names=disposition_norm_classes,
    zero_division=0
))
print("   Matriz de confusión:")
print(confusion_matrix(y_test, preds, labels=class_labels))