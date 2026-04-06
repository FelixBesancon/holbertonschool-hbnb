const API_BASE_URL = "http://127.0.0.1:5000/api/v1";
const PRICE_FILTER_OPTIONS = ["10", "50", "100", "All"];

let allPlaces = [];

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    const target = `${name}=`;

    for (let i = 0; i < cookies.length; i += 1) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(target)) {
            return decodeURIComponent(cookie.slice(target.length));
        }
    }

    return null;
}

function setTokenCookie(token) {
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

function showPlacesError(message) {
    const list = document.getElementById("places-list");
    if (!list) {
        return;
    }

    list.innerHTML = "";
    const errorText = document.createElement("p");
    errorText.textContent = message;
    errorText.style.color = "#b42318";
    list.appendChild(errorText);
}

function showAddReviewError(message) {
    const errorBox = document.getElementById("review-form-error");
    if (!errorBox) {
        return;
    }

    errorBox.textContent = message;
    errorBox.style.display = message ? "block" : "none";
}

function renderStars(rating) {
    const safeRating = Math.max(0, Math.min(5, Number(rating) || 0));
    let html = '<span class="review-stars" aria-label="Rating">';
    for (let i = 1; i <= 5; i += 1) {
        html += `<span class="star ${i <= safeRating ? "filled" : ""}">★</span>`;
    }
    html += "</span>";
    return html;
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

function updateLoginLinkVisibility() {
    const loginLink = document.getElementById("login-link");
    if (!loginLink) {
        return;
    }

    const token = getCookie("token");
    loginLink.style.display = token ? "none" : "inline-block";
}

function populatePriceFilter() {
    const filter = document.getElementById("price-filter");
    if (!filter) {
        return;
    }

    filter.innerHTML = "";
    PRICE_FILTER_OPTIONS.forEach((value) => {
        const option = document.createElement("option");
        option.value = value === "All" ? "all" : value;
        option.textContent = value;
        filter.appendChild(option);
    });

    filter.value = "all";
}

function displayPlaces(places) {
    const list = document.getElementById("places-list");
    if (!list) {
        return;
    }

    list.innerHTML = "";

    if (!places.length) {
        const empty = document.createElement("p");
        empty.textContent = "No places found.";
        list.appendChild(empty);
        return;
    }

    places.forEach((place) => {
        const card = document.createElement("div");
        card.className = "place-card";
        card.dataset.price = String(place.price);

        const title = document.createElement("h3");
        title.textContent = place.title || "Untitled place";

        const price = document.createElement("p");
        price.innerHTML = `<strong>Price per night:</strong> $${Number(place.price).toFixed(0)}`;

        const detailsButton = document.createElement("button");
        detailsButton.className = "details-button";
        detailsButton.textContent = "View Details";
        detailsButton.addEventListener("click", () => {
            window.location.href = `place.html?id=${encodeURIComponent(place.id)}`;
        });

        card.appendChild(title);
        card.appendChild(price);
        card.appendChild(detailsButton);
        list.appendChild(card);
    });
}

function applyPriceFilter() {
    const filter = document.getElementById("price-filter");
    if (!filter) {
        return;
    }

    const selected = filter.value;
    if (selected === "all") {
        displayPlaces(allPlaces);
        return;
    }

    const maxPrice = Number(selected);
    const filtered = allPlaces.filter((place) => Number(place.price) <= maxPrice);
    displayPlaces(filtered);
}

async function fetchPlaces() {
    const token = getCookie("token");
    const headers = {};

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/places/`, {
        method: "GET",
        headers
    });

    if (!response.ok) {
        throw new Error(`Unable to load places (${response.status})`);
    }

    return response.json();
}

async function fetchPlaceDetails(placeId) {
    const response = await fetch(`${API_BASE_URL}/places/${placeId}`);
    if (!response.ok) {
        throw new Error(`Unable to load place (${response.status})`);
    }
    return response.json();
}

async function fetchPlaceReviews(placeId) {
    const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews/`);
    if (!response.ok) {
        throw new Error(`Unable to load reviews (${response.status})`);
    }
    return response.json();
}

function renderPlaceDetails(place) {
    const detailsSection = document.getElementById("place-details");
    if (!detailsSection) {
        return;
    }

    detailsSection.innerHTML = "";

    const ownerName = place.owner
        ? `${place.owner.first_name || ""} ${place.owner.last_name || ""}`.trim()
        : "Unknown host";

    const amenityIconPath = (name) => {
        const key = String(name || "")
            .trim()
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, "")
            .replace(/\s+/g, "_");
        return `images/icon_${key}.png`;
    };

    const amenityItems = Array.isArray(place.amenities) && place.amenities.length
        ? `<h3>Amenities:</h3><ul class="amenity-list">${place.amenities
            .map((a) => {
                const name = a.name || "Amenity";
                const icon = amenityIconPath(name);
                return `
                    <li class="amenity-item">
                        <span class="amenity-main">
                            <img class="amenity-icon" src="${icon}" alt="${name} icon" loading="lazy" onerror="this.style.display='none'">
                            <span class="amenity-name">${name}</span>
                        </span>
                        <span class="amenity-check" aria-hidden="true">✓</span>
                    </li>
                `;
            })
            .join("")}</ul>`
        : "<h3>Amenities:</h3><p>No amenities listed.</p>";

    const wrapper = document.createElement("div");
    wrapper.className = "place-info";
    wrapper.innerHTML = `
        <h1>${place.title || "Untitled place"}</h1>
        <p><strong>Host:</strong> ${ownerName}</p>
        <p><strong>Price:</strong> $${Number(place.price || 0).toFixed(0)} per night</p>
        <p><strong>Description:</strong> ${place.description || "No description provided."}</p>
        ${amenityItems}
    `;

    detailsSection.appendChild(wrapper);
}

function renderPlaceReviews(reviews) {
    const reviewsSection = document.getElementById("reviews");
    if (!reviewsSection) {
        return;
    }

    reviewsSection.innerHTML = "<h2>Reviews</h2>";

    if (!reviews.length) {
        const empty = document.createElement("p");
        empty.textContent = "No reviews yet.";
        reviewsSection.appendChild(empty);
        return;
    }

    reviews.forEach((review) => {
        const authorName = review.author
            ? `${review.author.first_name || ""} ${review.author.last_name || ""}`.trim()
            : "Unknown user";

        const card = document.createElement("div");
        card.className = "review-card";
        card.innerHTML = `
            <p><strong>Author:</strong> ${authorName}</p>
            <p><strong>Comment:</strong> ${review.text || ""}</p>
            <p><strong>Rating:</strong> ${renderStars(review.rating)}</p>
        `;
        reviewsSection.appendChild(card);
    });
}

function initStarRatingWidget() {
    const starContainer = document.getElementById("star-rating");
    const ratingInput = document.getElementById("rating");
    if (!starContainer || !ratingInput) {
        return;
    }

        let currentRating = 0;

        const applyVisual = (value) => {
            starContainer.querySelectorAll(".star-btn").forEach((btn, idx) => {
                btn.classList.toggle("is-active", idx < value);
            });
        };

        const setRating = (value) => {
            currentRating = value;
            ratingInput.value = String(value);
            applyVisual(value);
            starContainer.querySelectorAll(".star-btn").forEach((btn, idx) => {
                btn.setAttribute("aria-checked", idx < value ? "true" : "false");
            });
        };

    starContainer.innerHTML = "";
    for (let i = 1; i <= 5; i += 1) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "star-btn";
        button.innerHTML = "★";
        button.setAttribute("aria-label", `${i} star${i > 1 ? "s" : ""}`);
        button.setAttribute("aria-checked", "false");
        button.addEventListener("click", () => setRating(i));
            button.addEventListener("mouseenter", () => applyVisual(i));
        starContainer.appendChild(button);
    }

        starContainer.addEventListener("mouseleave", () => applyVisual(currentRating));
        setRating(0);
}

async function submitReview(placeId, text, rating) {
    const token = getCookie("token");
    if (!token) {
        throw new Error("You must be logged in to submit a review.");
    }

    const response = await fetch(`${API_BASE_URL}/reviews/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            text,
            rating,
            place_id: placeId
        })
    });

    let payload = {};
    try {
        payload = await response.json();
    } catch (error) {
        payload = {};
    }

    if (!response.ok) {
        throw new Error(payload.error || `Unable to submit review (${response.status})`);
    }

    return payload;
}

function updateAddReviewLinkVisibility() {
    const addReviewLink = document.getElementById("add-review-link");
    if (!addReviewLink) {
        return;
    }

    const token = getCookie("token");
    addReviewLink.style.display = token ? "inline-block" : "none";
}

async function initPlacePage() {
    const placeDetails = document.getElementById("place-details");
    if (!placeDetails) {
        return;
    }

    updateLoginLinkVisibility();
    updateAddReviewLinkVisibility();

    const params = new URLSearchParams(window.location.search);
    const placeId = params.get("id");
    const addReviewLink = document.getElementById("add-review-link");

    if (!placeId) {
        placeDetails.innerHTML = "<p style=\"color:#b42318\">Missing place ID in URL.</p>";
        return;
    }

    if (addReviewLink) {
        addReviewLink.href = `add_review.html?id=${encodeURIComponent(placeId)}`;
    }

        placeDetails.innerHTML = "<p class=\"loading-msg\">Loading…</p>";

    try {
        const [place, reviews] = await Promise.all([
            fetchPlaceDetails(placeId),
            fetchPlaceReviews(placeId)
        ]);

        renderPlaceDetails(place);
        renderPlaceReviews(reviews);
    } catch (error) {
        placeDetails.innerHTML = `<p style=\"color:#b42318\">${error.message}</p>`;
    }
}

function initAddReviewPage() {
    const reviewForm = document.getElementById("review-form");
    const reviewText = document.getElementById("review");
    const ratingInput = document.getElementById("rating");
    if (!reviewForm || !reviewText || !ratingInput) {
        return;
    }

    updateLoginLinkVisibility();
    initStarRatingWidget();

    const token = getCookie("token");
    if (!token) {
        window.location.href = "index.html";
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const placeId = params.get("id");
    const context = document.getElementById("review-place-context");

    if (!placeId) {
        showAddReviewError("Missing place ID in URL.");
        reviewForm.querySelector("button[type='submit']").disabled = true;
        return;
    }

    if (context) {
        context.textContent = "Loading place…";
        fetchPlaceDetails(placeId)
            .then((place) => { context.textContent = `Reviewing: ${place.title}`; })
            .catch(() => { context.textContent = `Place ID: ${placeId}`; });
    }

    reviewForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        showAddReviewError("");

        const text = reviewText.value.trim();
        const rating = Number(ratingInput.value);

        if (!text) {
            showAddReviewError("Please write a review message.");
            return;
        }

        if (!rating || rating < 1 || rating > 5) {
            showAddReviewError("Please select a star rating between 1 and 5.");
            return;
        }

        try {
            await submitReview(placeId, text, rating);
            window.location.href = `place.html?id=${encodeURIComponent(placeId)}`;
        } catch (error) {
            showAddReviewError(`Review failed: ${error.message}`);
        }
    });
}

async function initIndexPage() {
    const placesList = document.getElementById("places-list");
    if (!placesList) {
        return;
    }

    updateLoginLinkVisibility();
    populatePriceFilter();

    try {
        allPlaces = await fetchPlaces();
        displayPlaces(allPlaces);
    } catch (error) {
        showPlacesError(`Error loading places: ${error.message}`);
    }

    const filter = document.getElementById("price-filter");
    if (filter) {
        filter.addEventListener("change", applyPriceFilter);
    }
}

function initLoginPage() {
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
}

document.addEventListener("DOMContentLoaded", () => {
    initLoginPage();
    initIndexPage();
    initPlacePage();
    initAddReviewPage();
});
