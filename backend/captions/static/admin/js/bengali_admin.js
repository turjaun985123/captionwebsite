(() => {
  const dialog = document.querySelector('#command-palette');
  const commandInput = document.querySelector('#command-input');
  const openCommand = () => {
    if (!dialog || dialog.open) return;
    dialog.showModal();
    commandInput?.focus();
  };
  document.querySelectorAll('[data-open-command]').forEach((button) => button.addEventListener('click', openCommand));
  document.querySelector('[data-close-command]')?.addEventListener('click', () => dialog?.close());

  if (dialog && commandInput) {
    const items = [...dialog.querySelectorAll('[data-command-item]')];
    commandInput.addEventListener('input', () => {
      const query = commandInput.value.trim().toLocaleLowerCase();
      items.forEach((item) => { item.hidden = query && !item.textContent.toLocaleLowerCase().includes(query); });
    });
    commandInput.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter') return;
      event.preventDefault();
      const query = commandInput.value.trim();
      const visible = items.find((item) => !item.hidden);
      if (query) location.href = `/admin/captions/caption/?q=${encodeURIComponent(query)}`;
      else if (visible) location.href = visible.href;
    });
    dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
  }

  let shortcutPrefix = '';
  let shortcutTimer;
  document.addEventListener('keydown', (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      openCommand();
      return;
    }
    if (event.target.matches('input,textarea,select,[contenteditable="true"]')) return;
    const key = event.key.toLowerCase();
    if (key === 'n') { location.href = '/admin/captions/caption/add/'; return; }
    if (shortcutPrefix === 'g' && key === 'o') location.href = '/admin/';
    if (shortcutPrefix === 'g' && key === 'c') location.href = '/admin/captions/caption/';
    shortcutPrefix = key === 'g' ? 'g' : '';
    clearTimeout(shortcutTimer);
    shortcutTimer = setTimeout(() => { shortcutPrefix = ''; }, 700);
  });

  const list = document.querySelector('#result_list');
  const listSearch = document.querySelector('#searchbar');
  if (listSearch && !listSearch.placeholder) {
    listSearch.placeholder = document.documentElement.lang === 'en'
      ? 'Search captions, categories, or authors'
      : 'ক্যাপশন, বিষয় বা লেখক খুঁজুন';
  }
  const navFilter = document.querySelector('#nav-filter');
  navFilter?.addEventListener('input', () => {
    const query = navFilter.value.trim().toLocaleLowerCase();
    document.querySelectorAll('#nav-sidebar .studio-nav-link').forEach((link) => {
      link.hidden = query && !link.textContent.toLocaleLowerCase().includes(query);
    });
  });
  const listFilters = document.querySelector('#changelist-filter');
  if (listFilters?.dataset.hasActiveFilters === 'false') {
    listFilters.querySelectorAll('details').forEach((filter) => { filter.open = false; });
  }
  const toggle = document.querySelector('[data-column-toggle]');
  const panel = document.querySelector('[data-column-panel]');
  if (list && toggle && panel) {
    const storageKey = `caption-columns:${location.pathname}`;
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(storageKey) || '{}'); } catch {}
    const headers = [...list.querySelectorAll('thead th')];
    const applyVisibility = (index, visible) => {
      list.querySelectorAll('tr').forEach((row) => {
        const cell = row.children[index];
        if (cell) cell.hidden = !visible;
      });
    };
    headers.forEach((header, index) => {
      if (index === 0) return;
      const title = header.innerText.trim();
      if (!title) return;
      const label = document.createElement('label');
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = saved[index] !== false;
      checkbox.setAttribute('aria-label', title);
      checkbox.addEventListener('change', () => {
        applyVisibility(index, checkbox.checked);
        saved[index] = checkbox.checked;
        localStorage.setItem(storageKey, JSON.stringify(saved));
      });
      label.append(checkbox, document.createTextNode(title));
      panel.append(label);
      if (!checkbox.checked) applyVisibility(index, false);
    });
    toggle.addEventListener('click', () => {
      const opening = panel.hidden;
      panel.hidden = !opening;
      toggle.setAttribute('aria-expanded', String(opening));
    });
    document.addEventListener('click', (event) => {
      if (!panel.hidden && !panel.contains(event.target) && !toggle.contains(event.target)) {
        panel.hidden = true;
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    toggle.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') { panel.hidden = true; toggle.focus(); }
    });
  }

  const form = document.querySelector('#content-main form#caption_form');
  if (form) {
    let dirty = false;
    const markDirty = () => { dirty = true; };
    form.addEventListener('input', markDirty);
    form.addEventListener('change', markDirty);
    form.addEventListener('submit', () => { dirty = false; });
    window.addEventListener('beforeunload', (event) => {
      if (!dirty) return;
      event.preventDefault();
      event.returnValue = '';
    });
  }
})();
