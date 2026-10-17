# Darmaltoon lead intake — production notes

## Data flow
- Homepage, Demo and Contact POST JSON to /api/lead.php on the same origin.
- PHP 8.1+ validates input, consent and origin; includes a hidden honeypot and
  hashed-IP rate limits (45s minimum, 5/hour, 16/day).
- Valid requests are durably stored in SQLite **outside document root**,
  /home/darmaltoon/.darmaltoon-leads/leads.sqlite.
- Success displays only after SQLite commits. Email notification goes to
  info@darmaltoon.com on a best-effort basis; local mail() success does NOT
  prove mailbox delivery.
- Unavailable API shows the email-draft fallback instead of false success.
- No public administrator endpoint exposes contacts.

## Security & operations
- The database and key are account-owned, chmod 0600, private directory 0700.
- Only keyed hashes of visitor IP are saved for throttling; no raw IPs.
- Never place database/backups in the public web root or GitHub.
- Use authenticated SSH and PHP PDO to query lead counts and notification_queued.
- Separately back up the private .darmaltoon-leads folder: the website archive
  does NOT include this private SQLite database.
- Set a documented lead retention/deletion schedule.
- Verify actual email delivery to the recipient mailbox before relying on
  notification emails; create a review/resend process for failed notifications.

## Deployment QA
- Endpoint GET 405, invalid origin 403, consent failure 422, valid POST 201,
  immediate repeat 429.
- Confirm homepage and demo/contact phone views and RTL demo navigation.

## Platform Admin Demo Requests sync (October 2026)

The Laravel Platform Admin offers a private **Demo Requests** inbox and the
internal-only `POST /api/v1/marketing/leads/import` endpoint (Pharmacy PR #102).
Its strong bearer credential must be explicitly configured on *both* servers.
It is intentionally **not** exposed to browsers.

### One-time private configuration (on the website cPanel account)

Create the following PHP config file **outside document root**:
`/home/darmaltoon/.darmaltoon-leads/platform-sync.php`
and set its permissions to 0600 and parent directory to 0700:

```php
<?php
return [
    'url' => 'https://YOUR-VERIFIED-PLATFORM-API-HOST/api/v1/marketing/leads/import',
    'token' => 'INSERT_SAME_RANDOM_64_CHAR_OR_LONGER_SECRET_AS_LARAVEL',
];
```

The destination must be the deployed Laravel **HTTPS** API endpoint (do not
assume DNS or vhosts are ready). Keep the token private; never put it in
HTML, Git, the browser or public website environment. On the central Laravel
platform set `DARMALTOON_LEAD_IMPORT_TOKEN` to the identical random token,
cache/refresh config according to deployment procedure, and run the migration
that creates `website_leads`. Rotate both credentials if exposed.

### Historical catch-up and new incoming requests

From the website account run:

```bash
php /home/darmaltoon/public_html/scripts/sync_leads_to_platform.php
```

Adapt the script path to the **actual website document root**. The script
loads `/home/darmaltoon/.darmaltoon-leads/leads.sqlite`, reads and sends up
to 50 requests per HTTPS batch, and stores only a numeric checkpoint in the
private lead directory. **The first run imports all historic requests**.
Future runs transmit just new website requests. A failed batch never advances
the checkpoint; retries are safe due to the platform's unique
`(source,source_id)` key. No lead PII is printed in cron logs.

After one successful manual run and confirmation of the inbox, schedule the
same PHP CLI command through **cPanel Cron Jobs every five minutes**.
Use an explicit PHP path if cPanel cron has a different PHP binary; it
requires PHP 8.1+, pdo_sqlite, curl, mbstring and valid trusted TLS.
Protect private SQLite backups separately; the marketing repo does not contain
the live lead database.

### Internal test submission

Open Platform Admin **Demo Requests**, identify the known test request by its
website submission ID and date, set **Status: Completed** and
**Classification: Test / internal**. This hides it from default genuine
lead lists and conversion counts while preserving an audit trail. Never
automatically mark all old leads as test submissions.

### Verification

1. Confirm main site still POSTs demo/contact forms to `/api/lead.php`
   with consent and private durable storage.
2. Import existing submissions; compare private SQLite count against the
   platform imported + already-present counts and inspect the inbox.
3. Run the CLI script a second time; expected zero new imports, no duplicates.
4. Submit one consented **controlled test** request; sync, mark it
   Completed+Test; verify no genuine-lead count inflation.
5. Remove/rotate any sample credentials and never copy lead contacts into
   issue/CI logs, frontend analytics, or public files.

Production release is pending until **both** website sender and Laravel
receiver have been deployed/configured and a real database catch-up succeeds.
