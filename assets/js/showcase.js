/* Preserve language preference while keeping the interface light-only. */
(() => {
  'use strict';
  const root = document.documentElement;
  root.dataset.theme = 'light';
  const lang = root.lang === 'fa-AF' ? 'fa' : root.lang === 'ps-AF' ? 'ps' : 'en';
  try { localStorage.setItem('darmaltoon.lang', lang); } catch (_) {}
})();
