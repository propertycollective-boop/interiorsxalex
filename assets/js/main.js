// ─── PHONE FORMAT ───
const phoneInput = document.getElementById('phone');
if (phoneInput) {
  phoneInput.addEventListener('input', e => {
    let v = e.target.value.replace(/\D/g, '').slice(0, 10);
    if (v.length >= 7) v = `(${v.slice(0,3)}) ${v.slice(3,6)}-${v.slice(6)}`;
    else if (v.length >= 4) v = `(${v.slice(0,3)}) ${v.slice(3)}`;
    else if (v.length > 0) v = `(${v}`;
    e.target.value = v;
  });
}

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

  form.addEventListener('submit', async e => {
    e.preventDefault();

    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';

    const val = name => (form.querySelector(`[name="${name}"]`) || {}).value || '';

    const payload = {
      access_key: 'a239424d-8411-478b-97db-62c7a37ec90f',
      subject: `New Inquiry from ${val('name')} — Interiors x Alex`,
      from_name: 'Interiors x Alex',
      name: val('name'),
      email: val('email'),
      message: [
        `Name: ${val('name')}`,
        `Email: ${val('email')}`,
        `Phone: ${val('phone') || '—'}`,
        `Project Type: ${val('project-type') || '—'}`,
        `Location: ${val('location') || '—'}`,
        `Timeline: ${val('timeline') || '—'}`,
        '',
        `Message:\n${val('message') || 'No message provided.'}`,
      ].join('\n'),
      botcheck: '',
    };

    try {
      const res = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.success) {
        form.innerHTML = '<p class="form-success">Thank you — we\'ll be in touch within 48 hours.</p>';
      } else {
        setFormError(form, data.message || 'Something went wrong. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send Inquiry';
      }
    } catch {
      setFormError(form, 'Network error. Please try again or email design@interiorsxalex.com.');
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

// ─── INSTAGRAM FEED ───
const igGrid = document.getElementById('insta-feed-grid');
if (igGrid) {
  fetch('/api/instagram')
    .then(r => r.json())
    .then(posts => {
      if (!posts || posts.length === 0) {
        igGrid.innerHTML = '<p class="insta-empty">Follow <a href="https://www.instagram.com/interiorsxalex" target="_blank" rel="noopener">@interiorsxalex</a> on Instagram.</p>';
        return;
      }
      igGrid.innerHTML = posts.map(post => {
        const img = post.media_type === 'VIDEO' ? post.thumbnail_url : post.media_url;
        const isCarousel = post.media_type === 'CAROUSEL_ALBUM';
        return `<a href="${post.permalink}" target="_blank" rel="noopener" class="insta-tile${isCarousel ? ' insta-carousel' : ''}">
          <img src="${img}" alt="${(post.caption || '').substring(0, 60)}" loading="lazy">
          ${isCarousel ? '<span class="insta-carousel-icon">&#10697;</span>' : ''}
          ${post.media_type === 'VIDEO' ? '<span class="insta-video-icon">&#9654;</span>' : ''}
        </a>`;
      }).join('');
    })
    .catch(() => {
      igGrid.innerHTML = '<p class="insta-empty">Follow <a href="https://www.instagram.com/interiorsxalex" target="_blank" rel="noopener">@interiorsxalex</a> on Instagram.</p>';
    });
}
