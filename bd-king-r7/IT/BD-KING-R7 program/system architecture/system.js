function checkNetwork() {
  if (navigator.onLine) {
    document.getElementById("netStatus").innerText = "Connected ✅";
  } else {
    document.getElementById("netStatus").innerText = "Disconnected ❌";
  }
}

// Demo device list (safe example)
const devices = [
  "Phone - 192.168.1.2",
  "Laptop - 192.168.1.5",
  "Tablet - 192.168.1.8"
];

const list = document.getElementById("deviceList");
devices.forEach(d => {
  const li = document.createElement("li");
  li.innerText = d;
  list.appendChild(li);
});

checkNetwork();