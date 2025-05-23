import streamlit as st
import pickle
import pandas as pd
import numpy as np

# Cargar los modelos, el escalador y las columnas de entrenamiento
with open('kmeans_model.pkl', 'rb') as kmeans_file:
    kmeans_model = pickle.load(kmeans_file)

with open('logistic_model.pkl', 'rb') as logistic_file:
    logistic_model = pickle.load(logistic_file)

with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

with open('features.pkl', 'rb') as features_file:
    expected_features = pickle.load(features_file)

# Título de la aplicación
st.title('Predicción del grupo y probabilidad de adquirir depósitos')

# Entrada de datos del usuario
month_encoded = st.selectbox('Momento del contacto de campaña (mes)', options=list(range(1, 13)))
age = st.number_input('Edad (años)', min_value=0)
balance = st.number_input('Balance (euros)', min_value=-5000.0, max_value=100000.0, step=100.0)
campaign = st.number_input('Número de campañas de contacto', min_value=0)

# Crear un DataFrame con las entradas
user_data = pd.DataFrame({
    'month': [month_encoded],
    'age': [age],
    'balance': [balance],
    'campaign': [campaign]
})

# Estandarizar las entradas (excepto 'month')
user_data_to_scale = user_data.drop(columns=['month'])  # Excluir 'month' de la estandarización
user_data_standardized = scaler.transform(user_data_to_scale)

# Combinar 'month' con los datos estandarizados
user_data_combined = pd.DataFrame(user_data_standardized, columns=user_data_to_scale.columns)
user_data_combined['month'] = user_data['month'].values  # Añadir de nuevo la columna 'month'

# Añadir las características faltantes y reordenar
for col in expected_features:
    if col not in user_data_combined:
        user_data_combined[col] = 0  # Características ausentes se llenan con 0

user_data_combined = user_data_combined[expected_features]  # Reordenar las columnas

# Predicción del clúster con K-means
user_data_kmeans = user_data_combined[['age', 'balance']]  # Cambia según las columnas utilizadas en KMeans
try:
    cluster_prediction = kmeans_model.predict(user_data_kmeans)[0]
except Exception as e:
    st.error(f"Error en predicción del clúster: {e}")

# Predicción de la probabilidad con el modelo de regresión logística
try:
    probability_prediction = logistic_model.predict_proba(user_data_combined)[0][1]
    st.write(f"El usuario pertenece al clúster: **{cluster_prediction}**")
    st.write(f"Probabilidad de adquirir un depósito: **{probability_prediction:.2f}**")
except Exception as e:
    st.error(f"Error en predicción de probabilidad: {e}")
