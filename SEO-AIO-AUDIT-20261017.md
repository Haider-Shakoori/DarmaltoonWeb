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

## Limitations / follow-up
- No ranking, traffic growth, Core Web Vitals field data or rich-result eligibility
  is implied by this code audit. Confirm in Google Search Console, Google Rich
  Results Test, PageSpeed Insights and Bing Webmaster Tools after deployment.
- Submit/refresh the sitemap in search tools and monitor indexing, coverage,
  regional search queries, search appearance and 404 redirects.
- Confirm all Dari/Pashto translations with native speakers before paid marketing.
- Publish a privacy/retention policy, especially because leads now contain
  personally supplied contact details; establish a regular deletion schedule.
- Test mailbox delivery of lead notifications. Private SQLite storage is the
  canonical record if mail transport is unavailable.
- Audit real Android feature parity, plan availability and pricing before making
  absolute public claims; availability caveats currently remain in site copy.
- Grow genuine pharmacy case studies and testimonials only once permissioned
  customers exist; do not create fabricated testimonials.
- Broaden localized informational/long-tail pharmacy help pages based on
  actual Search Console queries rather than keyword stuffing.
