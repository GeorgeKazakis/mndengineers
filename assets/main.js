(() => {
  // Sticky nav border once the page scrolls
  const nav = document.querySelector('.nav');
  const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 8);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile menu
  const toggle = document.querySelector('.nav__toggle');
  const menu = document.getElementById('nav-menu');
  const setMenu = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('is-open', open);
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });

  // Lightbox for drawings
  const box = document.getElementById('lightbox');
  const boxImg = box.querySelector('img');
  const boxCap = box.querySelector('.lightbox__cap');
  document.querySelectorAll('.zoom').forEach((btn) => {
    btn.addEventListener('click', () => {
      boxImg.src = btn.dataset.full;
      boxImg.alt = btn.dataset.caption || '';
      boxCap.textContent = btn.dataset.caption || '';
      box.showModal();
    });
  });
  box.querySelector('.lightbox__close').addEventListener('click', () => box.close());
  box.addEventListener('click', (e) => { if (e.target === box) box.close(); });

  // Reveal on scroll
  const targets = document.querySelectorAll('.card, .shot, .steps li, .person, .enquiry');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach((el) => { el.classList.add('reveal'); io.observe(el); });
  }

  // Enquiry form -> pre-filled email (no backend needed)
  const form = document.getElementById('enquiry');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let ok = true;
    form.querySelectorAll('[required]').forEach((f) => {
      const bad = !f.value.trim();
      f.setAttribute('aria-invalid', String(bad));
      if (bad && ok) { f.focus(); ok = false; }
    });
    if (!ok) return;
    const d = Object.fromEntries(new FormData(form));
    const subject = `Αίτημα: ${d.service} — ${d.name}`;
    const body = [
      `Ονοματεπώνυμο: ${d.name}`,
      d.phone && `Τηλέφωνο: ${d.phone}`,
      `Υπηρεσία: ${d.service}`,
      d.area && `Περιοχή: ${d.area}`,
      '',
      d.message,
    ].filter((l) => l !== undefined && l !== '').join('\n');
    const to = 'michalis.krikelis@gmail.com,di.krikelis@gmail.com';
    window.location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });

  document.getElementById('year').textContent = new Date().getFullYear();
})();
