from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Replace with your actual API details
RAPIDAPI_URL = "rapidapi.com"
RAPIDAPI_KEY = "619804f50dmsh3fdef34ebbc4d22p1ed324jsn1290b1d173ae"

@app.route('/')
def home():
    return jsonify({"message": "Taxi Price Prediction API is running!"})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    city1 = data.get('city1')
    city2 = data.get('city2')

    # API request to fetch taxi fare
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_URL.split("/")[2],  # Extract host from URL
    }
    params = {"from": city1, "to": city2}

    try:
        response = requests.get(RAPIDAPI_URL, headers=headers, params=params)
        api_data = response.json()
        
        # Modify based on actual API response structure
        estimated_fare = api_data.get("fare", "No fare data available")

        return jsonify({"estimated_fare": estimated_fare})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
