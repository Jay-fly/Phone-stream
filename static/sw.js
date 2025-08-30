const CACHE_NAME = 'vision-live-core-v1';
const CORE_ASSETS = [
  './manifest.webmanifest',
  './assets/apple-icon-180.png',
  './assets/manifest-icon-192.maskable.png',
  './assets/manifest-icon-512.maskable.png'
];

// 安裝：快取核心檔案
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

// 啟用：清掉舊快取
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// 取得：先網路，失敗才回快取
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});