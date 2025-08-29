const CACHE_NAME = 'livekit-mobile-v1';
const CORE_ASSETS = [
  '/',                      // 視你的首頁路徑調整
  '/manifest.webmanifest',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/apple-touch-icon-180.png',
  '/static/icons/apple-touch-icon-167.png',
  '/static/icons/apple-touch-icon-152.png',
  '/static/icons/apple-touch-icon-120.png',
];

// 安裝：逐一快取（避免任一失敗導致整批失敗）
self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    for (const url of CORE_ASSETS) {
      try { await cache.add(url); } catch (e) { /* 忽略單檔失敗 */ }
    }
  })());
});

// 啟用：清舊版快取
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)));
  })());
});

// 取得：快取優先，其餘網路
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // 跳過非 GET、API、LiveKit 動態串流
  const url = new URL(req.url);
  if (req.method !== 'GET' ||
    url.pathname.startsWith('/api/') ||
    url.hostname.endsWith('livekit.cloud')) {
    return; // 交給瀏覽器
  }

  event.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    try {
      const resp = await fetch(req);
      return resp;
    } catch (e) {
      // 導航請求回離線頁（存在才回）
      if (req.mode === 'navigate') {
        const offline = await caches.match('/index.html');
        if (offline) return offline;
      }
      throw e;
    }
  })());
});

// 可保留的佔位事件（未接註冊邏輯前不會觸發）
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    // TODO: 背景同步
  }
});

self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : '您有新的直播通知',
    icon: '/static/icons/icon-192.png',   // 修正路徑：icons/
    badge: '/static/icons/badge-72.png',  // 請確認檔案存在；否則移除此欄
    vibrate: [100, 50, 100]
  };
  event.waitUntil(self.registration.showNotification('LiveKit 直播', options));
});