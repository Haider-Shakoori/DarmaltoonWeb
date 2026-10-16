/* Darmaltoon: lightweight progressive enhancement. Static SEO content needs no JS. */
(function () {
  "use strict";
  var root = document.documentElement;
  var store = "darmaltoon.ref.design";
  var query = new URLSearchParams(location.search).get("theme");
  var saved;
  try { saved = localStorage.getItem(store); } catch (e) { saved = null; }
  var initial = query === "dark" || query === "light" ? query : (saved === "dark" ? "dark" : "light");
  function render(theme) {
    root.setAttribute("data-design", theme);
    var control = document.getElementById("designSwitch");
    if (control) {
      control.textContent = theme === "dark" ? "☀ Light" : "☾ Dark";
      control.setAttribute("aria-pressed", String(theme === "dark"));
      control.setAttribute("title", theme === "dark" ? "Switch to the light reference design" : "Switch to the dark reference design");
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#061420" : "#e8f3ff");
  }
  render(initial);
  document.addEventListener("DOMContentLoaded", function () {
    render(root.getAttribute("data-design") || initial);
    var btn = document.getElementById("designSwitch");
    if (btn) btn.addEventListener("click", function () {
      var value = root.getAttribute("data-design") === "dark" ? "light" : "dark";
      try { localStorage.setItem(store, value); } catch (e) {}
      render(value);
    });
    document.querySelectorAll('a[href="#faq"]').forEach(function (link) {
      link.addEventListener("click", function (ev) {
        if (root.getAttribute("data-design") !== "dark") return;
        var darkFaq = document.getElementById("faq-dark");
        if (!darkFaq) return;
        ev.preventDefault();
        darkFaq.scrollIntoView({behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start"});
      });
    });
  });
})();
