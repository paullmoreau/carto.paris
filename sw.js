// Carto : ouverture hors ligne et installation comme une app
const VERSION = "carto-v6";
const SHELL = ["./", "index.html", "config.js", "places.json", "events.json", "map-style.json", "map-style-dark.json",
  "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "favicon-32.png", "logo-336.jpg"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== "GET") return;
  // fichiers de l'app : réseau d'abord (toujours à jour), cache si hors ligne
  if (url.origin === location.origin && url.pathname.endsWith("version.txt")) return; // toujours le réseau
  if (url.origin === location.origin){
    e.respondWith(fetch(req, {cache:"no-cache"}).then(r => { if (r.ok){ const cp = r.clone(); caches.open(VERSION).then(c => c.put(req, cp)); } return r; })
      .catch(() => caches.match(req).then(r => r || caches.match("index.html"))));
    return;
  }
  // bibliothèques et polices : cache d'abord
  if (/^(cdnjs\.cloudflare\.com|unpkg\.com|fonts\.(googleapis|gstatic)\.com)$/.test(url.hostname) ||
      (url.hostname === "tiles.openfreemap.org" && /\/(fonts|sprites)\//.test(url.pathname))){
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { if (r.ok || r.type === "opaque"){ const cp = r.clone(); caches.open(VERSION).then(c => c.put(req, cp)); } return r; })));
  }
  // le reste (tuiles de carte, OpenStreetMap, Supabase) passe directement par le réseau
});
