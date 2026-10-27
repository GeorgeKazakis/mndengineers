"""Convert the Google My Maps export into the compact JSON used by the work map.

Usage:
    python3 tools/kml_to_json.py            # downloads the live map
    python3 tools/kml_to_json.py map.kml    # or converts a local KML file

Only point placemarks are kept (not the parcel polygons), rounded to ~10 m.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
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


def main():
    root = ET.fromstring(load(sys.argv[1] if len(sys.argv) > 1 else None))
    categories, points = [], []
    for folder in root.iterfind(".//k:Folder", NS):
        name = folder.findtext("k:name", "", NS).strip()
        coords = [
            pm.findtext("k:Point/k:coordinates", "", NS).strip()
            for pm in folder.iterfind("k:Placemark", NS)
        ]
        coords = [c for c in coords if c]
        if not coords:
            continue
        idx = len(categories)
        categories.append({"name": name, "count": len(coords)})
        for c in coords:
            lng, lat = map(float, c.split(",")[:2])
            points.append([round(lat, 4), round(lng, 4), idx])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"categories": categories, "points": points}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"{len(points)} points in {len(categories)} categories -> {OUT}")
    for c in categories:
        print(f"  {c['count']:4d}  {c['name']}")


if __name__ == "__main__":
    main()
