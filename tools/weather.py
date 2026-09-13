import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

from location_extractor import get_location_coordinates

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

def get_weather_forecast(location: str, days: int) -> dict:
    """
    This function returns the weather forecast of a location only for 16 days ahead. It cannot give the weather forecast data for 17th and further days.
    """

    location_coordinates = get_location_coordinates(location=location)
    latitude = location_coordinates['latitude']
    longitude = location_coordinates['longitude']

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": float(location_coordinates["latitude"]),
        "longitude": float(location_coordinates["longitude"]),
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum", "rain_sum", "precipitation_probability_max", "sunshine_duration", "wind_speed_10m_max", "sunrise", "sunset"],
        "forecast_days": days,
        "timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params = params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(5).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(6).ValuesAsNumpy()
    daily_precipitation_probability_max = daily.Variables(7).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(9).ValuesAsNumpy()
    daily_sunrise = daily.Variables(10).ValuesInt64AsNumpy()
    daily_sunset = daily.Variables(11).ValuesInt64AsNumpy()


    daily_forecast_data = []

    start_date = pd.to_datetime(
        daily.Time(),
        unit="s",
        utc=True
    )

    for i in range(days):
        current_date = start_date + pd.Timedelta(days=i)
        daily_forecast_data.append(
            {
                "date": current_date.strftime("%Y-%m-%d"),
                "weather_code": int(daily_weather_code[i]),
                "temperature_max": round(float(daily_temperature_2m_max[i]), 2),
                "temperature_min": round(float(daily_temperature_2m_min[i]), 2),
                "apparent_temperature_max": round(float(daily_apparent_temperature_max[i]), 2),
                "apparent_temperature_min": round(float(daily_apparent_temperature_min[i]), 2),
                "precipitation_sum_mm": round(float(daily_precipitation_sum[i]), 2),
                "rain_sum_mm": round(float(daily_rain_sum[i]), 2),
                "precipitation_probability": round(float(daily_precipitation_probability_max[i]), 2),
                "sunshine_duration_hours": round(float(daily_sunshine_duration[i] / 3600), 2),
                "wind_speed_max_kmh": round(float(daily_wind_speed_10m_max[i]), 2),
                "sunrise": pd.to_datetime(
                    daily_sunrise[i],
                    unit="s",
                ).isoformat(),
                "sunset": pd.to_datetime(
                    daily_sunset[i],
                    unit="s",
                ).isoformat()
            }
        )


    return {
        "location": location,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "daily_forecast": daily_forecast_data
    }



print(get_weather_forecast("new delhi", 10))
