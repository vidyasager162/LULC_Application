document
  .getElementById("locationForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const location = document.getElementById("location").value;
    const response = await fetch("/get_latlong", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location: location }),
    });

    const data = await response.json();
    if (data.latitude && data.longitude) {
      document.getElementById(
        "result"
      ).innerText = `Latitude: ${data.latitude}, Longitude: ${data.longitude}`;
    } else {
      document.getElementById("result").innerText =
        "Error fetching coordinates.";
    }
  });
