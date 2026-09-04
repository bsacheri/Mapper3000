// Service Worker for Mapper3000 PWA
const CACHE_NAME = 'mapper3000-v1';
const urlsToCache = [
  './',
  './garage-sale-map.html',
  './manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js',
  'https://cdnjs.cloudflare.com/ajax/libs/marked/11.1.1/marked.min.js'
];

// Install event - cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        // Cache main file
          return cache.add('./garage-sale-map.html').catch(err => {
          console.log('Could not cache garage-sale-map.html:', err);
        });
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event
// The app HTML/CHANGELOG are edited constantly during development, so they
// go network-first (always get the latest, cache is only a fallback for
// offline use). Third-party CDN libs rarely change, so they stay cache-first
// to save a round trip.
const NETWORK_FIRST_PATTERNS = ['garage-sale-map.html', 'CHANGELOG.md', 'manifest.json'];

self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  const isNetworkFirst = NETWORK_FIRST_PATTERNS.some(p => event.request.url.includes(p))
    || event.request.mode === 'navigate';

  if (isNetworkFirst) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200 && response.type === 'basic') {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseToCache));
          }
          return response;
        })
        .catch(() => caches.match(event.request).then(cached => cached || new Response('Offline - please check your connection', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({ 'Content-Type': 'text/plain' })
        })))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }

        return fetch(event.request).then(response => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseToCache));

          return response;
        });
      })
      .catch(() => new Response('Offline - please check your connection', {
        status: 503,
        statusText: 'Service Unavailable',
        headers: new Headers({ 'Content-Type': 'text/plain' })
      }))
  );
});
