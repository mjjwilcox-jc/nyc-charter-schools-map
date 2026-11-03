# NYC Charter Schools Map

An interactive map of every charter school in New York City's five boroughs.

**▶ Live map: https://mjjwilcox-jc.github.io/nyc-charter-schools-map/**

## What it shows

- **280 charter schools** plotted at their official locations, color-coded by borough
- **Search** by school name, street address or ZIP code
- **Filter** by borough, authorizer (SUNY, Board of Regents, NYC DOE) and school level
- **Click any school** for its address, grades served, 2024–25 enrollment, community school district, authorizer, year opened and phone number, plus a link to Google Maps
- Running totals of schools and students for whatever is currently filtered

| Borough | Schools mapped |
|---|---|
| Bronx | 99 |
| Brooklyn | 91 |
| Manhattan | 53 |
| Queens | 29 |
| Staten Island | 8 |
| **Total** | **280** |

## Data sources

The map joins two official public datasets on the 12-digit NYSED school (BEDS) code:

1. **[NYSED Charter Schools Directory, 2025–26](https://www.nysed.gov/charter-schools/charter-schools-directory)** (as of September 2, 2025). This is the authoritative list of charters operating in New York State. It lists **299 charters in NYC**, with each school's authorizer, year opened and community school district.
2. **[NCES Common Core of Data / EDGE school locations, 2024–25](https://nces.ed.gov/programs/edge/Geographic/SchoolLocations)** (U.S. Department of Education). This provides the street address, grades served, enrollment and geocoded latitude/longitude.

### Coverage note

19 of the 299 schools in the state directory are not on the map. Eighteen of them opened in fall 2025 or are approved to open in 2026, which is after the most recent federal location release (2024–25). The other one (Explore Exceed) has no 2024–25 federal location record. The map lists all 19 in its sidebar under "newly opened schools not yet mapped," so the gap is visible to the user instead of silently dropped. They will appear automatically once NCES publishes its next release and the data is rebuilt.

Each point is one charter (one state-registered school). Some charter networks run a single charter across more than one building; in those cases the point is the address of record.

## Project structure

```
index.html                     the map (Leaflet, no build step, no API keys)
data/
  nyc_charter_schools.csv      clean table of all 299 schools (mapped or not)
  nyc_charter_schools.geojson  mapped schools as GeoJSON
  schools.js                   same data, loaded by index.html
  raw/                         source extracts from NYSED and NCES
scripts/build_data.py          joins the raw sources and writes the files above
vendor/                        Leaflet 1.9.4 + Leaflet.markercluster (MIT / BSD)
```

## Run it locally

No install needed. Open `index.html` in a browser.

To rebuild the data after updating the files in `data/raw/`:

```bash
python3 scripts/build_data.py
```

(Python 3 standard library only.)

## Built with

[Leaflet](https://leafletjs.com/) · [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) · basemap tiles © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, © [CARTO](https://carto.com/attributions)
