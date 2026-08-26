# Opt-In Site

Privacy-conscious landing page for the Ambiguous Payment Recovery Kit.

## Live URL

Use this address for public traffic, partner mentions, and opt-in links:

```text
https://ambiguous-payment-recovery-kit.lovable.app/
```

Example partner-attributed link:

```text
https://ambiguous-payment-recovery-kit.lovable.app/?ref=partner-slug&utm_source=newsletter&utm_medium=partner&utm_campaign=ambiguous-payment-recovery
```

A static mirror is also maintained in `site/` and packaged by GitHub Actions. GitHub Pages remains an optional secondary host after its one-time repository setting is enabled.

## Local preview

```bash
python -m http.server 8080 -d site
```

Open `http://localhost:8080`.

## Submission behavior

The page does not store form data in the repository.

The current public site and the static mirror use a transparent email fallback: the browser opens a prefilled opt-in email containing the submitted fields, consent statement, partner ref, and UTM attribution. A consent-aware provider endpoint may be connected later.

Do not place a Resend, Kit, Buttondown, Beehiiv, Mailchimp, or other secret API key in frontend JavaScript. Use a provider-hosted public form action or a serverless endpoint that keeps secrets server-side.

## Partner attribution

The form preserves:

```text
ref
utm_source
utm_medium
utm_campaign
```

No advertising tracker is enabled by default. Subscriber addresses must not be transferred to partners.

## Validate

```bash
python scripts/validate_site.py
```

## CI package

Every successful validation run uploads a 30-day workflow artifact named:

```text
ambiguous-payment-recovery-site
```

This provides a reviewable static bundle independently of the public host.

## Optional GitHub Pages mirror

Expected mirror URL after bootstrap:

```text
https://safal207.github.io/valta-pilot-lab/
```

GitHub's standard `GITHUB_TOKEN` can deploy an existing Pages site but cannot create a Pages site for a repository that has never enabled it.

Complete the one-time setup only when the mirror is needed:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **Source: GitHub Actions**.
3. Open **Settings → Secrets and variables → Actions → Variables**.
4. Create repository variable `PAGES_ENABLED=true`.
5. Run the **Opt-in site** workflow manually with `deploy=true`, or merge a later site change to `main`.

Until then, CI remains green, packages the site as an artifact, and skips Pages deployment. The Lovable URL remains the canonical public destination.
