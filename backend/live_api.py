from flask import Flask, request, jsonify
from flask_cors import CORS

from live_prediction import predict_live_risk

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "NER Live Landslide Risk API"
    })


@app.route("/live-risk", methods=["GET"])
def live_risk():
    try:
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)

        if lat is None or lon is None:
            return jsonify({
                "error": "Latitude and longitude are required."
            }), 400

        # Northeast India approximate bounding box
        if not (21 <= lat <= 30 and 88 <= lon <= 98):
            return jsonify({
                "error": "Location is outside the supported NER region."
            }), 400

        result = predict_live_risk(lat, lon)

        return jsonify(result)

    except Exception as e:
        print("\nLIVE RISK ERROR:")
        print(str(e))

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    print("\n========================================")
    print("NER LIVE LANDSLIDE RISK API")
    print("========================================")
    print("API running at:")
    print("http://127.0.0.1:5000")

    print("\nHealth check:")
    print("http://127.0.0.1:5000/health")

    print("\nLive risk example:")
    print(
        "http://127.0.0.1:5000/live-risk"
        "?lat=25.5007&lon=93.9854"
    )

    print("========================================\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )