# Darmaltoon first-party analytics and cPanel lead intake

Website tracking sends cookie-free daily aggregates to /api/analytics.php.
It records page views, demo/contact link clicks, WhatsApp/email clicks,
and server-confirmed demo/contact conversions. No visitor identifiers,
raw IPs, full referrer URLs, names, messages, patient data or pharmacy
records enter the marketing analytics database.
GPC and Do Not Track disable browser tracking.

Metrics cover day, approved page path, language, device viewport class,
broad referring provider, source type, and sanitized campaign label.
Daily aggregates are retained for approximately 13 months. Page views
do NOT equal unique users or Google Search impressions/keyword queries.
Search Console data is required for actual search impressions.

Private files outside the web root:
- /home/darmaltoon/.darmaltoon-analytics/metrics.sqlite
- /home/darmaltoon/.darmaltoon-analytics/admin-password.hash
- /home/darmaltoon/.darmaltoon-leads/leads.sqlite
Directories need 0700, private files 0600 permissions.

Owner dashboard (no public reporting API):
https://web.darmaltoon.com/admin/analytics.php
Disabled until owner sets password with cPanel Terminal:
php /home/darmaltoon/darmaltoon-maintenance/setup_analytics_admin.php
CLI prints a random one-time password; copy it into a password manager.
Rotate with the same command plus --rotate.

Lead forms POST to /api/lead.php. Consent, honeypot, origin checks,
size validation, input validation and keyed-IP-hash throttling apply.
Requests are saved before a successful response. cPanel mail() attempts
a notification to info@darmaltoon.com with a noreply@darmaltoon.com
sender. A true mail() return indicates local queue acceptance only,
not verified inbox delivery. Private delivery flags record that distinction.
Optional cPanel cron (every 15 minutes) to retry local mail queue failures:
php /home/darmaltoon/darmaltoon-maintenance/retry_lead_notifications.php
(up to 3 total local attempts; avoids retrying mail() success).

Back up website and both private storage folders before an update. Never
publish databases, password hashes, or SMTP credentials.

Tests: python3 scripts/check_site.py; php -l on all PHP endpoints;
node --check assets/js/first-party-analytics.js. Live checks must show
HTTP 405 for GET /api/analytics.php and password protection for /admin.
Use TEST-labelled demo enquiries when verifying cPanel mail notifications.
