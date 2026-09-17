from flask import Flask, request, jsonify
from flask_cors import CORS

from live_prediction import predict_live_risk


app = Flask(__name__)

CORS(app)


# ============================================================
# ROOT
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "service": "NER Live Landslide Risk API",
        "status": "online",
        "message": "NER Landslide Monitoring Backend is running",
        "endpoints": {
            "health": "/health",
            "live_risk": "/live-risk?lat=25.5007&lon=93.9854"
        }
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({

        "status": "online",

        "service":
            "NER Live Landslide Risk API"
    })


# ============================================================
# LIVE LANDSLIDE RISK
# ============================================================

@app.route("/live-risk", methods=["GET"])
def live_risk():

    try:

        lat = request.args.get(
            "lat",
            type=float
        )

        lon = request.args.get(
            "lon",
            type=float
        )


        # ----------------------------------------------------
        # CHECK COORDINATES
        # ----------------------------------------------------

        if lat is None or lon is None:

            return jsonify({

                "error":
                    "Latitude and longitude are required."

            }), 400


        # ----------------------------------------------------
        # NER REGION CHECK
        # ----------------------------------------------------

        if not (
            21 <= lat <= 30
            and
            88 <= lon <= 98
        ):

            return jsonify({

                "error":
                    "Location is outside the supported NER region."

            }), 400


        print("")
        print("========================================")
        print("LIVE RISK REQUEST")
        print("========================================")

        print(
            f"Latitude : {lat}"
        )

        print(
            f"Longitude: {lon}"
        )

        print(
            "Running live prediction..."
        )


        # ----------------------------------------------------
        # MODEL PREDICTION
        # ----------------------------------------------------

        result = predict_live_risk(
            lat,
            lon
        )


        print(
            "Live prediction successful."
        )

        print(
            "========================================"
        )


        return jsonify(result)


    except Exception as e:

        print("")
        print("========================================")
        print("LIVE RISK ERROR")
        print("========================================")

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        print(
            "========================================"
        )


        return jsonify({

            "error":
                str(e),

            "error_type":
                type(e).__name__

        }), 500


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    import os

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    print("")
    print("========================================")
    print("NER LIVE LANDSLIDE RISK API")
    print("========================================")

    print(
        f"Running on port: {port}"
    )

    print("")
    print(
        "Health:"
    )

    print(
        "/health"
    )

    print("")
    print(
        "Live Risk:"
    )

    print(
        "/live-risk?lat=25.5007&lon=93.9854"
    )

    print(
        "========================================"
    )


    app.run(

        host="0.0.0.0",

        port=port,

        debug=False
    )