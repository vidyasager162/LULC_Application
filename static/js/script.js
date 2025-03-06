let map;
let tileLayer;
let lulcLayer;

document.addEventListener("DOMContentLoaded", function () {
  const getLocationBtn = document.getElementById("getLocationBtn");
  const resultText = document.getElementById("result");

  getLocationBtn.addEventListener("click", function () {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async function (position) {
          const latitude = position.coords.latitude;
          const longitude = position.coords.longitude;
          const bufferSize = 0.02;

          resultText.innerText = `Latitude: ${latitude}, Longitude: ${longitude}`;

          // Fetch Sentinel-2 tile from backend
          try {
            const response = await fetch("/get_tile", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ latitude, longitude }),
            });

            const tileData = await response.json();
            if (tileData.tile_url) {
              if (!map) {
                map = L.map("map").setView([latitude, longitude], 15);
                L.tileLayer(
                  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                  {
                    attribution: "&copy; OpenStreetMap contributors",
                  }
                ).addTo(map);
              } else {
                map.setView([latitude, longitude], 15);
              }

              // Remove existing tile layers
              if (tileLayer) map.removeLayer(tileLayer);
              if (lulcLayer) map.removeLayer(lulcLayer);

              // Add Sentinel-2 base tile
              tileLayer = L.tileLayer(tileData.tile_url, {
                attribution: "&copy; Google Earth Engine",
                tileSize: 256,
              }).addTo(map);

              // Add LULC overlay with transparency
              if (tileData.lulc_overlay) {
                const southWest = [
                  latitude - bufferSize,
                  longitude + bufferSize,
                ];
                const northEast = [
                  latitude + bufferSize,
                  longitude - bufferSize,
                ];
                const imageBounds = [southWest, northEast];

                lulcLayer = L.imageOverlay(tileData.lulc_overlay, imageBounds, {
                  opacity: 0.6,
                  interactive: false,
                }).addTo(map);
              }
            } else {
              resultText.innerText += "\nError fetching Sentinel-2 tile.";
            }
          } catch (error) {
            console.error("Error fetching tile:", error);
            resultText.innerText += "\nFailed to retrieve tile.";
          }
        },
        function (error) {
          console.error("Error getting location:", error);
          resultText.innerText = "Location access denied.";
        }
      );
    } else {
      resultText.innerText = "Geolocation is not supported in this browser.";
    }
  });
});
