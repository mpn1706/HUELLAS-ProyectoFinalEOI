"""Geocodifica el seed Jerez a ubicaciones exactas (Nominatim OSM, con pausa 1.2s).

Actualiza lat/lng + address_text de cada JSON en data/seed. Trazable a REQ-03.8.
Uso: python scripts/geocode_seed.py
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

QUERIES = {
    "lost_001": "Plaza del Arenal, Jerez de la Frontera",
    "lost_002": "Calle Santo Domingo, Jerez de la Frontera",
    "lost_003": "Chapin, Jerez de la Frontera",
    "lost_004": "Avenida de la Granja, Jerez de la Frontera",
    "lost_005": "Calle Larga, Jerez de la Frontera",
    "found_001": "Plaza del Arenal, Jerez de la Frontera",
    "found_002": "Parque González Hontoria, Jerez de la Frontera",
    "found_003": "Calle Santo Domingo, Jerez de la Frontera",
    "found_004": "Chapin, Jerez de la Frontera",
    "found_005": "Avenida de la Granja, Jerez de la Frontera",
    "found_006": "Plaza Santiago, Jerez de la Frontera",
    "found_007": "Avenida Puerta del Sur, Jerez de la Frontera",
    "found_008": "La Plata, Jerez de la Frontera",
    "found_009": "Vallesequillo, Jerez de la Frontera",
    "found_010": "Carretera de Sevilla, Jerez de la Frontera",
    "found_011": "El Peliron, Jerez de la Frontera",
    "found_012": "Icovesa, Jerez de la Frontera",
}


def geocode(q: str):
    url = ("https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "addressdetails": 1, "limit": 1,
         "viewbox": "-6.25,36.75,-6.00,36.60", "bounded": 0}))
    req = urllib.request.Request(url, headers={"User-Agent": "HUELLAS-EOI-MVP/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not data:
        return None
    d, addr = data[0], data[0].get("address", {})
    road = addr.get("road", "")
    num = addr.get("house_number", "")
    zona = addr.get("suburb", addr.get("neighbourhood", addr.get("city_district", "")))
    corto = ", ".join(p for p in [f"{road} {num}".strip(), zona, "Jerez de la Frontera"] if p)
    return round(float(d["lat"]), 5), round(float(d["lon"]), 5), corto or d.get("display_name", q)


def main():
    for i, (aid, q) in enumerate(QUERIES.items()):
        if i:
            time.sleep(1.2)
        folder = "lost" if aid.startswith("lost") else "found"
        fp = ROOT / "data" / "seed" / folder / f"{aid}.json"
        doc = json.loads(fp.read_text(encoding="utf-8"))
        try:
            lat, lng, addr = geocode(q)
        except Exception as e:
            print(f"{aid}: FALLO ({e}), se conserva valor previo")
            continue
        doc["location"] = {"lat": lat, "lng": lng, "address_text": addr}
        fp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{aid}: {lat},{lng} | {addr}")


if __name__ == "__main__":
    main()
