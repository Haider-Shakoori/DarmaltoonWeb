/* No backend or fake success: prepare a real email draft in the visitor's mail app. */
document.addEventListener('DOMContentLoaded', () => {
  if (!document.querySelector('.zip-desktop[data-theme="light"]')) return;
  const form = document.getElementById('df');
  if (!form) return;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    event.stopImmediatePropagation();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const read = (key) => String(data.get(key) || '').trim().slice(0, 600);
    const subject = 'Darmaltoon demo request — ' + (read('pharmacy_name') || 'New pharmacy');
    const body = [
      'Name: ' + read('full_name'),
      'Pharmacy: ' + read('pharmacy_name'),
      'Phone: ' + read('phone'),
      'Email: ' + read('email'),
      'Branches: ' + read('branches'),
      'Preferred language: ' + read('language'),
      'Message: ' + read('message'),
      '',
      'Prepared via the Darmaltoon website. Please send this email to submit your request.'
    ].join('\n');
    const url = 'mailto:info@businessos.af?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    const status = document.getElementById('ok');
    if (status) {
      status.style.display = 'block';
      status.setAttribute('role', 'status');
      status.replaceChildren();
      status.append('Your email application should open with the completed draft. Nothing has been sent yet. ');
      const link = document.createElement('a');
      link.href = url;
      link.textContent = 'Open email draft again';
      status.append(link);
    }
    window.location.href = url;
  }, true);
});
