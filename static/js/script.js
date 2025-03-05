let map;
let tileLayer;

document.addEventListener("DOMContentLoaded", function () {
  const getLocationBtn = document.getElementById("getLocationBtn");
  const resultText = document.getElementById("result");

  getLocationBtn.addEventListener("click", function () {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async function (position) {
          const latitude = position.coords.latitude;
          const longitude = position.coords.longitude;

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
              } else {
                map.setView([latitude, longitude], 15);
              }

              map.eachLayer((layer) => {
                if (layer instanceof L.TileLayer) {
                  map.removeLayer(layer);
                }
              });

              L.tileLayer(tileData.tile_url, {
                attribution: "&copy; Google Earth Engine",
                tileSize: 256,
              }).addTo(map);
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
