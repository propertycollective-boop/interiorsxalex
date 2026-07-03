// Mobile nav toggle
const toggle = document.querySelector('.nav-toggle');
const navLeft = document.querySelector('.nav-links.left');
const navRight = document.querySelector('.nav-links.right');

if (toggle) {
  toggle.addEventListener('click', () => {
    navLeft && navLeft.classList.toggle('open');
    navRight && navRight.classList.toggle('open');
  });
}

// Portfolio tab switching
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

// Contact form
const form = document.querySelector('.contact-form');
if (form) {
  form.addEventListener('submit', async e => {
    e.preventDefault();

    const btn = form.querySelector('[type="submit"]');
    const payload = {
      name: form.querySelector('[name="name"]').value,
      email: form.querySelector('[name="email"]').value,
      phone: form.querySelector('[name="phone"]').value,
      'project-type': form.querySelector('[name="project-type"]').value,
      location: form.querySelector('[name="location"]').value,
      timeline: form.querySelector('[name="timeline"]').value,
      message: form.querySelector('[name="message"]').value,
    };

    btn.disabled = true;
    btn.textContent = 'Sending…';

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        form.innerHTML = '<p class="form-success">Thank you! We\'ll be in touch within 48 hours.</p>';
      } else {
        const err = await res.json();
        setFormError(form, err.error || 'Something went wrong. Please try again.');
        btn.disabled = false;
        btn.textContent = 'Send Inquiry';
      }
    } catch {
      setFormError(form, 'Network error. Please try again.');
      btn.disabled = false;
      btn.textContent = 'Send Inquiry';
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
