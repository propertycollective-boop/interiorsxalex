// ─── MOBILE NAV ───
const toggle = document.querySelector('.nav-toggle');
const overlay = document.querySelector('.mobile-nav-overlay');
const closeBtn = document.querySelector('.mobile-nav-close');

function openNav() {
  overlay && overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeNav() {
  overlay && overlay.classList.remove('open');
  document.body.style.overflow = '';
}

toggle && toggle.addEventListener('click', openNav);
closeBtn && closeBtn.addEventListener('click', closeNav);
overlay && overlay.addEventListener('click', e => {
  if (e.target === overlay) closeNav();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeNav();
});

// ─── PORTFOLIO TABS ───
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;
    tabBtns.forEach(b => b.classList.remove('active'));
    tabPanels.forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    const panel = document.getElementById('tab-' + target);
    if (panel) panel.classList.add('active');
  });
});

// ─── CONTACT FORM ───
const form = document.querySelector('.contact-form');
if (form) {
  const submitBtn = form.querySelector('[type="submit"]');
  const note = form.querySelector('.form-note');

  form.addEventListener('submit', async e => {
    e.preventDefault();

    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';

    const payload = {
      name: form.querySelector('[name="name"]').value,
      email: form.querySelector('[name="email"]').value,
      phone: form.querySelector('[name="phone"]') ? form.querySelector('[name="phone"]').value : '',
      'project-type': form.querySelector('[name="project-type"]') ? form.querySelector('[name="project-type"]').value : '',
      location: form.querySelector('[name="location"]') ? form.querySelector('[name="location"]').value : '',
      timeline: form.querySelector('[name="timeline"]') ? form.querySelector('[name="timeline"]').value : '',
      message: form.querySelector('[name="message"]').value,
    };

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        form.innerHTML = '<p class="form-success">Thank you — we\'ll be in touch within 48 hours.</p>';
      } else {
        const err = await res.json();
        setFormError(form, err.error || 'Something went wrong. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send Inquiry';
      }
    } catch {
      setFormError(form, 'Network error. Please try again.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Send Inquiry';
    }
  });
}

function setFormError(form, msg) {
  let el = form.querySelector('.form-error');
  if (!el) {
    el = document.createElement('p');
    el.className = 'form-error';
    form.appendChild(el);
  }
  el.textContent = msg;
}
