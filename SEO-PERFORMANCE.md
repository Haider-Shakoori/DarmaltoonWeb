# Darmaltoon website — SEO-first, low-bandwidth deployment

This repository hosts the public *marketing* website for Darmaltoon, not the pharmacy application's transactional backend. Deploy the entire repository root to the site's document root (including `fa/`, `ps/`, `robots.txt`, `sitemap.xml`, and `.htaccess`). Apache with Brotli/Gzip and HTTPS recommended.

## Lightweight design
- The homepage is static HTML and contains a native CSS demonstration dashboard; no framework, API calls, or network-loaded fonts are needed.
- One small CSS file and one tiny progressive-enhancement JavaScript file support both light and dark design variants.
- To compare locally: open `/` for the light version or `/?theme=dark` for the dark version; the toggle persists your choice. Both have the same canonical URL, preventing duplicate indexing.
- The selected logo image is embedded in a small local SVG container and reused across marketing pages. It remains available without third-party network requests.

## Languages and SEO
- English: `/`; Dari: `/fa/`; Pashto: `/ps/`.
- Homepages have server-delivered localized content, canonical URLs, `hreflang`, descriptive titles, and JSON-LD for a Windows business software product.
- Features and desktop product pages also have static Dari and Pashto counterparts with reciprocal hreflang. Legacy demo, about and contact pages are still localized client-side; statically pre-rendering those remaining pages is a future SEO improvement.
- `robots.txt`, `sitemap.xml`, and `llms.txt` explain available public content. These are not promises of rankings or AI citations.

## Truthful marketing and screenshots
- The homepage dashboard contains *clearly marked illustrative data*. It does not display a real customer's transactions.
- The desktop product page uses an illustrative local fallback image until verified, privacy-cleared app screenshots are available.
- No invented customers, reviews, revenue, unsupported rankings, or price assertions.

## Outstanding before production release
1. Replace illustrative dashboard/screenshots with verified, sanitized exports of PharmaDesktop with realistic fictional demo data.
2. Confirm production domain, prices, contact details, and working demo/contact form submission endpoints. Existing forms currently validate only client-side.
3. Translate and statically pre-render all remaining informational pages per locale, with dedicated canonical/hreflang routes.
4. Run device/browser visual and accessibility QA, Lighthouse on the deployed site, and verify sitemap indexing in Google Search Console and Bing Webmaster Tools.
5. Prepare small PNG/WebP OpenGraph image from the approved logo (avoid broken OpenGraph image references).
6. Review legal disclosures, privacy notice, contact channels, and installation/download links before publishing.

## Validation
`python3 scripts/check_site.py` runs in GitHub Actions and requires no Python packages.
