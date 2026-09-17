import requests
import time
from datetime import datetime, timedelta

# ============================================================
# WEATHER CACHE
# ============================================================

_weather_cache = {}

CACHE_SECONDS = 600  # 10 minutes


# ============================================================
# OPEN-METEO WEATHER
# ============================================================

def get_open_meteo_weather(lat, lon):

    print("Trying Open-Meteo...")

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "precipitation_sum",
            "temperature_2m_max",
            "relative_humidity_2m_mean",
            "wind_speed_10m_max"
        ]),
        "timezone": "UTC",
        "past_days": 30,
        "forecast_days": 1
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    if response.status_code != 200:
        raise Exception(
            f"Open-Meteo error: {response.status_code}"
        )

    data = response.json()

    daily = data.get("daily")

    if not daily:
        raise Exception("Open-Meteo daily data missing")

    rain = daily.get("precipitation_sum", [])

    temperature = daily.get(
        "temperature_2m_max",
        []
    )

    humidity = daily.get(
        "relative_humidity_2m_mean",
        []
    )

    wind = daily.get(
        "wind_speed_10m_max",
        []
    )

    # Remove None values
    rain_values = [
        float(x) for x in rain
        if x is not None
    ]

    if not rain_values:
        raise Exception("Rainfall data missing")

    def safe_last(values, default=0.0):
        valid = [
            float(x)
            for x in values
            if x is not None
        ]

        if not valid:
            return default

        return valid[-1]

    rain_1d = sum(rain_values[-1:])
    rain_3d = sum(rain_values[-3:])
    rain_7d = sum(rain_values[-7:])
    rain_14d = sum(rain_values[-14:])
    rain_30d = sum(rain_values[-30:])

    last_30 = rain_values[-30:]

    max_rain_30d = (
        max(last_30)
        if last_30
        else 0.0
    )

    last_7 = rain_values[-7:]

    avg_rain_7d = (
        sum(last_7) / len(last_7)
        if last_7
        else 0.0
    )

    avg_rain_30d = (
        sum(last_30) / len(last_30)
        if last_30
        else 0.0
    )

    return {
        "rain_1d_mm": float(rain_1d),
        "rain_3d_mm": float(rain_3d),
        "rain_7d_mm": float(rain_7d),
        "rain_14d_mm": float(rain_14d),
        "rain_30d_mm": float(rain_30d),

        "max_rain_30d_mm": float(max_rain_30d),

        "avg_rain_7d_mm": float(avg_rain_7d),
        "avg_rain_30d_mm": float(avg_rain_30d),

        "temperature_C": safe_last(
            temperature,
            0.0
        ),

        "humidity_percent": safe_last(
            humidity,
            0.0
        ),

        "wind_speed_mps": safe_last(
            wind,
            0.0
        ),

        "weather_source": "Open-Meteo"
    }


# ============================================================
# NASA POWER FALLBACK
# ============================================================

def get_nasa_power_weather(lat, lon):

    print("Trying NASA POWER fallback...")

    end_date = datetime.utcnow().date()

    start_date = end_date - timedelta(days=30)

    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")

    url = (
        "https://power.larc.nasa.gov/api/temporal/"
        "daily/point"
    )

    params = {
        "parameters": ",".join([
            "PRECTOTCORR",
            "T2M",
            "RH2M",
            "WS10M"
        ]),
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(
            f"NASA POWER error: {response.status_code}"
        )

    data = response.json()

    properties = data.get("properties", {})

    parameter = properties.get(
        "parameter",
        {}
    )

    rainfall = parameter.get(
        "PRECTOTCORR",
        {}
    )

    temperature = parameter.get(
        "T2M",
        {}
    )

    humidity = parameter.get(
        "RH2M",
        {}
    )

    wind = parameter.get(
        "WS10M",
        {}
    )

    if not rainfall:
        raise Exception(
            "NASA POWER rainfall data missing"
        )

    # --------------------------------------------------------
    # Convert dictionaries to ordered daily values
    # --------------------------------------------------------

    def clean_values(dictionary):

        values = []

        for value in dictionary.values():

            try:

                value = float(value)

                # NASA POWER sometimes uses -999
                # for missing values.

                if value <= -900:
                    continue

                values.append(value)

            except (TypeError, ValueError):
                continue

        return values

    rain_values = clean_values(rainfall)
    temp_values = clean_values(temperature)
    humidity_values = clean_values(humidity)
    wind_values = clean_values(wind)

    if not rain_values:
        raise Exception(
            "NASA POWER rainfall values unavailable"
        )

    # --------------------------------------------------------
    # Rainfall calculations
    # --------------------------------------------------------

    rain_1d = sum(rain_values[-1:])
    rain_3d = sum(rain_values[-3:])
    rain_7d = sum(rain_values[-7:])
    rain_14d = sum(rain_values[-14:])
    rain_30d = sum(rain_values[-30:])

    last_30 = rain_values[-30:]

    max_rain_30d = (
        max(last_30)
        if last_30
        else 0.0
    )

    last_7 = rain_values[-7:]

    avg_rain_7d = (
        sum(last_7) / len(last_7)
        if last_7
        else 0.0
    )

    avg_rain_30d = (
        sum(last_30) / len(last_30)
        if last_30
        else 0.0
    )

    # --------------------------------------------------------
    # Actual weather values
    # --------------------------------------------------------

    temperature_value = (
        temp_values[-1]
        if temp_values
        else 0.0
    )

    humidity_value = (
        humidity_values[-1]
        if humidity_values
        else 0.0
    )

    wind_value = (
        wind_values[-1]
        if wind_values
        else 0.0
    )

    result = {

        "rain_1d_mm": float(rain_1d),

        "rain_3d_mm": float(rain_3d),

        "rain_7d_mm": float(rain_7d),

        "rain_14d_mm": float(rain_14d),

        "rain_30d_mm": float(rain_30d),

        "max_rain_30d_mm": float(
            max_rain_30d
        ),

        "avg_rain_7d_mm": float(
            avg_rain_7d
        ),

        "avg_rain_30d_mm": float(
            avg_rain_30d
        ),

        "temperature_C": float(
            temperature_value
        ),

        "humidity_percent": float(
            humidity_value
        ),

        "wind_speed_mps": float(
            wind_value
        ),

        "weather_source": "NASA POWER"
    }

    print("NASA POWER fallback successful.")

    print("NASA WEATHER DATA:")

    print(result)

    return result


# ============================================================
# MAIN WEATHER FUNCTION
# ============================================================

def get_weather(lat, lon):

    print("WEATHER FUNCTION START")

    # --------------------------------------------------------
    # Cache key
    # --------------------------------------------------------

    cache_key = (
        round(float(lat), 2),
        round(float(lon), 2)
    )

    now = time.time()

    # --------------------------------------------------------
    # Check cache
    # --------------------------------------------------------

    if cache_key in _weather_cache:

        cached_time, cached_data = (
            _weather_cache[cache_key]
        )

        if now - cached_time < CACHE_SECONDS:

            print(
                "Using cached weather data."
            )

            return cached_data

    # --------------------------------------------------------
    # Try Open-Meteo
    # --------------------------------------------------------

    try:

        weather = get_open_meteo_weather(
            lat,
            lon
        )

        _weather_cache[cache_key] = (
            now,
            weather
        )

        return weather

    except Exception as e:

        print(
            f"Open-Meteo failed: {e}"
        )

        print(
            "Open-Meteo unavailable."
        )

    # --------------------------------------------------------
    # NASA POWER fallback
    # --------------------------------------------------------

    try:

        weather = get_nasa_power_weather(
            lat,
            lon
        )

        _weather_cache[cache_key] = (
            now,
            weather
        )

        return weather

    except Exception as e:

        print(
            f"NASA POWER failed: {e}"
        )

    # --------------------------------------------------------
    # Final fallback
    # --------------------------------------------------------

    print(
        "WARNING: All weather APIs failed."
    )

    fallback = {

        "rain_1d_mm": 0.0,

        "rain_3d_mm": 0.0,

        "rain_7d_mm": 0.0,

        "rain_14d_mm": 0.0,

        "rain_30d_mm": 0.0,

        "max_rain_30d_mm": 0.0,

        "avg_rain_7d_mm": 0.0,

        "avg_rain_30d_mm": 0.0,

        "temperature_C": 0.0,

        "humidity_percent": 0.0,

        "wind_speed_mps": 0.0,

        "weather_source": "Fallback"
    }

    return fallback