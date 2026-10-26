from __future__ import annotations

THEME_FIXUP_CSS = r'''
<style>
  :root {
    --lco-bg:#0d0d0c;
    --lco-surface:#181612;
    --lco-surface-2:#211e18;
    --lco-text:#f4f0e8;
    --lco-muted:#aaa49a;
    --lco-gold:#c69a52;
    --lco-gold-bright:#e1b969;
    --lco-border:rgba(244,240,232,.10);
    --lco-border-strong:rgba(198,154,82,.34);
  }

  body {
    background:
      radial-gradient(circle at 82% 7%, rgba(198,154,82,.08), transparent 28rem),
      radial-gradient(circle at 7% 46%, rgba(198,154,82,.03), transparent 34rem),
      linear-gradient(180deg, #0d0d0c 0%, #100f0d 55%, #0d0d0c 100%) !important;
    color:var(--lco-text) !important;
    font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif !important;
    -webkit-font-smoothing:antialiased;
  }

  body::before {
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    opacity:.13;
    background-image:
      linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.014) 1px, transparent 1px);
    background-size:72px 72px;
    mask-image:linear-gradient(180deg,#000 0,transparent 80%);
    z-index:-1;
  }

  .wrap { max-width:1240px !important; padding:26px 24px 56px !important; }

  body .hero,
  body .editor,
  body .upload-box,
  body .file-list,
  body .paths,
  body .log,
  body .card {
    background:rgba(255,255,255,.014) !important;
    color:var(--lco-text) !important;
    box-shadow:none !important;
  }

  body h1, body h2, body h3, body .section-title { color:var(--lco-text) !important; }
  body .lead, body .note, body .hint, body .lang-status { color:var(--lco-muted) !important; }
  body .value { color:var(--lco-text) !important; }

  body input[type=text],
  body input[type=file],
  body textarea,
  body select {
    background:rgba(255,255,255,.018) !important;
    color:var(--lco-text) !important;
    border-color:var(--lco-border) !important;
  }
  body input::placeholder, body textarea::placeholder { color:#777169 !important; }

  body th {
    background:#15130f !important;
    color:#cfc7bb !important;
    border-bottom-color:var(--lco-border) !important;
  }
  body td { border-bottom-color:var(--lco-border) !important; }
  body td.readonly { color:#8e887f !important; }

  body button {
    min-height:44px;
    border-radius:11px !important;
    box-shadow:none !important;
    font-weight:700;
  }
  body button:not(.ghost):not(.light):not(.secondary):not(.lco-theme-toggle) {
    background:var(--lco-gold) !important;
    color:#17120d !important;
  }
  body button.secondary {
    background:rgba(198,154,82,.07) !important;
    color:var(--lco-text) !important;
    border:1px solid var(--lco-border-strong) !important;
  }
  body button.ghost, body button.light {
    background:rgba(255,255,255,.018) !important;
    color:var(--lco-muted) !important;
    border:1px solid var(--lco-border) !important;
  }

  .lco-top-toggles { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-top:14px; }
  .lco-theme-toggle, #lang-toggle {
    min-height:38px !important;
    padding:0 12px !important;
    background:rgba(255,255,255,.018) !important;
    color:var(--lco-muted) !important;
    border:1px solid var(--lco-border) !important;
    font-size:.82rem !important;
  }

  body .next-step {
    background:
      radial-gradient(circle at 88% 18%, rgba(198,154,82,.10), transparent 20rem),
      rgba(255,255,255,.014) !important;
    color:#c8c0b5 !important;
  }

  body .chip {
    background:rgba(198,154,82,.08) !important;
    color:var(--lco-gold-bright) !important;
    border-color:rgba(198,154,82,.25) !important;
  }

  body .paths, body .log {
    background:#090a09 !important;
    color:#c6d7c8 !important;
    border:1px solid rgba(255,255,255,.06) !important;
  }

  body.lco-light {
    --lco-bg:#efe9df;
    --lco-surface:#fbf8f2;
    --lco-surface-2:#f1eadf;
    --lco-text:#211d18;
    --lco-muted:#6f675e;
    --lco-gold:#9b7135;
    --lco-gold-bright:#7f591f;
    --lco-border:rgba(50,40,28,.12);
    --lco-border-strong:rgba(155,113,53,.36);
    background:
      radial-gradient(circle at 82% 7%, rgba(155,113,53,.08), transparent 28rem),
      linear-gradient(180deg,#efe9df 0%,#f6f1e8 55%,#efe9df 100%) !important;
    color:var(--lco-text) !important;
  }
  body.lco-light .hero,
  body.lco-light .editor,
  body.lco-light .upload-box,
  body.lco-light .file-list,
  body.lco-light .card { background:rgba(255,255,255,.48) !important; }
  body.lco-light th { background:#eee5d8 !important; color:#574c3f !important; }
  body.lco-light input[type=text],
  body.lco-light input[type=file],
  body.lco-light textarea,
  body.lco-light select { background:#fbf8f2 !important; color:#211d18 !important; }
</style>
'''

THEME_FIXUP_SCRIPT = r'''
<script>
(function () {
  const LABELS = {
    en: { to_dark:'Dark', to_light:'Light', dark:'Dark view', light:'Light view' },
    de: { to_dark:'Dunkel', to_light:'Hell', dark:'Dunkle Ansicht', light:'Helle Ansicht' }
  };

  function lang() {
    const value = localStorage.getItem('local_case_organizer_ui_lang') || document.documentElement.lang || 'en';
    return String(value).toLowerCase().startsWith('de') ? 'de' : 'en';
  }

  function theme() {
    return localStorage.getItem('local_case_organizer_ui_theme') === 'light' ? 'light' : 'dark';
  }

  function applyTheme() {
    document.body.classList.toggle('lco-light', theme() === 'light');
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

    updateThemeButton();
  }

  function updateThemeButton() {
    const button = document.getElementById('theme-toggle');
    const labels = LABELS[lang()];
    if (button) button.textContent = theme() === 'dark' ? labels.to_light : labels.to_dark;
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
    setTimeout(() => { ensureThemeButton(); applyTheme(); }, 250);
  });
  window.addEventListener('load', () => {
    ensureThemeButton();
    applyTheme();
    document.getElementById('lang-toggle')?.addEventListener('click', () => {
      setTimeout(() => { ensureThemeButton(); updateThemeButton(); }, 140);
    });
  });
})();
</script>
'''
