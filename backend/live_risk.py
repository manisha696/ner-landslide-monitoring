import requests
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# GET LIVE + RECENT WEATHER
# ============================================================

def get_weather_features(lat, lon):

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=30)

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,

        # Current weather
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),

        # Last 30 days
        "past_days": 30,

        # Hourly rainfall
        "hourly": "rain",

        "timezone": "auto",

        # Units matching our ML dataset
        "temperature_unit": "celsius",
        "wind_speed_unit": "ms",
        "precipitation_unit": "mm"
    }

    print("\nConnecting to live weather API...")

    response = requests.get(url, params=params, timeout=30)

    if response.status_code != 200:
        raise Exception(
            f"Weather API error: {response.status_code}\n"
            f"{response.text}"
        )

    data = response.json()

    # --------------------------------------------------------
    # CURRENT CONDITIONS
    # --------------------------------------------------------

    current = data["current"]

    temperature = float(current["temperature_2m"])
    humidity = float(current["relative_humidity_2m"])
    wind_speed = float(current["wind_speed_10m"])

    # --------------------------------------------------------
    # HOURLY RAIN
    # --------------------------------------------------------

    hourly_time = data["hourly"]["time"]
    hourly_rain = data["hourly"]["rain"]

    weather_df = pd.DataFrame({
        "time": pd.to_datetime(hourly_time),
        "rain": hourly_rain
    })

    weather_df["date"] = weather_df["time"].dt.date

    daily_rain = (
        weather_df
        .groupby("date")["rain"]
        .sum()
        .reset_index()
    )

    # Last available date
    latest_date = daily_rain["date"].max()

    # --------------------------------------------------------
    # RAINFALL WINDOWS
    # --------------------------------------------------------

    def rainfall_last_days(days):

        cutoff = latest_date - timedelta(days=days - 1)

        values = daily_rain[
            daily_rain["date"] >= cutoff
        ]["rain"]

        return float(values.sum())

    rain_1d = rainfall_last_days(1)
    rain_3d = rainfall_last_days(3)
    rain_7d = rainfall_last_days(7)
    rain_14d = rainfall_last_days(14)
    rain_30d = rainfall_last_days(30)

    # --------------------------------------------------------
    # DERIVED RAINFALL FEATURES
    # --------------------------------------------------------

    max_rain_30d = float(
        daily_rain["rain"].tail(30).max()
    )

    avg_rain_7d = rain_7d / 7

    avg_rain_30d = rain_30d / 30

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    features = {
        "rain_1d_mm": rain_1d,
        "rain_3d_mm": rain_3d,
        "rain_7d_mm": rain_7d,
        "rain_14d_mm": rain_14d,
        "rain_30d_mm": rain_30d,

        "max_rain_30d_mm": max_rain_30d,

        "avg_rain_7d_mm": avg_rain_7d,
        "avg_rain_30d_mm": avg_rain_30d,

        "temperature_C": temperature,
        "humidity_percent": humidity,
        "wind_speed_mps": wind_speed
    }

    return features


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Example location in Northeast India
    lat = 25.5007
    lon = 93.9854

    features = get_weather_features(lat, lon)

    print("\n========================================")
    print("LIVE WEATHER FEATURES")
    print("========================================")

    for key, value in features.items():
        print(f"{key:25s}: {value:.3f}")

    print("========================================")