import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

from tools.location_extractor import get_location_coordinates

from langchain_core.tools import tool

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

openmeteo = openmeteo_requests.Client(session=retry_session)

@tool
def get_historical_weather(location: str, start_date: str, end_date: str, years: int = 5) -> dict:
    """
    This function returns the weather forecast of a location for more than 16 days ahead. This function fetches the historical weather data of past 5 years for the specific dates mentioned of that particular location and returns the average of it.
    """

    location_coordinates = get_location_coordinates(location=location)

    latitude = float(location_coordinates["latitude"])
    longitude = float(location_coordinates["longitude"])

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    url = "https://archive-api.open-meteo.com/v1/archive"

    historical_data = {}

    for year in range(start.year - years, start.year):

        historical_start = start.replace(year=year)
        historical_end = end.replace(year=year)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": historical_start.strftime("%Y-%m-%d"),
            "end_date": historical_end.strftime("%Y-%m-%d"),
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "precipitation_sum", "rain_sum", "sunshine_duration", "wind_speed_10m_max", "precipitation_hours"],
            "timezone": "auto"
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()

        daily_weather_code = (daily.Variables(0).ValuesAsNumpy())
        daily_temperature_2m_max = (daily.Variables(1).ValuesAsNumpy())
        daily_temperature_2m_min = (daily.Variables(2).ValuesAsNumpy())
        daily_apparent_temperature_max = (daily.Variables(3).ValuesAsNumpy())
        daily_apparent_temperature_min = (daily.Variables(4).ValuesAsNumpy())
        daily_sunrise = (daily.Variables(5).ValuesInt64AsNumpy())
        daily_sunset = (daily.Variables(6).ValuesInt64AsNumpy())
        daily_precipitation_sum = (daily.Variables(7).ValuesAsNumpy())
        daily_rain_sum = (daily.Variables(8).ValuesAsNumpy())
        daily_sunshine_duration = (daily.Variables(9).ValuesAsNumpy())
        daily_wind_speed_10m_max = (daily.Variables(10).ValuesAsNumpy())
        daily_precipitation_hours = (daily.Variables(11).ValuesAsNumpy())
        timezone = response.Timezone().decode()

        dates = pd.date_range(
            start=pd.to_datetime(
                daily.Time(),
                unit="s",
                utc=True
            ),
            end=pd.to_datetime(
                daily.TimeEnd(),
                unit="s",
                utc=True
            ),
            freq=pd.Timedelta(
                seconds=daily.Interval()
            ),
            inclusive="left"
        ).tz_convert(timezone)

        year_data = []

        for i in range(len(dates)):
            year_data.append(
                {
                    "date": dates[i].strftime("%Y-%m-%d"),

                    "weather_code": int(daily_weather_code[i]),
                    "temperature_max": round(float(daily_temperature_2m_max[i]), 2),
                    "temperature_min": round(float(daily_temperature_2m_min[i]), 2),
                    "apparent_temperature_max": round(float(daily_apparent_temperature_max[i]),2),
                    "apparent_temperature_min": round(float(daily_apparent_temperature_min[i]),2),
                    "precipitation_sum_mm": round(float(daily_precipitation_sum[i]),2),
                    "rain_sum_mm": round(float(daily_rain_sum[i]),2),
                    "sunshine_duration_hours": round(float(daily_sunshine_duration[i] / 3600),2),
                    "wind_speed_max_kmh": round(float(daily_wind_speed_10m_max[i]), 2),
                    "precipitation_hours": round(float(daily_precipitation_hours[i]), 2),
                    "sunrise": pd.to_datetime(
                        daily_sunrise[i],
                        unit="s",
                        utc=True
                    ).tz_convert(timezone).isoformat(),

                    "sunset": pd.to_datetime(
                        daily_sunset[i],
                        unit="s",
                        utc=True
                    ).tz_convert(timezone).isoformat()
                }
            )

        historical_data[str(year)] = year_data


    all_days = []
    for year_data in historical_data.values():
        all_days.extend(year_data)

    average_data = {
        "temperature_max": round(sum(day["temperature_max"] for day in all_days) / len(all_days), 2),
        "temperature_min": round(sum(day["temperature_min"] for day in all_days) / len(all_days), 2),
        "apparent_temperature_max": round(sum(day["apparent_temperature_max"] for day in all_days) / len(all_days), 2),
        "apparent_temperature_min": round(sum(day["apparent_temperature_min"] for day in all_days) / len(all_days), 2),
        "precipitation_sum_mm": round(sum(day["precipitation_sum_mm"] for day in all_days) / len(all_days),2),
        "rain_sum_mm": round(sum(day["rain_sum_mm"] for day in all_days) / len(all_days),2),
        "sunshine_duration_hours": round(sum(day["sunshine_duration_hours"] for day in all_days) / len(all_days),2),
        "wind_speed_max_kmh": round(sum(day["wind_speed_max_kmh"] for day in all_days) / len(all_days),2),
        "precipitation_hours": round(sum(day["precipitation_hours"] for day in all_days) / len(all_days),2)
    }

    weather_codes = [day["weather_code"] for day in all_days]
    average_data["most_common_weather_code"] = max(set(weather_codes), key=weather_codes.count)

    sunrise_seconds = [
        pd.to_datetime(day["sunrise"]).hour * 3600
        + pd.to_datetime(day["sunrise"]).minute * 60
        + pd.to_datetime(day["sunrise"]).second
        for day in all_days
    ]

    sunset_seconds = [
        pd.to_datetime(day["sunset"]).hour * 3600
        + pd.to_datetime(day["sunset"]).minute * 60
        + pd.to_datetime(day["sunset"]).second
        for day in all_days
    ]

    average_sunrise = sum(sunrise_seconds) / len(sunrise_seconds)
    average_sunset = sum(sunset_seconds) / len(sunset_seconds)


    average_data["average_sunrise"] = (
        pd.Timestamp("2000-01-01")
        + pd.Timedelta(seconds=average_sunrise)
    ).strftime("%H:%M:%S")

    average_data["average_sunset"] = (
        pd.Timestamp("2000-01-01")
        + pd.Timedelta(seconds=average_sunset)
    ).strftime("%H:%M:%S")

    return {
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "trip_start_date": start_date,
        "trip_end_date": end_date,
        "historical_years_used": years,
        "average_weather": average_data
    }