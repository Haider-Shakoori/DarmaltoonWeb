# Darmaltoon — Public Pharmacy Management Website

The public marketing website is https://darmaltoon.com/. The legacy host web.darmaltoon.com redirects to the primary domain.

## Presentation
- Premium **light-only** design; no dark-mode switch or dark homepage.
- Responsive native HTML/CSS for desktop/mobile, with real crawlable text rather than screenshot-only navigation.
- English homepage `/`, Dari `/fa/`, and Pashto `/ps/` with RTL support on localized pages.
- Retired `/dark.html` permanently redirects to `/` and is excluded from the sitemap.
- Marketing heading: **Modern Pharmacy Management, Made Simple.**

## Functional scope
- Product, Features, About, Demo, Contact and multilingual privacy pages.
- Lead forms use `/api/lead.php`, consent/validation, private SQLite storage outside web root, and notifications to `info@darmaltoon.com`.
- Privacy-conscious aggregate analytics with a password-protected owner dashboard.
- Canonical/hreflang metadata, structured data, sitemap and robot rules point to the apex domain.
- Sample dashboard visuals are illustrations, not real patient records or verified customer counts.

## Release checks
Run `python3 scripts/check_site.py` and `python3 scripts/check_approved_ui.py`, `php -l` on PHP files, and `node --check` on JavaScript files. Verify public redirects, content and API origin checks. Deploy only after backing up both the public document root and separate private leads data. Do not commit secrets, mailboxes, server settings, or private databases.

This repository is the public marketing site, **not** the pharmacy web application or native Windows application.

## Follow-up decisions
Approval of lead-data retention rules, native-speaker copy review, and Google Search Console coverage/Core Web Vitals are separate operational tasks. Confirm Android/platform and subscription claims before public marketing expansion.
