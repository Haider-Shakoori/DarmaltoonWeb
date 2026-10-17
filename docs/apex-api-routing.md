# Main-domain Laravel API reverse mount

Canonical API: `https://darmaltoon.com/api/v1/**`. The root marketing website and Laravel platform run in separate project directories on the same cPanel user.

## Apache routing

Only rewrite `^api/v1(?:/.*)?$` to `/platform/index.php` at the main-domain document root. This lets Laravel handle the original URI `/api/v1/...`. The `/platform/index.php` front controller must boot the Laravel app outside the web root and normalize `SCRIPT_NAME`/ `PHP_SELF` to `/index.php` before `Request::capture()`. Preserve HTTPS, cookies and Host headers.

Do not intercept `/api/lead.php`, `/api/founding-offer.php`, `/api/analytics.php`, static assets or SEO routes. The versioned API requires Laravel auth/licensing as normal. The legacy `pharmacy.darmaltoon.com/api/v1/**` remains available until all current clients are upgraded.

Keep `public_html/.htaccess` cPanel-generated PHP directives intact when merging this repo's `.htaccess` into production, and preserve the existing www and light-only redirects. Avoid overwriting live root `.htaccess` wholesale.

Source of truth for client endpoints: `PharmaDesktop` cloud JSON settings and `Pharmacy` Flutter production build workflows. They will use the root origin when the **final** installer and IPA builds are requested.

## Acceptance

A public GET on `/api/v1/marketing/launch-offer` responds with an aggregate JSON offer; GET on `/api/v1/desktop/sync/status` returns 401 without auth; GET on `/api/v1/license/activate` returns 405 (POST-only). The website's existing `/api/lead.php` returns 405 for GET and continues accepting validated POSTs. Old signed clients continue working on the legacy hostname during transition.

Production routing and private sync files have backups in the cPanel user's private `.migration-backups/platform-20261017-2300` directory. Do not expose this folder under the public document root.
