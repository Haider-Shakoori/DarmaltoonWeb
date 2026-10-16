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

  function showNotConfigured(box) {
    if (!box) return;
    const lang = document.documentElement.getAttribute("lang");
    box.textContent = lang === "ps"
      ? "دا فورم لا نه دی نښلول شوی؛ ستاسو معلومات نه دي استول شوي. مهرباني وکړئ وروسته بیا هڅه وکړئ."
      : lang === "fa"
      ? "این فورم هنوز وصل نشده است؛ اطلاعات شما ارسال نشده است. لطفاً بعداً دوباره تلاش کنید."
      : "This form is not connected yet. Your details have NOT been sent. Please check back later.";
    box.hidden = false;
    box.setAttribute("role", "alert");
    box.classList.add("form-unavailable");
    box.scrollIntoView({ behavior: "smooth", block: "center" });
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

      // No submission endpoint is configured. Never imply that the lead was delivered.
      showNotConfigured(success);
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

      // No submission endpoint is configured. Never imply that a message was sent.
      showNotConfigured(success);
    });
  }

  ready(function () {
    initDemoForm();
    initContactForm();
  });
})();
