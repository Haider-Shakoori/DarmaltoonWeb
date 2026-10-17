/* Read live verified founding-customer availability; never manufacture a count. */
(function () {
  const el = document.querySelector('[data-founding-availability]');
  if (!el) return;
  const msg = 'Founding offer availability is confirmed only when your first payment is verified.';
  el.textContent = msg;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 6500);
  fetch('/api/founding-offer.php', {
    headers: { Accept: 'application/json' },
    credentials: 'same-origin',
    signal: controller.signal,
    cache: 'no-store'
  })
    .then(response => {
      if (!response.ok) throw Error('Unavailable');
      return response.json();
    })
    .then(info => {
      const remaining = info.founding_remaining;
      if (info.ok !== true || !Number.isInteger(remaining) || remaining < 0 || remaining > 10
        || info.renewal_price_afn !== '5000.00'
        || info.regular_first_year_price_afn !== '7000.00') return;
      if (remaining === 0) {
        el.textContent = 'All 10 founding-customer places have been taken. Standard first-year pricing is AFN 7,000.';
        return;
      }
      el.textContent = remaining + ' of 10 founding-customer places available at the time of this check. Places are confirmed only after verified payment.';
    })
    .catch(() => { el.textContent = msg; })
    .finally(() => clearTimeout(timeout));
})();
