import requests
import pandas as pd
from datetime import datetime, timedelta
import time


# ============================================================
# WEATHER CACHE
# ============================================================

WEATHER_CACHE = {}
CACHE_DURATION_SECONDS = 600


def get_cache_key(lat, lon):
    return (
        round(float(lat), 3),
        round(float(lon), 3)
    )


def get_cached_weather(lat, lon):

    key = get_cache_key(lat, lon)

    if key not in WEATHER_CACHE:
        return None

    cached_time, cached_data = WEATHER_CACHE[key]

    if time.time() - cached_time < CACHE_DURATION_SECONDS:

        print("Using cached weather data.")

        return cached_data

    del WEATHER_CACHE[key]

    return None


def save_cached_weather(lat, lon, data):

    key = get_cache_key(lat, lon)

    WEATHER_CACHE[key] = (
        time.time(),
        data
    )


# ============================================================
# OPEN-METEO
# ============================================================

def get_open_meteo_weather(lat, lon):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": lat,

        "longitude": lon,

        "current":
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m",

        "past_days": 30,

        "hourly":
            "rain",

        "timezone":
            "auto",

        "temperature_unit":
            "celsius",

        "wind_speed_unit":
            "ms",

        "precipitation_unit":
            "mm"
    }

    print("")
    print("Trying Open-Meteo...")

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    if response.status_code != 200:

        raise Exception(
            f"Open-Meteo error: "
            f"{response.status_code}"
        )

    data = response.json()

    current = data["current"]

    temperature = float(
        current["temperature_2m"]
    )

    humidity = float(
        current["relative_humidity_2m"]
    )

    wind_speed = float(
        current["wind_speed_10m"]
    )

    hourly_time = data["hourly"]["time"]

    hourly_rain = data["hourly"]["rain"]

    weather_df = pd.DataFrame({

        "time":
            pd.to_datetime(
                hourly_time
            ),

        "rain":
            [
                0 if value is None
                else float(value)

                for value in hourly_rain
            ]
    })

    weather_df["date"] = (
        weather_df["time"].dt.date
    )

    daily_rain = (
        weather_df
        .groupby("date")["rain"]
        .sum()
        .reset_index()
    )

    latest_date = daily_rain["date"].max()

    def rainfall_last_days(days):

        cutoff = (
            latest_date
            -
            timedelta(
                days=days - 1
            )
        )

        values = daily_rain[
            daily_rain["date"] >= cutoff
        ]["rain"]

        return float(
            values.sum()
        )

    rain_1d = rainfall_last_days(1)

    rain_3d = rainfall_last_days(3)

    rain_7d = rainfall_last_days(7)

    rain_14d = rainfall_last_days(14)

    rain_30d = rainfall_last_days(30)

    max_rain_30d = float(
        daily_rain["rain"]
        .tail(30)
        .max()
    )

    avg_rain_7d = (
        rain_7d / 7
    )

    avg_rain_30d = (
        rain_30d / 30
    )

    features = {

        "rain_1d_mm":
            rain_1d,

        "rain_3d_mm":
            rain_3d,

        "rain_7d_mm":
            rain_7d,

        "rain_14d_mm":
            rain_14d,

        "rain_30d_mm":
            rain_30d,

        "max_rain_30d_mm":
            max_rain_30d,

        "avg_rain_7d_mm":
            avg_rain_7d,

        "avg_rain_30d_mm":
            avg_rain_30d,

        "temperature_C":
            temperature,

        "humidity_percent":
            humidity,

        "wind_speed_mps":
            wind_speed,

        "weather_source":
            "Open-Meteo"
    }

    return features


# ============================================================
# NASA POWER FALLBACK
# ============================================================

def get_nasa_power_weather(lat, lon):

    print("")
    print("Open-Meteo unavailable.")

    print(
        "Trying NASA POWER fallback..."
    )

    end_date = datetime.utcnow().date()

    start_date = (
        end_date
        -
        timedelta(days=30)
    )

    start_string = (
        start_date.strftime("%Y%m%d")
    )

    end_string = (
        end_date.strftime("%Y%m%d")
    )

    url = (
        "https://power.larc.nasa.gov/api/"
        "temporal/daily/point"
    )

    params = {

        "parameters":
            "PRECTOTCORR,"
            "T2M,"
            "RH2M,"
            "WS2M",

        "community":
            "AG",

        "longitude":
            lon,

        "latitude":
            lat,

        "start":
            start_string,

        "end":
            end_string,

        "format":
            "JSON"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    if response.status_code != 200:

        raise Exception(
            f"NASA POWER error: "
            f"{response.status_code}"
        )

    data = response.json()

    parameter_data = (
        data["properties"]["parameter"]
    )

    precipitation = (
        parameter_data["PRECTOTCORR"]
    )

    temperature_data = (
        parameter_data["T2M"]
    )

    humidity_data = (
        parameter_data["RH2M"]
    )

    wind_data = (
        parameter_data["WS2M"]
    )

    rows = []

    for date_string in precipitation.keys():

        rain = precipitation.get(
            date_string,
            0
        )

        temp = temperature_data.get(
            date_string,
            None
        )

        humidity = humidity_data.get(
            date_string,
            None
        )

        wind = wind_data.get(
            date_string,
            None
        )

        if rain is None or rain < -900:

            rain = 0

        if temp is None or temp < -900:

            temp = 0

        if humidity is None or humidity < -900:

            humidity = 0

        if wind is None or wind < -900:

            wind = 0

        rows.append({

            "date":
                datetime.strptime(
                    date_string,
                    "%Y%m%d"
                ).date(),

            "rain":
                float(rain),

            "temperature":
                float(temp),

            "humidity":
                float(humidity),

            "wind":
                float(wind)
        })

    weather_df = pd.DataFrame(rows)

    weather_df = (
        weather_df
        .sort_values("date")
    )

    def rainfall_last_days(days):

        values = (
            weather_df
            .tail(days)["rain"]
        )

        return float(
            values.sum()
        )

    rain_1d = rainfall_last_days(1)

    rain_3d = rainfall_last_days(3)

    rain_7d = rainfall_last_days(7)

    rain_14d = rainfall_last_days(14)

    rain_30d = rainfall_last_days(30)

    max_rain_30d = float(
        weather_df["rain"]
        .tail(30)
        .max()
    )

    avg_rain_7d = (
        rain_7d / 7
    )

    avg_rain_30d = (
        rain_30d / 30
    )

    latest = weather_df.iloc[-1]

    temperature = float(
        latest["temperature"]
    )

    humidity = float(
        latest["humidity"]
    )

    wind_speed = float(
        latest["wind"]
    )

    features = {

        "rain_1d_mm":
            rain_1d,

        "rain_3d_mm":
            rain_3d,

        "rain_7d_mm":
            rain_7d,

        "rain_14d_mm":
            rain_14d,

        "rain_30d_mm":
            rain_30d,

        "max_rain_30d_mm":
            max_rain_30d,

        "avg_rain_7d_mm":
            avg_rain_7d,

        "avg_rain_30d_mm":
            avg_rain_30d,

        "temperature_C":
            temperature,

        "humidity_percent":
            humidity,

        "wind_speed_mps":
            wind_speed,

        "weather_source":
            "NASA POWER"
    }

    print(
        "NASA POWER fallback successful."
    )

    return features


# ============================================================
# MAIN WEATHER FUNCTION
# ============================================================

def get_weather_features(lat, lon):

    cached = get_cached_weather(
        lat,
        lon
    )

    if cached is not None:

        return cached

    # --------------------------------------------------------
    # TRY OPEN-METEO
    # --------------------------------------------------------

    try:

        features = (
            get_open_meteo_weather(
                lat,
                lon
            )
        )

        print(
            "Open-Meteo weather successful."
        )

        save_cached_weather(
            lat,
            lon,
            features
        )

        return features

    except Exception as open_meteo_error:

        print(
            f"Open-Meteo failed: "
            f"{open_meteo_error}"
        )

    # --------------------------------------------------------
    # FALLBACK TO NASA POWER
    # --------------------------------------------------------

    try:

        features = (
            get_nasa_power_weather(
                lat,
                lon
            )
        )

        save_cached_weather(
            lat,
            lon,
            features
        )

        return features

    except Exception as nasa_error:

        print(
            f"NASA POWER failed: "
            f"{nasa_error}"
        )

        raise Exception(
            "Both weather services are "
            "currently unavailable."
        )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    lat = 25.5007

    lon = 93.9854

    try:

        features = (
            get_weather_features(
                lat,
                lon
            )
        )

        print("")
        print(
            "========================================"
        )

        print(
            "WEATHER FEATURES"
        )

        print(
            "========================================"
        )

        for key, value in features.items():

            if isinstance(
                value,
                (int, float)
            ):

                print(
                    f"{key:25s}: "
                    f"{value:.3f}"
                )

            else:

                print(
                    f"{key:25s}: "
                    f"{value}"
                )

        print(
            "========================================"
        )

    except Exception as error:

        print("")
        print(
            "Weather system failed:"
        )

        print(error)