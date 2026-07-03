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

// Contact form (no backend — opens mailto as fallback)
const form = document.querySelector('.contact-form');
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const name = form.querySelector('[name="name"]').value;
    const email = form.querySelector('[name="email"]').value;
    const message = form.querySelector('[name="message"]').value;
    const subject = encodeURIComponent('New inquiry from ' + name);
    const body = encodeURIComponent(message + '\n\nFrom: ' + name + '\nEmail: ' + email);
    window.location.href = 'mailto:catuogno.gm@gmail.com?subject=' + subject + '&body=' + body;
  });
}
