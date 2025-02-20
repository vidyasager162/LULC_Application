from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

GEOCODING_API_URL = "http://api.openweathermap.org/geo/1.0/direct"
SENTINEL_API_URL = "https://api.sentinel-hub.com/ogc/wms/your_instance_id"

@app.route('/')
def index():
    return render_template('index.html')

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