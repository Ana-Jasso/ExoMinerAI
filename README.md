# ExoMinerAI 🚀🔭

AI-powered exoplanet discovery using NASA's open-source datasets.

## 🌠 Descripción

ExoMinerAI es una herramienta de inteligencia artificial diseñada para identificar exoplanetas utilizando datos públicos de las misiones Kepler, K2 y TESS. Aprovechando técnicas avanzadas de machine learning, este proyecto busca automatizar el análisis de señales de tránsito planetario y facilitar la interacción con los datos a través de una interfaz web intuitiva.

## 🎯 Objetivo del Proyecto

- Entrenar modelos de clasificación para detectar exoplanetas, candidatos planetarios y falsos positivos.
- Evaluar el impacto de variables como período orbital, duración del tránsito y radio planetario en la predicción.
- Proporcionar una interfaz web para que investigadores y entusiastas puedan cargar nuevos datos, visualizar resultados y ajustar parámetros del modelo.

## 📊 Funcionalidades Clave

- Preprocesamiento automático de datos astronómicos.
- Modelos de clasificación con métricas de rendimiento visibles.
- Interfaz web para carga de datos, visualización y ajuste de hiperparámetros.
- Soporte para aprendizaje incremental con nuevos datos.

## 🧠 Tecnologías Utilizadas

- Python 3.12
- Scikit-learn / XGBoost / TensorFlow / PyTorch
- Pandas / NumPy / Matplotlib / Seaborn
- Flask / Streamlit / FastAPI (para la interfaz web)
- Docker (opcional para despliegue)

## 📂 Estructura del Proyecto
ExoMinerAI/
├── data/                  # Datasets originales y procesados
│   ├── raw/               # Datos sin procesar (Kepler, K2, TESS)
│   └── processed/         # Datos limpios y listos para modelar
├── notebooks/             # Exploración, visualización y prototipos
│   ├── EDA.ipynb          # Análisis exploratorio de datos
│   └── ModelTests.ipynb   # Pruebas de modelos y métricas
├── src/                   # Código fuente
│   ├── preprocessing/     # Scripts de limpieza y transformación
│   ├── models/            # Entrenamiento, evaluación y predicción
│   ├── webapp/            # Código de la interfaz web
│   └── utils/             # Funciones auxiliares (visualización, métricas)
├── tests/                 # Pruebas unitarias y de integración
├── reports/               # Resultados, gráficas, documentación técnica
├── requirements.txt       # Dependencias del proyecto
├── README.md              # Descripción del proyecto
└── .gitignore             # Archivos que no deben subirse a GitHub

## 📚 Recursos

- [A World Away: Hunting for Exoplanets with AI](https://www.spaceappschallenge.org/2025/challenges/a-world-away-hunting-for-exoplanets-with-ai/)
