from flask import Flask, render_template, request, jsonify
import requests
import ee
import torch
import numpy as np
import rasterio
from rasterio.transform import from_bounds
import torchvision.transforms as transforms
import torchvision.io as tvio
from PIL import Image
from matplotlib import pyplot as plt
import segmentation_models_pytorch as smp

app = Flask(__name__)

try:
    ee.Initialize(project='ee-vidyasager162')
except Exception:
    ee.Authenticate()
    ee.Initialize()

NUM_CLASSES = 8
MODEL_PATH = "./static/PSPNet_res101_320_74.pt"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = smp.PSPNet(
    encoder_name = 'resnet101',
    encoder_weights = 'imagenet',
    classes = NUM_CLASSES,
    activation = None,
).to(device)

state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict)
model.eval()

def preprocess_sentinel_image(image):
    transform = transforms.Compose([
        transforms.Resize((320, 320)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0).to(device)

def get_sentinel_tile(lat, lon, buffer_size=0.02):
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
        return tile_url, collection
        
    except Exception as e:
        print("Error fetching Sentinel-2 tile:", str(e))
        return None, None
    
def classify_sentinel_image(image):
    output = model(image)
    predicted = torch.argmax(output, dim=1).squeeze(0).cpu().numpy()
    return predicted
    
def get_lulc_overlay(lat, lon, buffer_size=0.02):
    try:
        tile_url, image = get_sentinel_tile(lat, lon, buffer_size)
        if image is None:
            return None, None

        url = image.select(['B4', 'B3', 'B2']).getThumbURL({'min': 0, 'max': 3000, 'dimensions': [320, 320]})
        print(url)
        img = Image.open(requests.get(url, stream=True).raw).convert("RGB")
        img.save("./static/sentinel_image.png")
        print(img)
        processed_image = preprocess_sentinel_image(img)
        print(processed_image)
        lulc_mask = classify_sentinel_image(processed_image)

        transforms = from_bounds(lon - buffer_size, lat - buffer_size, lon + buffer_size, lat + buffer_size, lulc_mask.shape[1], lulc_mask.shape[0])
        lulc_path = "./static/lulc_overlay.tif"

        with rasterio.open(
            lulc_path, 'w', driver='GTiff',
            height=lulc_mask.shape[0], width=lulc_mask.shape[1],
            count=1, dtype=lulc_mask.dtype,
            crs='EPSG:4326', transform=transforms
        ) as dst:
            dst.write(lulc_mask, 1)

        lulc_png_path = "./static/lulc_overlay.png"
        plt.imsave(lulc_png_path, lulc_mask, cmap='tab10')

        return tile_url, lulc_png_path
    
    except Exception as e:
        print("Error generating LULC overlay:", str(e))
        return None, None
    
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
        tile_url, lulc_overlay = get_lulc_overlay(latitude, longitude)
        return jsonify({"tile_url": tile_url, "lulc_overlay": lulc_overlay})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)