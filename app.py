from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Google Maps API details
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "your_google_maps_api_key")
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
GOOGLE_MAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

# Taxi rates per km in Chennai based on car type
TAXI_RATES_CHENNAI = {
    "sedan": 14,
    "suv": 19,
    "hatchback": 11
}

@app.route('/')
def home():
    return jsonify({"message": "Exclusive Taxi Price Prediction API is running!"})

# Auto-suggest locations within Tamil Nadu (Top 3 Results)
@app.route('/suggest', methods=['GET'])
def suggest_locations():
    query = request.args.get('query', '')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    params = {
        "input": query,
        "types": "geocode",
        "components": "country:IN|administrative_area:Tamil Nadu",  # Tamil Nadu filtering
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        response = requests.get(GOOGLE_PLACES_URL, params=params)
        api_data = response.json()

        # Extract top 3 location suggestions
        suggestions = [
            place["description"]
            for place in api_data.get("predictions", []) if "Tamil Nadu" in place["description"]
        ][:3]  # Limit to top 3 results

        return jsonify({"suggestions": suggestions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get taxi fare and route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    area1 = data.get('area1')
    area2 = data.get('area2')
    car_type = data.get('car_type', 'sedan').lower()

    if not area1 or not area2:
        return jsonify({"error": "Both area1 and area2 are required"}), 400

    if car_type not in TAXI_RATES_CHENNAI:
        return jsonify({"error": "Invalid car type. Available types: sedan, suv, hatchback"}), 400

    # API request to fetch distance
    params = {
        "origins": f"{area1}, Tamil Nadu, India",
        "destinations": f"{area2}, Tamil Nadu, India",
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        response = requests.get(GOOGLE_MAPS_URL, params=params)
        api_data = response.json()

        if "rows" in api_data and api_data["rows"]:
            distance_text = api_data["rows"][0]["elements"][0]["distance"]["text"]
            distance_km = float(distance_text.split()[0])
        else:
            return jsonify({"error": "Could not retrieve distance data."}), 500

        # Calculate estimated fare
        rate_per_km = TAXI_RATES_CHENNAI[car_type]
        estimated_fare = distance_km * rate_per_km

        # Get directions route URL
        directions_url = f"https://www.google.com/maps/dir/{area1}/{area2}/"

        return jsonify({
            "area1": area1,
            "area2": area2,
            "car_type": car_type,
            "distance_km": distance_km,
            "estimated_fare": estimated_fare,
            "route_url": directions_url,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
