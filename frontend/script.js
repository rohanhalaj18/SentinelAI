const video = document.getElementById("video");
const socket = io("http://localhost:5000");
const alertList = document.getElementById("alertList");

// Receive alerts
socket.on("alert", (data) => {
  addAlert(data.type);
});

function addAlert(type) {
  const li = document.createElement("li");
  li.className = "alert-item";
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  
  li.innerHTML = `<span><strong>${type.toUpperCase()}</strong> DETECTED</span><span class="alert-time">${time}</span>`;
  
  alertList.insertBefore(li, alertList.firstChild);
  
  if (alertList.children.length > 50) alertList.removeChild(alertList.lastChild);
}

navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;
  })
  .catch((err) => {
    console.error("Error accessing camera:", err);
    alert("Allow camera permission to use Sentinel AI");
  });
