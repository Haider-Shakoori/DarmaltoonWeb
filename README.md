# Darmaltoon — Public Pharmacy Software Website

Premium, lightweight, static marketing site for **Darmaltoon** pharmacy management software, designed for pharmacies in Afghanistan. The Windows desktop application and Laravel backend live in separate repositories; this website does not modify either system.

## Architecture and low-bandwidth approach

- Static **HTML5**, modern **CSS3**, minimal **vanilla JavaScript**.
- No frontend framework, app bundle, mandatory font download, or frontend API call to render the homepage.
- One stylesheet and a tiny progressive-enhancement script power the homepage and light/dark design selector.
- Apache/cPanel compression and caching rules are in `.htaccess`.

## SEO, AI and localization

The main site and product pages are **pre-rendered** for crawlers in three languages:

| Language | Homepage | Features | Desktop product |
|---|---|---|---|
| English | `/` | `/features.html` | `/pharmadesktop.html` |
| Dari | `/fa/` | `/fa/features.html` | `/fa/pharmadesktop.html` |
| Pashto | `/ps/` | `/ps/features.html` | `/ps/pharmadesktop.html` |

- Each pre-rendered page has localized metadata, canonical URLs and `hreflang` relationships. Dari and Pashto use RTL.
- `sitemap.xml`, `robots.txt`, `llms.txt` and structured data describe the public site.
- Legacy demo, contact, about and 404 pages remain localized using the original language script.
- No fake testimonials, invented clientele, search ranking claims or unsupported prices.

## Preview locally

Use a **local HTTP server** at the repository root. Because the new pages use site-root asset URLs, opening `index.html` with a `file://` link is not supported.

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/`, switch the theme in the navigation bar, or use `http://localhost:8000/?theme=dark`. Also inspect `/fa/` and `/ps/`.

The dashboard is an illustrative visual with sample numbers, not real customer data. Existing desktop screenshots were absent from the original repository, so an honest illustrative fallback remains until verified, privacy-cleared real screenshots can be added.

## Release notes

- `python3 scripts/check_site.py` runs static SEO, localization, internal-link and size tests in GitHub Actions.
- Demo and contact forms have **no delivery backend yet**. They do not submit data and now explicitly warn visitors instead of giving a false success message. This must be connected before public marketing campaigns.
- See [SEO-PERFORMANCE.md](SEO-PERFORMANCE.md) for the launch checklist.

## Current branch

`feat/seo-first-bilingual-showcase` — under review through a draft pull request, not merged or deployed.
