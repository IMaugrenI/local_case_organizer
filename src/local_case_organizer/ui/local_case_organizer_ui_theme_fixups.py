from __future__ import annotations

THEME_FIXUP_CSS = '''
<style>
  .lco-top-toggles { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: 12px; }
  .lco-theme-toggle {
    border: 0;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 15px;
    cursor: pointer;
    background: #0f766e;
    color: white;
  }

  body.lco-dark {
    background: #0b1220 !important;
    color: #e5e7eb !important;
  }

  body.lco-dark .hero,
  body.lco-dark .editor,
  body.lco-dark .upload-box,
  body.lco-dark .file-list,
  body.lco-dark .paths,
  body.lco-dark .log,
  body.lco-dark .card {
    background: #111827 !important;
    color: #e5e7eb !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.28) !important;
    border: 1px solid #1f2937 !important;
  }

  body.lco-dark .hero {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
  }

  body.lco-dark .section-title,
  body.lco-dark h1,
  body.lco-dark h2,
  body.lco-dark h3 {
    color: #f8fafc !important;
  }

  body.lco-dark .lead,
  body.lco-dark .note,
  body.lco-dark .hint,
  body.lco-dark #cards .card > div:first-child,
  body.lco-dark .lang-status {
    color: #cbd5e1 !important;
  }

  body.lco-dark .value {
    color: #f8fafc !important;
  }

  body.lco-dark input[type=text],
  body.lco-dark input[type=file],
  body.lco-dark textarea,
  body.lco-dark select {
    background: #0f172a !important;
    color: #e5e7eb !important;
    border-color: #334155 !important;
  }

  body.lco-dark input::placeholder,
  body.lco-dark textarea::placeholder {
    color: #94a3b8 !important;
  }

  body.lco-dark td.readonly,
  body.lco-dark th {
    color: #cbd5e1 !important;
  }

  body.lco-dark th {
    background: #172033 !important;
    border-bottom-color: #334155 !important;
  }

  body.lco-dark td {
    border-bottom-color: #334155 !important;
  }

  body.lco-dark table {
    background: transparent !important;
  }

  body.lco-dark button {
    box-shadow: none !important;
  }

  body.lco-dark button:not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle):not(.lco-log-toggle) {
    background: #2563eb !important;
    color: #eff6ff !important;
  }

  body.lco-dark button.secondary {
    background: #0f766e !important;
    color: #ecfeff !important;
  }

  body.lco-dark button.ghost {
    background: #1f2937 !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
  }

  body.lco-dark button.light,
  body.lco-dark .lco-log-toggle {
    background: #334155 !important;
    color: #f8fafc !important;
  }

  body.lco-dark .lco-theme-toggle {
    background: #7c3aed !important;
    color: #faf5ff !important;
  }

  body.lco-dark .next-step {
    background: linear-gradient(180deg, #0f2433 0%, #102737 100%) !important;
    border-color: #155e75 !important;
    color: #dbeafe !important;
  }

  body.lco-dark .chip {
    background: #1e293b !important;
    color: #c7d2fe !important;
    border-color: #4338ca !important;
  }

  body.lco-dark .paths {
    background: #091226 !important;
    color: #dbeafe !important;
  }

  body.lco-dark .log {
    background: #081120 !important;
    color: #d1fae5 !important;
  }

  body.lco-dark .editor-actions,
  body.lco-dark .upload-row,
  body.lco-dark .actions {
    row-gap: 10px;
  }
</style>
'''

THEME_FIXUP_SCRIPT = r'''
<script>
(function () {
  const LABELS = {
    en: { to_dark: 'Dark mode', to_light: 'Light mode', dark: 'Theme: dark', light: 'Theme: light' },
    de: { to_dark: 'Dunkelmodus', to_light: 'Hellmodus', dark: 'Farbschema: dunkel', light: 'Farbschema: hell' }
  };

  function lang() {
    const value = localStorage.getItem('local_case_organizer_ui_lang') || document.documentElement.lang || 'en';
    return String(value).toLowerCase().startsWith('de') ? 'de' : 'en';
  }

  function theme() {
    return localStorage.getItem('local_case_organizer_ui_theme') === 'dark' ? 'dark' : 'light';
  }

  function applyTheme() {
    document.body.classList.toggle('lco-dark', theme() === 'dark');
    updateThemeButton();
  }

  function toggleTheme() {
    localStorage.setItem('local_case_organizer_ui_theme', theme() === 'dark' ? 'light' : 'dark');
    applyTheme();
  }

  function ensureThemeButton() {
    const langButton = document.getElementById('lang-toggle');
    if (!langButton) return;
    const container = langButton.parentElement;
    if (!container) return;

    let row = container.querySelector('.lco-top-toggles');
    if (!row) {
      row = document.createElement('div');
      row.className = 'lco-top-toggles';
      container.insertBefore(row, langButton);
      row.appendChild(langButton);
    }

    let button = document.getElementById('theme-toggle');
    if (!button) {
      button = document.createElement('button');
      button.id = 'theme-toggle';
      button.type = 'button';
      button.className = 'lco-theme-toggle';
      button.addEventListener('click', toggleTheme);
      row.appendChild(button);
    }

    let status = document.getElementById('theme-status');
    if (!status) {
      status = document.createElement('div');
      status.id = 'theme-status';
      status.className = 'lang-status';
      container.appendChild(status);
    }

    updateThemeButton();
  }

  function updateThemeButton() {
    const button = document.getElementById('theme-toggle');
    const status = document.getElementById('theme-status');
    const labels = LABELS[lang()];
    if (button) button.textContent = theme() === 'dark' ? labels.to_light : labels.to_dark;
    if (status) status.textContent = theme() === 'dark' ? labels.dark : labels.light;
  }

  const originalToggleLanguage = window.toggleLanguage;
  if (typeof originalToggleLanguage === 'function') {
    window.toggleLanguage = function () {
      const result = originalToggleLanguage.apply(this, arguments);
      setTimeout(() => { ensureThemeButton(); applyTheme(); }, 0);
      return result;
    };
  }

  const originalApplyLanguage = window.applyLanguage;
  if (typeof originalApplyLanguage === 'function') {
    window.applyLanguage = function () {
      const result = originalApplyLanguage.apply(this, arguments);
      setTimeout(() => { ensureThemeButton(); applyTheme(); }, 0);
      return result;
    };
  }

  document.addEventListener('DOMContentLoaded', () => {
    ensureThemeButton();
    applyTheme();
    setTimeout(() => { ensureThemeButton(); applyTheme(); }, 300);
  });
})();
</script>
'''
