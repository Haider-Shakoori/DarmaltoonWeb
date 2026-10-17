/* Light-only progressive enhancement; localized content is server-rendered. */
(() => {
  'use strict';
  document.documentElement.dataset.design = 'light';
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = '#e8f3ff';
})();
