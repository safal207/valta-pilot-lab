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

## Deployment

`.github/workflows/optin-site.yml` validates pull requests and deploys the `site/` directory to GitHub Pages after a merge to `main`.

The repository may still require GitHub Pages to be configured with **Source: GitHub Actions** in repository settings. If the deployment job reports that Pages is not enabled, enable that setting and rerun the workflow.
