/* Live Earth Interactive Map & Controller */

let map = null;
let currentBaseLayer = null;
let currentOverlayLayer = null;
let markersGroup = null;
let currentCameras = [];
let activeCamera = null;
let activeCategory = "all";

const CARTO_DARK_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png";
const ESRI_SATELLITE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  bindUIEvents();
  loadCameras(activeCategory, "");
  updateStatusPanel();
});

function initMap() {
  // Center on world view
  map = L.map("leafletMap", {
    center: [20.0, 0.0],
    zoom: 3,
    zoomControl: false,
  });

  currentBaseLayer = L.tileLayer(CARTO_DARK_URL, {
    maxZoom: 19,
    subdomains: "abcd",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; CARTO',
  }).addTo(map);

  if (typeof L.markerClusterGroup === "function") {
    markersGroup = L.markerClusterGroup({
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      maxClusterRadius: 45,
    });
    map.addLayer(markersGroup);
  } else {
    markersGroup = L.featureGroup().addTo(map);
  }

  setTimeout(() => {
    map.invalidateSize();
  }, 250);
}

function bindUIEvents() {
  // Base map toggle
  const satToggle = document.getElementById("satelliteBasemapToggle");
  if (satToggle) {
    satToggle.addEventListener("change", (e) => {
      if (currentBaseLayer) map.removeLayer(currentBaseLayer);

      if (e.target.checked) {
        currentBaseLayer = L.tileLayer(ESRI_SATELLITE_URL, {
          maxZoom: 18,
          attribution: "Tiles &copy; Esri &mdash; Earthstar Geographics",
        }).addTo(map);
        updateStatusSource("Esri World Imagery Satellite");
      } else {
        currentBaseLayer = L.tileLayer(CARTO_DARK_URL, {
          maxZoom: 19,
          subdomains: "abcd",
          attribution: '&copy; OpenStreetMap &copy; CARTO',
        }).addTo(map);
        updateStatusSource("CartoDB Dark Matter Base");
      }
    });
  }

  // Category sidebar buttons
  document.querySelectorAll(".cat-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".cat-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeCategory = btn.dataset.category;

      if (activeCategory === "Favorites") {
        renderFavoritesOnMap();
      } else if (activeCategory === "Weather Satellite" || activeCategory === "Earth Imagery") {
        toggleLayerPanel(true);
        loadCameras("all", "");
      } else {
        loadCameras(activeCategory, "");
      }
    });
  });

  // Search input & button
  const searchBtn = document.getElementById("leSearchBtn");
  const searchInput = document.getElementById("leSearchInput");

  if (searchBtn && searchInput) {
    searchBtn.addEventListener("click", () => handleSearch(searchInput.value));
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") handleSearch(searchInput.value);
    });
  }

  // Floating toolbar buttons
  document.getElementById("btnZoomIn")?.addEventListener("click", () => map.zoomIn());
  document.getElementById("btnZoomOut")?.addEventListener("click", () => map.zoomOut());
  document.getElementById("btnResetView")?.addEventListener("click", () => map.setView([20.0, 0.0], 3));
  document.getElementById("btnLocateMe")?.addEventListener("click", locateUser);
  document.getElementById("btnRefresh")?.addEventListener("click", () => {
    showLoading(true);
    loadCameras(activeCategory, searchInput ? searchInput.value : "");
    setTimeout(() => showLoading(false), 600);
  });
  document.getElementById("btnToggleFullscreen")?.addEventListener("click", toggleFullscreen);

  // Weather overlay radios
  document.querySelectorAll('input[name="weatherOverlay"]').forEach((radio) => {
    radio.addEventListener("change", (e) => handleWeatherOverlayChange(e.target.value));
  });

  // Earth overlay radios
  document.querySelectorAll('input[name="earthOverlay"]').forEach((radio) => {
    radio.addEventListener("change", (e) => handleEarthOverlayChange(e.target.value));
  });

  // Favorite button inside camera modal
  document.getElementById("camFavBtn")?.addEventListener("click", () => {
    if (activeCamera) {
      const isFav = toggleFavorite(activeCamera);
      const favBtn = document.getElementById("camFavBtn");
      if (favBtn) favBtn.classList.toggle("active", isFav);
      if (activeCategory === "Favorites") renderFavoritesOnMap();
    }
  });
}

function showLoading(show) {
  const overlay = document.getElementById("mapLoading");
  if (overlay) overlay.classList.toggle("active", show);
}

function loadCameras(category, query) {
  showLoading(true);
  const url = `/api/live-earth/cameras?category=${encodeURIComponent(category)}&q=${encodeURIComponent(query)}`;

  fetch(url)
    .then((res) => res.json())
    .then((data) => {
      showLoading(false);
      if (data.status === "success") {
        currentCameras = data.cameras || [];
        renderCameraMarkers(currentCameras);
        updateStatusCamCount(currentCameras.length);

        if (query && currentCameras.length === 0) {
          alert(`No public live camera is available for "${query}".`);
        }
      }
    })
    .catch((err) => {
      showLoading(false);
      console.error("Error loading cameras:", err);
    });
}

function renderCameraMarkers(cameras) {
  markersGroup.clearLayers();

  if (!cameras || cameras.length === 0) return;

  const bounds = L.latLngBounds();

  cameras.forEach((cam) => {
    const customIcon = L.divIcon({
      className: "custom-map-pin",
      html: `<div style="background: rgba(13,28,50,0.92); border: 2px solid #5bb2ff; color: #fff; padding: 4px 8px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; display: flex; align-items: center; gap: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
        <span>${getCategoryEmoji(cam.category)}</span>
        <span>${cam.city}</span>
      </div>`,
      iconSize: [110, 30],
      iconAnchor: [55, 15],
    });

    const marker = L.marker([cam.lat, cam.lon], { icon: customIcon });
    marker.bindPopup(`
      <div style="font-family: Inter, sans-serif; color: #0d1c32; padding: 4px;">
        <h4 style="margin: 0 0 4px; font-size: 0.95rem;">${cam.name}</h4>
        <p style="margin: 0 0 8px; font-size: 0.82rem; color: #475569;">${cam.city}, ${cam.country} &bull; ${cam.category}</p>
        <button onclick="openCameraModalById('${cam.id}')" style="background: #0284c7; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 700; cursor: pointer; width: 100%;">
          ▶ View Live Feed
        </button>
      </div>
    `);

    bounds.extend([cam.lat, cam.lon]);
    markersGroup.addLayer(marker);
  });

  if (cameras.length === 1) {
    map.setView([cameras[0].lat, cameras[0].lon], 11);
  } else if (cameras.length > 1) {
    map.fitBounds(bounds, { padding: [50, 50] });
  }
}

function getCategoryEmoji(cat) {
  if (cat.includes("Traffic")) return "🚦";
  if (cat.includes("Airport")) return "✈";
  if (cat.includes("Harbor")) return "🚢";
  if (cat.includes("Webcam") || cat.includes("Public Webcams")) return "🏖";
  return "🌍";
}

function renderFavoritesOnMap() {
  const favs = getFavorites();
  currentCameras = favs;
  renderCameraMarkers(favs);
  updateStatusCamCount(favs.length);
  if (favs.length === 0) {
    alert("You have no saved favorites yet. Click the ⭐ star icon inside any camera feed to bookmark it!");
  }
}

function handleSearch(query) {
  if (!query || !query.strip?.() && !query.trim()) return;

  showLoading(true);
  fetch(`/api/live-earth/search?q=${encodeURIComponent(query.trim())}`)
    .then((res) => res.json())
    .then((data) => {
      showLoading(false);
      const locations = data.locations || [];
      const cameras = data.cameras || [];

      if (locations.length > 0) {
        const loc = locations[0];
        map.setView([loc.lat, loc.lon], 11);
      }

      if (cameras.length > 0) {
        currentCameras = cameras;
        renderCameraMarkers(cameras);
        updateStatusCamCount(cameras.length);
      } else {
        renderNoCameraMessage(query);
      }
    })
    .catch((err) => {
      showLoading(false);
      console.error("Search error:", err);
    });
}

function renderNoCameraMessage(query) {
  const noMsg = document.getElementById("noCamMsg");
  const iframe = document.getElementById("camIframe");
  const title = document.getElementById("camModalTitle");
  const modal = document.getElementById("cameraModal");

  if (modal && noMsg && iframe && title) {
    title.textContent = query;
    iframe.style.display = "none";
    noMsg.style.display = "flex";
    modal.classList.add("active");
  }
}

function executeQuickSearch(city) {
  const searchInput = document.getElementById("leSearchInput");
  if (searchInput) searchInput.value = city;
  handleSearch(city);
}

let activeCamMode = "video";
let autoRefreshTimer = null;

function switchCamMode(mode) {
  if (!activeCamera) return;
  activeCamMode = mode;

  const btnVideo = document.getElementById("btnModeVideo");
  const btnImage = document.getElementById("btnModeImage");
  const iframe = document.getElementById("camIframe");
  const imgElem = document.getElementById("camImg");
  const noMsg = document.getElementById("noCamMsg");

  if (btnVideo) btnVideo.classList.toggle("active", mode === "video");
  if (btnImage) btnImage.classList.toggle("active", mode === "image");

  if (iframe) iframe.style.display = "none";
  if (imgElem) imgElem.style.display = "none";
  if (noMsg) noMsg.style.display = "none";

  if (mode === "video" && activeCamera.embed_url) {
    let embedUrl = activeCamera.embed_url;
    if (embedUrl.includes("youtube.com/embed/") && !embedUrl.includes("autoplay=")) {
      embedUrl += (embedUrl.includes("?") ? "&" : "?") + "autoplay=1&mute=1&rel=0";
    }
    iframe.src = embedUrl;
    iframe.style.display = "block";
  } else {
    const streamUrl = activeCamera.fallback_stream || activeCamera.image_url || (activeCamera.type === "image" ? activeCamera.embed_url : null);
    if (streamUrl && imgElem) {
      const sep = streamUrl.includes("?") ? "&" : "?";
      imgElem.src = streamUrl + sep + "t=" + Date.now();
      imgElem.style.display = "block";
    } else if (mode === "video" && !activeCamera.embed_url && streamUrl && imgElem) {
      imgElem.src = streamUrl;
      imgElem.style.display = "block";
    } else if (noMsg) {
      noMsg.style.display = "flex";
    }
  }
}

function refreshCamFeed() {
  if (!activeCamera) return;
  if (activeCamMode === "image") {
    const imgElem = document.getElementById("camImg");
    const streamUrl = activeCamera.fallback_stream || activeCamera.image_url;
    if (imgElem && streamUrl) {
      const sep = streamUrl.includes("?") ? "&" : "?";
      imgElem.src = streamUrl + sep + "t=" + Date.now();
    }
  } else {
    switchCamMode("video");
  }
}

function openCameraModalById(camId) {
  const cam = currentCameras.find((c) => c.id === camId) || getFavorites().find((f) => f.id === camId);
  if (!cam) return;

  activeCamera = cam;
  const modal = document.getElementById("cameraModal");
  const title = document.getElementById("camModalTitle");
  const badge = document.getElementById("camModalBadge");
  const loc = document.getElementById("camModalLocation");
  const prov = document.getElementById("camModalProvider");
  const status = document.getElementById("camModalStatus");
  const updated = document.getElementById("camModalUpdated");
  const favBtn = document.getElementById("camFavBtn");

  if (title) title.textContent = cam.name;
  if (badge) badge.textContent = cam.category;
  if (loc) loc.textContent = `${cam.city}, ${cam.state ? cam.state + ", " : ""}${cam.country}`;
  if (prov) prov.textContent = cam.provider;
  if (status) status.textContent = cam.status;
  if (updated) updated.textContent = cam.last_updated;

  if (favBtn) favBtn.classList.toggle("active", isFavorite(cam.id));

  const defaultMode = (cam.embed_url && cam.type !== "image") ? "video" : "image";
  switchCamMode(defaultMode);

  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  autoRefreshTimer = setInterval(() => {
    if (activeCamMode === "image" && activeCamera) {
      refreshCamFeed();
    }
  }, 10000);

  modal?.classList.add("active");
}

function closeCameraModal() {
  const modal = document.getElementById("cameraModal");
  const iframe = document.getElementById("camIframe");
  const imgElem = document.getElementById("camImg");
  if (iframe) iframe.src = "";
  if (imgElem) imgElem.src = "";
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
  }
  modal?.classList.remove("active");
}

function locateUser() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }
  showLoading(true);
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      showLoading(false);
      map.setView([pos.coords.latitude, pos.coords.longitude], 12);
      L.marker([pos.coords.latitude, pos.coords.longitude])
        .addTo(map)
        .bindPopup("📍 Your Current Location")
        .openPopup();
    },
    () => {
      showLoading(false);
      alert("Unable to retrieve your current position.");
    }
  );
}

function toggleFullscreen() {
  const mapElem = document.getElementById("mapWrapper");
  if (!document.fullscreenElement) {
    mapElem.requestFullscreen().catch((err) => alert("Could not enter fullscreen mode"));
  } else {
    document.exitFullscreen();
  }
}

function toggleLayerPanel(forceOpen) {
  const panel = document.getElementById("layerControlPanel");
  if (panel) {
    if (forceOpen !== undefined) {
      panel.classList.toggle("active", forceOpen);
    } else {
      panel.classList.toggle("active");
    }
  }
}

function handleWeatherOverlayChange(layerId) {
  if (currentOverlayLayer) map.removeLayer(currentOverlayLayer);

  if (layerId === "none") {
    updateStatusSource("Public Camera Network");
    return;
  }

  showLoading(true);
  fetch("/api/live-earth/satellites")
    .then((res) => res.json())
    .then((data) => {
      showLoading(false);
      const layers = data.layers || [];
      const selected = layers.find((l) => l.id === layerId);
      if (selected && selected.url_template) {
        currentOverlayLayer = L.tileLayer(selected.url_template, {
          opacity: selected.opacity || 0.7,
          attribution: selected.attribution,
        }).addTo(map);
        updateStatusSource(selected.name);
      } else {
        alert("This layer requires an API key in your .env configuration.");
      }
    });
}

function handleEarthOverlayChange(layerId) {
  if (currentOverlayLayer) map.removeLayer(currentOverlayLayer);

  if (layerId === "none") {
    updateStatusSource("Public Camera Network");
    return;
  }

  showLoading(true);
  fetch("/api/live-earth/earth-imagery")
    .then((res) => res.json())
    .then((data) => {
      showLoading(false);
      const layers = data.layers || [];
      const selected = layers.find((l) => l.id === layerId);
      if (selected && selected.url_template) {
        currentOverlayLayer = L.tileLayer(selected.url_template, {
          opacity: selected.opacity || 0.85,
          attribution: selected.attribution,
        }).addTo(map);
        updateStatusSource(selected.name);
      }
    });
}

function updateStatusPanel() {
  fetch("/api/live-earth/status")
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("statusConn").textContent = data.connection_status || "Online";
      document.getElementById("statusRefresh").textContent = data.last_refresh || "Just Now";
    });
}

function updateStatusSource(sourceName) {
  const elem = document.getElementById("statusSource");
  if (elem) elem.textContent = sourceName;
}

function updateStatusCamCount(count) {
  const elem = document.getElementById("statusCamCount");
  if (elem) elem.textContent = `${count} Camera${count === 1 ? "" : "s"} Found`;
}

function retryActiveSearch() {
  closeCameraModal();
  const searchInput = document.getElementById("leSearchInput");
  if (searchInput && searchInput.value) {
    handleSearch(searchInput.value);
  } else {
    loadCameras(activeCategory, "");
  }
}
