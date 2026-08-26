# Opt-In Site

Static, privacy-conscious landing page for the Ambiguous Payment Recovery Kit.

Expected GitHub Pages URL after a successful deployment:

```text
https://safal207.github.io/valta-pilot-lab/
```

## Local preview

```bash
python -m http.server 8080 -d site
```

Open `http://localhost:8080`.

## Submission behavior

The page never stores form data in the repository.

`site/config.js` supports two modes:

1. **Consent-aware form endpoint** — set `formEndpoint` and choose `submissionMode: "form"` or `"json"`.
2. **Email fallback** — while the endpoint is empty, the browser opens a prefilled opt-in email to the configured address.

Do not place a Resend, ConvertKit, Buttondown, Beehiiv, Mailchimp, or other secret API key in frontend JavaScript. Use a provider-hosted public form action or a serverless endpoint that keeps secrets server-side.

## Partner attribution

Use consent-based partner links:

```text
https://safal207.github.io/valta-pilot-lab/?ref=partner-slug&utm_source=newsletter&utm_medium=partner&utm_campaign=ambiguous-payment-recovery
```

The form passes `ref` and standard UTM values to the configured endpoint. The static page enables no advertising tracker by default.

## Validate

```bash
python scripts/validate_site.py
```

## CI package

Every successful validation run uploads a 30-day workflow artifact named:

```text
ambiguous-payment-recovery-site
```

This provides a reviewable static bundle even before GitHub Pages is enabled.

## One-time GitHub Pages bootstrap

GitHub's standard `GITHUB_TOKEN` can deploy an existing Pages site but cannot create the Pages site for a repository that has never enabled it.

Complete the one-time repository setup:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **Source: GitHub Actions**.
3. Open **Settings → Secrets and variables → Actions → Variables**.
4. Create repository variable:

```text
PAGES_ENABLED=true
```

5. Run the **Opt-in site** workflow manually with `deploy=true`, or merge any later site change to `main`.

Until `PAGES_ENABLED=true`, CI remains green, packages the site as an artifact, and emits a notice instead of failing deployment.

## Automated deployment

After the bootstrap, `.github/workflows/optin-site.yml` validates and packages every relevant change and deploys `site/` to GitHub Pages from `main`.
