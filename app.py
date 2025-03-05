from flask import Flask, render_template, request, jsonify
import requests
import ee

app = Flask(__name__)

try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

# cloud_project = 'ee-vidyasager162'
# try:
#     ee.Initialize(project=cloud_project)
# except Exception:
#     ee.Authenticate()
#     ee.Initialize(project=cloud_project)

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
    lat, lon = location_data['lat'], location_data['lon']
    return jsonify({'latitude': lat, 'longitude': lon})

@app.route('/get_tile', methods=['POST'])
def get_tile():
    data = request.json
    lat, lon = data.get('latitude'), data.get('longitude')

    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude required"}), 400
    
    buffer_size = 0.02
    region = ee.Geometry.BBox(lon - buffer_size, lat - buffer_size, lon + buffer_size, lat + buffer_size)

    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(region) \
        .filterDate('2024-01-01', '2024-02-01') \
        .sort('CLOUDY_PIXEL_PERCENTAGE') \
        .first()
    
    if not collection:
        return jsonify({'error': 'No image found for this location'}), 400
    
    vis_params = {
        'bands': ['B4', 'B3', 'B2'],
        'min': 0,
        'max': 3000,
    }

    map_id_dict = collection.getMapId(vis_params)
    print(map_id_dict)
    tile_url = f"https://earthengine.googleapis.com/v1/{map_id_dict['mapid']}/tiles/{{z}}/{{x}}/{{y}}"
    print(tile_url)
    return jsonify({'tile_url': tile_url, 'latitude': lat, 'longitude': lon})

if __name__ == '__main__':
    app.run(debug=True)