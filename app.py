from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Taxi Price Prediction API is running!"})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    city1 = data.get('city1')
    city2 = data.get('city2')

    # Dummy price prediction logic
    price = len(city1) * len(city2) * 2  # Replace with actual ML model logic
    return jsonify({"estimated_fare": price})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
