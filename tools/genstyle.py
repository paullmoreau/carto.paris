# Génère map-style.json (style « Carto ») à partir du style Positron d'OpenFreeMap :
#   git clone https://github.com/hyperknot/openfreemap-styles
#   python3 tools/genstyle.py openfreemap-styles/styles/positron/style.json map-style.json
# Les couleurs se règlent dans PALETTES ci-dessous (3e argument : bump, clair ou sombre ; bump par défaut).
import json, sys, copy
src, out = sys.argv[1], sys.argv[2]
s = json.load(open(src))
txt = json.dumps(s).replace("__TILEJSON_DOMAIN__", "tiles.openfreemap.org")
s = json.loads(txt)
s["name"] = "Carto"
s["sources"].pop("ne2_shaded", None)
PALETTES = {
 "clair": dict(
  land="#f5f3ee", park="#dbead3", wood="#d4e6cb", water="#c6dee8", resid="#eeebe4",
  building="#e8e4db", building_line="#ddd7cc", path="#e0dace", road="#ffffff", casing="#e3ded3",
  motor="#fbf1dc", motor_casing="#ead9b8", rail="#d5d0c4", aero="#ebe8e1",
  label="#3f4843", label_halo="#f5f3ee", street="#737a74", water_label="#4f8aa1", boundary="#c8c2d4"),
 # Façon Bump / Snap Map : sol gris très clair, rues blanches, parcs vert vif, eau bleu ciel
 "bump": dict(
  land="#eef1ee", park="#c3ebb5", wood="#b5e3a6", water="#9fd6f5", resid="#eaedea",
  building="#e1e4e1", building_line="#d6dad6", path="#dde1dd", road="#ffffff", casing="#dde1dc",
  motor="#fff1b8", motor_casing="#f1dc8a", rail="#d2d6d2", aero="#e6e9e6",
  label="#4b5057", label_halo="#ffffff", street="#8a9097", water_label="#2f87c0", boundary="#c9c9d6"),
 # Nuit façon Plans d'Apple : gris anthracite, parcs vert profond, eau bleu nuit
 "nuit": dict(
  land="#1d1f21", park="#1f3326", wood="#203828", water="#0e2a3f", resid="#202224",
  building="#26292c", building_line="#2e3135", path="#34383c", road="#3a3e43", casing="#25282b",
  motor="#5c5340", motor_casing="#3a3427", rail="#3b3f44", aero="#25282b",
  label="#d9dce0", label_halo="#1d1f21", street="#a1a7ad", water_label="#6fa3c4", boundary="#5b6068"),
 # Sombre « chrome » : asphalte presque noir, rues gris acier, grands axes teintés de jaune
 "sombre": dict(
  land="#121417", park="#16201a", wood="#17221b", water="#0b1620", resid="#15171a",
  building="#1c1f23", building_line="#24282d", path="#262a2f", road="#2c3137", casing="#16191c",
  motor="#5a4a10", motor_casing="#2a230a", rail="#30353b", aero="#1a1d21",
  label="#d5d9dd", label_halo="#121417", street="#8f959c", water_label="#6d93ab", boundary="#5b6068"),
}
P = PALETTES[sys.argv[3] if len(sys.argv) > 3 else "bump"]
drop = {"highway-shield-non-us","highway-shield-us-interstate","road_shield_us","boundary_disputed"}
layers = []
for l in s["layers"]:
    i, t, p = l["id"], l["type"], l.setdefault("paint", {})
    if i in drop: continue
    if t == "background": p["background-color"] = P["land"]
    elif i == "park": p["fill-color"] = P["park"]; p["fill-opacity"] = 1
    elif i == "landcover_wood": p["fill-color"] = P["wood"]; p["fill-opacity"] = .8
    elif i == "water": p["fill-color"] = P["water"]
    elif i == "waterway": p["line-color"] = P["water"]
    elif i == "landuse_residential": p["fill-color"] = P["resid"]; p["fill-opacity"] = .6
    elif i == "building": p["fill-color"] = P["building"]; p["fill-outline-color"] = P["building_line"]
    elif i.startswith("aeroway"): 
        k = "fill-color" if t == "fill" else "line-color"; p[k] = P["aero"]
    elif i in ("road_area_pier","road_pier"):
        p["fill-color" if t == "fill" else "line-color"] = P["land"]
    elif i == "highway_path": p["line-color"] = P["path"]; p["line-opacity"] = 1
    elif i.startswith("highway_motorway") or i.startswith("tunnel_motorway"):
        p["line-color"] = P["motor_casing"] if "casing" in i else P["motor"]
    elif i.startswith("highway_"):
        p["line-color"] = P["casing"] if "casing" in i else P["road"]
        if i == "highway_minor": p["line-opacity"] = 1
    elif i.startswith("railway"): p["line-color"] = P["rail"]
    elif i.startswith("boundary"): p["line-color"] = P["boundary"]; p["line-opacity"] = .35
    elif t == "symbol":
        sl = l.get("source-layer")
        if sl in ("water_name","waterway"): col, halo = P["water_label"], P["water"]
        elif sl == "transportation_name": col, halo = P["street"], P["road"]
        else: col, halo = P["label"], P["label_halo"]
        p["text-color"] = col; p["text-halo-color"] = halo; p["text-halo-width"] = 1.5; p.pop("text-halo-blur", None)
    layers.append(l)
s["layers"] = layers
json.dump(s, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
print("layers", len(layers), "bytes", len(json.dumps(s)))
