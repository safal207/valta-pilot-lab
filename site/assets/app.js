(() => {
  "use strict";

  const config = window.VT_CONFIG || {};
  const form = document.querySelector("[data-optin-form]");
  if (!form) return;

  const status = document.querySelector("[data-form-status]");
  const fallbackLink = document.querySelector("[data-fallback-link]");
  const submitButton = form.querySelector('button[type="submit"]');
  const trackingKeys = [
    "ref",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term"
  ];
  const params = new URLSearchParams(window.location.search);

  trackingKeys.forEach((key) => {
    const input = form.querySelector(`[name="${key}"]`);
    if (input) input.value = params.get(key) || "";
  });

  const partner = params.get("ref");
  const partnerNote = document.querySelector("[data-partner-note]");
  if (partner && partnerNote) {
    partnerNote.textContent = `Shared by partner: ${partner}`;
    partnerNote.hidden = false;
  }

  const setStatus = (message, kind = "info") => {
    if (!status) return;
    status.textContent = message;
    status.dataset.kind = kind;
    status.hidden = false;
  };

  const getPayload = () => {
    const data = new FormData(form);
    const payload = Object.fromEntries(data.entries());
    payload.consent = data.get("consent") === "yes";
    payload.campaign = config.campaign || "ambiguous-payment-recovery";
    payload.source = config.source || "github-pages";
    payload.submitted_at = new Date().toISOString();
    payload.page = window.location.href.split("#")[0];
    return payload;
  };

  const safeSuccessUrl = () => {
    const target = new URL(config.successPath || "thanks.html", window.location.href);
    trackingKeys.forEach((key) => {
      const value = params.get(key);
      if (value) target.searchParams.set(key, value);
    });
    return target.toString();
  };

  const submitToEndpoint = async (payload) => {
    const mode = config.submissionMode === "json" ? "json" : "form";
    const options = {
      method: "POST",
      headers: {
        Accept: "application/json"
      }
    };

    if (mode === "json") {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(payload);
    } else {
      options.headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8";
      options.body = new URLSearchParams(
        Object.entries(payload).map(([key, value]) => [key, String(value)])
      ).toString();
    }

    const response = await fetch(config.formEndpoint, options);
    if (!response.ok) {
      throw new Error(`Subscription endpoint returned ${response.status}`);
    }
  };

  const openEmailFallback = (payload) => {
    const recipient = config.fallbackEmail || "safal0645@gmail.com";
    const subject = "Ambiguous Payment Recovery Kit request";
    const body = [
      "Please send me the Ambiguous Payment Recovery Kit and up to three educational follow-up emails.",
      "",
      `Work email: ${payload.email}`,
      `Company: ${payload.company || "Not provided"}`,
      `Unknown transition: ${payload.transition}`,
      `Partner/ref: ${payload.ref || "Direct"}`,
      `Campaign: ${payload.campaign}`,
      "",
      "Consent: yes. I understand I can unsubscribe at any time."
    ].join("\n");

    const mailto = `mailto:${encodeURIComponent(recipient)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    if (fallbackLink) {
      fallbackLink.href = mailto;
      fallbackLink.hidden = false;
    }
    window.location.href = mailto;
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) return;

    const payload = getPayload();
    if (!payload.consent) {
      setStatus("Please confirm consent so the kit and educational follow-ups can be sent.", "error");
      return;
    }

    submitButton.disabled = true;
    submitButton.setAttribute("aria-busy", "true");
    setStatus("Preparing your kit…", "info");

    try {
      if (config.formEndpoint) {
        await submitToEndpoint(payload);
        sessionStorage.setItem("vt_kit_requested", "yes");
        window.location.assign(safeSuccessUrl());
        return;
      }

      openEmailFallback(payload);
      sessionStorage.setItem("vt_kit_requested", "email-fallback");
      setStatus(
        "Your email app should open with a prefilled opt-in request. Send it, then use the resource link below.",
        "success"
      );
    } catch (error) {
      console.error(error);
      openEmailFallback(payload);
      setStatus(
        "The subscription endpoint was unavailable, so a prefilled email fallback has been opened. No form data was stored on this site.",
        "error"
      );
    } finally {
      submitButton.disabled = false;
      submitButton.removeAttribute("aria-busy");
    }
  });
})();
