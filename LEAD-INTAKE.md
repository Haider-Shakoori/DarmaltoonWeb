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


## Secure Platform Admin Demo Requests integration

The private website SQLite database remains the source of truth until the central
Platform Admin acknowledges a batch. Existing and future rows use the same
\`source=darmaltoon.com\` + \`source_id\` key, so retries never duplicate records
or overwrite sales statuses/notes.

The website sends batches from \`scripts/platform-lead-sync.php\`, including a
best-effort attempt following each successful \`api/lead.php\` insert. Failed
delivery does not change the form's response or lose the saved lead.

The central Pharmacy Laravel platform must have \`DARMALTOON_LEAD_IMPORT_TOKEN\`
configured in its server-side environment, using a random secret of at least
32 characters. The website needs the **exact same** secret and a valid HTTPS
endpoint ending in \`/api/v1/marketing/leads/import\`.

Configure the website by setting both environment variables:
- \`DARMALTOON_PLATFORM_LEADS_URL\` (e.g. the actual API domain + path)
- \`DARMALTOON_PLATFORM_LEADS_TOKEN\`

Alternatively, on cPanel place a 0600 permissions JSON file outside the
public document root at
\`/home/darmaltoon/.darmaltoon-leads/platform-sync.json\`
with properties \`url\` and \`token\`. Never commit it or publish the secret.

### Historical backfill and retry

Run the CLI script from **the cPanel website hosting account** (not the
unrelated VPS), e.g.:

\`\`\`bash
/usr/local/bin/php /home/darmaltoon/public_html/scripts/sync_leads_to_platform.php
\`\`\`

Use a 5-minute cPanel cron for new request retries and historical backfill.
Verify the actual PHP executable and deployed website path first. The script
reads existing rows in ascending ID, imports up to 500 per execution, and
records a private acknowledgement for each successful batch. On any network
or platform failure, unsent requests remain in SQLite for the next run.
Historical records are not deleted.

### Handling an assistant-generated test

After importing, identify the exact test row by its original website ID and
timestamp and open it in **Platform Admin → Demo Requests**. Set
**Status = Completed** and **Classification = Test / internal submission**.
Keep notes such as "Internal website-to-platform integration test; no sales
follow-up". It remains accessible under the **Test requests only** filter
but is excluded from the genuine-new-lead count. Do not classify a real
customer request as a test merely because it has no pharmacy name.

### Security

- No public GET/read API for contact records.
- The central POST importer uses an explicit high-entropy bearer token
  over HTTPS, validation, rate limiting and source-ID deduplication.
- Only authenticated platform administrators may view and change requests.
- All email/phone/message fields remain outside anonymous marketing analytics.
- The platform's local secret must never be exposed to JavaScript or browsers.
- Do not assume emails were delivered just because \`mail()\` returned true.
- Test the import against staging before any live change.
