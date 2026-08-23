// Leaflet map initialization - will be implemented in Phase 3
document.addEventListener("DOMContentLoaded", () => {
    const mapEl = document.getElementById("map");
    if (!mapEl) return;

    // Default: Niš city center
    const map = L.map("map").setView([43.3209, 21.8958], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);
});
