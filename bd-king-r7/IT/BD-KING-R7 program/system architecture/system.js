// Create map
const map = L.map('map').setView([23.685, 90.3563], 7); // Bangladesh example

// Map tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
}).addTo(map);

// Demo network devices (SAFE DEMO)
const devices = [
  { name: "Router", lat: 23.8103, lng: 90.4125 },
  { name: "Laptop", lat: 22.3569, lng: 91.7832 },
  { name: "Mobile", lat: 24.3636, lng: 88.6241 }
];

// Add markers
devices.forEach(device => {
  L.marker([device.lat, device.lng])
    .addTo(map)
    .bindPopup("📡 Device: " + device.name);
});

// Network status check
function checkNetwork() {
  const status = document.getElementById("status");
  if (navigator.onLine) {
    status.innerText = "Network: Connected ✅";
  } else {
    status.innerText = "Network: Disconnected ❌";
  }
}

// Auto check
checkNetwork();