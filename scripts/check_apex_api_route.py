"""Regression guard: marketing PHP and Laravel versioned APIs coexist on main host."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rules = (root / ".htaccess").read_text()
assert "RewriteRule ^api/v1(?:/.*)?$ /platform/index.php [END,QSA,NC]" in rules
assert "RewriteRule ^api/.*" not in rules
assert "RewriteRule ^api/" not in rules.replace(
    "RewriteRule ^api/v1(?:/.*)?$ /platform/index.php [END,QSA,NC]", ""
)
for path in ("api/lead.php", "api/founding-offer.php", "api/analytics.php", "api/analytics-store.php"):
    assert (root / path).is_file(), f"Marketing API missing: {path}"
print("Darmaltoon apex API routing preserves marketing PHP entrypoints.")
