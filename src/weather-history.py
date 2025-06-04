import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import pymongo
import sys
import os

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
print(daily_dataframe)

# DB connection
# Make sure to set the environment variable DB_URI with your MongoDB connection string
# Example: export DB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/myDatabase?retryWrites=true&w=majority"
# if "DB_URI" not in os.environ:
#   print("Please set the environment variable DB_URI with your MongoDB connection string.")
#   sys.exit(1)

try:
  client = pymongo.MongoClient("mongodb+srv://rm564246:JukZNw2FKA0ErgCn@cluster0.y85rsvt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
  
# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  sys.exit(1)

print("MongoDB connection successful. Loading data into the database...")
# Cria uma nova database chamada "weather_data"
db = client["global_solution_weather_data_raw"]

# Salva os dados diários na coleção "daily"
daily_records = daily_dataframe.to_dict(orient="records")
if daily_records:
    db.daily.insert_many(daily_records)
    print(f"{len(daily_records)} registros diários inseridos na coleção 'daily'.")