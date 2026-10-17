# Darmaltoon founding-customer website display

**Source-only / not yet deployed.** This is the website companion to the Laravel verified-payment rules in Pharmacy PR #104.

## Commercial wording

- First 10 **verified paying** pharmacies: AFN 5,000 first year.
- 11th onward: AFN 7,000 first year.
- All renewals: AFN 5,000/year (unless an existing customer has a separately honored contractual price).
- Standard entitlement: 1 pharmacy location, 1 Windows PC, 2 Android devices. Check actual device and sync readiness before public fulfilment.
- Demo inquiries and 7-day trials do **not** reserve a founding slot. A paid receipt recorded by an authorized Platform Admin is the only slot allocation event.

The English homepage `#pricing` explains these terms. The `data-founding-availability` element defaults to a neutral message until the platform provides a trustworthy aggregate; it does **not** fabricate a "remaining places" count.

## Site-side live aggregate proxy

`/api/founding-offer.php` has no customer data, payment receipt IDs, tokens or public lead-list access. It reads **one private config file outside the website document root**:

`/home/darmaltoon/.darmaltoon-leads/platform-offer.php` (permissions 0600):

```php
<?php
return [
    'url' => 'https://YOUR-VERIFIED-LARAVEL-API-HOST/api/v1/marketing/launch-offer',
];
```

The configured HTTPS host must actually serve the Laravel API on the intended endpoint. Do **not** point it at the new static marketing site, or the admin login HTML. This configuration is deployment-specific. PHP curl/TLS verification are required; remote redirect is disabled.

The response is validated as integer aggregates plus exact prices; the proxy returns only the allowlisted fields, or a generic 503 when unavailable. The browser JS will **not** show a numeric count when unavailable or inconsistent. Once real first payments are confirmed, the count changes from 10 to zero; it is not a reservation.

## Release gates

- Wait for the Laravel backend pricing PR's final CI and manual staging checks.
- Run website CI; lint `api/founding-offer.php`; test no private file, missing PHP curl, bad endpoint and valid aggregate endpoint.
- Verify the actual live 7-day trial form is connected to the platform before announcing that clicking Request Demo starts a trial; it currently does not.
- Activate the annual Standard plan only after customer/contract review, staff training, renewal price migration, and device compatibility tests.
- Update localized Dari and Pashto offer copy before marketing launch; root English is staged only in this PR.
- Do not delete the old pharmacy/API host until desktop/mobile license refresh dependencies are fully migrated.
