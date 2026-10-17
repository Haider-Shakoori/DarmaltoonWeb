/* Progressive enhancement; all content/navigation is server-rendered HTML. */
(() => {
  'use strict';
  const root = document.documentElement;
  const button = document.getElementById('designSwitch');
  const key = 'darmaltoon.ref.design';
  const productImage = document.querySelector('.rtl-product-frame img[data-light-src]');
  let stored = '';
  try { stored = localStorage.getItem(key) || ''; } catch (_) {}
  const requested = new URLSearchParams(location.search).get('theme');
  const first = ['dark', 'light'].includes(requested) ? requested :
    (stored === 'dark' ? 'dark' : 'light');
  const update = (mode) => {
    root.dataset.design = mode;
    if (productImage) {
      const wanted = mode === 'dark' ? productImage.dataset.darkSrc : productImage.dataset.lightSrc;
      if (productImage.getAttribute('src') !== wanted) productImage.setAttribute('src', wanted);
    }
    if (button) {
      button.textContent = mode === 'dark' ? button.dataset.light : button.dataset.dark;
      button.setAttribute('aria-pressed', String(mode === 'dark'));
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = mode === 'dark' ? '#061320' : '#ecf6ff';
  };
  update(first);
  button?.addEventListener('click', () => {
    const mode = root.dataset.design === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(key, mode); } catch (_) {}
    update(mode);
  });
  const menu = document.querySelector('.rtl-mobile-menu');
  menu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { menu.open = false; }));
  document.addEventListener('click', (ev) => {
    if (menu?.open && !menu.contains(ev.target)) menu.open = false;
  });
})();
