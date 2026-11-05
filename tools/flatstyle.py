# Style « flat » de Carto : aplats de couleurs vives, sans contours ni détails.
# S'applique sur les styles générés par tools/googlestyle.py (idempotent) :
#   python3 tools/flatstyle.py
import json

PALETTES = {
  "map-style.json": dict(
    land="#efede6", park="#a6e38f", wood="#95da80", water="#5ec2f7", water_label="#0a7cc4",
    building="#e6e4dc", street="#ffffff", major="#ffffff", trunk="#ffffff", motor="#ffffff",
    label="#22252b", halo="#ffffff", road_label="#4a4f57", outside="#2a2d34"),
  "map-style-dark.json": dict(
    land="#16181d", park="#1f6b42", wood="#1d6640", water="#1565a8", water_label="#8fd0ff",
    building="#1d2026", street="#2b2f37", major="#353a44", trunk="#353a44", motor="#353a44",
    label="#f2f4f7", halo="#16181d", road_label="#b9bec7", outside="#0b0c0f"),
}
# couches retirées : contours de routes (aspect plat), motifs, bordures et détails inutiles
DROP = ("_casing", "park_outline", "landcover_wetland", "landcover_sand", "landcover_ice",
        "waterway_tunnel", "landuse_hospital", "landuse_school", "landuse_track", "label_country", "label_town", "label_city", "outside-paris")

def flat(s, P):
    out = []
    for l in s["layers"]:
        i, t = l["id"], l["type"]
        if any(d in i for d in DROP): continue
        p = l.setdefault("paint", {})
        if t == "background": p["background-color"] = P["land"]
        elif i == "landuse_residential": p["fill-color"] = P["land"]
        elif i in ("park", "landcover_grass", "landuse_pitch", "landuse_cemetery"):
            p["fill-color"] = P["park"]; p["fill-opacity"] = 1; p.pop("fill-outline-color", None)
        elif i == "landcover_wood": p["fill-color"] = P["wood"]; p["fill-opacity"] = 1
        elif i == "water": p["fill-color"] = P["water"]
        elif i.startswith("waterway"): p["line-color"] = P["water"]
        elif i == "building":
            # bâtiments en aplat très léger, seulement de près, sans contour
            l["minzoom"] = 15.5; p["fill-color"] = P["building"]; p.pop("fill-outline-color", None)
            p["fill-opacity"] = ["interpolate", ["linear"], ["zoom"], 15.5, 0, 16.5, 1]
        elif t == "line" and l.get("source-layer") == "transportation":
            if "motorway" in i: p["line-color"] = P["motor"]
            elif "trunk_primary" in i: p["line-color"] = P["trunk"]
            elif "secondary_tertiary" in i or "link" in i: p["line-color"] = P["major"]
            else: p["line-color"] = P["street"]
        elif t == "symbol" and "text-field" in l.get("layout", {}):
            sl = l.get("source-layer")
            if sl in ("water_name", "waterway"): p["text-color"], p["text-halo-color"] = P["water_label"], P["water"]
            elif sl == "transportation_name": p["text-color"], p["text-halo-color"] = P["road_label"], P["halo"]
            else: p["text-color"], p["text-halo-color"] = P["label"], P["halo"]
            p["text-halo-width"] = 1.6
        out.append(l)
    # zones résidentielles juste après le fond, pour ne jamais recouvrir les parcs
    out.sort(key=lambda l: 0 if l["id"] == "background" else 1 if l["id"] == "landuse_residential" else 2)
    # Hors de Paris : un aplat sombre uni, sans noms ni textures,
    # et aucune tuile chargée au-delà du rectangle de Paris
    ring = json.load(open("tools/paris.geojson"))["geometry"]["coordinates"][0]
    s["sources"]["paris-mask"] = {"type": "geojson", "data": {"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [[[-180, -85], [180, -85], [180, 85], [-180, 85], [-180, -85]], ring[::-1]]}}}
    s["sources"]["openmaptiles"]["bounds"] = [2.215, 48.81, 2.48, 48.908]
    out.append({"id": "outside-paris", "type": "fill", "source": "paris-mask", "paint": {"fill-color": P["outside"], "fill-antialias": False}})
    s["layers"] = out
    s["name"] = "Carto – flat"
    return s

if __name__ == "__main__":
    for name, P in PALETTES.items():
        st = flat(json.load(open(name)), P)
        json.dump(st, open(name, "w"), ensure_ascii=False, separators=(",", ":"))
        print(name, len(st["layers"]), "couches")
