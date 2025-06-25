// ========== Crop Health Chatbot ==========
function sendToBot() {
  const msg = document.getElementById("chat-input").value;
  if (!msg.trim()) return;

  fetch("http://localhost:5000/api/chatbot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  })
  .then(res => res.json())
  .then(data => {
    const responseText = data.response || data.error || "No response from bot.";
    document.getElementById("bot-response").textContent = responseText;
  })
  .catch(err => {
    document.getElementById("bot-response").textContent = "Error contacting bot.";
    console.error("Chatbot error:", err);
  });
}

// ========== Live Sensor Plot Auto-Refresh ==========
function refreshSensorPlot() {
  const plot = document.getElementById("sensor-plot");
  if (plot) {
    plot.src = "http://localhost:8000/plot?" + new Date().getTime(); // Bypass cache
  }
}

// Auto-refresh every 15 seconds
setInterval(refreshSensorPlot, 15000);

window.addEventListener("load", () => {
  refreshSensorPlot();
});



console.log("Shop page loaded.");

// Add event listeners to nav icons
document.getElementById('profile-icon').addEventListener('click', () => {
    // Profile functionality will be added here
});

document.getElementById('notifications-icon').addEventListener('click', () => {
    // Notifications functionality will be added here
});

document.getElementById('mail-icon').addEventListener('click', () => {
    // Mail functionality will be added here
});

document.getElementById('hi-icon').addEventListener('click', () => {
    // Hi functionality will be added here
});