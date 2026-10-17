# Darmaltoon SEO / AI Discoverability Audit — 17 October 2026

## Implemented and verified
- The main English, Dari and Pashto homepages have unique language-specific
  titles, meta descriptions, canonical URLs, reciprocal hreflang signals
  (en, fa-AF, ps-AF, x-default) and structured data.
- The static sitemap includes the public canonical landing, features, desktop,
  demo, about and contact URLs. The separate dark theme canonicalizes to the
  main English homepage rather than competing in search.
- Localized landing pages include one crawlable H1, eight native HTML feature
  cards, five matching FAQ entries, and SoftwareApplication/WebPage/FAQPage JSON-LD.
  Their content is not a full-page raster image.
- Secondary pages include per-page WebPage/AboutPage/ContactPage schema,
  social image and Twitter preview metadata, informative page titles,
  and real email/phone links.
- The robots policy permits indexing public content, references the sitemap and
  disallows the API endpoint. llms.txt describes actual verified capabilities and
  links to localized and product pages.
- Dashboard/sales figures on marketing imagery are explicitly labeled sample
  data. No manufactured client counts, five-star ratings, or leadership rankings.
- Client-side JS not needed to render core public landing-page content.
- CSS+JS for RTL page is approximately 18 KB uncompressed combined; server
  compression and browser caching are configured in Apache.
- The site has accessible skip links, descriptive image alt text, native
  summary/details FAQ controls and keyboard-focus outlines.

## Remaining operational follow-up
- Public indexing and rankings are not guaranteed by markup or this QA. Review
  Google Search Console and Bing Webmaster Tools, inspect sitemap coverage, and
  monitor actual queries and Core Web Vitals after search engines crawl the site.
- Validate Dari/Pashto marketing translations with native speakers.
- Trilingual privacy notices are **already published**. Establish an approved
  lead retention/deletion schedule and private data access procedure.
- Verify receipt of an actual lead email at info@businessos.af from the mailbox.
  The SQLite database is the durable canonical lead record; server-side
  mail() queueing does **not** guarantee mailbox delivery.
- Confirm Android feature availability, licensing and exact plan entitlements
  with the product team before making stronger public claims.
- Collect genuine, permissioned customer case studies only after clients exist.
- Build localized informational pages based on real search query data, not
  fabricated reviews, claims or keyword stuffing.

## Live verification — 17 October 2026
- English, Dari, Pashto landing pages, three privacy notices, robots.txt,
  sitemap.xml and llms.txt responded with HTTP 200.
- Exact SHA-256 checksums of the two localized HTML pages, RTL stylesheet and
  RTL JavaScript on cPanel match the currently checked-in Git worktree.
- Headless Chromium covered localized pages at 320, 390, 768, 1024 and 1440px.
  No horizontal overflow, missing visible images or JavaScript errors.
  Light/dark switching and mobile menu both functioned.
- Each localized page has one semantic H1, eight native feature cards,
  three platform cards and five crawlable FAQ entries.
- Secure lead endpoint: GET returned 405; an invalid same-origin POST returned
  422 without saving a lead; a cross-origin POST returned 403.
- PHP PDO SQLite extension present; the private leads directory and database
  were verified outside document root with restrictive permissions.
- Updated current-design UI regression test and main SEO check both pass.
- No sample lead was added to production during this audit.

## Privacy and RTL follow-up
- Trilingual crawlable privacy notices and localized consent links in forms/footers.
- Reciprocal canonical and hreflang on privacy pages and new sitemap entries.
- The mobile light RTL background now favors readable text over faded dashboard lettering.
- No automatic lead-deletion interval is yet defined. Operational retention policy is still pending approval.
