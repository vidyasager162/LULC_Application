let map;
document
  .getElementById("locationForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const location = document.getElementById("location").value;
    document.getElementById("result").innerText = "Fetching data...";

    try {
      const locResponse = await fetch("/get_latlong", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location: location }),
      });

      const locData = await locResponse.json();
      if (!locData.latitude || !locData.longitude) {
        throw new Error("Error fetching coordinates.");
      }

      document.getElementById(
        "result"
      ).innerText = `Latitude: ${locData.latitude}, Longitude: ${locData.longitude}`;

      const tileResponse = await fetch("/get_tile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latitude: locData.latitude,
          longitude: locData.longitude,
        }),
      });

      const tileData = await tileResponse.json();
      if (tileData.tile_url) {
        if (!map) {
          map = L.map("map").setView([locData.latitude, locData.longitude], 12);
        } else {
          map.setView([locData.latitude, locData.longitude], 12);
        }

        map.eachLayer((layer) => {
          if (layer instanceof L.TileLayer) {
            map.removeLayer(layer);
          }
        });

        L.tileLayer(tileData.tile_url, {
          attribution:
            "&copy; <a href='https://earthengine.google.com/'>Google Earth Engine</a>",
          tileSize: 256,
        }).addTo(map);
      } else {
        document.getElementById("result").innerText +=
          "\nError fetching Sentinel-2 tile.";
      }
    } catch (error) {
      document.getElementById("result").innerText = error.message;
    }
  });
