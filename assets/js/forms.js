/* Darmaltoon — localized client validation, private lead intake and email fallback. */

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
    const url = "mailto:info@darmaltoon.com?subject=" + encodeURIComponent(subject)
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

  function leadPayload(form, kind) {
    const f = collectFormData(form);
    const read = key => String(f[key] || "").trim();
    const lang = document.documentElement.lang === "fa" ? "fa"
      : document.documentElement.lang === "ps" ? "ps" : "en";
    return {
      kind, language:lang, website:read("website"),
      consent:kind === "demo" ? !!form.querySelector('input[name="agree"]')?.checked
        : !!form.querySelector('input[name="contactConsent"]')?.checked,
      name:read("fullName"), phone:read("phone"), email:read("email"),
      pharmacy:read("pharmacyName") || read("company"), message:read("message"),
      whatsapp:read("whatsapp"), province:read("province"), city:read("city"),
      computers:read("computers"), preferredContact:read("preferredContact"),
      subject:read("subject"), inquiryType:read("inquiryType")
    };
  }

  async function submitLead(form, box, kind) {
    const payload = leadPayload(form, kind);
    const button = form.querySelector('button[type="submit"]');
    const lang = payload.language;
    const received = {
      en:"Your request has been received and saved. We will use your contact details to follow up.",
      fa:"درخواست شما دریافت و ثبت شد. برای پاسخ با شما تماس خواهیم گرفت.",
      ps:"ستاسو غوښتنه ترلاسه او ثبت شوه. د ځواب لپاره به له تاسو سره اړیکه ونیسو."
    };
    const tooMany = {
      en:"Please wait before sending another request.",
      fa:"لطفاً پیش از ارسال درخواست دیگر کمی صبر کنید.",
      ps:"مهرباني وکړئ د بلې غوښتنې تر لېږلو لږ انتظار وکړئ."
    };
    if (button) button.disabled = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch("/api/lead.php", {
        method:"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},
        body:JSON.stringify(payload),signal:controller.signal,credentials:"same-origin"
      });
      const result = await response.json();
      if (response.ok && result.received === true) {
        if (box) {
          box.hidden = false;box.classList.remove("form-unavailable","form-draft");
          box.classList.add("form-draft");box.setAttribute("role","status");
          box.textContent = received[lang] || received.en;
        }
        form.reset();
      } else if (response.status === 429) {
        if (box) {
          box.hidden=false;box.setAttribute("role","alert");box.classList.add("form-draft");
          box.textContent=tooMany[lang]||tooMany.en;
        }
      } else {
        prepareEmailDraft(form,box,kind);
      }
    } catch (err) {
      prepareEmailDraft(form,box,kind);
    } finally {
      window.clearTimeout(timeout);
      if (button) button.disabled = false;
    }
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

      // The server confirms durable storage before a success message is shown.
      void submitLead(form, success, "demo");
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

      // Avoid claiming success until the lead endpoint confirms receipt.
      void submitLead(form, success, "contact");
    });
  }

  ready(function () {
    initDemoForm();
    initContactForm();
  });
})();
