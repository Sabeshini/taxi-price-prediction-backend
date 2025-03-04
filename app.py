import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.distance import geodesic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Base fare and per km rate (Example: Chennai taxi pricing)
BASE_FARE = 50  # Initial fare
PER_KM_RATE = 12  # Price per km

def get_distance(area1, area2):
    """Fetch the distance between two areas using OpenStreetMap"""
    def get_coordinates(area):
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={area}, Tamil Nadu"
        response = requests.get(url).json()
        if response:
            return (float(response[0]['lat']), float(response[0]['lon']))
        return None

    coords1, coords2 = get_coordinates(area1), get_coordinates(area2)
    if coords1 and coords2:
        return geodesic(coords1, coords2).km
    return None

@app.route("/predict", methods=["POST"])
def predict_fare():
    """API endpoint to calculate taxi fare"""
    data = request.json
    area1, area2 = data.get("area1"), data.get("area2")

    if not area1 or not area2:
        return jsonify({"error": "Both area names are required"}), 400

    distance = get_distance(area1, area2)

    if distance:
        fare = round(BASE_FARE + (PER_KM_RATE * distance), 2)
        return jsonify({"estimated_fare": fare, "distance_km": round(distance, 2)})
    
    return jsonify({"error": "Could not calculate distance"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

