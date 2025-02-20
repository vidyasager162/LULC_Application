from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


OPENWEATHER_API_KEY = "967f157b9df6e5e2933da70873682fc4"
GEOCODING_API_URL = "http://api.openweathermap.org/geo/1.0/direct"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_latlong', methods=['POST'])
def get_latlong():
    data = request.json
    location_name = data.get('location')

    if not location_name:
        return jsonify({"error": "No location provided"}), 400

    params = {'q': location_name, 'appid': OPENWEATHER_API_KEY}
    response = requests.get(GEOCODING_API_URL, params=params)
    if response.status_code != 200 or not response.json():
        return jsonify({'error': 'Could not fetch location'}), 400
    
    location_data = response.json()[0]
    print(location_data)
    print(response.json())
    lat, lon = location_data['lat'], location_data['lon']
    return jsonify({'latitude': lat, 'longitude': lon})

# @app.route('/get_tile', methods=['POST'])
# def get_tile():
#     data = request.json
#     address = data.get('address')

#     geeocoding_params = {'q': address, 'format': 'json', 'appid': 'your_appid'}
#     response = requests.get(GEOCODING_API_URL, params=geeocoding_params)
#     if response.status_code != 200 or not response.json():
#         return jsonify({'error': 'Invalid address'}), 400
    
#     location = response.json()[0]
#     lat, lon = float(location['lat']), float(location['lon'])

#     tile_url = f"{SENTINEL_API_URL}?REQUEST=GetMap&BBOX={lon-0.05},{lat-0.05},{lon+0.05},{lat+0.05}&LAYERS=TRUE_COLOR&WIDTH=512&HEIGHT=512"
#     return jsonify({'tile_url': tile_url})

if __name__ == '__main__':
    app.run(debug=True)