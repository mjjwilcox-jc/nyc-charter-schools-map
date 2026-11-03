"""
Build the NYC charter school dataset used by the map.

Joins two official sources on the 12-digit NYSED (BEDS) code:
  1. NYSED 2025-26 Charter School Directory  -> the authoritative list of charters,
     plus authorizer, year opened and community school district.
  2. NCES Common Core of Data / EDGE, 2024-25 -> street address, grades served,
     enrollment and geocoded latitude/longitude.

Outputs:
  data/nyc_charter_schools.geojson   (mapped schools)
  data/nyc_charter_schools.csv       (every school in the NYSED list, mapped or not)

Usage:  python3 scripts/build_data.py
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

BOROUGH = {
    "Bronx": "Bronx",
    "Kings": "Brooklyn",
    "New York": "Manhattan",
    "Queens": "Queens",
    "Richmond": "Staten Island",
}
GRADE_LABEL = {"PK": "Pre-K", "KG": "K"}


def read_pipe(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="|"))


def grade(g):
    if g in GRADE_LABEL:
        return GRADE_LABEL[g]
    return str(int(g)) if g.isdigit() else g


def tidy_street(s):
    """NCES addresses are upper case, e.g. '250 E 156TH ST-4TH FL'.
    Make them readable: '250 E 156th St, 4th Fl'. Queens-style house
    numbers ('136-25 218TH ST') are left alone because the hyphen sits
    between digits."""
    s = re.sub(r"(?<=[A-Z])\s*-\s*(?=[A-Z0-9])", ", ", s)
    s = s.title()
    s = re.sub(r"\b(\d+)(St|Nd|Rd|Th)\b", lambda m: m.group(1) + m.group(2).lower(), s)
    s = re.sub(r"\b(Ne|Nw|Se|Sw|Ii|Iii|Iv)\b", lambda m: m.group(1).upper(), s)
    return s


def main():
    nysed = read_pipe(RAW / "nysed_charter_directory_nyc.txt")
    nces = {r["sed_code"]: r for r in read_pipe(RAW / "nces_ccd_nyc_charters_2024_25.txt")}

    features, rows, unmapped = [], [], []
    for s in nysed:
        name = " ".join(s["name"].split())  # collapse double spaces in source
        borough = BOROUGH[s["county"]]
        n = nces.get(s["sed_code"])
        rec = {
            "name": name,
            "sed_code": s["sed_code"],
            "borough": borough,
            "district": s["district"].replace("NYC CSD ", "CSD "),
            "authorizer": s["authorizer"],
            "year_opened": int(s["year_opened"]),
            "address": "",
            "zip": "",
            "phone": "",
            "grades": "",
            "level": "",
            "enrollment": None,
            "nces_id": "",
            "lat": None,
            "lon": None,
        }
        if n:
            rec.update(
                address=f"{tidy_street(n['street'])}, {n['city'].title()}, NY {n['zip']}",
                zip=n["zip"],
                phone=n["phone"],
                grades=f"{grade(n['grade_low'])}–{grade(n['grade_high'])}"
                if n["grade_low"] != n["grade_high"] else grade(n["grade_low"]),
                level=n["level"],
                enrollment=int(n["enrollment"]) if n["enrollment"] else None,
                nces_id=n["nces_id"],
                lat=float(n["lat"]),
                lon=float(n["lon"]),
            )
            props = {k: v for k, v in rec.items() if k not in ("lat", "lon")}
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [rec["lon"], rec["lat"]]},
                "properties": props,
            })
        else:
            unmapped.append(rec)
        rows.append(rec)

    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "New York City Charter Schools",
            "sources": [
                "NYSED Charter Schools Directory 2025-26 (as of 2025-09-02)",
                "NCES Common Core of Data / EDGE school locations, 2024-25",
            ],
            "total_charters_in_directory": len(nysed),
            "mapped": len(features),
            "not_yet_mapped": [u["name"] for u in unmapped],
        },
        "features": features,
    }
    (ROOT / "data" / "nyc_charter_schools.geojson").write_text(
        json.dumps(geojson, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    # Same data as a script, so index.html works on GitHub Pages *and* when opened from disk.
    (ROOT / "data" / "schools.js").write_text(
        "window.CHARTER_SCHOOLS = " + json.dumps(geojson, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    with open(ROOT / "data" / "nyc_charter_schools.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["borough"], r["name"])))

    print(f"NYSED charters in NYC: {len(nysed)}")
    print(f"Mapped with NCES coordinates: {len(features)}")
    print("By borough:", dict(Counter(f["properties"]["borough"] for f in features)))
    print(f"Not yet in federal location data ({len(unmapped)}):")
    for u in unmapped:
        print(f"  - {u['name']} ({u['borough']}, opened {u['year_opened']})")
    extra = set(nces) - {s["sed_code"] for s in nysed}
    if extra:
        print("NCES charters not in NYSED directory:", [nces[e]["nces_name"] for e in extra])


if __name__ == "__main__":
    main()
