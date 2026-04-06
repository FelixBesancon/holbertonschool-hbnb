const API_BASE_URL = "http://127.0.0.1:5000/api/v1";

function setTokenCookie(token) {
    // Keep cookie simple for the project; path=/ makes it available on all pages.
    document.cookie = `token=${encodeURIComponent(token)}; path=/; SameSite=Lax`;
}

function showLoginError(message) {
    const loginForm = document.getElementById("login-form");
    if (!loginForm) {
        return;
    }

    let errorBox = document.getElementById("login-error");
    if (!errorBox) {
        errorBox = document.createElement("p");
        errorBox.id = "login-error";
        errorBox.setAttribute("role", "alert");
        errorBox.style.color = "#b42318";
        errorBox.style.marginTop = "0.75rem";
        loginForm.appendChild(errorBox);
    }

    errorBox.textContent = message;
}

async function loginUser(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    let payload = {};
    try {
        payload = await response.json();
    } catch (error) {
        payload = {};
    }

    if (!response.ok) {
        const errorMessage = payload.error || "Invalid credentials";
        throw new Error(errorMessage);
    }

    return payload;
}

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    if (!loginForm) {
        return;
    }

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const emailInput = document.getElementById("email");
        const passwordInput = document.getElementById("password");
        const email = emailInput ? emailInput.value.trim() : "";
        const password = passwordInput ? passwordInput.value : "";

        if (!email || !password) {
            showLoginError("Please enter both email and password.");
            return;
        }

        try {
            const data = await loginUser(email, password);
            if (!data.access_token) {
                throw new Error("No token returned by API.");
            }

            setTokenCookie(data.access_token);
            window.location.href = "index.html";
        } catch (error) {
            showLoginError(`Login failed: ${error.message}`);
        }
    });
});
