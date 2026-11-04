# Génère map-style.json et map-style-dark.json façon Google Maps
# à partir du style « Liberty » d'OpenFreeMap (tuiles gratuites, sans clé) :
#   git clone https://github.com/hyperknot/openfreemap-styles
#   python3 tools/googlestyle.py openfreemap-styles/styles/liberty/style.json
import json, sys, copy

PALETTES = {
  "map-style.json": dict(
    land="#f2f3f5", resid="#eceef1", park="#c3ecb2", wood="#b5e3a3", grass="#c8eebb", pitch="#d3efc6",
    cemetery="#d6ebcd", hospital="#fce8e6", school="#eef0f4", sand="#f6edd3", ice="#eef5f7",
    water="#90daee", water_label="#2f86b0", aero="#e9eaee",
    building="#e5e6ea", building_line="#d9dadf",
    minor="#ffffff", minor_casing="#dadce0", major="#ffffff", major_casing="#d2d5da",
    trunk="#fff1b8", trunk_casing="#efcb62", motor="#fcd56b", motor_casing="#e4ae3c",
    path="#ffffff", rail="#c4c8cd",
    label="#3c4043", label_halo="#ffffff", road_label="#5f6368", poi_label="#5f6368", transit="#1a73e8",
    boundary="#9aa0a6"),
  "map-style-dark.json": dict(
    land="#1f2022", resid="#232427", park="#1d3427", wood="#1f3a29", grass="#1d3427", pitch="#20392a",
    cemetery="#1f3528", hospital="#3a2a2c", school="#26282c", sand="#2f2c25", ice="#2a2f33",
    water="#14324a", water_label="#7fb4d6", aero="#2a2c30",
    building="#2b2d31", building_line="#33363a",
    minor="#3a3d42", minor_casing="#2a2c30", major="#474a50", major_casing="#2e3034",
    trunk="#5c5546", trunk_casing="#3f3a30", motor="#7a6a43", motor_casing="#4f4530",
    path="#3a3d42", rail="#4a4d52",
    label="#e8eaed", label_halo="#1f2022", road_label="#b0b4b9", poi_label="#a8adb3", transit="#8ab4f8",
    boundary="#6b7075"),
}
DROP_SOURCE_LAYERS = set()
DROP_IDS = {"natural_earth", "building-3d", "poi_r7", "poi_r20", "poi_r1", "poi_transit", "airport", "road_one_way_arrow", "road_one_way_arrow_opposite", "highway-shield-non-us", "highway-shield-us-interstate", "road_shield_us", "boundary_disputed", "road_area_pattern"}

def recolor(src, P):
    s = copy.deepcopy(src)
    s = json.loads(json.dumps(s).replace("__TILEJSON_DOMAIN__", "tiles.openfreemap.org"))
    s["name"] = "Carto – façon Google Maps"
    s["sources"].pop("ne2_shaded", None)
    out = []
    for l in s["layers"]:
        i, t = l["id"], l["type"]
        if i in DROP_IDS: continue
        p = l.setdefault("paint", {})
        def setc(k, v):
            p[k] = v
        if t == "background": setc("background-color", P["land"])
        elif i == "park": setc("fill-color", P["park"]); p.pop("fill-outline-color", None)
        elif i == "park_outline": setc("line-color", P["park"]); p["line-opacity"] = 0
        elif i == "landuse_residential": setc("fill-color", P["resid"])
        elif i == "landcover_wood": setc("fill-color", P["wood"])
        elif i == "landcover_grass": setc("fill-color", P["grass"])
        elif i == "landcover_ice": setc("fill-color", P["ice"])
        elif i in ("landuse_pitch", "landuse_track"): setc("fill-color", P["pitch"])
        elif i == "landuse_cemetery": setc("fill-color", P["cemetery"])
        elif i == "landuse_hospital": setc("fill-color", P["hospital"])
        elif i == "landuse_school": setc("fill-color", P["school"])
        elif i == "landcover_sand": setc("fill-color", P["sand"])
        elif i.startswith("waterway") and t == "line": setc("line-color", P["water"])
        elif i == "water": setc("fill-color", P["water"])
        elif i.startswith("aeroway"): setc("fill-color" if t == "fill" else "line-color", P["aero"])
        elif i == "building": setc("fill-color", P["building"]); setc("fill-outline-color", P["building_line"])
        elif l.get("source-layer") == "transportation" and t == "line":
            casing = "casing" in i
            if "rail" in i: setc("line-color", P["rail"])
            elif "motorway" in i: setc("line-color", P["motor_casing"] if casing else P["motor"])
            elif "trunk_primary" in i: setc("line-color", P["trunk_casing"] if casing else P["trunk"])
            elif "secondary_tertiary" in i or "link" in i: setc("line-color", P["major_casing"] if casing else P["major"])
            elif "path" in i or "pedestrian" in i: setc("line-color", P["minor_casing"] if casing else P["path"])
            else: setc("line-color", P["minor_casing"] if casing else P["minor"])
        elif i.startswith("boundary"): setc("line-color", P["boundary"])
        elif t == "symbol":
            sl = l.get("source-layer")
            if sl in ("water_name", "waterway"): col, halo = P["water_label"], P["water"]
            elif sl == "transportation_name": col, halo = P["road_label"], P["minor"]
            elif i == "poi_transit": col, halo = P["transit"], P["label_halo"]
            elif sl == "poi" or sl == "aerodrome_label": col, halo = P["poi_label"], P["label_halo"]
            else: col, halo = P["label"], P["label_halo"]
            if "text-field" in l.get("layout", {}):
                setc("text-color", col); setc("text-halo-color", halo); p["text-halo-width"] = 1.4; p.pop("text-halo-blur", None)
        # police Open Sans (servie depuis le dossier fonts/ du site) à la place de Noto Sans
        tf = l.get("layout", {}).get("text-font")
        if tf:
            m = {"Noto Sans Regular":"Open Sans Regular", "Noto Sans Bold":"Open Sans Semibold", "Noto Sans Italic":"Open Sans Italic"}
            l["layout"]["text-font"] = [m.get(f, "Open Sans Regular") for f in tf] if isinstance(tf, list) else tf
        out.append(l)
    s["layers"] = out
    s["glyphs"] = "fonts/{fontstack}/{range}.pbf"   # rendue absolue au chargement par l'app
    return s

if __name__ == "__main__":
    src = json.load(open(sys.argv[1]))
    for name, P in PALETTES.items():
        st = recolor(src, P)
        json.dump(st, open(name, "w"), ensure_ascii=False, separators=(",", ":"))
        print(name, len(st["layers"]), "couches")
