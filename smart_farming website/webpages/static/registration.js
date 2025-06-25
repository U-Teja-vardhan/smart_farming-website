document.getElementById("signup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;
  const esp32_id = document.getElementById("esp32_id").value;

  const res = await fetch("http://localhost:5000/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role, esp32_id })
  });

  const data = await res.json();
  alert(data.message);
});

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const response = await fetch("http://localhost:5000/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const result = await response.json();

  if (result.success) {
    if (result.role === "farmer") {
      localStorage.setItem("esp32_id", result.esp32_id);
      window.location.href = "farmer_dashboard.html";
    } else {
      localStorage.setItem("username", result.username);
      window.location.href = "customer.html";
    }
  } else {
    alert("Invalid credentials.");
  }
});
