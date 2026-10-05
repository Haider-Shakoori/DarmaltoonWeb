/* =========================================================
   Darmaltoon — Language switching + localization
   ========================================================= */

(function () {
  const STORAGE_KEY = "darmaltoon.lang";
  const SUPPORTED = ["en", "fa", "ps"];
  const RTL_LANGS = ["fa", "ps"];

  function getTranslations() {
    return window.DARMALTOON_I18N || {};
  }

  function getStoredLang() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored && SUPPORTED.includes(stored)) return stored;
    } catch (e) {}
    return "en";
  }

  function applyTranslations(lang) {
    const dict = getTranslations()[lang] || getTranslations().en || {};
    const fallback = getTranslations().en || {};

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const value = dict[key] || fallback[key];
      if (typeof value === "string") {
        el.textContent = value;
      }
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      const value = dict[key] || fallback[key];
      if (typeof value === "string") el.setAttribute("placeholder", value);
    });
  }

  function applyDirection(lang) {
    const dir = RTL_LANGS.includes(lang) ? "rtl" : "ltr";
    document.documentElement.setAttribute("lang", lang === "fa" ? "fa" : lang === "ps" ? "ps" : "en");
    document.documentElement.setAttribute("dir", dir);
  }

  function setActiveButtons(lang) {
    document.querySelectorAll("[data-lang]").forEach((btn) => {
      btn.classList.toggle("is-active", btn.getAttribute("data-lang") === lang);
      btn.setAttribute("aria-pressed", btn.getAttribute("data-lang") === lang ? "true" : "false");
    });
  }

  function setLanguage(lang) {
    if (!SUPPORTED.includes(lang)) lang = "en";
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
    applyDirection(lang);
    applyTranslations(lang);
    setActiveButtons(lang);
    document.dispatchEvent(new CustomEvent("darmaltoon:langchange", { detail: { lang } }));
  }

  function bindSwitchers() {
    document.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-lang]");
      if (!btn) return;
      setLanguage(btn.getAttribute("data-lang"));
    });
  }

  function init() {
    bindSwitchers();
    setLanguage(getStoredLang());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.DarmaltoonLang = { setLanguage, getStoredLang };
})();
