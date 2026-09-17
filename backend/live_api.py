from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from live_prediction import predict_live_risk


# ============================================================
# PATHS
# ============================================================

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


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    static_folder=WEB_DIR,
    static_url_path=""
)

CORS(app)


# ============================================================
# WEBSITE
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return send_from_directory(
        WEB_DIR,
        "index.html"
    )


# ============================================================
# OTHER FRONTEND FILES
# ============================================================

@app.route("/<path:filename>")
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


# ============================================================
# HEALTH
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({

        "status": "online",

        "service":
            "NER Live Landslide Risk API"

    })


# ============================================================
# LIVE RISK
# ============================================================

@app.route(
    "/live-risk",
    methods=["GET"]
)
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


        if lat is None or lon is None:

            return jsonify({

                "error":
                    "Latitude and longitude are required."

            }), 400


        # NER bounding box

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
# LOCAL / RENDER START
# ============================================================

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