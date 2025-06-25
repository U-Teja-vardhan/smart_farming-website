document.getElementById("request-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const res = await fetch("http://localhost:5000/api/send-request", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_id: document.getElementById("customer-id").value,
        farmer_id: document.getElementById("farmer-id").value,
        quantity: document.getElementById("quantity").value,
        price: document.getElementById("price").value,
        requested_date: document.getElementById("date").value
      })
    });
    const result = await res.json();
    alert(result.message);
  });