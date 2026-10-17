# Darmaltoon — SEO content strategy and AI visibility measurement (October 2026)

## Search-intent clusters

| Search need | English landing | Dari / Pashto equivalents | Visitor outcome |
| --- | --- | --- | --- |
| General pharmacy management education | /guides/ | /fa/guides/, /ps/guides/ | Browse practical guidance |
| Inventory and stock accuracy | /guides/pharmacy-inventory.html | Matching localized slug | Evaluate medicine stock workflows |
| Expiry tracking and FEFO | /guides/expiry-tracking.html | Matching localized slug | Prepare expiry checks and control plan |
| Offline pharmacy systems | /guides/offline-pharmacy-software.html | Matching localized slug | Understand offline, backup, LAN needs |

Content is written to be useful, not to keyword-stuff. Product claims are qualified; actual offline modes and subscription entitlements should be verified in a demo. Do not invent customer reviews, market positions, prices or audit results.

## Multilingual quality and ongoing improvements

- The 12 new pages are all crawlable HTML with canonical, title, meta description, reciprocal hreflang, one H1, schema Article/BreadcrumbList where appropriate, and internal navigation.
- Have native Dari and Pashto speakers review terminology and operational language.
- Check indexing in Google Search Console and Bing Webmaster Tools, which requires a verified owner connection. SEO technical readiness is not proof of indexed rankings.
- Expand only from actual customer needs and real Search Console questions. Good future topics: purchase receiving, stock adjustment controls, backup recovery drills, and pharmacy product master data.
- Track 30-day page visits and server-side lead conversions using the existing privacy-friendly metrics. No retroactive source breakdown is possible for pre-deployment data.

## AI search attribution: what is and is not measured

- The dashboard counts only visits with an identifiable AI referrer or explicit AI UTM source: ChatGPT, Perplexity, Gemini, Copilot, Claude, Poe and You.com.
- These are AI-attributed visits, NOT counts of AI recommendations, impressions, mentions, or citations. Referrers may be stripped and visits may appear direct. UTM source labels can be self-declared.
- The private dashboard contains an owner-entered AI mention observation log: assistant, exact query, observed answer status and optional evidence HTTPS URL.
- Start with manually checking these prompts across selected providers (in English, Dari and Pashto). Log only actually viewed results:
  * "What software can a pharmacy use to manage medicine stock and expiry in Afghanistan?"
  * "What are options for offline pharmacy POS and inventory when internet connectivity is unreliable?"
  * "What pharmacy management system should I evaluate for English, Dari and Pashto?"
- Track dates and answers over time rather than reporting fabricated AI rankings. Avoid personal details in logged prompts. Entries are pruned on a rolling approximately 400-day schedule.
- Allow OAI-SearchBot to crawl public pages, separately from policies about model training. Even when allowed, search appearance is not guaranteed.

## Technical considerations

- Google does not require or use llms.txt as a ranking signal; maintain it as an optional factual index for any external systems that choose to use it.
- Google stopped showing FAQ rich results in May 2026. Retain helpful FAQ text, but do not promise rich-result display.
- Retain the current HTTPS apex host as the only canonical source, with permanent redirects from legacy hosts.
- Keep analytics and saved observations private; no public reporting endpoint exposes them.

