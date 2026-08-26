from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

REQUIRED = {
    "index.html",
    "thanks.html",
    "privacy.html",
    "404.html",
    "config.js",
    "assets/styles.css",
    "assets/app.js",
    "downloads/ambiguous-payment-recovery-self-test.txt",
    "downloads/cross-system-payment-proof-card.txt",
    "downloads/cross-system-proof-sample.json",
}

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bsk_[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(r"api[_-]?key\s*[:=]\s*[\"'][^\"']{12,}[\"']", re.IGNORECASE),
]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.forms: list[dict[str, str]] = []
        self.inputs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])
        if tag in {"a", "link", "script"}:
            key = "href" if tag in {"a", "link"} else "src"
            if values.get(key):
                self.links.append((tag, values[key]))
        if tag == "form":
            self.forms.append(values)
        if tag in {"input", "textarea"} and values.get("name"):
            self.inputs.add(values["name"])


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def is_external(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "mailto", "tel", "data"} or value.startswith("//")


def validate_html(path: Path) -> list[str]:
    errors: list[str] = []
    parser = LinkParser()
    text = path.read_text(encoding="utf-8")
    parser.feed(text)

    if "<title>" not in text:
        errors.append(f"{path.relative_to(ROOT)} has no <title>")

    for _, link in parser.links:
        if not link or is_external(link):
            continue
        target_part, _, anchor = link.partition("#")
        target = path if not target_part else (path.parent / target_part).resolve()
        if target_part and not target.exists():
            errors.append(f"{path.relative_to(ROOT)} links to missing {target_part}")
        if anchor and target.exists() and target.suffix == ".html":
            target_parser = LinkParser()
            target_parser.feed(target.read_text(encoding="utf-8"))
            if anchor not in target_parser.ids:
                errors.append(
                    f"{path.relative_to(ROOT)} links to missing anchor #{anchor} in "
                    f"{target.relative_to(ROOT)}"
                )

    if path.name == "index.html":
        required_inputs = {"email", "company", "transition", "consent", "ref", "utm_source"}
        missing = required_inputs - parser.inputs
        if missing:
            errors.append(f"index.html missing form fields: {sorted(missing)}")
        if "data-optin-form" not in text:
            errors.append("index.html missing data-optin-form hook")
        if 'href="privacy.html"' not in text:
            errors.append("index.html missing privacy link")

    return errors


def main() -> int:
    errors: list[str] = []

    for relative in sorted(REQUIRED):
        if not (SITE / relative).exists():
            errors.append(f"missing required site file: {relative}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret in {path.relative_to(ROOT)}: {pattern.pattern}")

    for path in SITE.glob("*.html"):
        errors.extend(validate_html(path))

    proof_path = SITE / "downloads/cross-system-proof-sample.json"
    if proof_path.exists():
        try:
            proof = json.loads(proof_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid proof JSON: {exc}")
        else:
            required_keys = {
                "schema",
                "status",
                "scenario",
                "control_evidence",
                "economic_observation",
                "verdict",
                "claim_boundary",
                "non_claims",
            }
            missing = required_keys - proof.keys()
            if missing:
                errors.append(f"proof JSON missing keys: {sorted(missing)}")
            if proof.get("status") != "PUBLIC_SANDBOX_SUMMARY":
                errors.append("proof JSON must identify itself as PUBLIC_SANDBOX_SUMMARY")

    config_path = SITE / "config.js"
    if config_path.exists():
        config_text = config_path.read_text(encoding="utf-8")
        if "Never place secret API keys here" not in config_text:
            errors.append("config.js must preserve the frontend-secret warning")
        if re.search(r'formEndpoint:\s*"https?://', config_text):
            print("INFO: a live form endpoint is configured; verify its privacy and consent behavior.")

    if errors:
        for error in errors:
            fail(error)
        return 1

    print("Static opt-in site validation: PASS")
    print(f"Checked {len(list(SITE.glob('*.html')))} HTML pages and {len(REQUIRED)} required files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
