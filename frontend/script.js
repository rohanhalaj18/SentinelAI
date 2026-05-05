const video = document.getElementById("video");
const socket = io("http://localhost:5000");
const alertList = document.getElementById("alertList");

// Receive alerts from backend
socket.on("newAlert", (data) => {
  addAlert(data.type, data.severity, data.time);
});

function addAlert(type, severity, time) {
  const li = document.createElement("li");
  li.className = "alert-item";

  // Set border color based on severity
  if (severity === "CRITICAL") {
    li.style.borderLeftColor = "#ff0000";
    li.style.background = "linear-gradient(135deg, rgba(255, 0, 0, 0.15) 0%, rgba(255, 0, 0, 0.05) 100%)";
  } else if (severity === "HIGH") {
    li.style.borderLeftColor = "#ff8c00";
    li.style.background = "linear-gradient(135deg, rgba(255, 140, 0, 0.15) 0%, rgba(255, 140, 0, 0.05) 100%)";
  }

  const msgSpan = document.createElement("span");
  msgSpan.innerText = `⚠ ${type.toUpperCase()} DETECTED`;

  const timeSpan = document.createElement("span");
  timeSpan.className = "alert-time";
  timeSpan.innerText = time || new Date().toLocaleTimeString();

  li.appendChild(msgSpan);
  li.appendChild(timeSpan);

  // Newest alerts on top
  alertList.prepend(li);
}

// Camera feed — detect.py uses the camera for AI detection,
// so the browser may not be able to access it simultaneously.
navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;
  })
  .catch((err) => {
    console.warn("Camera unavailable (likely in use by detect.py):", err.message);
    // Show a friendly status overlay instead of a popup alert
    const container = document.querySelector(".video-container");
    const overlay = document.createElement("div");
    overlay.className = "camera-offline";
    overlay.innerHTML = `
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ff4b4b" stroke-width="1.5">
        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
        <circle cx="12" cy="13" r="4"/>
      </svg>
      <p>Camera in use by AI Detection</p>
      <span>Alerts will appear in real-time →</span>
    `;
    video.style.display = "none";
    container.appendChild(overlay);
  });
