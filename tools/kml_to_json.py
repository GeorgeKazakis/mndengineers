"""Convert the Google My Maps export into the compact JSON used by the work map.

Usage:
    python3 tools/kml_to_json.py            # downloads the live map
    python3 tools/kml_to_json.py map.kml    # or converts a local KML file

Output (assets/data/projects.json):
    categories: [{name, count, color}]       one per My Maps layer, colour taken from its point icons
    styles:     [{color, fill}]              polygon outline colour + fill opacity (0-1)
    points:     [[lat, lng, cat], ...]
    polygons:   [[cat, style, [lat, lng, lat, lng, ...]], ...]   parcel outlines (outer ring only)
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

MAP_ID = "1qmLJsp2BFmF42RjINLkJpctVU_zZthLZ"
KML_URL = f"https://www.google.com/maps/d/kml?mid={MAP_ID}&forcekml=1"
OUT = Path(__file__).resolve().parent.parent / "assets" / "data" / "projects.json"
NS = {"k": "http://www.opengis.net/kml/2.2"}


def load(src):
    if src:
        return Path(src).read_bytes()
    with urllib.request.urlopen(KML_URL, timeout=30) as r:
        return r.read()


def kml_color(abgr):
    """KML 'aabbggrr' -> ('#rrggbb', alpha 0-1)."""
    abgr = abgr.strip().lower()
    return f"#{abgr[6:8]}{abgr[4:6]}{abgr[2:4]}", round(int(abgr[0:2], 16) / 255, 2)


def resolve_styles(root):
    """Map '#styleMapId' -> the <Style> element used in its 'normal' state."""
    styles = {s.get("id"): s for s in root.iterfind(".//k:Style", NS)}
    resolved = {}
    for sm in root.iterfind(".//k:StyleMap", NS):
        for pair in sm.iterfind("k:Pair", NS):
            if pair.findtext("k:key", "", NS) == "normal":
                target = pair.findtext("k:styleUrl", "", NS).lstrip("#")
                resolved["#" + sm.get("id")] = styles.get(target)
    resolved.update({"#" + k: v for k, v in styles.items()})
    return resolved


def coords(text, nd):
    out = []
    for tok in text.split():
        lng, lat = map(float, tok.split(",")[:2])
        out.append([round(lat, nd), round(lng, nd)])
    return out


def main():
    root = ET.fromstring(load(sys.argv[1] if len(sys.argv) > 1 else None))
    style_of = resolve_styles(root)
    categories, points, polygons = [], [], []
    poly_styles, poly_style_idx = [], {}

    for folder in root.iterfind(".//k:Folder", NS):
        name = folder.findtext("k:name", "", NS).strip()
        cat_pts, cat_polys, icon_colors = [], [], Counter()
        for pm in folder.iterfind("k:Placemark", NS):
            st = style_of.get(pm.findtext("k:styleUrl", "", NS).strip())
            pt = pm.findtext("k:Point/k:coordinates", "", NS).strip()
            ring = pm.findtext(".//k:Polygon/k:outerBoundaryIs/k:LinearRing/k:coordinates", "", NS).strip()
            if pt:
                cat_pts.append(coords(pt, 5)[0])
                ic = st is not None and st.findtext("k:IconStyle/k:color", "", NS)
                if ic:
                    icon_colors[kml_color(ic)[0]] += 1
            elif ring:
                line = st is not None and st.findtext("k:LineStyle/k:color", "", NS) or "ff000000"
                fill = st is not None and st.findtext("k:PolyStyle/k:color", "", NS) or "00000000"
                key = (kml_color(line)[0], kml_color(fill)[1])
                if key not in poly_style_idx:
                    poly_style_idx[key] = len(poly_styles)
                    poly_styles.append({"color": key[0], "fill": key[1]})
                flat = [v for ll in coords(ring, 6) for v in ll]
                cat_polys.append((poly_style_idx[key], flat))
        if not cat_pts and not cat_polys:
            continue
        idx = len(categories)
        color = icon_colors.most_common(1)[0][0] if icon_colors else "#000000"
        categories.append({"name": name, "count": len(cat_pts), "color": color})
        points += [[lat, lng, idx] for lat, lng in cat_pts]
        polygons += [[idx, s, flat] for s, flat in cat_polys]

    # Refuse to overwrite good data with an empty or badly truncated export
    if not points:
        sys.exit("No points found in KML; leaving existing data untouched.")
    if OUT.exists():
        previous = len(json.loads(OUT.read_text(encoding="utf-8"))["points"])
        if len(points) < previous * 0.5:
            sys.exit(f"Point count fell from {previous} to {len(points)}; refusing to overwrite. "
                     "Delete assets/data/projects.json and re-run if this is intended.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {"categories": categories, "styles": poly_styles, "points": points, "polygons": polygons}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(points)} points, {len(polygons)} polygons in {len(categories)} categories -> {OUT}")
    for c in categories:
        print(f"  {c['count']:4d}  {c['color']}  {c['name']}")


if __name__ == "__main__":
    main()
