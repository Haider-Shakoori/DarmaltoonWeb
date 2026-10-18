# Darmaltoon QA traffic exclusion

The public marketing-site trackers (Google Analytics 4 and the first-party
visitor dashboard) share an opt-out gate. Automated QA and developer browsers
must be marked **before they first visit a public page**.

## Start QA (this browser, 30 days)
Visit `https://darmaltoon.com/?dt_qa=1` once in the browser used for QA.
The browser stores `dt_analytics_qa_exclude=1` in a Secure, SameSite=Lax,
same-site cookie and in localStorage. Both GA4 and first-party analytics skip
these visits; the first-party server also discards marked events.

For automated Playwright/Puppeteer jobs, set the cookie **before navigating**:

```js
await context.addCookies([{
  name: 'dt_analytics_qa_exclude',
  value: '1',
  domain: 'darmaltoon.com',
  path: '/',
  secure: true,
  sameSite: 'Lax'
}]);
// Now visit the website. Do not spoof webdriver=true to false just for testing.
```

This uses the same cookie across the English, Dari, and Pashto sections. Each
separate browser, private browsing profile, or remote QA session needs its own
mark. Tests that intentionally inspect GA4 should intercept or block collect
requests so they do **not** create production users or page views.

## Return browser to normal tracking

Visit `https://darmaltoon.com/?dt_qa=0`. This clears only the QA exclusion
cookie/storage, not the platform-owner exclusion or privacy preferences.

## Important limitations

- Query parameters do not cause a GA4 data filter or delete historical visits.
- Automated browsers with real-looking UAs and overridden `navigator.webdriver`
  cannot all be identified reliably. The QA cookie is therefore a **required**
  part of the workflow for our test sessions.
- Do not exclude all US traffic, all datacenter IPs, or all VPN traffic. Those
  are not reliable bot indicators and would omit possible genuine visitors.
- A GA4 `traffic_type=internal` filter can optionally be configured in GA4
  Admin for **known stable office IP ranges**, but should be tested before
  activation. It does not cover dynamic cloud/browser-proxy addresses.
- Exclusions take effect prospectively. The two earlier GA4 Realtime users
  cannot be established as bots or deleted through these controls.
