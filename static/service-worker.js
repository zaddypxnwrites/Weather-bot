const CACHE_NAME = 'cozy-weather-bot-v5';
const URLS_TO_CACHE = [
  '/',
  '/static/manifest.webmanifest',
  '/static/icon.svg',
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => caches.delete(key))
      ),
    ),
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  // Ignore non-http/https requests (e.g. chrome-extension://)
  if (!event.request.url.startsWith('http://') && !event.request.url.startsWith('https://')) {
    return;
  }

  const requestUrl = new URL(event.request.url);

  // Never cache API endpoints or JS/CSS static bundles
  if (requestUrl.pathname.startsWith('/api/') || requestUrl.pathname.startsWith('/static/js/') || requestUrl.pathname.startsWith('/static/css/')) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }

  // Network-First strategy for all other GET requests
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
        }
        return networkResponse;
      })
      .catch(() => caches.match(event.request))
  );
});