/* Read live verified founding-customer availability; never manufacture a count. */
(function () {
  const el = document.querySelector('[data-founding-availability]');
  if (!el) return;
  const lang = (document.documentElement.lang || 'en').slice(0, 2);
  const messages = {
    en: {
      wait: 'Founding offer availability is confirmed only when your first payment is verified.',
      gone: 'All 10 founding-customer places have been taken. Standard first-year pricing is AFN 7,000.',
      remaining: n => n + ' of 10 founding-customer places available at the time of this check. Places are confirmed only after verified payment.'
    },
    fa: {
      wait: 'ظرفیت پیشنهاد ویژه تنها پس از تأیید پرداخت قابل تأیید است.',
      gone: 'تمام ۱۰ جایگاه مشتریان نخست تکمیل شده است. قیمت سال اول اکنون ۷٬۰۰۰ افغانی است.',
      remaining: n => n + ' جایگاه از ۱۰ جایگاه ویژه هنگام بررسی موجود است. جایگاه فقط پس از تأیید پرداخت نهایی می‌شود.'
    },
    ps: {
      wait: 'ځانګړی ځای یوازې د تادیې تر تایید وروسته ثبتېږي.',
      gone: 'د لومړنیو ۱۰ پېرودونکو ټول ځایونه ډک شوي دي. د لومړي کال عادي بیه ۷٬۰۰۰ افغانۍ ده.',
      remaining: n => 'له ۱۰ څخه ' + n + ' ځانګړي ځایونه د دې کتنې پر وخت پاتې دي. ځای یوازې د تادیې تر تایید وروسته ثبتېږي.'
    }
  };
  const words = messages[lang] || messages.en;
  const msg = words.wait;
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
        el.textContent = words.gone;
        return;
      }
      el.textContent = words.remaining(remaining);
    })
    .catch(() => { el.textContent = msg; })
    .finally(() => clearTimeout(timeout));
})();
