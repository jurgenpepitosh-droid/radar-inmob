/* =============================================================
   Radar Inmobiliario · Editorial / utilitarian aesthetic
   Palette: cream paper, ink, single terracotta accent
   ============================================================= */

:root {
  --bg: #f4f0e8;
  --bg-card: #fbf8f2;
  --ink: #181511;
  --ink-mute: #5a5247;
  --line: #d8cfbc;
  --accent: #c24b26;           /* terracotta */
  --accent-soft: #f1ddd0;
  --green: #2e6b42;
  --green-soft: #d9e8df;
  --red: #8a1f1f;
  --red-soft: #ecd4d4;
  --blue: #1f4e6b;

  --serif: "Fraunces", ui-serif, Georgia, serif;
  --sans: "IBM Plex Sans", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, monospace;

  --shadow: 0 1px 0 rgba(24,21,17,.05), 0 8px 24px -16px rgba(24,21,17,.18);
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.5;
  min-height: 100vh;
  padding-bottom: 80px;
  background-image:
    radial-gradient(circle at 15% 10%, rgba(194,75,38,.04) 0%, transparent 40%),
    radial-gradient(circle at 85% 90%, rgba(31,78,107,.03) 0%, transparent 35%);
}

a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--line); text-underline-offset: 3px; }
a:hover { text-decoration-color: var(--accent); }

.mono { font-family: var(--mono); font-feature-settings: "tnum"; }
.muted { color: var(--ink-mute); }
.accent { color: var(--accent); }
.hidden { display: none !important; }

/* --- Header -------------------------------------------------- */
.site-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 40px 48px 24px;
  border-bottom: 1px solid var(--line);
  max-width: 1400px;
  margin: 0 auto;
}
.brand { display: flex; gap: 16px; align-items: center; }
.brand-mark {
  font-size: 42px;
  color: var(--accent);
  line-height: 1;
  transform: translateY(-2px);
}
.brand h1 {
  font-family: var(--serif);
  font-weight: 800;
  font-size: 34px;
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1;
}
.brand-sub {
  margin: 4px 0 0;
  font-size: 13px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ink-mute);
}
.meta { font-size: 13px; }

/* --- Stats --------------------------------------------------- */
.stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0;
  max-width: 1400px;
  margin: 32px auto 0;
  padding: 0 48px;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}
.stat {
  padding: 20px 24px;
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.stat:last-child { border-right: none; }
.stat-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ink-mute);
}
.stat-value {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

/* --- Tabs ---------------------------------------------------- */
.tabs {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 48px 0;
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--line);
}
.tab {
  background: transparent;
  border: none;
  font-family: var(--sans);
  font-size: 14px;
  font-weight: 500;
  padding: 12px 20px;
  cursor: pointer;
  color: var(--ink-mute);
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color .15s;
}
.tab:hover { color: var(--ink); }
.tab.active { color: var(--ink); border-bottom-color: var(--accent); font-weight: 600; }

/* --- Main view ---------------------------------------------- */
main { max-width: 1400px; margin: 0 auto; padding: 32px 48px; }
.view { animation: fadeIn .25s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

/* --- Filters ------------------------------------------------- */
.filters {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 28px;
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: 4px;
}
.filter-group { display: flex; flex-direction: column; gap: 6px; }
.filter-group label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-mute);
  font-weight: 600;
}
.filters select, .filters input {
  background: var(--bg);
  border: 1px solid var(--line);
  padding: 8px 10px;
  font-family: var(--sans);
  font-size: 14px;
  color: var(--ink);
  border-radius: 2px;
  outline: none;
  transition: border-color .15s;
}
.filters select:focus, .filters input:focus { border-color: var(--accent); }

/* --- Grid of listings --------------------------------------- */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.card {
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  transition: transform .15s, box-shadow .15s, border-color .15s;
  position: relative;
}
.card:hover {
  transform: translateY(-2px);
  border-color: var(--ink);
  box-shadow: var(--shadow);
}
.card.inactive {
  opacity: 0.55;
  background: transparent;
}
.card.inactive::after {
  content: "Retirado";
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--red);
  background: var(--red-soft);
  padding: 3px 8px;
  border-radius: 2px;
}
.card-price {
  font-family: var(--mono);
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.card-meta {
  font-size: 12px;
  color: var(--ink-mute);
  font-family: var(--mono);
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.card-meta span { white-space: nowrap; }
.card-title {
  font-family: var(--serif);
  font-weight: 600;
  font-size: 16px;
  line-height: 1.35;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-location {
  font-size: 13px;
  color: var(--ink-mute);
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid var(--line);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.portal-tag {
  font-weight: 600;
  color: var(--accent);
}
.card-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  padding: 2px 8px;
  border-radius: 2px;
  margin-right: 4px;
}
.badge-new     { background: var(--accent-soft); color: var(--accent); }
.badge-drop    { background: var(--green-soft); color: var(--green); }

.empty { text-align: center; padding: 60px; color: var(--ink-mute); font-style: italic; }

/* --- Events timeline ---------------------------------------- */
.events-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.chip {
  background: transparent;
  border: 1px solid var(--line);
  font-family: var(--sans);
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 999px;
  cursor: pointer;
  color: var(--ink-mute);
  transition: all .15s;
}
.chip:hover { border-color: var(--ink); color: var(--ink); }
.chip.active { background: var(--ink); color: var(--bg); border-color: var(--ink); }

.timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  border-left: 1px solid var(--line);
  padding-left: 28px;
  position: relative;
}
.event {
  position: relative;
  padding: 14px 0 14px 12px;
  border-bottom: 1px solid var(--line);
}
.event:last-child { border-bottom: none; }
.event::before {
  content: "";
  position: absolute;
  left: -35px;
  top: 22px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--ink-mute);
}
.event.price_drop::before { background: var(--green); }
.event.new::before { background: var(--accent); }
.event.price_rise::before { background: var(--red); }
.event.removed::before { background: var(--ink-mute); }
.event.relisted::before { background: var(--blue); }

.event-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 4px;
}
.event-title {
  font-family: var(--serif);
  font-weight: 600;
  font-size: 16px;
  margin: 0;
}
.event-when {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--ink-mute);
  white-space: nowrap;
}
.event-meta {
  font-size: 13px;
  color: var(--ink-mute);
}
.event-price {
  font-family: var(--mono);
  font-weight: 600;
}
.event-delta-down { color: var(--green); }
.event-delta-up { color: var(--red); }

/* --- Modal --------------------------------------------------- */
.modal { position: fixed; inset: 0; z-index: 100; display: flex; align-items: center; justify-content: center; }
.modal-backdrop { position: absolute; inset: 0; background: rgba(24,21,17,.5); backdrop-filter: blur(2px); }
.modal-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 32px;
  max-width: 600px;
  width: calc(100% - 32px);
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,.25);
}
.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 6px 10px;
  color: var(--ink-mute);
}
.modal-close:hover { color: var(--ink); }

.price-chart {
  margin-top: 20px;
  padding: 16px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 4px;
}
.price-chart-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-mute);
  margin: 0 0 8px;
}

/* --- About prose -------------------------------------------- */
.prose { max-width: 680px; font-family: var(--serif); font-size: 17px; line-height: 1.6; }
.prose h2 { font-family: var(--serif); font-weight: 800; font-size: 22px; margin-top: 28px; }
.prose code { font-family: var(--mono); font-size: 14px; background: var(--accent-soft); padding: 1px 6px; border-radius: 2px; }

/* --- Footer -------------------------------------------------- */
.site-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 14px 48px;
  background: var(--bg);
  border-top: 1px solid var(--line);
  text-align: right;
  font-size: 12px;
}

/* --- Responsive --------------------------------------------- */
@media (max-width: 900px) {
  .site-header { padding: 24px; flex-direction: column; align-items: flex-start; gap: 16px; }
  .stats { grid-template-columns: repeat(2, 1fr); padding: 0 24px; }
  .stat { border-right: none; border-bottom: 1px solid var(--line); }
  .stat:nth-child(2n) { border-right: none; }
  .tabs { padding: 16px 24px 0; }
  main { padding: 20px 24px; }
  .filters { grid-template-columns: 1fr 1fr; padding: 12px; }
  .grid { grid-template-columns: 1fr; }
  .site-footer { padding: 12px 24px; }
}
