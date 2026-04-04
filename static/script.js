// REGISTER
function registerUser() {
    let name = document.getElementById("reg-name").value;
    let email = document.getElementById("reg-email").value;
    let password = document.getElementById("reg-password").value;

    if (name === "" || email === "" || password === "") {
        alert("All fields are required");
        return;
    }

    let user = {
        name: name,
        email: email,
        password: password
    };

    localStorage.setItem("user", JSON.stringify(user));
    alert("Registration successful! Please login.");
    window.location.href = "login.html";
}

// LOGIN
function loginUser() {
    let email = document.getElementById("login-email").value;
    let password = document.getElementById("login-password").value;

    let storedUser = JSON.parse(localStorage.getItem("user"));

    if (!storedUser) {
        alert("No user found. Please register first.");
        return;
    }

    if (email === storedUser.email && password === storedUser.password) {
        localStorage.setItem("loggedIn", "true");
        alert("Login successful!");
        window.location.href = "dashboard.html";
    } else {
        alert("Wrong email or password");
    }
}

// LOGOUT
function logoutUser() {
    localStorage.removeItem("loggedIn");
    window.location.href = "login.html";
}

// DASHBOARD PROTECTION
function checkLogin() {
    let loggedIn = localStorage.getItem("loggedIn");
    if (loggedIn !== "true") {
        window.location.href = "login.html";
    }
}
