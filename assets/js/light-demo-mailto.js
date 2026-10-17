/* Homepage lead intake. The direct email link remains the fallback for poor connectivity. */
document.addEventListener('DOMContentLoaded', () => {
  if (!document.querySelector('.zip-desktop')) return;
  const form = document.getElementById('df');
  if (!form) return;
  const box = document.getElementById('ok');
  const read = (fd, key) => String(fd.get(key) || '').trim().slice(0, 550);
  function fallback(fd) {
    const subject = 'Darmaltoon demo request — ' + (read(fd,'pharmacy_name') || 'New pharmacy');
    const body = [
      'Name: '+read(fd,'full_name'),'Pharmacy: '+read(fd,'pharmacy_name'),
      'Phone: '+read(fd,'phone'),'Email: '+read(fd,'email'),
      'Branches: '+read(fd,'branches'),'Language: '+read(fd,'language'),
      'Message: '+read(fd,'message'),
      '','Prepared through the Darmaltoon website. Press Send in your email app.'
    ].join('\n');
    const url = 'mailto:info@businessos.af?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
    if (box) {
      box.style.display='block';box.setAttribute('role','alert');box.replaceChildren();
      box.append('Online submission is unavailable. Your details have NOT been received. ');
      const link=document.createElement('a');link.href=url;link.textContent='Open your prepared email draft';
      box.append(link);
    }
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    event.stopImmediatePropagation(); // stop older mock form intercept from overwriting status
    if (!form.reportValidity()) return;
    const fd = new FormData(form);
    const chosen = read(fd,'language');
    const lang = chosen.includes('دری')?'fa':chosen.includes('پښتو')?'ps':'en';
    const payload = {
      kind:'demo',language:lang,website:read(fd,'website'),name:read(fd,'full_name'),
      pharmacy:read(fd,'pharmacy_name'),phone:read(fd,'phone'),email:read(fd,'email'),
      branches:read(fd,'branches'),message:read(fd,'message'),
      consent:fd.get('agree')==='on'
    };
    const button=form.querySelector('button');
    if (button) button.disabled=true;
    const controller=new AbortController();
    const timeout=window.setTimeout(()=>controller.abort(),15000);
    try {
      const response=await fetch('/api/lead.php',{
        method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
        body:JSON.stringify(payload),signal:controller.signal,credentials:'same-origin'
      });
      const result=await response.json();
      if (response.ok && result.received===true){
        if (box) {
          box.style.display='block';box.setAttribute('role','status');box.replaceChildren();
          box.append('Your demo request has been received and securely recorded. We will contact you using the details provided.');
        }
        form.reset();
      } else if (response.status===429) {
        if (box){box.style.display='block';box.setAttribute('role','alert');box.textContent='Please wait before sending another request, or contact us by WhatsApp.'}
      } else fallback(fd);
    } catch (e){ fallback(fd) }
    finally {window.clearTimeout(timeout);if(button)button.disabled=false}
  },true);
});
