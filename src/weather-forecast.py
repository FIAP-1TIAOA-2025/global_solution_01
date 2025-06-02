import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"daily": ["temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "sunrise", "sunset", "uv_index_max", "rain_sum", "precipitation_sum", "precipitation_hours", "precipitation_probability_max"],
	"forecast_days": 3
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
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(2).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(3).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(4).ValuesAsNumpy()
daily_sunrise = daily.Variables(5).ValuesInt64AsNumpy()
daily_sunset = daily.Variables(6).ValuesInt64AsNumpy()
daily_uv_index_max = daily.Variables(7).ValuesAsNumpy()
daily_rain_sum = daily.Variables(8).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(9).ValuesAsNumpy()
daily_precipitation_hours = daily.Variables(10).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(11).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
daily_data["sunrise"] = daily_sunrise
daily_data["sunset"] = daily_sunset
daily_data["uv_index_max"] = daily_uv_index_max
daily_data["rain_sum"] = daily_rain_sum
daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["precipitation_hours"] = daily_precipitation_hours
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)
