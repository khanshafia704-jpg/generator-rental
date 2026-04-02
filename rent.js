const prices = {
    "5KVA": 500,
    "10KVA": 1000,
    "20KVA": 2000,
    "30KVA": 3000,
    "50KVA": 4000,
    "75KVA": 5500,
    "100KVA": 7000,
    "150KVA": 9000,
    "200KVA": 12000
};

const gen = localStorage.getItem("selectedGen");
document.getElementById("genName").innerText = gen + " Generator";
document.getElementById("pricePerDay").innerText =
    "Price per day: ₹" + prices[gen];

function calculate() {
    const days = document.getElementById("days").value;
    const total = prices[gen] * days;
    document.getElementById("totalPrice").innerText =
        "Total: ₹" + total;
}

document.getElementById("days").addEventListener("input", calculate);
calculate();

function confirmRent() {
    localStorage.setItem("days", document.getElementById("days").value);
    localStorage.setItem("total", document.getElementById("totalPrice").innerText);
    window.location.href = "/payment";
}
