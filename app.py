import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.distance import geodesic
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])  # Return an empty list if no query is provided

    params = {
        "format": "json",
        "q": query,
        "limit": 5  # Limit suggestions to 5 results
    }

    response = requests.get(NOMINATIM_URL, params=params)
    data = response.json()

    suggestions = [{"name": place["display_name"], "lat": place["lat"], "lon": place["lon"]} for place in data]

    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)


load_dotenv()

app = Flask(__name__)
CORS(app)

# Define fare rates for different vehicle types
FARE_RATES = {
    "auto": {"base": 30, "per_km": 10},
    "sedan": {"base": 50, "per_km": 12},
    "suv": {"base": 70, "per_km": 15},
    "luxury": {"base": 100, "per_km": 20},
}

def get_coordinates(area):
    """Fetch latitude and longitude of an area"""
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={area}, Tamil Nadu"
    response = requests.get(url).json()
    if response:
        return (float(response[0]['lat']), float(response[0]['lon']))
    return None

@app.route("/predict", methods=["POST"])
def predict_fare():
    """API endpoint to calculate taxi fare"""
    data = request.json
    area1, area2, vehicle_type = data.get("area1"), data.get("area2"), data.get("vehicle_type")

    if not area1 or not area2 or not vehicle_type:
        return jsonify({"error": "All fields are required"}), 400

    if vehicle_type not in FARE_RATES:
        return jsonify({"error": "Invalid vehicle type"}), 400

    coords1, coords2 = get_coordinates(area1), get_coordinates(area2)
    if coords1 and coords2:
        distance = geodesic(coords1, coords2).km
        base_fare = FARE_RATES[vehicle_type]["base"]
        per_km_rate = FARE_RATES[vehicle_type]["per_km"]
        fare = round(base_fare + (per_km_rate * distance), 2)
        return jsonify({"estimated_fare": fare, "distance_km": round(distance, 2), "vehicle_type": vehicle_type})
    
    return jsonify({"error": "Could not calculate distance"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)


