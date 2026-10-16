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
  const form=document.getElementById('df');
  if(form)form.addEventListener('submit',function(e){
    e.preventDefault();
    const box=document.getElementById('ok');
    if(!box)return;
    box.style.display='block';box.setAttribute('role','status');
    box.innerHTML='The online request form is not connected yet; your details have <strong>not</strong> been sent. Please email <a href="mailto:info@businessos.af">info@businessos.af</a> to arrange a demo.';
    box.scrollIntoView({behavior:'smooth',block:'nearest'});
  });
})();
