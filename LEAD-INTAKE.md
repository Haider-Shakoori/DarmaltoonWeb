# Darmaltoon lead intake — production notes

## Data flow
- Homepage, Demo and Contact POST JSON to /api/lead.php on the same origin.
- PHP 8.1+ validates input, consent and origin; includes a hidden honeypot and
  hashed-IP rate limits (45s minimum, 5/hour, 16/day).
- Valid requests are durably stored in SQLite **outside document root**,
  /home/darmaltoon/.darmaltoon-leads/leads.sqlite.
- Success displays only after SQLite commits. Email notification goes to
  info@businessos.af on a best-effort basis; local mail() success does NOT
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
