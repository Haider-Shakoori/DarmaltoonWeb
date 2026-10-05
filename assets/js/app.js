/* =========================================================
   Darmaltoon — App interactions
   Mobile nav, sticky header, tabs, back-to-top, reveal
   ========================================================= */

(function () {
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  ready(function () {
    // ---- Mobile nav ----
    const menuToggle = document.getElementById("menuToggle");
    const mobileNav = document.getElementById("mobileNav");
    if (menuToggle && mobileNav) {
      menuToggle.addEventListener("click", () => {
        const isOpen = !mobileNav.hidden;
        mobileNav.hidden = isOpen;
        menuToggle.setAttribute("aria-expanded", String(!isOpen));
      });
      mobileNav.querySelectorAll("a").forEach((a) => {
        a.addEventListener("click", () => {
          mobileNav.hidden = true;
          menuToggle.setAttribute("aria-expanded", "false");
        });
      });
    }

    // ---- Sticky header ----
    const header = document.getElementById("siteHeader");
    if (header) {
      const onScroll = () => {
        header.classList.toggle("is-scrolled", window.scrollY > 8);
      };
      onScroll();
      window.addEventListener("scroll", onScroll, { passive: true });
    }

    // ---- Screenshot tabs ----
    const tabsRoot = document.getElementById("pdTabs");
    if (tabsRoot) {
      const tabs = tabsRoot.querySelectorAll(".tab");
      const panels = document.querySelectorAll(".tab-panel");
      tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
          const key = tab.getAttribute("data-tab");
          tabs.forEach((t) => {
            const active = t === tab;
            t.classList.toggle("is-active", active);
            t.setAttribute("aria-selected", String(active));
          });
          panels.forEach((p) => {
            p.classList.toggle("is-active", p.getAttribute("data-panel") === key);
          });
        });
      });
    }

    // ---- Back to top ----
    const backTop = document.getElementById("backTop");
    if (backTop) {
      const update = () => { backTop.hidden = window.scrollY < 400; };
      update();
      window.addEventListener("scroll", update, { passive: true });
      backTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    }

    // ---- Reveal on scroll ----
    const reveals = document.querySelectorAll(".section, .page-hero, .hero");
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
      reveals.forEach((el) => {
        el.classList.add("reveal");
        io.observe(el);
      });
    }

    // ---- Year ----
    const year = document.getElementById("year");
    if (year) year.textContent = new Date().getFullYear();
  });
})();
