# --- Librerías ---
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC   # <- fix typo (SVC1 -> SVC)
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
import seaborn as sns

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

# --- Cargar catálogos ---
tess = pd.read_csv("../../data/raw/TESS_TOI_2025.10.04_12.41.47.csv")
kepler = pd.read_csv("../../data/raw/Kepler_cumulative_2025.10.04_12.41.25.csv")
k2 = pd.read_csv("../../data/raw/k2pandc_2025.10.04_12.42.17.csv")

# --- Renombrar/homogeneizar ---
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

# --- Unir ---
combined = pd.concat([tess_reduced_df, kepler_reduced_df, k2_reduced_df], ignore_index=True)

# --- Normalizar etiqueta ---
combined['disposition_norm'] = combined['disposition_raw'].apply(normalize_disposition)

# (Opcional) si no quieres UNKNOWN en el entrenamiento:
# combined = combined[combined['disposition_norm'] != 'UNKNOWN']

# --- Limpieza ---
# Evita SettingWithCopy usando asignación sin inplace
cleaned_df = combined.dropna().drop(columns=['disposition_raw']).reset_index(drop=True)

# --- Codificación ---
encoded_df = cleaned_df.copy()
label_encoders = {}
encoding_maps = {}

for col in encoded_df.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    encoded_df[col] = le.fit_transform(encoded_df[col])
    label_encoders[col] = le
    encoding_maps[col] = dict(zip(le.classes_, le.transform(le.classes_)))

# Guarda datasets si lo necesitas
encoded_df.to_csv("../../data/processed/encoded_datasets.csv", index=False)
cleaned_df.to_csv("../../data/processed/cleaned_datasets.csv", index=False)

# --- Variables ---
data = encoded_df.copy()  # <- fuera del bucle
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
disposition_norm_classes = le_status.classes_              # e.g., ['CANDIDATE','CONFIRMED','FALSE','UNKNOWN']
class_labels = list(range(len(disposition_norm_classes)))  # [0,1,2,3]

# --- Modelo ---
name = 'Random Forest'
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)

print(f"🔹 {name}")
print(f"   Exactitud: {acc:.4f}")

# --- Reporte (forzando todas las clases en orden consistente) ---
print("   Reporte:")
print(classification_report(
    y_test, preds,
    labels=class_labels,
    target_names=disposition_norm_classes,
    zero_division=0
))


# --- Matrices de confusión ---
cm = confusion_matrix(y_test, preds, labels=class_labels)
cm_norm = cm.astype(float) / (cm.sum(axis=1, keepdims=True) + 1e-8)

plt.figure(figsize=(6,4))
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Greens',
            xticklabels=disposition_norm_classes, yticklabels=disposition_norm_classes)
plt.xlabel('Predicted'); plt.ylabel('Actual')
plt.title(f'Matriz de Confusión Normalizada - {name}')
plt.tight_layout(); plt.show()

plt.figure(figsize=(6,4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=disposition_norm_classes, yticklabels=disposition_norm_classes)
plt.xlabel('Predicted'); plt.ylabel('Actual')
plt.title(f'Matriz de Confusión - {name}')
plt.tight_layout(); plt.show()
