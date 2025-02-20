document
  .getElementById("locationForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const address = document.getElementById("address").value;
    const response = await fetch("/get_tile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address: address }),
    });

    const data = await response.json();
    if (data.tile_url) {
      document.getElementById("tileImage").src = data.tile_url;
      document.getElementById("tileImage").style.display = "block";
    } else {
      alert("Error fetching tile.");
    }
  });
