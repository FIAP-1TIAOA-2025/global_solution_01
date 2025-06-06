import openmeteo_requests
import pandas as pd
import requests_cache
import matplotlib.pyplot as plt
import seaborn as sns
from retry_requests import retry
import pymongo
import sys

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": -30.03508379255499,
	"longitude": -51.19020276769795,
	"start_date": "2023-04-30",
	"end_date": "2025-04-30",
	"daily": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "precipitation_sum", "rain_sum"]
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process daily data. The order of variables needs to be the same as requested.

daily = response.Daily()
daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(4).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(5).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(6).ValuesAsNumpy()
daily_rain_sum = daily.Variables(7).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["rain_sum"] = daily_rain_sum

daily_dataframe = pd.DataFrame(data = daily_data)

# Add 'flood_event' column: 1 for 2024-04-30, 0 otherwise
# Simulate flood events based on lagged high rainfall and accumulated rainfall
daily_dataframe['flood_event'] = 0 # Initialize to no flood

# A flood might occur if precipitation_sum was high yesterday and day before
# Or if accumulated rain over 3 days is high
daily_dataframe['precipitation_sum_lag1'] = daily_dataframe['precipitation_sum'].shift(1)
daily_dataframe['precipitation_sum_lag2'] = daily_dataframe['precipitation_sum'].shift(2)
daily_dataframe['precipitation_sum_3day_sum'] = daily_dataframe['precipitation_sum'].rolling(window=3).sum().shift(1) # Sum of previous 3 days

# Define flood conditions (example logic)
# A flood event (1) if:
# - Daily precipitation was > 80mm yesterday OR
# - Accumulated 3-day precipitation was > 150mm
# - And these events are somewhat rare
daily_dataframe.loc[
    (daily_dataframe['precipitation_sum_lag1'] > 80) |
    (daily_dataframe['precipitation_sum_3day_sum'] > 150)
    , 'flood_event'
] = 1

# Ensure flood_event is int type
daily_dataframe['flood_event'] = daily_dataframe['flood_event'].astype(int)

# Drop helper columns and NaNs from shifts
daily_dataframe.drop(columns=['precipitation_sum_lag1', 'precipitation_sum_lag2', 'precipitation_sum_3day_sum'], inplace=True)
daily_dataframe.dropna(inplace=True)

print(daily_dataframe)

# DB connection
# Make sure to set the environment variable DB_URI with your MongoDB connection string
# Example: export DB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/myDatabase?retryWrites=true&w=majority"
# if "DB_URI" not in os.environ:
#   print("Please set the environment variable DB_URI with your MongoDB connection string.")
#   sys.exit(1)

local_connection_string = "mongodb://localhost:27017/"

try:
  client = pymongo.MongoClient(local_connection_string)
  
# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  sys.exit(1)

print("MongoDB connection successful. Loading data into the database...")
# Create or connect to the database
db = client["global_solution_weather_data_poc_raw"]

# Salva os dados diários na coleção "daily"
daily_records = daily_dataframe.to_dict(orient="records")
if daily_records:
    db.daily.insert_many(daily_records)
    print(f"{len(daily_records)} registros diários inseridos na coleção 'daily'.")
    print(db.daily.find_one())  # Exibe o primeiro registro inserido
    
# --- 1. Target Variable Correlation ---

print("\n--- 1. Target Variable Correlation ---")

# Step 1.1: Feature Engineering for Flood Prediction
# This is crucial for time-series data.
# We're predicting floods based on *past* conditions.
# The 'shift(-N)' is used because we want to predict a flood that occurs N days *after* the current weather conditions.
# If flood_event is the *result* of the weather, then shift(-1) means "flood on the next day".
# If flood_event is recorded on the *same day* as the weather that caused it, then no shift is needed.
# Let's assume you want to predict a flood 1, 2, or 3 days ahead.
# If your 'flood_event' in the original data is the result of the *current* day's conditions,
# then `df['flood_event']` without shifting is your target.
# If your 'flood_event' occurs *after* the conditions, you need to align it.
# For simplicity and common practice in prediction, we'll try to predict 'flood_event' based on *current* (non-shifted) features.
# If you want to predict a flood that happens *tomorrow* (1 day ahead), you'd need to shift the target like `df['flood_event'].shift(-1)`.
# For this example, let's assume `flood_event` on a given row implies conditions on that day lead to a flood or a flood is present.

# Let's create some relevant lagged features for precipitation
# These are often the most important for flood prediction
for lag in [1, 2, 3]: # Rainfall from 1, 2, and 3 days ago
    daily_dataframe[f'precipitation_sum_lag_{lag}d'] = daily_dataframe['precipitation_sum'].shift(lag)

# Accumulated rainfall over past periods
daily_dataframe['precipitation_sum_rolling_3d'] = daily_dataframe['precipitation_sum'].rolling(window=3).sum().shift(1) # sum of past 3 days, excluding current
daily_dataframe['precipitation_sum_rolling_7d'] = daily_dataframe['precipitation_sum'].rolling(window=7).sum().shift(1) # sum of past 7 days, excluding current

# Drop NaNs created by shifting and rolling
df_correlated = daily_dataframe.dropna().copy()

# Select features for correlation with the target
# Exclude original 'rain_sum' as it's redundant with 'precipitation_sum'
features_for_correlation = [
    'temperature_2m_mean',
    'wind_direction_10m_dominant',
    'precipitation_sum', # Current day's rainfall
    'precipitation_sum_lag_1d',
    'precipitation_sum_lag_2d',
    'precipitation_sum_lag_3d',
    'precipitation_sum_rolling_3d',
    'precipitation_sum_rolling_7d',
    # Add other relevant features like river levels, tide data, if available
]

# Calculate correlations with the target variable 'flood_event'
# The target `flood_event` should be binary (0 or 1) for this to be meaningful.
correlations_with_target = df_correlated[features_for_correlation].corrwith(df_correlated['flood_event'])

print("\nCorrelação das variáveis com 'flood_event' (Target):")
print(correlations_with_target.sort_values(ascending=False))

# Interpretation:
# - Features with high absolute correlation values (closer to 1 or -1) are potentially strong predictors.
# - Positive correlations mean higher values of the feature are associated with a higher likelihood of flood.
# - Negative correlations mean higher values of the feature are associated with a lower likelihood of flood.
# - For flood prediction, often rainfall (current and lagged/accumulated) will show the strongest positive correlation.
# - Note: This is linear correlation. Your model might pick up non-linear relationships.

# --- 2. Visualization ---
df = daily_dataframe

print("\n--- 2. Visualization ---")

# 2.1. Heatmap da Matriz de Correlação Completa
# Include the target variable in the correlation matrix for a comprehensive view
full_correlation_matrix = df_correlated[features_for_correlation + ['flood_event']].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(full_correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Matriz de Correlação Completa (incluindo flood_event)')
plt.show()

# Interpretation:
# - This heatmap visually reinforces the high correlations (e.g., between lagged precipitation features).
# - It clearly shows the strength and direction of correlation with 'flood_event'.

# 2.2. Time Series Plot of Key Variables vs. Flood Events
# This is crucial for understanding the temporal dynamics of floods.
plt.figure(figsize=(15, 8))

# Plot rainfall and accumulated rainfall
plt.plot(df.index, df['precipitation_sum'], label='Precipitação Diária (mm)', color='skyblue', alpha=0.7)
plt.plot(df.index, df['precipitation_sum_rolling_3d'], label='Precipitação Acumulada 3D (mm)', color='blue', alpha=0.8)

# Mark flood events
# We need to filter df_correlated for the flood events that actually happened
flood_events_dates = df_correlated[df_correlated['flood_event'] == 1].index
plt.scatter(flood_events_dates, df_correlated.loc[flood_events_dates, 'precipitation_sum'],
            color='red', marker='o', s=50, label='Evento de Inundação', zorder=5)


plt.title('Precipitação e Eventos de Inundação ao Longo do Tempo')
plt.xlabel('Data')
plt.ylabel('Precipitação (mm)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Interpretation:
# - Visually confirm if peaks in precipitation align with flood events.
# - Observe if sustained periods of moderate rain (seen in rolling sums) also lead to floods.
# - This helps validate your flood event definition and the impact of lagged features.

# 2.3. Distribution Plots (e.g., Rainfall distribution for flood vs. non-flood days)
# This is particularly insightful for classification problems.
plt.figure(figsize=(12, 6))
sns.boxplot(x='flood_event', y='precipitation_sum_rolling_3d', data=df_correlated)
plt.title('Precipitação Acumulada em 3 Dias para Dias Sem e Com Inundação')
plt.xlabel('Evento de Inundação (0: Não, 1: Sim)')
plt.ylabel('Precipitação Acumulada em 3 Dias (mm)')
plt.grid(axis='y')
plt.show()

# Interpretation:
# - Look for clear separation in distributions. If precipitation_sum_rolling_3d is significantly higher on flood days, it's a good predictor.
# - This helps identify thresholds that might be useful for rules-based alerts or feature engineering.

# --- 3. Domain Knowledge Integration ---

print("\n--- 3. Domain Knowledge Integration ---")

# Based on knowledge of Salvador and flood dynamics:

# 3.1. Identify and Source Additional Critical Data:
print("\n3.1. Sourcing Additional Critical Data (Conceptual - needs actual data sources):")
print("- Dados de Nível de Rios/Canais: Fundamentais para rios que cortam Salvador e podem transbordar.")
print("  - Ex: Nível do Rio Joanes, Canal da Saramandaia.")
print("- Dados de Maré: Absolutamente crucial para uma cidade costeira como Salvador.")
print("  - A combinação de chuva forte e maré alta agrava o risco de inundação.")
print("- Dados Topográficos e de Uso do Solo (Geospatial):")
print("  - Elevação (DEM): Áreas de baixa elevação são mais propensas.")
print("  - Inclinação do Terreno: Afeta o escoamento superficial.")
print("  - Impermeabilização do Solo: Áreas urbanizadas (concreto, asfalto) aumentam o escoamento.")
print("  - Capacidade da Rede de Drenagem: Dados sobre bueiros, galerias pluviais (se disponíveis).")
print("- Dados de Eventos de Inundação Históricos Detalhados:")
print("  - Localização precisa, gravidade, duração. Essencial para rotular seu target de forma mais granular (ex: inundação leve, moderada, severa).")

# 3.2. Advanced Feature Engineering based on Domain Knowledge:

print("\n3.2. Advanced Feature Engineering (Implementation Examples):")

# Example: Interaction Feature (Rainfall and Tide)
# If you had 'tide_level_m' data:
# df['rainfall_x_tide'] = df['precipitation_sum'] * df['tide_level_m']
# This feature captures the amplified risk when both are high.
# print("Adding interaction feature: 'rainfall_x_tide' (if tide data available)")

# Example: Threshold-based features for accumulated rainfall (e.g., for early warning)
# If 24-hour rainfall exceeds a certain threshold, it's a strong indicator.
threshold_24h_heavy_rain = 80 # Example threshold in mm for 24h
threshold_72h_extreme_rain = 200 # Example threshold in mm for 72h

df['is_heavy_rain_24h'] = (df['precipitation_sum_lag_1d'] > threshold_24h_heavy_rain).astype(int)
df['is_extreme_rain_72h'] = (df['precipitation_sum_rolling_7d'] > threshold_72h_extreme_rain).astype(int)

print(f"Added binary feature 'is_heavy_rain_24h' (if > {threshold_24h_heavy_rain}mm lagged rain)")
print(f"Added binary feature 'is_extreme_rain_72h' (if > {threshold_72h_extreme_rain}mm 7-day rolling rain)")

# Example: Incorporating a 'dry spell' feature (relevant for soil saturation)
# A long dry spell followed by sudden heavy rain can be dangerous
# This requires more complex logic, e.g., counting consecutive days below a rain threshold
# df['days_since_last_rain'] = ...

print("\n3.3. Adapting Model Evaluation and Thresholds:")
print("- Foco no Recall (Sensibilidade): Para previsão de inundações, é crucial minimizar Falsos Negativos (dizer que não haverá inundação quando haverá). O recall é a métrica mais importante.")
print("- Matriz de Confusão: Analise cuidadosamente a matriz de confusão para entender os tipos de erros (Falsos Positivos vs. Falsos Negativos).")
print("- Ajuste de Limiar de Classificação: Você pode ajustar o limiar de probabilidade do seu modelo (ex: se a probabilidade > 0.3, preveja enchente) para balancear Recall e Precisão com base no custo de Falsos Positivos vs. Falsos Negativos.")

print("\n3.4. Continuous Monitoring and Retraining:")
print("- Os padrões climáticos e urbanos mudam. Seu modelo precisará ser re-treinado periodicamente com novos dados para manter a precisão.")
print("- Monitorar a performance do modelo em tempo real é crucial para identificar degradação.")

print("\nDomain Knowledge Integration Summary:")
print("A integração do conhecimento de domínio é um processo contínuo que enriquece o dataset, melhora a relevância das features e informa as escolhas do modelo e estratégias de avaliação. É a ponte entre os dados brutos e um modelo de IA verdadeiramente útil para prever inundações em Salvador.")