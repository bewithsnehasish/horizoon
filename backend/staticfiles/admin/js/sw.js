// static/admin/js/sw.js
const CACHE_NAME = 'django-admin-prefetch-v1';
const PREFETCH_TIMEOUT = 3000; // 3 seconds

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME));
});

self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request);
      })
    );
  }
});

// Prefetch and cache URLs
self.addEventListener('message', (event) => {
  if (event.data.type === 'PREFETCH_ADMIN_URL') {
    const url = event.data.url;
    fetch(url, {
      credentials: 'include',
      headers: {
        'X-Prefetch': 'true'
      }
    })
      .then(response => {
        if (response.ok) {
          const clonedResponse = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(url, clonedResponse));
        }
      })
      .catch(() => {});
  }
});