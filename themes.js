// Apply the saved theme before the page paints, including when storage is unavailable.
(() => {
  const allowed = new Set(['default', 'luffy', 'zoro', 'nami', 'usopp', 'sanji', 'chopper', 'robin', 'franky', 'brook', 'jinbe']);
  window.setDashboardTheme = (theme) => {
    const selected = allowed.has(theme) ? theme : 'default';
    document.documentElement.dataset.theme = selected;
    try { localStorage.setItem('valorant-straw-hat-theme', selected); } catch { /* Theme selection still works without browser storage. */ }
  };
  let saved = 'default';
  try { saved = localStorage.getItem('valorant-straw-hat-theme') || 'default'; } catch { /* Use the original palette. */ }
  window.setDashboardTheme(saved);
})();
