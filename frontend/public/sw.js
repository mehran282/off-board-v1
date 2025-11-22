// Service Worker for off-board PWA
const CACHE_NAME = 'off-board-v1';
const urlsToCache = [
  '/',
  '/en',
  '/de',
  '/icon.svg',
  '/icon-192.png',
  '/icon-512.png',
  '/manifest.json',
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - Network First strategy (always fetch from network, fallback to cache)
self.addEventListener('fetch', (event) => {
  // Skip caching for API routes and Next.js internal routes
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/_next/') ||
      event.request.url.includes('/_vercel/')) {
    return; // Let browser handle these requests normally
  }

  // For HTML pages, always fetch from network (no caching)
  if (event.request.destination === 'document' || 
      event.request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Always return fresh content for HTML pages - don't cache
          return response;
        })
        .catch(() => {
          // Only use cache if network fails completely (offline mode)
          return caches.match(event.request).then((cachedResponse) => {
            return cachedResponse || caches.match('/');
          });
        })
    );
    return;
  }

  // For static assets (images, icons, etc.), use cache-first strategy
  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          // Return cached version, but also update in background
          fetch(event.request).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, responseToCache);
              });
            }
          }).catch(() => {
            // Network failed, keep using cache
          });
          return cachedResponse;
        }

        // Not in cache, fetch from network
        return fetch(event.request).then((response) => {
          // Only cache successful GET responses for static assets
          if (event.request.method === 'GET' && 
              response && 
              response.status === 200 &&
              (event.request.destination === 'image' || 
               event.request.destination === 'font' ||
               event.request.url.includes('/icon') ||
               event.request.url.includes('/manifest.json'))) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return response;
        });
      })
      .catch(() => {
        // If both cache and network fail, return offline page if available
        if (event.request.destination === 'document') {
          return caches.match('/');
        }
      })
  );
});

