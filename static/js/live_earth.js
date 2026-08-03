let map = null;
let currentBaseLayer = null;
let currentOverlayLayer = null;
let markersGroup = null;
let eventsGroup = null;
let userMarker = null;

let currentCameras = [];
let allCamerasList = [];
let activeCamera = null;
let activeCategory = "all";
let activeCamMode = "video";
let autoRefreshTimer = null;
let searchDebounceTimer = null;
let currentLayerOpacity = 0.8;

// Timeline Player State
let timelineFrames = [];
let timelineIndex = 0;
let timelineTimer = null;
let isTimelinePlaying = false;
let timelineOverlayLayer = null;

const CARTO_DARK_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png";
const ESRI_SATELLITE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const LOCAL_STORAGE_SIDEBAR_KEY = "cozy_live_earth_sidebar_collapsed";

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initSidebarState();
  bindUIEvents();
  bindKeyboardShortcuts();
  loadCameras(activeCategory, "");
  updateStatusPanel();
  initRadarTimeline();
  requestBrowserLocation();
});

function initMap() {
  console.log("MAP INITIALIZATION STARTED");

  // Physics inertia, hardware accelerated canvas, smooth zooming
  map = L.map("leafletMap", {
    center: [20.0, 0.0],
    zoom: 3,
    zoomControl: false,
    preferCanvas: true,
    bounceAtZoomLimits: false,
    inertia: true,
    inertiaDeceleration: 3000,
    easeLinearity: 0.25,
    zoomSnap: 0.5,
    zoomDelta: 0.5,
    fadeAnimation: true,
    zoomAnimation: true,
  });

  currentBaseLayer = L.tileLayer(CARTO_DARK_URL, {
    maxZoom: 19,
    subdomains: "abcd",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; CARTO',
  });

  currentBaseLayer.on("tileerror", function (err) {
    console.warn("CartoDB tile loading error, applying OpenStreetMap fallback:", err);
    if (map && currentBaseLayer) {
      map.removeLayer(currentBaseLayer);
      currentBaseLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }).addTo(map);
    }
  });

  currentBaseLayer.addTo(map);
  console.log("MAP OBJECT:", map);

  // Live mouse cursor coordinate & zoom tracking
  map.on("mousemove", (e) => {
    const coordsElem = document.getElementById("statusCoords");
    if (coordsElem && e.latlng) {
      const latStr = e.latlng.lat >= 0 ? `${e.latlng.lat.toFixed(3)}° N` : `${Math.abs(e.latlng.lat).toFixed(3)}° S`;
      const lonStr = e.latlng.lng >= 0 ? `${e.latlng.lng.toFixed(3)}° E` : `${Math.abs(e.latlng.lng).toFixed(3)}° W`;
      const zoomLevel = map ? map.getZoom() : 3;
      coordsElem.textContent = `${latStr}, ${lonStr} (z${zoomLevel})`;
    }
  });

  // Marker cluster groups
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

  eventsGroup = L.featureGroup().addTo(map);

  // Interactive Map Click Listener -> Weather Card Popup
  map.on("click", (e) => {
    fetchWeatherForCoordinates(e.latlng.lat, e.latlng.lng);
  });

  // Responsive Invalidation Triggers
  [50, 150, 300, 600, 1200].forEach((delay) => {
    setTimeout(() => {
      if (map) map.invalidateSize();
    }, delay);
  });

  window.addEventListener("resize", () => {
    if (map) map.invalidateSize();
  });
}

// Sidebar Collapse & Expand with LocalStorage Memory
function initSidebarState() {
  const sidebar = document.getElementById("leSidebar");
  const isCollapsed = localStorage.getItem(LOCAL_STORAGE_SIDEBAR_KEY) === "true";

  if (sidebar && isCollapsed) {
    sidebar.classList.add("collapsed");
    updateFloatingSidebarBtn(true);
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById("leSidebar");
  if (!sidebar) return;

  const willCollapse = !sidebar.classList.contains("collapsed");
  sidebar.classList.toggle("collapsed", willCollapse);
  localStorage.setItem(LOCAL_STORAGE_SIDEBAR_KEY, willCollapse);

  updateFloatingSidebarBtn(willCollapse);

  // Invalidate map size after smooth CSS transition
  setTimeout(() => {
    if (map) map.invalidateSize();
  }, 320);
}

function updateFloatingSidebarBtn(isCollapsed) {
  const btnFloat = document.getElementById("btnExpandSidebarFloating");
  const floatingSearch = document.querySelector(".floating-search-hud");

  if (btnFloat) {
    btnFloat.style.display = isCollapsed ? "block" : "none";
  }

  if (floatingSearch) {
    floatingSearch.style.left = isCollapsed ? "130px" : "16px";
  }
}

function requestBrowserLocation() {
  if (!navigator.geolocation) return;

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      map.setView([lat, lon], 9);

      if (userMarker) map.removeLayer(userMarker);

      const pulseIcon = L.divIcon({
        className: "custom-user-marker",
        html: `<div class="user-location-pulse" title="Your Location"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      });

      userMarker = L.marker([lat, lon], { icon: pulseIcon }).addTo(map);
      fetchWeatherForCoordinates(lat, lon, true);
    },
    (err) => {
      console.log("Geolocation permission declined or unavailable:", err.message);
    },
    { timeout: 8000 }
  );
}

function loadCameras(category, query) {
  showLoading(true, "Loading camera feeds...");
  const url = `/api/live-earth/cameras?category=${encodeURIComponent(category)}&q=${encodeURIComponent(query)}`;

  fetch(url)
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return res.json();
    })
    .then((data) => {
      showLoading(false);
      if (data.status === "success") {
        currentCameras = data.cameras || [];
        console.log("CAMERAS RECEIVED:", currentCameras.length);
        if (!query) allCamerasList = currentCameras;
        renderCameraMarkers(currentCameras);
        updateStatusCamCount(currentCameras.length);

        const connElem = document.getElementById("statusConn");
        if (connElem) {
          connElem.textContent = "Synced";
          connElem.className = "status-hud-dot";
        }
      }
    })
    .catch((err) => {
      showLoading(false);
      console.error("Error loading cameras:", err);
      const connElem = document.getElementById("statusConn");
      if (connElem) {
        connElem.textContent = "Offline";
      }
    });
}

function renderCameraMarkers(cameras) {
  markersGroup.clearLayers();

  if (!cameras || cameras.length === 0) {
    console.log("MARKERS CREATED: 0");
    return;
  }

  const bounds = L.latLngBounds();

  cameras.forEach((cam) => {
    const catClass = getCategoryClass(cam.category);
    const customIcon = L.divIcon({
      className: "custom-map-pin",
      html: `<div class="pin-badge-container ${catClass}">
        <span class="live-pulse-badge"></span>
        <span>${getCategoryEmoji(cam.category)}</span>
        <span>${cam.city || "Camera"}</span>
      </div>`,
      iconSize: [120, 32],
      iconAnchor: [60, 16],
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

  const createdCount = markersGroup.getLayers ? markersGroup.getLayers().length : cameras.length;
  console.log("MARKERS CREATED:", createdCount);

  if (cameras.length === 1) {
    map.setView([cameras[0].lat, cameras[0].lon], 11);
  } else if (cameras.length > 1 && activeCategory !== "all") {
    map.fitBounds(bounds, { padding: [50, 50] });
  }
}

function loadLiveEvents() {
  showLoading(true, "Loading active NASA natural events...");
  fetch("/api/live-earth/events")
    .then((res) => res.json())
    .then((data) => {
      showLoading(false);
      const events = data.events || [];
      eventsGroup.clearLayers();

      events.forEach((ev) => {
        const emoji = getEventEmoji(ev.category);
        const eventIcon = L.divIcon({
          className: "custom-map-pin",
          html: `<div style="background: rgba(220,38,38,0.92); border: 2px solid #fca5a5; color: #fff; padding: 4px 8px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; display: flex; align-items: center; gap: 4px; box-shadow: 0 4px 14px rgba(239,68,68,0.6);">
            <span>${emoji}</span>
            <span>${ev.category}</span>
          </div>`,
          iconSize: [120, 30],
          iconAnchor: [60, 15],
        });

        const marker = L.marker([ev.lat, ev.lon], { icon: eventIcon });
        marker.bindPopup(`
          <div style="font-family: Inter, sans-serif; color: #0d1c32; padding: 4px;">
            <span style="font-size:0.75rem; font-weight:800; color:#dc2626; text-transform:uppercase;">🔥 NASA EONET LIVE EVENT</span>
            <h4 style="margin: 4px 0; font-size: 0.95rem;">${ev.title}</h4>
            <p style="margin: 0 0 6px; font-size: 0.82rem; color: #475569;">Category: ${ev.category} &bull; Date: ${ev.date}</p>
            ${ev.link ? `<a href="${ev.link}" target="_blank" style="display:inline-block; font-size:0.8rem; color:#0284c7; font-weight:700;">🔗 View Official Event Data &rarr;</a>` : ""}
          </div>
        `);
        eventsGroup.addLayer(marker);
      });

      updateStatusSource(`NASA EONET (${events.length} Events)`);
    })
    .catch((err) => {
      showLoading(false);
      console.error("Error loading natural events:", err);
    });
}

function getEventEmoji(cat) {
  const c = String(cat).toLowerCase();
  if (c.includes("wildfire") || c.includes("fire")) return "🔥";
  if (c.includes("storm") || c.includes("cyclone") || c.includes("hurricane")) return "🌀";
  if (c.includes("volcano")) return "🌋";
  if (c.includes("earthquake")) return "🫨";
  if (c.includes("flood")) return "⛈️";
  return "⚠️";
}

function getCategoryEmoji(cat) {
  if (!cat || typeof cat !== "string") return "🌍";
  if (cat.includes("Traffic")) return "🚦";
  if (cat.includes("Airport")) return "✈";
  if (cat.includes("Harbor")) return "🚢";
  if (cat.includes("Webcam") || cat.includes("Public Webcams")) return "🏖";
  return "🌍";
}

function getCategoryClass(cat) {
  if (!cat || typeof cat !== "string") return "cat-default";
  if (cat.includes("Traffic")) return "cat-traffic";
  if (cat.includes("Airport")) return "cat-airports";
  if (cat.includes("Harbor")) return "cat-harbors";
  if (cat.includes("Webcam") || cat.includes("Public Webcams")) return "cat-webcams";
  return "cat-default";
}

// Map Click Interactive Weather Card
function fetchWeatherForCoordinates(lat, lon, isUserLoc = false) {
  const modal = document.getElementById("mapWeatherModal");
  const body = document.getElementById("mwmBody");
  const cityElem = document.getElementById("mwmCity");
  const countryElem = document.getElementById("mwmCountry");

  if (cityElem) cityElem.textContent = "Fetching weather...";
  if (countryElem) countryElem.textContent = `${lat.toFixed(3)}, ${lon.toFixed(3)}`;
  if (body) {
    body.innerHTML = `<div style="text-align:center; padding: 20px;"><div class="spinner"></div><p>Retrieving atmospheric data...</p></div>`;
  }
  if (modal) modal.classList.add("active");

  fetch(`/api/live-earth/weather?lat=${lat}&lon=${lon}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success" && data.weather) {
        const w = data.weather;
        if (cityElem) cityElem.textContent = `${w.city} ${w.country_flag || ""}`;
        if (countryElem) countryElem.textContent = isUserLoc ? "📍 Your Detected Location" : `${w.country || "Global Coordinates"}`;

        if (body) {
          body.innerHTML = `
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;">
              <div>
                <span style="font-size:2.2rem; font-weight:800; color:#fff;">${w.temperature}</span>
                <p style="margin:2px 0 0; color:var(--muted); font-size:0.85rem;">Feels like ${w.feels_like} &bull; ${w.weather}</p>
              </div>
              <div style="font-size:3rem;">${w.temperature_emoji || "☀️"}</div>
            </div>

            <div class="wm-grid">
              <div class="wm-card">
                <span class="wm-card-label">Humidity</span>
                <span class="wm-card-val">${w.humidity}</span>
              </div>
              <div class="wm-card">
                <span class="wm-card-label">Wind</span>
                <span class="wm-card-val">${w.wind_speed}</span>
              </div>
              <div class="wm-card">
                <span class="wm-card-label">Barometer</span>
                <span class="wm-card-val">${w.pressure}</span>
              </div>
              <div class="wm-card">
                <span class="wm-card-label">Visibility</span>
                <span class="wm-card-val">${w.visibility}</span>
              </div>
              <div class="wm-card">
                <span class="wm-card-label">Air Quality</span>
                <span class="wm-card-val">${w.air_quality}</span>
              </div>
              <div class="wm-card">
                <span class="wm-card-label">Sun Cycle</span>
                <span class="wm-card-val">${w.sunrise} / ${w.sunset}</span>
              </div>
            </div>

            <div style="background:rgba(91,178,255,0.1); border:1px solid rgba(91,178,255,0.3); padding:10px; border-radius:10px; margin-top:10px; font-size:0.85rem;">
              <strong>👕 Outfit Recommendation:</strong> ${w.wear_advice}
            </div>
          `;
        }
      }
    })
    .catch((err) => {
      console.error("Error fetching weather card:", err);
      if (body) body.innerHTML = `<p style="color:#ef4444; text-align:center;">Unable to load weather data for these coordinates.</p>`;
    });
}

function closeMapWeatherModal() {
  const modal = document.getElementById("mapWeatherModal");
  if (modal) modal.classList.remove("active");
}

// Zoom Earth Style Radar Timeline Scrubber Player
function initRadarTimeline() {
  fetch("/api/live-earth/radar-timeline")
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success" && data.timeline && data.timeline.length > 0) {
        timelineFrames = data.timeline;
        timelineIndex = timelineFrames.length - 1;

        const range = document.getElementById("timelineRange");
        if (range) {
          range.max = timelineFrames.length - 1;
          range.value = timelineIndex;
          range.addEventListener("input", (e) => {
            timelineIndex = parseInt(e.target.value, 10);
            updateTimelineFrame();
          });
        }

        const btnPlay = document.getElementById("btnTimelinePlay");
        const btnPrev = document.getElementById("btnTimelinePrev");
        const btnNext = document.getElementById("btnTimelineNext");

        let timelineSpeedMs = 800;

        document.querySelectorAll(".speed-btn").forEach((sBtn) => {
          sBtn.addEventListener("click", (e) => {
            document.querySelectorAll(".speed-btn").forEach((b) => b.classList.remove("active"));
            e.currentTarget.classList.add("active");
            timelineSpeedMs = parseInt(e.currentTarget.getAttribute("data-speed"), 10) || 800;

            if (isTimelinePlaying) {
              clearInterval(timelineTimer);
              timelineTimer = setInterval(() => {
                timelineIndex = (timelineIndex + 1) % timelineFrames.length;
                if (range) range.value = timelineIndex;
                updateTimelineFrame();
              }, timelineSpeedMs);
            }
          });
        });

        if (btnPlay) {
          btnPlay.addEventListener("click", () => {
            isTimelinePlaying = !isTimelinePlaying;
            btnPlay.textContent = isTimelinePlaying ? "⏸" : "▶";
            if (isTimelinePlaying) {
              timelineTimer = setInterval(() => {
                timelineIndex = (timelineIndex + 1) % timelineFrames.length;
                if (range) range.value = timelineIndex;
                updateTimelineFrame();
              }, timelineSpeedMs);
            } else {
              clearInterval(timelineTimer);
              timelineTimer = null;
            }
          });
        }

        if (btnPrev) {
          btnPrev.addEventListener("click", () => {
            timelineIndex = (timelineIndex - 1 + timelineFrames.length) % timelineFrames.length;
            if (range) range.value = timelineIndex;
            updateTimelineFrame();
          });
        }

        if (btnNext) {
          btnNext.addEventListener("click", () => {
            timelineIndex = (timelineIndex + 1) % timelineFrames.length;
            if (range) range.value = timelineIndex;
            updateTimelineFrame();
          });
        }

        updateTimelineFrame();
      }
    })
    .catch((err) => console.error("Radar timeline error:", err));
}

function updateTimelineFrame() {
  if (!timelineFrames || timelineFrames.length === 0) return;
  const frame = timelineFrames[timelineIndex];
  if (!frame) return;

  const textElem = document.getElementById("timelineTimeText");
  if (textElem) textElem.textContent = `Radar: ${frame.formatted_time}`;

  if (timelineOverlayLayer) map.removeLayer(timelineOverlayLayer);

  timelineOverlayLayer = L.tileLayer(frame.tile_url, {
    opacity: 0.75,
    attribution: "Radar &copy; RainViewer",
  }).addTo(map);
}

// AI Assistant Drawer Functions
function toggleAiDrawer() {
  const drawer = document.getElementById("aiDrawer");
  if (drawer) drawer.classList.toggle("active");
}

function sendAiQuickPrompt(promptText) {
  const input = document.getElementById("aiInput");
  if (input) input.value = promptText;
  sendAiMessage();
}

function sendAiMessage() {
  const input = document.getElementById("aiInput");
  const messages = document.getElementById("aiMessages");
  if (!input || !input.value.trim() || !messages) return;

  const prompt = input.value.trim();
  input.value = "";

  const userMsg = document.createElement("div");
  userMsg.className = "ai-msg user";
  userMsg.textContent = prompt;
  messages.appendChild(userMsg);
  messages.scrollTop = messages.scrollHeight;

  const botMsg = document.createElement("div");
  botMsg.className = "ai-msg bot";
  botMsg.textContent = "Analyzing Earth observation data...";
  messages.appendChild(botMsg);
  messages.scrollTop = messages.scrollHeight;

  fetch("/api/live-earth/ai-assistant", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: prompt }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        botMsg.textContent = data.response;
      } else {
        botMsg.textContent = "Unable to process AI response at this moment.";
      }
      messages.scrollTop = messages.scrollHeight;
    })
    .catch((err) => {
      console.error("AI assistant error:", err);
      botMsg.textContent = "Network error connecting to AI assistant.";
    });
}

function bindUIEvents() {
  // Sidebar collapse toggle buttons
  document.getElementById("btnToggleSidebar")?.addEventListener("click", toggleSidebar);
  document.getElementById("btnExpandSidebarFloating")?.addEventListener("click", toggleSidebar);

  // Category menu buttons
  document.querySelectorAll(".cat-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".cat-btn").forEach((b) => b.classList.remove("active"));
      const target = e.currentTarget;
      target.classList.add("active");

      activeCategory = target.getAttribute("data-category");

      if (activeCategory === "Favorites") {
        renderFavoritesOnMap();
      } else if (activeCategory === "Live Events") {
        loadLiveEvents();
      } else {
        eventsGroup.clearLayers();
        loadCameras(activeCategory, "");
      }
    });
  });

  // Search input button with 300ms debounce
  const searchBtn = document.getElementById("leSearchBtn");
  const searchInput = document.getElementById("leSearchInput");

  if (searchBtn && searchInput) {
    searchBtn.addEventListener("click", () => handleSearch(searchInput.value));
    searchInput.addEventListener("input", (e) => {
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        if (e.target.value.length >= 3) {
          handleSearch(e.target.value);
        }
      }, 350);
    });
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") handleSearch(searchInput.value);
    });
  }

  // Toolbar action buttons
  document.getElementById("btnZoomIn")?.addEventListener("click", () => map.zoomIn());
  document.getElementById("btnZoomOut")?.addEventListener("click", () => map.zoomOut());
  document.getElementById("btnLocateMe")?.addEventListener("click", requestBrowserLocation);
  document.getElementById("btnResetView")?.addEventListener("click", () => map.setView([20.0, 0.0], 3));
  document.getElementById("btnRefresh")?.addEventListener("click", () => {
    loadCameras(activeCategory, "");
    updateStatusPanel();
  });
  document.getElementById("btnToggleFullscreen")?.addEventListener("click", toggleFullscreen);

  // Basemap inset switcher buttons
  document.querySelectorAll(".bm-option").forEach((bmBtn) => {
    bmBtn.addEventListener("click", (e) => {
      document.querySelectorAll(".bm-option").forEach((b) => b.classList.remove("active"));
      const btn = e.currentTarget;
      btn.classList.add("active");

      const bmType = btn.getAttribute("data-bm");
      if (currentBaseLayer) map.removeLayer(currentBaseLayer);

      if (bmType === "esri-satellite") {
        currentBaseLayer = L.tileLayer(ESRI_SATELLITE_URL, {
          maxZoom: 18,
          attribution: "Tiles &copy; Esri &mdash; Earthstar Geographics",
        }).addTo(map);
        updateStatusSource("Esri Satellite");
        if (satToggle) satToggle.checked = true;
      } else if (bmType === "osm-streets") {
        currentBaseLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 19,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        }).addTo(map);
        updateStatusSource("OpenStreetMap");
        if (satToggle) satToggle.checked = false;
      } else if (bmType === "opentopo") {
        currentBaseLayer = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
          maxZoom: 17,
          attribution: 'Map data &copy; OpenStreetMap, SRTM | Map style &copy; OpenTopoMap',
        }).addTo(map);
        updateStatusSource("OpenTopoMap");
        if (satToggle) satToggle.checked = false;
      } else {
        currentBaseLayer = L.tileLayer(CARTO_DARK_URL, {
          maxZoom: 19,
          subdomains: "abcd",
          attribution: '&copy; OpenStreetMap &copy; CARTO',
        }).addTo(map);
        updateStatusSource("CartoDB Dark");
        if (satToggle) satToggle.checked = false;
      }
    });
  });

  // Satellite Base map toggle
  const satToggle = document.getElementById("satelliteBasemapToggle");
  if (satToggle) {
    satToggle.addEventListener("change", (e) => {
      if (currentBaseLayer) map.removeLayer(currentBaseLayer);

      if (e.target.checked) {
        currentBaseLayer = L.tileLayer(ESRI_SATELLITE_URL, {
          maxZoom: 18,
          attribution: "Tiles &copy; Esri &mdash; Earthstar Geographics",
        }).addTo(map);
        updateStatusSource("Esri Satellite");
        document.querySelectorAll(".bm-option").forEach((b) => b.classList.remove("active"));
        document.querySelector('.bm-option[data-bm="esri-satellite"]')?.classList.add("active");
      } else {
        currentBaseLayer = L.tileLayer(CARTO_DARK_URL, {
          maxZoom: 19,
          subdomains: "abcd",
          attribution: '&copy; OpenStreetMap &copy; CARTO',
        }).addTo(map);
        updateStatusSource("CartoDB Dark");
        document.querySelectorAll(".bm-option").forEach((b) => b.classList.remove("active"));
        document.querySelector('.bm-option[data-bm="carto-dark"]')?.classList.add("active");
      }
    });
  }

  // Weather overlay radios
  document.querySelectorAll('input[name="weatherOverlay"]').forEach((radio) => {
    radio.addEventListener("change", (e) => handleWeatherOverlayChange(e.target.value));
  });

  // Earth overlay radios
  document.querySelectorAll('input[name="earthOverlay"]').forEach((radio) => {
    radio.addEventListener("change", (e) => handleEarthOverlayChange(e.target.value));
  });

  // Layer Opacity slider
  const opacityRange = document.getElementById("layerOpacityRange");
  const opacityValText = document.getElementById("opacityValDisplay");
  if (opacityRange) {
    opacityRange.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      currentLayerOpacity = val / 100.0;
      if (opacityValText) opacityValText.textContent = `${val}%`;
      if (currentOverlayLayer && typeof currentOverlayLayer.setOpacity === "function") {
        currentOverlayLayer.setOpacity(currentLayerOpacity);
      }
      if (timelineOverlayLayer && typeof timelineOverlayLayer.setOpacity === "function") {
        timelineOverlayLayer.setOpacity(currentLayerOpacity);
      }
      if (typeof currentEarthLayer !== "undefined" && currentEarthLayer && typeof currentEarthLayer.setOpacity === "function") {
        currentEarthLayer.setOpacity(currentLayerOpacity);
      }
    });
  }
}

function bindKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Ignore keypress if typing inside input boxes
    if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;

    if (e.key === "b" || e.key === "B") {
      toggleSidebar();
    } else if (e.key === "f" || e.key === "F") {
      toggleFullscreen();
    } else if (e.key === "h" || e.key === "H") {
      if (map) map.setView([20.0, 0.0], 3);
    } else if (e.key === "+" || e.key === "=") {
      if (map) map.zoomIn();
    } else if (e.key === "-") {
      if (map) map.zoomOut();
    }
  });
}

function handleSearch(query) {
  if (!query || !query.trim()) return;

  showLoading(true, `Searching locations for "${query.trim()}"...`);
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

        if (cameras[0]) {
          openCameraModalById(cameras[0].id);
        }
      } else {
        renderNoCameraMessage(query);
      }
    })
    .catch((err) => {
      showLoading(false);
      console.error("Search error:", err);
    });
}

function handleWeatherOverlayChange(layerId) {
  if (currentOverlayLayer) map.removeLayer(currentOverlayLayer);

  if (layerId === "none") {
    updateStatusSource("Public Camera Network");
    return;
  }

  showLoading(true, "Loading weather layers...");
  fetch("/api/live-earth/satellites")
    .then((res) => res.json())
    .then((data) => {
      showLoading(false);
      console.log("SATELLITE DATA:", data);
      const layers = data.layers || [];
      const selected = layers.find((l) => l.id === layerId);
      if (selected && selected.url_template) {
        currentOverlayLayer = L.tileLayer(selected.url_template, {
          opacity: currentLayerOpacity,
          attribution: selected.attribution,
        }).addTo(map);
        console.log("SATELLITE LAYER ADDED");
        updateStatusSource(selected.name);
      } else {
        alert("This layer requires an API key in your .env configuration.");
      }
    })
    .catch((err) => {
      showLoading(false);
      console.error("Satellite overlay error:", err);
    });
}

function handleEarthOverlayChange(layerId) {
  if (currentOverlayLayer) map.removeLayer(currentOverlayLayer);

  if (layerId === "none") {
    updateStatusSource("Public Camera Network");
    return;
  }

  showLoading(true, "Loading satellite imagery...");
  fetch("/api/live-earth/earth-imagery")
    .then((res) => res.json())
    .then((data) => {
      showLoading(false);
      console.log("SATELLITE DATA:", data);
      const layers = data.layers || [];
      const selected = layers.find((l) => l.id === layerId);
      if (selected && selected.url_template) {
        currentOverlayLayer = L.tileLayer(selected.url_template, {
          opacity: selected.opacity || 0.85,
          attribution: selected.attribution,
        }).addTo(map);
        console.log("SATELLITE LAYER ADDED");
        updateStatusSource(selected.name);
      }
    })
    .catch((err) => {
      showLoading(false);
      console.error("Earth imagery overlay error:", err);
    });
}

function openCameraModalById(camId) {
  const cam = currentCameras.find((c) => c.id === camId) ||
              allCamerasList.find((c) => c.id === camId) ||
              getFavorites().find((f) => f.id === camId);
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
  }, 5000);

  modal?.classList.add("active");
}

function closeCameraModal() {
  const modal = document.getElementById("cameraModal");
  const iframe = document.getElementById("camIframe");
  const imgElem = document.getElementById("camImg");
  const noMsg = document.getElementById("noCamMsg");
  if (iframe) iframe.src = "";
  if (imgElem) imgElem.src = "";
  if (noMsg) noMsg.style.display = "none";
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
  }
  modal?.classList.remove("active");
}

function showLoading(show, message = "Loading Live Earth Platform...") {
  const overlay = document.getElementById("mapLoading");
  const textElem = document.getElementById("mapLoadingText");
  if (overlay) {
    overlay.classList.toggle("active", show);
    if (textElem && message) textElem.textContent = message;
  }
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

function updateStatusPanel() {
  fetch("/api/live-earth/status")
    .then((res) => res.json())
    .then((data) => {
      const connElem = document.getElementById("statusConn");
      if (connElem) connElem.textContent = data.connection_status || "Synced";
    });
}

function updateStatusSource(sourceName) {
  const elem = document.getElementById("statusSource");
  if (elem) elem.textContent = sourceName;
}

function updateStatusCamCount(count) {
  const elem = document.getElementById("statusCamCount");
  if (elem) elem.textContent = `${count} Cameras`;
}

function requestBrowserLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;

      if (userMarker) {
        map.removeLayer(userMarker);
      }

      const pulseIcon = L.divIcon({
        className: "user-location-marker",
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });

      userMarker = L.marker([lat, lon], { icon: pulseIcon }).addTo(map);
      userMarker.bindPopup("<b>📍 Your Current Location</b>").openPopup();

      map.flyTo([lat, lon], 12, { animate: true, duration: 1.5 });

      fetch(`/api/live-earth/cameras?lat=${lat}&lon=${lon}&radius=100`)
        .then((res) => res.json())
        .then((data) => {
          if (data.status === "success" && data.cameras) {
            currentCameras = data.cameras;
            renderCameraMarkers(currentCameras);
            updateStatusCamCount(data.cameras.length);
          }
        })
        .catch((err) => console.warn("Failed to load nearby webcams:", err));
    },
    (error) => {
      console.warn("Geolocation permission error:", error.message);
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
  );
}
