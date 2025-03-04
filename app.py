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

# Pricing (Example: Chennai taxi rates)
BASE_FARE = 50  # Initial fare
PER_KM_RATE = 12  # Per km price

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
    area1, area2 = data.get("area1"), data.get("area2")

    if not area1 or not area2:
        return jsonify({"error": "Both area names are required"}), 400

    coords1, coords2 = get_coordinates(area1), get_coordinates(area2)
    if coords1 and coords2:
        distance = geodesic(coords1, coords2).km
        fare = round(BASE_FARE + (PER_KM_RATE * distance), 2)
        return jsonify({"estimated_fare": fare, "distance_km": round(distance, 2)})
    
    return jsonify({"error": "Could not calculate distance"}), 500

@app.route("/search", methods=["GET"])
def search_areas():
    """API to fetch matching area names"""
    query = request.args.get("query")
    if not query:
        return jsonify([])

    url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}, Tamil Nadu"
    response = requests.get(url).json()
    
    areas = [{"name": result["display_name"]} for result in response[:5]]
    return jsonify(areas)

if __name__ == "__main__":
    app.run(debug=True, port=5000)


