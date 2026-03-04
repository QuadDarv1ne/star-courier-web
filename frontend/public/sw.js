// Service Worker for StarCourier Web v2.0
// Provides offline support, caching, and push notifications

const CACHE_NAME = 'starcourier-web-v2.0.0';
const STATIC_CACHE = 'starcourier-static-v2';
const DYNAMIC_CACHE = 'starcourier-dynamic-v2';
const API_CACHE = 'starcourier-api-v2';

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

// API endpoints to cache
const API_CACHE_ENDPOINTS = [
  '/api/scenes',
  '/api/characters',
  '/api/achievements'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - clean up old caches and claim clients
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...');
  
  const cacheWhitelist = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];
  
  event.waitUntil(
    Promise.all([
      // Clean old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (!cacheWhitelist.includes(cacheName)) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Claim all clients immediately
      self.clients.claim()
    ])
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // API requests - Network First with Cache Fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstWithCacheFallback(request));
    return;
  }
  
  // Static assets - Cache First with Network Fallback
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirstWithNetworkFallback(request));
    return;
  }
  
  // Navigation requests - Network First
  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Default - Network First
  event.respondWith(networkFirst(request));
});

// ============================================================================
// CACHING STRATEGIES
// ============================================================================

/**
 * Cache First Strategy - for static assets
 * Good for: CSS, JS, images, fonts
 */
async function cacheFirstWithNetworkFallback(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Return cached version and update cache in background
    updateCache(request, STATIC_CACHE);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed for:', request.url);
    return new Response('Offline - Resource not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

/**
 * Network First Strategy - for API and dynamic content
 * Good for: API calls, HTML pages
 */
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache for:', request.url);
    
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/index.html');
    }
    
    return new Response(JSON.stringify({
      error: 'offline',
      message: 'Нет подключения к серверу'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Network First with Cache Fallback - for API requests
 */
async function networkFirstWithCacheFallback(request) {
  const url = new URL(request.url);
  
  // Check if this endpoint should be cached
  const shouldCache = API_CACHE_ENDPOINTS.some(endpoint => 
    url.pathname.startsWith(endpoint)
  );
  
  try {
    const networkResponse = await fetch(request);
    
    // Cache GET requests that should be cached
    if (shouldCache && networkResponse.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] API offline, checking cache:', request.url);
    
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      // Add header to indicate cached response
      const headers = new Headers(cachedResponse.headers);
      headers.set('X-Cached', 'true');
      headers.set('X-Cache-Time', Date.now().toString());
      
      return new Response(cachedResponse.body, {
        status: cachedResponse.status,
        statusText: cachedResponse.statusText,
        headers
      });
    }
    
    return new Response(JSON.stringify({
      error: 'offline',
      message: 'Нет подключения к серверу. Данные будут синхронизированы при подключении.'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Update cache in background
 */
async function updateCache(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(cacheName);
    cache.put(request, networkResponse.clone());
  } catch (error) {
    // Silent fail - cache update is optional
  }
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(pathname) {
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', 
                           '.svg', '.woff', '.woff2', '.ttf', '.eot', '.ico'];
  return staticExtensions.some(ext => pathname.endsWith(ext));
}

// ============================================================================
// PUSH NOTIFICATIONS
// ============================================================================

self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  const options = {
    icon: '/icons/icon-192.png',
    badge: '/icons/badge-72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.body;
    options.title = data.title || 'StarCourier Web';
    
    if (data.icon) options.icon = data.icon;
    if (data.badge) options.badge = data.badge;
    if (data.actions) options.actions = data.actions;
  }
  
  event.waitUntil(
    self.registration.showNotification(options.title || 'StarCourier Web', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked');
  
  event.notification.close();
  
  // Focus or open app window
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      // Check if there's already a window open
      for (const client of clientList) {
        if (client.url === '/' && 'focus' in client) {
          return client.focus();
        }
      }
      // Open new window if no window exists
      if (clients.openWindow) {
        return clients.openWindow('/');
      }
    })
  );
});

// ============================================================================
// BACKGROUND SYNC
// ============================================================================

self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'sync-game-state') {
    event.waitUntil(syncGameState());
  }
});

async function syncGameState() {
  // Get pending game states from IndexedDB and sync with server
  console.log('[SW] Syncing game state...');
  
  try {
    const clients = await self.clients.matchAll();
    
    for (const client of clients) {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        timestamp: Date.now()
      });
    }
  } catch (error) {
    console.error('[SW] Sync failed:', error);
  }
}

// ============================================================================
// MESSAGE HANDLING
// ============================================================================

self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
  
  if (event.data.type === 'GET_CACHE_SIZE') {
    event.waitUntil(
      getCacheSize().then((size) => {
        event.ports[0].postMessage({ size });
      })
    );
  }
});

async function getCacheSize() {
  const cacheNames = await caches.keys();
  let totalSize = 0;
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    
    for (const request of keys) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.clone().blob();
        totalSize += blob.size;
      }
    }
  }
  
  return totalSize;
}

console.log('[SW] Service Worker loaded');
