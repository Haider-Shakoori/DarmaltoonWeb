/* =========================================================
   Darmaltoon — Form validation (frontend only)
   ========================================================= */

(function () {
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const PHONE_RE = /^[+()\-\s\d]{6,}$/;

  function setError(input, message) {
    const field = input.closest(".field");
    const errorEl = document.querySelector('[data-error-for="' + input.id + '"]');
    if (field) field.classList.add("has-error");
    if (errorEl) errorEl.textContent = message || "";
  }

  function clearError(input) {
    const field = input.closest(".field");
    const errorEl = document.querySelector('[data-error-for="' + input.id + '"]');
    if (field) field.classList.remove("has-error");
    if (errorEl) errorEl.textContent = "";
  }

  function validateField(input, rules) {
    clearError(input);
    const value = (input.value || "").trim();
    if (input.type === "checkbox") {
      if (input.required && !input.checked) {
        setError(input, "Please confirm to continue.");
        return false;
      }
      return true;
    }
    if (input.required && !value) {
      setError(input, "This field is required.");
      return false;
    }
    if (!value) return true;
    if (input.type === "email" && value && !EMAIL_RE.test(value)) {
      setError(input, "Please enter a valid email.");
      return false;
    }
    if (input.type === "tel" && value && !PHONE_RE.test(value)) {
      setError(input, "Please enter a valid phone number.");
      return false;
    }
    if (rules) {
      for (const r of rules) {
        const msg = r(input, value);
        if (msg) { setError(input, msg); return false; }
      }
    }
    return true;
  }

  function collectFormData(form) {
    const fd = new FormData(form);
    const data = {};
    fd.forEach((v, k) => { data[k] = v; });
    return data;
  }

  function initDemoForm() {
    const form = document.getElementById("demoForm");
    if (!form) return;
    const success = document.getElementById("demoSuccess");
    const inputs = form.querySelectorAll("input, select, textarea");

    inputs.forEach((input) => {
      input.addEventListener("blur", () => validateField(input));
      input.addEventListener("input", () => {
        if (input.closest(".field")?.classList.contains("has-error")) validateField(input);
      });
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      let valid = true;
      inputs.forEach((input) => { if (!validateField(input)) valid = false; });

      if (!valid) {
        const first = form.querySelector(".has-error input, .has-error select, .has-error textarea");
        if (first) first.focus();
        return;
      }

      const payload = collectFormData(form);

      // TODO: Connect demo request to backend endpoint.
      console.info("[Darmaltoon] Demo form payload (not submitted):", payload);

      if (success) {
        success.hidden = false;
        success.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      form.reset();
    });
  }

  function initContactForm() {
    const form = document.getElementById("contactForm");
    if (!form) return;
    const success = document.getElementById("contactSuccess");
    const inputs = form.querySelectorAll("input, select, textarea");

    inputs.forEach((input) => {
      input.addEventListener("blur", () => validateField(input));
      input.addEventListener("input", () => {
        if (input.closest(".field")?.classList.contains("has-error")) validateField(input);
      });
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      let valid = true;
      inputs.forEach((input) => { if (!validateField(input)) valid = false; });

      if (!valid) {
        const first = form.querySelector(".has-error input, .has-error select, .has-error textarea");
        if (first) first.focus();
        return;
      }

      const payload = collectFormData(form);

      // TODO: Connect contact form to backend endpoint.
      console.info("[Darmaltoon] Contact form payload (not submitted):", payload);

      if (success) {
        success.hidden = false;
        success.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      form.reset();
    });
  }

  ready(function () {
    initDemoForm();
    initContactForm();
  });
})();
