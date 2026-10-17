/* Localized pages use the light design only; keep the mobile menu functional. */
(() => {
  'use strict';
  document.documentElement.dataset.design = 'light';
  const image = document.querySelector('.rtl-product-frame img[data-light-src]');
  if (image && image.dataset.lightSrc) image.setAttribute('src', image.dataset.lightSrc);
  const color = document.querySelector('meta[name="theme-color"]');
  if (color) color.content = '#ecf6ff';
  const menu = document.querySelector('.rtl-mobile-menu');
  menu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { menu.open = false; }));
  document.addEventListener('click', ev => {
    if (menu?.open && !menu.contains(ev.target)) menu.open = false;
  });
})();
