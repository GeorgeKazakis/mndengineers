# M&D Engineers — website

Static redesign of https://mndengineers.wixsite.com/mndengineers (Greek, single page).

```
index.html          page (services, work gallery, process, contact)
assets/styles.css   styles, no framework
assets/main.js      mobile menu, lightbox, scroll reveal, mailto enquiry form
assets/img/         drawings from the Wix site, resized to 1800px WebP
tem.html            saved copy of the original Wix page (reference only)
```

No build step. Preview locally with `python3 -m http.server` and open http://localhost:8000.

## Deploy

Any static host works: GitHub Pages (Settings → Pages → deploy from branch, root), Netlify or Vercel (drag-and-drop the folder / import the repo, no build command).

## Notes

- The enquiry form opens the visitor's email client (`mailto:`) addressed to both engineers. To receive submissions directly, point the form at a service such as Formspree or Netlify Forms.
- Update `og:image` to an absolute URL once a domain is set.
