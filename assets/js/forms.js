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

  // No form backend is configured. This uses the visitor's own email app,
  // never claiming a lead has been sent or storing sensitive form data here.
  function prepareEmailDraft(form, box, kind) {
    const data = collectFormData(form);
    const get = (key) => String(data[key] || "").trim().slice(0, 550);
    const name = get("fullName");
    const subject = kind === "demo"
      ? "Darmaltoon demo request — " + (get("pharmacyName") || "Pharmacy")
      : "Darmaltoon enquiry — " + (get("subject") || "New message");
    const fields = kind === "demo"
      ? [["Name",name],["Pharmacy",get("pharmacyName")],["Phone",get("phone")],
         ["WhatsApp",get("whatsapp")],["Email",get("email")],["Province",get("province")],
         ["City",get("city")],["Computers",get("computers")],
         ["Preferred language",get("preferredLanguage")],["Preferred contact",get("preferredContact")],
         ["Message",get("message")]]
      : [["Name",name],["Pharmacy / company",get("company")],["Phone",get("phone")],
         ["Email",get("email")],["Subject",get("subject")],["Enquiry type",get("inquiryType")],
         ["Message",get("message")]];
    const body = fields.filter(pair => pair[1]).map(pair => pair[0] + ": " + pair[1])
      .concat(["","Prepared through the Darmaltoon website. Please press Send in your email app."])
      .join("\n");
    const url = "mailto:info@businessos.af?subject=" + encodeURIComponent(subject)
      + "&body=" + encodeURIComponent(body);
    const lang = document.documentElement.getAttribute("lang");
    const messages = {
      en:"Your email application should open with this draft. Nothing has been sent yet.",
      fa:"برنامه ایمیل با پیش‌نویس باز می‌شود. تا زمانی که ارسال نکنید، هیچ چیزی فرستاده نشده است.",
      ps:"ستاسو د ایمیل پروګرام باید له مسودې سره پرانیستل شي. تر اوسه هېڅ پیغام نه دی استول شوی."
    };
    if (box) {
      box.hidden = false;
      box.classList.remove("form-unavailable");
      box.classList.add("form-draft");
      box.setAttribute("role","status");
      box.replaceChildren();
      const text = document.createElement("span");
      text.textContent = messages[lang] || messages.en;
      box.append(text," ");
      const link = document.createElement("a");
      link.href = url;
      link.textContent = lang === "fa" ? "باز کردن دوباره پیش‌نویس ایمیل"
        : lang === "ps" ? "د ایمیل مسوده بیا پرانیزئ"
        : "Open email draft again";
      box.append(link);
    }
    window.location.href = url;
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
      prepareEmailDraft(form, success, "demo");
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
      prepareEmailDraft(form, success, "contact");
    });
  }

  ready(function () {
    initDemoForm();
    initContactForm();
  });
})();
