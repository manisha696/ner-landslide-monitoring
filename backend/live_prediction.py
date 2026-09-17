import os
import json
import joblib
import numpy as np
import xgboost as xgb

from live_risk import get_weather_features
from terrain_test import find_dem_tile, get_terrain


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "xgboost_no_coordinates_model.json"
)

# ============================================================
# MODEL LOADING
# ============================================================

def load_model():

    print("\nLoading trained XGBoost model...")

    model = xgb.XGBClassifier()

    model.load_model(MODEL_FILE)

    print("XGBoost model loaded successfully.")

    return model


# ============================================================
# BUILD MODEL FEATURES
# ============================================================

def build_features(weather, terrain):

    features = {

        # ---------------- WEATHER ----------------

        "rain_1d_mm": weather["rain_1d_mm"],
        "rain_3d_mm": weather["rain_3d_mm"],
        "rain_7d_mm": weather["rain_7d_mm"],
        "rain_14d_mm": weather["rain_14d_mm"],
        "rain_30d_mm": weather["rain_30d_mm"],

        "max_rain_30d_mm":
            weather["max_rain_30d_mm"],

        "avg_rain_7d_mm":
            weather["avg_rain_7d_mm"],

        "avg_rain_30d_mm":
            weather["avg_rain_30d_mm"],

        "temperature_C":
            weather["temperature_C"],

        "humidity_percent":
            weather["humidity_percent"],

        "wind_speed_mps":
            weather["wind_speed_mps"],

        # ---------------- TERRAIN ----------------

        "elevation":
            terrain["elevation"],

        "slope":
            terrain["slope"],

        "aspect":
            terrain["aspect"]
    }

    return features


# ============================================================
# LIVE RISK PREDICTION
# ============================================================

def predict_live_risk(lat, lon):

    print("\n========================================")
    print("REAL-TIME LANDSLIDE RISK ENGINE")
    print("========================================")

    print(f"Latitude : {lat}")
    print(f"Longitude: {lon}")

    # --------------------------------------------------------
    # 1. LIVE WEATHER
    # --------------------------------------------------------

    print("\nFetching live weather...")

    weather = get_weather_features(
        lat,
        lon
    )

    # --------------------------------------------------------
    # 2. REAL TERRAIN
    # --------------------------------------------------------

    print("Extracting terrain from SRTM...")

    dem_file = find_dem_tile(
        lat,
        lon
    )

    if dem_file is None:

        raise Exception(
            "No DEM tile found for this location."
        )

    terrain = get_terrain(
        lat,
        lon
    )

    # --------------------------------------------------------
    # 3. BUILD FEATURES
    # --------------------------------------------------------

    features = build_features(
        weather,
        terrain
    )

    # --------------------------------------------------------
    # 4. LOAD MODEL
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # 5. PREPARE FEATURE VECTOR
    # --------------------------------------------------------

    feature_names = [
        "rain_1d_mm",
        "rain_3d_mm",
        "rain_7d_mm",
        "rain_14d_mm",
        "rain_30d_mm",
        "max_rain_30d_mm",
        "avg_rain_7d_mm",
        "avg_rain_30d_mm",
        "temperature_C",
        "humidity_percent",
        "wind_speed_mps",
        "elevation",
        "slope",
        "aspect"
    ]

    X = np.array([
        features[name]
        for name in feature_names
    ]).reshape(1, -1)

    # --------------------------------------------------------
    # 6. XGBOOST PREDICTION
    # --------------------------------------------------------

    probability = float(
        model.predict_proba(X)[0][1]
    )

    risk_percent = probability * 100

    # --------------------------------------------------------
    # 7. RISK LEVEL
    # --------------------------------------------------------

    if risk_percent < 25:

        risk_level = "LOW"

    elif risk_percent < 50:

        risk_level = "MODERATE"

    elif risk_percent < 75:

        risk_level = "HIGH"

    else:

        risk_level = "VERY HIGH"

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print("\n========================================")
    print("LIVE LANDSLIDE RISK RESULT")
    print("========================================")

    print(
        f"Risk Probability : {risk_percent:.2f}%"
    )

    print(
        f"Risk Level       : {risk_level}"
    )

    print("\nLIVE WEATHER")
    print("----------------------------------------")

    print(
        f"Rain 1 day      : {weather['rain_1d_mm']:.2f} mm"
    )

    print(
        f"Rain 3 days     : {weather['rain_3d_mm']:.2f} mm"
    )

    print(
        f"Rain 7 days     : {weather['rain_7d_mm']:.2f} mm"
    )

    print(
        f"Rain 14 days    : {weather['rain_14d_mm']:.2f} mm"
    )

    print(
        f"Rain 30 days    : {weather['rain_30d_mm']:.2f} mm"
    )

    print(
        f"Temperature     : {weather['temperature_C']:.2f} °C"
    )

    print(
        f"Humidity        : {weather['humidity_percent']:.2f}%"
    )

    print(
        f"Wind            : {weather['wind_speed_mps']:.2f} m/s"
    )

    print("\nREAL TERRAIN")
    print("----------------------------------------")

    print(
        f"Elevation       : {terrain['elevation']:.2f} m"
    )

    print(
        f"Slope           : {terrain['slope']:.2f}°"
    )

    print(
        f"Aspect          : {terrain['aspect']:.2f}°"
    )

    print("========================================")

    return {
        "latitude": lat,
        "longitude": lon,
        "risk_probability": probability,
        "risk_percent": risk_percent,
        "risk_level": risk_level,
        "weather": weather,
        "terrain": terrain
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Test location
    lat = 25.5007
    lon = 93.9854

    predict_live_risk(
        lat,
        lon
    )