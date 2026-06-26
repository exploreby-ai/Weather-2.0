import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables securely
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend requests

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

def fetch_weather(endpoint, params):
    """Helper to fetch data and handle errors."""
    params['appid'] = API_KEY
    params['units'] = 'metric'
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=5)
        response.raise_for_status()
        return response.json(), 200
    except requests.exceptions.HTTPError as e:
        return {"error": "Weather API error or location not found"}, e.response.status_code
    except requests.exceptions.RequestException:
        return {"error": "Network or timeout error"}, 503

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "api_key_loaded": bool(API_KEY)})

@app.route('/api/weather', methods=['GET'])
def current_weather():
    city = request.args.get('city')
    if not city: return jsonify({"error": "Missing 'city' parameter"}), 400
    
    data, status = fetch_weather("weather", {"q": city})
    if status == 200:
        # Return only required fields
        data = {
            "location": data['name'],
            "temperature": data['main']['temp'],
            "condition": data['weather'][0]['main'],
            "icon": data['weather'][0]['icon']
        }
    return jsonify(data), status

@app.route('/api/forecast', methods=['GET'])
def forecast():
    city = request.args.get('city')
    if not city: return jsonify({"error": "Missing 'city' parameter"}), 400
    
    data, status = fetch_weather("forecast", {"q": city})
    return jsonify(data), status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))