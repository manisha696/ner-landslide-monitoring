import os
import pandas as pd
import xgboost as xgb

from live_risk import get_weather_features
from terrain_test import get_terrain


# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "xgboost_no_coordinates_model.json"
)


# =========================================================
# LOAD XGBOOST MODEL
# =========================================================

print("")
print("==============================================")
print("NER XGBOOST MODEL")
print("==============================================")

print(
    f"Loading model from: {MODEL_FILE}",
    flush=True
)

model = xgb.XGBClassifier()

model.load_model(
    MODEL_FILE
)

print(
    "XGBoost model loaded successfully.",
    flush=True
)


# =========================================================
# LIVE PREDICTION
# =========================================================

def predict_live_risk(lat, lon):

    print("")
    print("==============================================", flush=True)
    print("STARTING LIVE PREDICTION", flush=True)
    print("==============================================", flush=True)

    print(f"Latitude: {lat}", flush=True)
    print(f"Longitude: {lon}", flush=True)

    print("ABOUT TO CALL WEATHER FUNCTION", flush=True)

    weather = get_weather_features(lat, lon)

    print("WEATHER FUNCTION RETURNED", flush=True)
    print(weather, flush=True)

    print("ABOUT TO CALL TERRAIN FUNCTION", flush=True)

    terrain = get_terrain(lat, lon)

    print("TERRAIN FUNCTION RETURNED", flush=True)
    print(terrain, flush=True)

    # keep the rest of your existing feature/XGBoost code below


    # =====================================================
    # WEATHER
    # =====================================================

    print("")
    print("STEP 1: Fetching weather...", flush=True)

    weather = get_weather_features(
        lat,
        lon
    )

    print(
        "STEP 1 COMPLETE: Weather received",
        flush=True
    )

    print(
        weather,
        flush=True
    )


    # =====================================================
    # TERRAIN
    # =====================================================

    print("")
    print("STEP 2: Getting terrain...", flush=True)

    terrain = get_terrain(
        lat,
        lon
    )

    print(
        "STEP 2 COMPLETE: Terrain received",
        flush=True
    )

    print(
        terrain,
        flush=True
    )


    # =====================================================
    # FEATURES
    # =====================================================

    print("")
    print("STEP 3: Creating model features...", flush=True)

    features = {

        "rain_1d_mm":
            weather["rain_1d_mm"],

        "rain_3d_mm":
            weather["rain_3d_mm"],

        "rain_7d_mm":
            weather["rain_7d_mm"],

        "rain_14d_mm":
            weather["rain_14d_mm"],

        "rain_30d_mm":
            weather["rain_30d_mm"],

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

        "elevation":
            terrain["elevation"],

        "slope":
            terrain["slope"],

        "aspect":
            terrain["aspect"]
    }


    X = pd.DataFrame(
        [features]
    )


    print(
        "Features created:",
        flush=True
    )

    print(
        X.to_dict(orient="records")[0],
        flush=True
    )


    # =====================================================
    # XGBOOST
    # =====================================================

    print("")
    print(
        "STEP 4: Running XGBoost prediction...",
        flush=True
    )

    probability = float(
        model.predict_proba(X)[0][1]
    )


    print(
        "STEP 4 COMPLETE: XGBoost prediction finished",
        flush=True
    )

    print(
        f"Probability: {probability}",
        flush=True
    )


    # =====================================================
    # RISK LEVEL
    # =====================================================

    risk_percent = float(
        probability * 100
    )


    if risk_percent < 25:

        risk_level = "LOW"

    elif risk_percent < 50:

        risk_level = "MODERATE"

    elif risk_percent < 75:

        risk_level = "HIGH"

    else:

        risk_level = "VERY HIGH"


    print("")
    print(
        f"FINAL RISK: {risk_level} ({risk_percent:.2f}%)",
        flush=True
    )


    # =====================================================
    # RESULT
    # =====================================================

    result = {
    "latitude": float(lat),
    "longitude": float(lon),

    "risk_level": risk_level,

    "risk_percent": float(risk_percent),

    "risk_probability": float(probability),

    "weather": weather,

    "terrain": terrain,

    "model": "XGBoost",

    "status": "success"
}


    print("")
    print("==============================================")
    print("LIVE PREDICTION COMPLETED")
    print("==============================================")

    return result