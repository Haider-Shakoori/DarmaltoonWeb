# Darmaltoon revenue engine — launch blueprint (draft)
Date: 2026-10-17
Status: Owner-confirmed launch price and one-pharmacy scope; implementation readiness and public publication still require verification.
Scope: Afghanistan pharmacy-management market. Marketing site: `DarmaltoonWeb`; SaaS backend: `Pharmacy`; Windows application: `PharmaDesktop`.

## Principle
Start from 0 verified paying pharmacies. First goal is 10 paying installations, then 25, 100, and ultimately 1,000. These are targets, not testimonials or existing clients. Sell verified functionality only. Keep site light-only and English/Dari/Pashto, and avoid the retired "Built for Afghan pharmacies" phrase. Do not publish fabricated traffic, customers, ROI, prices, or promised features.

## Baseline verified from repos
- Marketing site: `/demo.html` and contact/home forms POST to `/api/lead.php`; consent, honeypot, basic abuse limits; private SQLite `.darmaltoon-leads/leads.sqlite` with notification attempt flags. Analytics are anonymous aggregate and cannot identify genuine unique users or paid customers.
- Platform: central Laravel database separates plans, trial requests, subscriptions, activations, licenses and commercial data from per-tenant pharmacy databases. Plans already configure price/billing period, branches/users/Windows/Android seats, offline grace and optional features.
- Windows app: .NET/WPF offline-first SQLite deployment; validate each supported perpetual/annual/offline license and LAN scenario before offering as a commercial commitment.
- Known gap: public marketing leads are not currently evidenced as connected to a managed sales pipeline, demo outcome, quote, payment receipt, onboarding and renewals.

## Confirmed launch prices (owner decision, 2026-10-17)
- **AFN 5,000 for the first 12 months of a standard license for one pharmacy location (one branch).**
- **AFN 3,000 for each subsequent 12-month renewal for the same pharmacy location.**
- Year 1 and annual renewal are *not* monthly subscriptions. Do not market the above as monthly.
- Renewal represents a 40% discount relative to year 1. No separate onboarding/setup component has been promised or priced.
- **Exactly one pharmacy location / one branch, one registered Windows PC, and up to two registered Android POS phones/tablets on that same pharmacy subscription are included.** Neither Windows PC #2 nor Android device #3 nor a second branch is included. Staff user count and optional cloud/hosting services remain separately unconfirmed. The existing Windows and Android software must pass mixed-device sync and stock consistency QA before promising a fully shared local inventory or offline multi-device mode. Installation/training, support hours, migration, disconnected renewal/activation, grace/recovery, refunds and price changes require published terms.
- Additional pharmacy locations / branches require their own license or a separately approved commercial arrangement; exact multi-location price and policy are **not yet approved**. Extra devices, premium support and integrations may need separately quoted pricing.
- Keep safety-critical controls (expiry integrity, audited stock movement, Daily Closing and export of customer data) available in the base licensed product.
- Configure the named commercial Standard plan with `currency=AFN`, `billing_period=yearly`, `max_branches=1`, `max_windows_devices=1`, and `max_android_devices=2`; preserve existing customer plans and trials. Existing one-time Windows activation remains suitable for the single included PC; verify two separate Android activations, reject a third, and enforce one branch. Crucially validate Android/Windows sync topology and FEFO stock correctness before advertising any connected mobile POS workflow. See `Haider-Shakoori/Pharmacy/docs/darmaltoon-standard-license.md` (pending replacement PR).
- Confirm commercial invoices/receipts and verified collected payments, not plans or uncollected invoices, are counted as revenue.
- These are owner-set launch prices, not validated willingness-to-pay or a claim of current production availability.

## Sales funnel and metrics
**Source (non-PII aggregate) -> qualified lead -> contact made -> demo scheduled -> demo completed -> trial approved -> paid -> activated/onboarded -> renewed/upgraded**.
Track optional quote sent, lost reason, owner, next task, promised follow-up and invoice payment status.
Do NOT place pharmacy owner contact details, patient data or raw visitor IP in marketing analytics. Keep PII behind authenticated platform admin, apply retention and access controls.
Prospect conversion and paid revenue are different from page views: calculate true lead-to-paid rate, demo-to-paid, MRR/ARR, ARPA, gross churn, net retention, CAC, payback and unpaid renewals from commercial records only. Attribute UTM campaign and channel after validation and consent; search terms/impressions require GSC aggregate integration, not fake user keyword inference. Filter own activity and bots from website reports and report uncertainty accurately.

## First 14 days — Phase 0, commercial readiness
1. Confirm all key demo, contact and WhatsApp CTAs work on mobile and RTL (EN, Dari, Pashto).
2. Verify leads.sqlite writes and email delivery end-to-end; test failure and retry handling; do not expose it to public endpoints.
3. Add sales-lead status and owner follow-up through authenticated platform-side CRM or tightly authorized private owner tool, not marketing public HTML. Existing lead storage remains authoritative until a verified idempotent import is deployed.
4. Review actual licensing, 7-day trials, provisioning, installer SmartScreen/codesigning, multi-PC and fully offline renewal. No marketing claim until tested.
5. Draft customer onboarding checklist: demo account, medicine master CSV, opening balances, receipt template, employee training, signed acceptance, backup/export demonstration.
6. Interview at least 10 Kabul pharmacies; record size, branch count, computers, losses from expiries, responses to the set 5,000 AFN initial / 3,000 AFN renewal prices, willingness to pay, and renewal objections. Do not change owner-approved prices without a new decision. No fake social proof.
7. Write one-page EN/Dari/Pashto offer and 3-minute walkthrough using verified, sanitized app screenshots, not image-only text.

## Days 15–30 — Phase 1, first revenue
- Direct outreach to 10 qualified owners a week; track conversations and demos.
- First 10 paid pilots: collect documented offer acceptance and invoice/receipt; avoid recording amounts as paid until reconciled.
- Make payment methods practical for Afghan customers: manually confirmed cash/bank transfer where permitted, without claiming a live online payment gateway; add audited payment status to platform. Company funds kept separate from tenant POS accounting.
- Produce owner training, support FAQ, and lightweight onboarding videos; support Windows local installation first.
- Define refunds/cancellation, device transfer, renewal reminders, license recovery, and customer data export policy.

## Days 31–60 — Phase 2, conversion and repeatability
- Add private sales/revenue dashboard: qualified leads, stage conversion, response time, installs, active trials, paid, renewals due (7/30 days), failed payment follow-up, MRR and churn.
- Establish monthly customer interviews and referrals (no incentives that compromise medical purchasing).
- Publish customer-approved case studies only after signed permission; earn searchable product-intent content for pharmacy software, stock, expiry and offline POS in all 3 languages.
- A/B test onboarding copy and offers without unapproved pricing changes; document sample sizes.

## Days 61–90 — Phase 3, channel scalability
- Start field resellers/installation technicians with written commission paid on collected revenue, clear pricing, reversible license issue workflows.
- Pilot chains and distributor referrals; avoid selling patient data, medication purchase profiles, or public pharma ads disguised as advice.
- Implement renewal and collections reporting; qualify expansion after support load and churn are understood.
- Validate SaaS security: tenant scoping, billing idempotency, signed licenses, privacy compliance and disaster recovery.

## Prioritized backlog
P0. Secure leads-to-platform CRM import/status history and owner tasks with deduplication and consent.
P0. Payment ledger for Darmaltoon commercial invoices/receipts (central database only); manual payment verification before activation; no fake Stripe/DAB integration.
P0. Paid conversion/renewal dashboard and license state consistency between Laravel and Windows.
P0. Correct lead source/campaign attribution and owner/bot filtering; GSC query data as aggregate only.
P1. 7/3/1-day renewal reminders with consented WhatsApp/email where compliant, sent only when opt-in and delivery provider is verified.
P1. Trial-to-paid onboarding screens, signed acceptance, migration CSV, and support handoff.
P1. Localized landing-page proof (verified screenshots, real flows), FAQ and SEO.
P2. Branch/chain account management, sales partner program and advanced analytics upsells.
P3. Optional wholesaler integration subject to regulation, security, partnership approval and proof of value. No patient data monetization.

## Financial model
Annual customer cash collection is billed at 5,000 AFN for the first year, 3,000 AFN for the annual renewal from year two onward. Hypothetical full collection, no churn: 10 clients = 50,000 AFN first-year / 30,000 AFN subsequent renewal-year receipts; 25 = 125,000 / 75,000; 100 = 500,000 / 300,000; 1,000 = 5,000,000 / 3,000,000. These are cohort illustrations, not forecasts or realized revenue. New customers in later years each still start with 5,000 AFN. Revenue recognition may differ from cash collection and should be accrued over the service period. Do not treat annual invoices as monthly cash collections; if useful, describe the 5,000 / 12 and 3,000 / 12 monthly equivalents as ratios only.
Gross margin needs payment collection, server/support, travel/onboarding, acquisition, tax and customer care costs; measure by cohort. Do not promise profitability before real unit economics.

## Acceptance gates
- No breaking changes to existing website/Pharmacy/Desktop deployments; no public price publishing before sign-off.
- Every qualified lead has a stage, owner, next follow-up and optional lost reason; PII never leaks into public analytics.
- Reports distinguish leads/demo/trial/invoice/collected payment/activated pharmacy.
- Subscription expiry and fully offline paid operation tested in a disconnected Windows environment.
- Tests and CI green before feature merges, then backup + staged deployment + smoke test.
