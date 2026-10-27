# M&D Engineers — website

Static redesign of https://mndengineers.wixsite.com/mndengineers (Greek, single page).

```
index.html          page (services, work gallery, process, contact)
assets/styles.css   styles, no framework
assets/main.js      mobile menu, lightbox, scroll reveal, mailto enquiry form
assets/map.js       work map (Leaflet + OpenStreetMap, clustered, category filters)
assets/data/        projects.json — work-map points, generated from Google My Maps
tools/kml_to_json.py  regenerates projects.json from the Google My Maps map
assets/img/         drawings from the Wix site, resized to 1800px WebP
tem.html            saved copy of the original Wix page (reference only)
```

No build step. Preview locally with `python3 -m http.server` and open http://localhost:8000.

## Deploy

Any static host works: GitHub Pages (Settings → Pages → deploy from branch, root), Netlify or Vercel (drag-and-drop the folder / import the repo, no build command).

## Updating the work map

Locations are maintained in the existing Google My Maps map ("Θεματικός Χάρτης Εργασιών").
A GitHub Action (`.github/workflows/update-map.yml`) pulls it nightly at 02:17 UTC and commits
`assets/data/projects.json` only when something changed, so edits appear on the site by the next morning.
To update immediately: Actions → "Update work map" → Run workflow (or run `python3 tools/kml_to_json.py` locally).
The script refuses to overwrite the data if the export is empty or loses more than half the points.
Only points are published (no parcel polygons), rounded to ~10 m.

## Notes

- The enquiry form opens the visitor's email client (`mailto:`) addressed to both engineers. To receive submissions directly, point the form at a service such as Formspree or Netlify Forms.
- Update `og:image` to an absolute URL once a domain is set.
