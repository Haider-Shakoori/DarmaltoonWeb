"""Regression contract for the consolidated Darmaltoon marketing enquiry form."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
demo = (ROOT / "demo.html").read_text(encoding="utf-8")
forms = (ROOT / "assets/js/forms.js").read_text(encoding="utf-8")
intake = (ROOT / "api/lead.php").read_text(encoding="utf-8")
sync = (ROOT / "scripts/sync_leads_to_platform.php").read_text(encoding="utf-8")
translations = (ROOT / "assets/js/translations.js").read_text(encoding="utf-8")
analytics = (ROOT / "api/analytics-store.php").read_text(encoding="utf-8")
offer = (ROOT / "api/founding-offer.php").read_text(encoding="utf-8")

for token in ['id="demoForm"', 'name="requestType"', 'value="demo"', 'value="trial"', 'name="email"', 'name="pharmacyName"', 'id="dTrialHelp"']:
    assert token in demo, f"Missing unified enquiry form element: {token}"

for token in ['kind === "trial"', 'email.required = trial', 'submitLead(form, success, selected)', 'fetch("/api/lead.php"']:
    assert token in forms, f"Missing trial client validation or submission: {token}"

assert "['demo', 'contact', 'trial']" in intake
assert "Email and pharmacy are required for a trial request" in intake
assert "$db->commit();" in intake
assert "'trial_requested'" in analytics
assert "PDO::PARAM_INT" in sync
assert "'kind' => (string) $row['kind']" in sync
assert "'trial.requestType'" in translations and '"trial.trialOption"' in translations
assert "'fa-AF'" not in forms  # UI uses supported short language keys en/fa/ps.
assert "API" not in offer or "api" in offer  # proxy is isolated from admin data.
assert "Authorization: Bearer" not in demo and "password" not in forms.lower().split("function leadPayload")[1].split("async function submitLead")[0]
for path in ("index.html", "fa/index.html", "ps/index.html", "demo.html"):
    text = (ROOT / path).read_text(encoding="utf-8")
    assert "data-founding-availability" in text, path
    assert "/assets/js/founding-offer.js" in text, path

print("Unified demo / 7-day trial and founding-offer site contract passed.")
