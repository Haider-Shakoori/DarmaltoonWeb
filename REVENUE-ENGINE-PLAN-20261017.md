# Darmaltoon revenue engine — launch blueprint (draft)
Date: 2026-10-17
Status: Commercial hypotheses and implementation plan, **NOT approved public pricing**.
Scope: Afghanistan pharmacy-management market. Marketing site: `DarmaltoonWeb`; SaaS backend: `Pharmacy`; Windows application: `PharmaDesktop`.

## Principle
Start from 0 verified paying pharmacies. First goal is 10 paying installations, then 25, 100, and ultimately 1,000. These are targets, not testimonials or existing clients. Sell verified functionality only. Keep site light-only and English/Dari/Pashto, and avoid the retired "Built for Afghan pharmacies" phrase. Do not publish fabricated traffic, customers, ROI, prices, or promised features.

## Baseline verified from repos
- Marketing site: `/demo.html` and contact/home forms POST to `/api/lead.php`; consent, honeypot, basic abuse limits; private SQLite `.darmaltoon-leads/leads.sqlite` with notification attempt flags. Analytics are anonymous aggregate and cannot identify genuine unique users or paid customers.
- Platform: central Laravel database separates plans, trial requests, subscriptions, activations, licenses and commercial data from per-tenant pharmacy databases. Plans already configure price/billing period, branches/users/Windows/Android seats, offline grace and optional features.
- Windows app: .NET/WPF offline-first SQLite deployment; validate each supported perpetual/annual/offline license and LAN scenario before offering as a commercial commitment.
- Known gap: public marketing leads are not currently evidenced as connected to a managed sales pipeline, demo outcome, quote, payment receipt, onboarding and renewals.

## Proposed offers (UNAPPROVED price-test hypotheses)
| Segment | Initial offer | Price hypothesis | Validation |
| - | - | - | - |
| 1-PC pharmacy | Essential: safe core POS, batch/expiry, stock, closing | 790 AFN/month | 10+ owner interviews, willingness to pay |
| 2+ workstations | Professional: LAN, more Windows seats, optional sync, reports | 1,490 AFN/month | run paid pilot; verify feature gates |
| Chain | Enterprise: multi-branch, migration, priority support | case-by-case quotation | discovery call and written SOW |
| Fully offline | annual paid desktop license + separately priced maintenance | TBD | offline activation/renewal QA without internet |

Never gate medicine safety controls, stock audit integrity, POS closing, or access to export of the customer's own data behind premium upsell. Respect actual supported features. Annual payment discounted only after commercial validation. Setup/import/training billed separately when stated clearly.

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
6. Interview at least 10 Kabul pharmacies; record size, branch count, computers, losses from expiries, preferred billing/payment frequency, willingness to pay. No fake social proof.
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
- A/B test no more than one price or onboarding variable at a time, document sample sizes.

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
MRR = sum of paid recurring subscriptions normalized to months; exclude setup fees, unpaid invoices, trial accounts and one-time license sales.
Annualized run-rate = 12 × current MRR (not booked revenue or profit). Revenue targets at constant 1,490 AFN monthly ARPA: 10=14,900 AFN, 25=37,250, 100=149,000, 1000=1,490,000. All hypothetical gross recurring revenue, excluding costs, churn and discounts.
Gross margin needs payment collection, server/support, travel/onboarding, acquisition, tax and customer care costs; measure by cohort. Do not promise profitability before real unit economics.

## Acceptance gates
- No breaking changes to existing website/Pharmacy/Desktop deployments; no public price publishing before sign-off.
- Every qualified lead has a stage, owner, next follow-up and optional lost reason; PII never leaks into public analytics.
- Reports distinguish leads/demo/trial/invoice/collected payment/activated pharmacy.
- Subscription expiry and fully offline paid operation tested in a disconnected Windows environment.
- Tests and CI green before feature merges, then backup + staged deployment + smoke test.
