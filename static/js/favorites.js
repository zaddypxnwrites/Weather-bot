/* LocalStorage Manager for Live Earth Favorites */

const FAV_KEY = "cozy_live_earth_favorites";

function getFavorites() {
  try {
    const raw = localStorage.getItem(FAV_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveFavorites(favs) {
  try {
    localStorage.setItem(FAV_KEY, JSON.stringify(favs));
    updateFavBadge();
  } catch (e) {
    console.error("Failed to save favorites", e);
  }
}

function isFavorite(camId) {
  const favs = getFavorites();
  return favs.some((f) => f.id === camId);
}

function toggleFavorite(camera) {
  let favs = getFavorites();
  const index = favs.findIndex((f) => f.id === camera.id);

  if (index >= 0) {
    favs.splice(index, 1);
  } else {
    favs.push(camera);
  }

  saveFavorites(favs);
  return isFavorite(camera.id);
}

function updateFavBadge() {
  const badge = document.getElementById("favCount");
  if (badge) {
    const count = getFavorites().length;
    badge.textContent = count;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  updateFavBadge();
});
