let map;
let marker;
let tileLayer;

document.addEventListener("DOMContentLoaded", function () {
  const mapContainer = document.getElementById("map");
  const resultText = document.getElementById("result");
  const coordinatesText = document.getElementById("coordinates");
  const getTileBtn = document.getElementById("getTileBtn");
  const radiusInput = document.getElementById("radius");

  // Initialize Leaflet map with OpenStreetMap tiles
  map = L.map(mapContainer).setView([12.9716, 77.5946], 13); // Default: Bangalore

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  // Add a draggable marker to select a location
  marker = L.marker([12.9716, 77.5946], { draggable: true }).addTo(map);

  // Update coordinates when the marker is dragged
  marker.on("dragend", function (event) {
    const position = marker.getLatLng();
    coordinatesText.innerText = `Selected Location: Latitude: ${position.lat}, Longitude: ${position.lng}`;
  });

  // Fetch Sentinel-2 tile when button is clicked
  getTileBtn.addEventListener("click", async function () {
    const position = marker.getLatLng();
    const latitude = position.lat;
    const longitude = position.lng;
    const radius = parseFloat(radiusInput.value);

    resultText.innerText = `Fetching Sentinel-2 tile...`;

    try {
      const response = await fetch("/get_tile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude, longitude }),
      });

      const tileData = await response.json();
      if (tileData.tile_url) {
        // Remove old Sentinel-2 tile layer if exists
        if (tileLayer) {
          map.removeLayer(tileLayer);
        }

        // Add new Sentinel-2 tile layer
        tileLayer = L.tileLayer(tileData.tile_url, {
          attribution: "&copy; Google Earth Engine",
          tileSize: 256,
        }).addTo(map);

        resultText.innerText = `Sentinel-2 image displayed for selected location (Radius: ${radius} km).`;
      } else {
        resultText.innerText = "Error fetching Sentinel-2 tile.";
      }
    } catch (error) {
      console.error("Error fetching tile:", error);
      resultText.innerText = "Failed to retrieve tile.";
    }
  });
});
