/* Dermaltoon ZIP UI: keep image-precise desktop, readable mobile and transparent demo contact. */
(function(){
  const root=document.getElementById('designFrame');
  const art=document.getElementById('s');
  const mobile=window.matchMedia('(max-width:900px)');
  const ORIGINAL_WIDTH=1448, ORIGINAL_HEIGHT=1086;
  function fit(){
    if(!root || !art)return;
    if(mobile.matches){root.style.height='0';return;}
    const k=window.innerWidth/ORIGINAL_WIDTH;
    art.style.transform=`scale(${k})`;
    root.style.height=`${ORIGINAL_HEIGHT*k}px`;
  }
  let scheduled=false;
  window.addEventListener('resize',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(()=>{scheduled=false;fit()})}},{passive:true});
  fit();
  for (const link of document.querySelectorAll('#s a[href^="#"]')) {
    link.addEventListener('click',function(e){
      const h=this.getAttribute('href');
      if(h==='#' || h==='#top'){e.preventDefault();scrollTo({top:0,behavior:'smooth'});return;}
      const target=document.getElementById(h.slice(1));
      if(target){e.preventDefault();target.scrollIntoView({behavior:'smooth',block:'start'})}
    });
  }
  // The active homepage form handler lives in light-demo-mailto.js.
  // Do not register a second outdated submit listener here.
})();
