from flask import Flask, render_template, request, jsonify
import requests
import ee

app = Flask(__name__)

try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()

def get_sentinel_tile_url(lat, lon, buffer_size=0.02):
    try:
        region = ee.Geometry.BBox(lon - buffer_size, lat - buffer_size, lon + buffer_size, lat + buffer_size)

        collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(region)
                .filterDate('2024-01-01', '2024-02-01')
                .sort('CLOUDY_PIXEL_PERCENTAGE')
                .first())
        
        vis_params = {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 3000,
        }

        map_id_dict = collection.getMapId(vis_params)
        tile_url = f"https://earthengine.googleapis.com/v1/{map_id_dict['mapid']}/tiles/{{z}}/{{x}}/{{y}}"
        return tile_url
        
    except Exception as e:
        print("Error fetching Sentinel-2 tile:", str(e))
        return None
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map_view')
def map_view():
    return render_template('map_view.html')

@app.route('/get_tile', methods=['POST'])
def get_tile():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"error": "Invalid coordinates"}), 400
    
    try:
        tile_url = get_sentinel_tile_url(latitude, longitude)
        return jsonify({"tile_url": tile_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)