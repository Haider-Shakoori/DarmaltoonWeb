/* One tiny enhancement. Content, language, and navigation work without JS. */
(function(){
  var key='darmaltoon.website.theme',root=document.documentElement;
  var params=new URLSearchParams(location.search);
  var requested=params.get('theme');
  var saved='';
  try{saved=localStorage.getItem(key)||''}catch(e){}
  var theme=(requested==='dark'||requested==='light')?requested:(saved==='dark'?'dark':'light');
  function render(){root.dataset.theme=theme;var b=document.getElementById('themeToggle');if(b){b.setAttribute('aria-pressed',String(theme==='dark'));b.textContent=theme==='dark'?(b.dataset.light||'☀ Light'):(b.dataset.dark||'☾ Dark');}}
  render();
  var lang=root.lang==='fa-AF'?'fa':root.lang==='ps-AF'?'ps':'en';
  try{localStorage.setItem('darmaltoon.lang',lang)}catch(e){}
  document.addEventListener('DOMContentLoaded',function(){render();var b=document.getElementById('themeToggle');if(!b)return;b.addEventListener('click',function(){theme=theme==='dark'?'light':'dark';try{localStorage.setItem(key,theme)}catch(e){}render();});});
})();