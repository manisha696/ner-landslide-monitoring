from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback

from live_prediction import predict_live_risk


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BASE_DIR
)

WEB_DIR = os.path.join(
    PROJECT_DIR,
    "web"
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# HOME / FRONTEND
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return send_from_directory(
        WEB_DIR,
        "index.html"
    )


@app.route("/<path:filename>", methods=["GET"])
def frontend_files(filename):

    file_path = os.path.join(
        WEB_DIR,
        filename
    )

    if os.path.isfile(file_path):

        return send_from_directory(
            WEB_DIR,
            filename
        )

    return jsonify({
        "error": "File not found"
    }), 404


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health", methods=["GET"])
def health():

    print("HEALTH CHECK RECEIVED", flush=True)

    return jsonify({
        "status": "online",
        "service": "NER Live Landslide Risk API"
    })


# =========================================================
# LIVE RISK
# =========================================================

@app.route("/live-risk", methods=["GET"])
def live_risk():

    print("", flush=True)
    print("========================================", flush=True)
    print("LIVE RISK REQUEST RECEIVED", flush=True)
    print("========================================", flush=True)

    try:

        lat = request.args.get(
            "lat",
            type=float
        )

        lon = request.args.get(
            "lon",
            type=float
        )

        print(
            f"Received coordinates: {lat}, {lon}",
            flush=True
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if lat is None or lon is None:

            print(
                "ERROR: Missing latitude or longitude",
                flush=True
            )

            return jsonify({
                "error":
                    "Latitude and longitude are required."
            }), 400


        if not (
            21 <= lat <= 30
            and
            88 <= lon <= 98
        ):

            print(
                "ERROR: Location outside NER",
                flush=True
            )

            return jsonify({
                "error":
                    "Location is outside the supported NER region."
            }), 400


        # -------------------------------------------------
        # RUN MODEL
        # -------------------------------------------------

        print(
            "Calling predict_live_risk()...",
            flush=True
        )

        result = predict_live_risk(
            lat,
            lon
        )

        print(
            "predict_live_risk() COMPLETED",
            flush=True
        )

        print(
            f"Result: {result}",
            flush=True
        )

        print(
            "========================================",
            flush=True
        )

        return jsonify(result)


    except Exception as e:

        print("", flush=True)
        print("========================================", flush=True)
        print("LIVE RISK ERROR", flush=True)
        print("========================================", flush=True)

        print(
            f"Error type: {type(e).__name__}",
            flush=True
        )

        print(
            f"Error: {str(e)}",
            flush=True
        )

        traceback.print_exc()

        print(
            "========================================",
            flush=True
        )

        return jsonify({

            "error": str(e),

            "error_type":
                type(e).__name__

        }), 500


# =========================================================
# LOCAL SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )