/* Darmaltoon first-party analytics: anonymous browser/session estimates, privacy opt-outs. */
(() => {
  'use strict';
  // Owner browser exclusion is also enforced by the server; never send owner events.
  if ((document.cookie || '').split(';').some(v => v.trim() === 'dt_analytics_exclude=1')) return;
  if (typeof localStorage !== 'undefined' && localStorage.getItem('dt_analytics_optout') === '1') return;
  // Respect the browser's expressed tracking preferences.
  if (navigator.globalPrivacyControl === true || navigator.doNotTrack === '1'
      || window.doNotTrack === '1') return;
  const known = new Set([
    '/', '/about.html', '/features.html', '/pharmadesktop.html',
    '/demo.html', '/contact.html', '/privacy.html', '/fa/', '/ps/',
    '/fa/features.html', '/ps/features.html', '/fa/pharmadesktop.html',
    '/ps/pharmadesktop.html', '/fa/privacy.html', '/ps/privacy.html',
    '/guides/', '/fa/guides/', '/ps/guides/',
    '/guides/pharmacy-inventory.html', '/fa/guides/pharmacy-inventory.html', '/ps/guides/pharmacy-inventory.html',
    '/guides/expiry-tracking.html', '/fa/guides/expiry-tracking.html', '/ps/guides/expiry-tracking.html',
    '/guides/offline-pharmacy-software.html', '/fa/guides/offline-pharmacy-software.html', '/ps/guides/offline-pharmacy-software.html'
  ]);
  const path = location.pathname;
  if (!known.has(path)) return;
  const language = document.documentElement.lang.toLowerCase().startsWith('fa') ? 'fa'
    : document.documentElement.lang.toLowerCase().startsWith('ps') ? 'ps' : 'en';
  const device = window.innerWidth <= 600 ? 'mobile'
    : window.innerWidth <= 1000 ? 'tablet' : 'desktop';
  const params = new URLSearchParams(location.search);
  const campaign = (params.get('utm_campaign') || '').slice(0, 48).replace(/[^a-zA-Z0-9_-]/g, '');
  let source = 'direct';
  let referrer = 'none';
  const providers = [
    // Identifiable AI assistant referral hostnames; not proof of an answer mentioning us.
    ['chatgpt', /(^|\.)(chatgpt\.com|chat\.openai\.com)$/],
    ['perplexity', /(^|\.)perplexity\.ai$/],
    ['gemini', /^gemini\.google\.com$/],
    ['copilot', /^(copilot\.microsoft\.com|copilot\.com)$/],
    ['claude', /(^|\.)claude\.ai$/],
    ['youcom', /(^|\.)you\.com$/],
    ['poe', /(^|\.)poe\.com$/],
    ['google', /(^|\.)google\.[a-z.]+$/],['bing', /(^|\.)bing\.com$/],
    ['duckduckgo', /(^|\.)duckduckgo\.com$/],['yahoo', /(^|\.)yahoo\.[a-z.]+$/],
    ['yandex', /(^|\.)yandex\.[a-z.]+$/],['facebook', /(^|\.)facebook\.com$/],
    ['instagram', /(^|\.)instagram\.com$/],['whatsapp', /(^|\.)whatsapp\.com$/],
    ['tiktok', /(^|\.)tiktok\.com$/],['youtube', /(^|\.)youtube\.com$/],
    ['linkedin', /(^|\.)linkedin\.com$/],['x', /(^|\.)((twitter|x)\.com)$/],
    ['telegram', /(^|\.)((t\.me|telegram\.org))$/]
  ];
  const aiProviders = ['chatgpt','perplexity','gemini','copilot','claude','youcom','poe'];
  const utmSource = (params.get('utm_source') || '').toLowerCase();
  const utmProvider = aiProviders.includes(utmSource) ? utmSource : 'none';
  if (document.referrer) {
    try {
      const host = new URL(document.referrer).hostname.toLowerCase();
      if (host === location.hostname) source = 'internal';
      else {
        referrer = providers.find(x=>x[1].test(host))?.[0] || 'other';
        source = aiProviders.includes(referrer) ? 'ai_referral' : ['google','bing','duckduckgo','yahoo','yandex'].includes(referrer) ? 'organic' : 'referral';
      }
    } catch { /* ignore invalid referrer */ }
  }
  // Explicit AI campaign attribution is a declared source, not independent evidence of an AI mention.
  if (source !== 'ai_referral' && utmProvider !== 'none') {
    source = 'ai_referral';
    referrer = utmProvider;
  } else if (source === 'direct' && params.has('utm_source')) {
    source = 'campaign';
  }
  const makeId = () => {
    try {
      const bytes = new Uint8Array(16);
      crypto.getRandomValues(bytes);
      return [...bytes].map(b => b.toString(16).padStart(2,'0')).join('');
    } catch { return ''; }
  };
  const now = Date.now();
  let visitorId = '', sessionId = '';
  try {
    const old = JSON.parse(localStorage.getItem('dt_visitor_v1') || 'null');
    visitorId = old && /^[a-f0-9]{32}$/.test(old.id) && old.expires > now ? old.id : makeId();
    if (visitorId) localStorage.setItem('dt_visitor_v1', JSON.stringify({id:visitorId,expires:now+30*86400000}));
    const prior = JSON.parse(sessionStorage.getItem('dt_session_v1') || 'null');
    sessionId = prior && /^[a-f0-9]{32}$/.test(prior.id) && now-prior.active < 30*60000 ? prior.id : makeId();
    if (sessionId) sessionStorage.setItem('dt_session_v1', JSON.stringify({id:sessionId,active:now}));
  } catch { /* storage blocked: continue only aggregated counters */ }
  // Campaign terms are explicitly supplied UTMs, NOT Google organic search queries.
  const utmTerm = (params.get('utm_term') || '').slice(0,90).replace(/[^a-zA-Z0-9 _-]/g,'').trim();
  const send = (event) => {
    const payload = JSON.stringify({event,path,language,source,referrer,campaign,device,visitorId,sessionId,utmTerm});
    try {
      const blob = new Blob([payload], {type:'application/json'});
      if (navigator.sendBeacon && navigator.sendBeacon('/api/analytics.php',blob)) return;
    } catch { /* fall back */ }
    fetch('/api/analytics.php',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:payload,credentials:'same-origin',keepalive:true
    }).catch(()=>{});
  };
  send('page_view');
  // Simple engagement signal, not a precise time-on-page measurement.
  let engaged = false;
  const markEngaged = () => { if (!engaged && document.visibilityState !== 'hidden') { engaged = true; send('engaged'); } };
  if (typeof setTimeout === 'function') setTimeout(markEngaged, 12000);
  document.addEventListener('click', (event)=>{
    const a = event.target.closest?.('a[href]');
    if (!a) return;
    const href = a.getAttribute('href') || '';
    let kind='';
    if (/^https:\/\/wa\.me\//i.test(href)) kind='whatsapp_click';
    else if (/^mailto:/i.test(href)) kind='email_click';
    else if (/^(\/|(?:\.\.\/)*)(demo\.html|demo\/)|#demo(?:$|[?])/i.test(href)) kind='demo_click';
    else if (/^(\/|(?:\.\.\/)*)(contact\.html|contact\/)/i.test(href)) kind='contact_click';
    if (kind) send(kind);
  }, {passive:true});
})();
