# ExoMinerAI 🚀🔭

ExoMinerAI es un proyecto para entrenar y evaluar modelos de machine learning destinados a identificar exoplanetas utilizando datos públicos de Kepler, K2 y TESS.

Este repositorio contiene scripts de preprocesamiento, notebooks de análisis exploratorio, modelos y una pequeña interfaz web para visualizar resultados.

## Índice

- Descripción
- Rápido inicio (Quickstart)
- Estructura del proyecto
- Datos
- Uso del modelo (CLI)
- Notebooks
- Desarrollo y contribución
- Licencia

## Descripción

El objetivo es facilitar la preparación de datos procedentes de diferentes misiones astronómicas, entrenar clasificadores (p. ej. Random Forest) y exponer utilidades para predecir la clasificación de eventos transitivos (Confirmado / Candidato / Falso positivo). También incluye una pequeña web para exploración.

## Rápido inicio (Quickstart)

1) Clonar el repositorio:

```powershell
git clone <tu-repo-url>
cd ExoMinerAI
```

2) Crear un entorno virtual e instalar dependencias (si tienes un `requirements.txt`):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Nota: hay un requirements en src/webapp/ si usas la web
pip install -r src/webapp/requirements.txt
```

3) Asegúrate de que las rutas de los archivos CSV están en `data/raw/` y `data/processed/` (el repositorio incluye ejemplos en `data/`).

4) Ejecuta el script de predicción (ejemplo):

```powershell
python src/preprocessing/rf_predict.py --ra 123.45 --dec -23.4 --pl_orbper 10.5 --pl_rade 2.3 --pl_insol 150.0 --pl_eqt 500 --st_teff 5500 --st_logg 4.4 --st_rad 1.0 --st_tmag 12.3 --mission TESS
```

El script entrenará y guardará un modelo cacheado en `src/preprocessing/rf_model.joblib` si no existe y luego imprimirá la etiqueta predicha (`CONFIRMED`, `CANDIDATE`, `FALSE`, etc.). Añade `--retrain` para forzar reentrenamiento.

## Estructura del proyecto

Resumen de archivos y carpetas más relevantes:

- `data/`
  - `raw/` : CSVs originales (Kepler, K2, TESS)
  - `processed/` : CSVs limpiados y preparados para modelado (ej.: `cleaned_datasets.csv`)
- `src/preprocessing/` : Notebooks y scripts de limpieza y preparación (`concat_files.ipynb`, `k2_cleaning.ipynb`, etc.). Contiene `rf_predict.py` para predicción por CLI.
- `src/models/` : (vacío/ubicación prevista) para scripts de entrenamiento/guardado de modelos.
- `src/webapp/` : Código de la aplicación web (Flask/Streamlit/FastAPI) y sus dependencias.
- `notebooks/` : Notebooks de exploración y EDA.

## Datos

Rutas usadas en los notebooks y scripts del proyecto (relativas al repositorio):

- Datos sin procesar: `data/raw/Kepler_cumulative_*.csv`, `data/raw/k2pandc_*.csv`, `data/raw/TESS_TOI_*.csv`
- Datos procesados/limpios: `data/processed/cleaned_datasets.csv`, `data/processed/encoded_datasets.csv`

Si usas los scripts desde `src/preprocessing/`, las rutas relativas en los notebooks usan `../../data/...` para alcanzar la carpeta `data/` en la raíz del proyecto.

## Uso del modelo (rf_predict)

El script `src/preprocessing/rf_predict.py` ofrece una interfaz simple por línea de comandos que recibe las 11 características principales y devuelve la predicción de `disposition_norm`.

Campos esperados (orden/flags CLI):

- `--ra` (float)
- `--dec` (float)
- `--pl_orbper` (float)
- `--pl_rade` (float)
- `--pl_insol` (float)
- `--pl_eqt` (float)
- `--st_teff` (float)
- `--st_logg` (float)
- `--st_rad` (float)
- `--st_tmag` (float)
- `--mission` (string) — ejemplos: `TESS`, `Kepler`, `K2`

Ejemplo:

```powershell
python src/preprocessing/rf_predict.py --ra 123.45 --dec -23.4 --pl_orbper 10.5 --pl_rade 2.3 --pl_insol 150.0 --pl_eqt 500 --st_teff 5500 --st_logg 4.4 --st_rad 1.0 --st_tmag 12.3 --mission TESS
```

Salida: una sola línea con la etiqueta predicha (por ejemplo `CONFIRMED`).

Problemas comunes:
- Si aparece un error de archivo no encontrado, verifica tu directorio de trabajo o que `data/processed/cleaned_datasets.csv` exista.
- Si `mission` tiene un valor que no apareció en el entrenamiento, el script devolverá un error; puedes reentrenar el modelo usando `--retrain`.

## Notebooks

Los notebooks en `src/preprocessing/` y `notebooks/` contienen pasos de limpieza, unión de catálogos y EDA. Para reproducir los resultados:

1. Abre el notebook en Jupyter (o VS Code).
2. Ejecuta las celdas de import y carga de datos (asegúrate que las rutas relativas a `data/` son correctas).

Consejo: usa rutas basadas en `pathlib.Path` cuando conviertas los notebooks a scripts para mayor robustez.

## Desarrollo y contribución

- Añade issues para bugs o features.
- Usa ramas para cambios grandes y PRs para revisión.
- Añade tests en `tests/` cuando modifiques lógica de preprocesamiento o modelos.

## Licencia y contacto

Este repositorio no incluye una licencia específica por defecto. Añade un `LICENSE` si quieres que sea open-source con condiciones claras (MIT, Apache-2.0, etc.).

Contacto: abre un issue en el repositorio o contacta al mantenedor del proyecto.

---

Recursos externos: algunos notebooks y ejemplos fueron creados a partir de catálogos públicos de Kepler, K2 y TESS proporcionados por la NASA y sus colaboradores.
