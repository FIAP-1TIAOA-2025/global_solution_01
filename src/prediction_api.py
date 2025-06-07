import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import joblib
import datetime
import numpy as np

# Carrega o modelo treinado e o scaler
MODEL_PATH = "./models/trained_models/flood_prediction_model_v1.pkl"
SCALER_PATH = "./models/trained_models/StandardScaler_v1.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

def get_today_weather_data():
    # Configura o cliente da API Open-Meteo
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Define as datas para hoje
    today = datetime.date.today()
    params = {
        "latitude": -30.03508379255499,
        "longitude": -51.19020276769795,
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date": today.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
            "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
            "precipitation_sum", "rain_sum"
        ]
    }
    url = "https://archive-api.open-meteo.com/v1/archive"
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()

    # Extrai os dados diários
    data = {
        "temperature_2m_mean": daily.Variables(0).ValuesAsNumpy()[0],
        "temperature_2m_max": daily.Variables(1).ValuesAsNumpy()[0],
        "temperature_2m_min": daily.Variables(2).ValuesAsNumpy()[0],
        "wind_speed_10m_max": daily.Variables(3).ValuesAsNumpy()[0],
        "wind_gusts_10m_max": daily.Variables(4).ValuesAsNumpy()[0],
        "wind_direction_10m_dominant": daily.Variables(5).ValuesAsNumpy()[0],
        "precipitation_sum": daily.Variables(6).ValuesAsNumpy()[0],
        "rain_sum": daily.Variables(7).ValuesAsNumpy()[0],
    }
    return pd.DataFrame([data])

def predict_flood():
    # Obtém os dados do dia
    df_today = get_today_weather_data()
    
    # Garante que todos os recursos esperados estejam presentes
    expected_features = scaler.feature_names_in_
    for col in expected_features:
        if col not in df_today.columns:
            df_today[col] = 0  # ou outro valor padrão apropriado
    df_today = df_today[expected_features]
    
    # Aplica o scaler
    X_scaled = scaler.transform(df_today)
    # Faz a previsão
    prediction = model.predict(X_scaled)
    probability = model.predict_proba(X_scaled)[0][1] if hasattr(model, "predict_proba") else None

    if prediction[0] == 1:
        print("ALERTA: Possível enchente detectada para hoje!")
    else:
        print("Sem risco de enchente detectado para hoje.")

    if probability is not None:
        print(f"Probabilidade prevista de enchente: {probability:.2%}")
        
    return prediction[0], probability

if __name__ == "__main__":
    predict_flood()