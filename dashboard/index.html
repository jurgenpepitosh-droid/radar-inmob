<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Radar Inmobiliario · Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,600;0,800;1,400&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css" />
</head>
<body>

<header class="site-header">
  <div class="brand">
    <span class="brand-mark">◎</span>
    <div>
      <h1>Radar Inmobiliario</h1>
      <p class="brand-sub">Alquiler · Vallès Occidental</p>
    </div>
  </div>
  <div class="meta">
    <span id="updated-at" class="mono muted">—</span>
  </div>
</header>

<section class="stats">
  <div class="stat">
    <span class="stat-label">Activos</span>
    <span class="stat-value mono" id="stat-active">—</span>
  </div>
  <div class="stat">
    <span class="stat-label">Nuevos (24h)</span>
    <span class="stat-value mono" id="stat-new24">—</span>
  </div>
  <div class="stat">
    <span class="stat-label">Bajadas (7d)</span>
    <span class="stat-value mono accent" id="stat-drops">—</span>
  </div>
  <div class="stat">
    <span class="stat-label">Precio medio</span>
    <span class="stat-value mono" id="stat-avg">—</span>
  </div>
  <div class="stat">
    <span class="stat-label">€/m² medio</span>
    <span class="stat-value mono" id="stat-perm2">—</span>
  </div>
</section>

<nav class="tabs">
  <button class="tab active" data-tab="listings">Anuncios</button>
  <button class="tab" data-tab="events">Eventos</button>
  <button class="tab" data-tab="about">Acerca</button>
</nav>

<main>
  <!-- LISTINGS TAB -->
  <section class="view view-listings" data-view="listings">
    <div class="filters">
      <div class="filter-group">
        <label>Portal</label>
        <select id="filter-portal">
          <option value="">Todos</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Zona</label>
        <select id="filter-location">
          <option value="">Todas</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Precio máx</label>
        <input type="number" id="filter-max-price" placeholder="1500" />
      </div>
      <div class="filter-group">
        <label>Hab. mín</label>
        <input type="number" id="filter-min-rooms" placeholder="2" />
      </div>
      <div class="filter-group">
        <label>Ordenar</label>
        <select id="filter-sort">
          <option value="newest">Más recientes</option>
          <option value="price-asc">Precio ↑</option>
          <option value="price-desc">Precio ↓</option>
          <option value="size-desc">Tamaño ↓</option>
          <option value="perm2">€/m² ↑</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Estado</label>
        <select id="filter-status">
          <option value="active">Activos</option>
          <option value="all">Todos</option>
          <option value="inactive">Retirados</option>
        </select>
      </div>
    </div>
    <div class="grid" id="listings-grid"></div>
    <p class="empty" id="listings-empty" hidden>Sin resultados para los filtros.</p>
  </section>

  <!-- EVENTS TAB -->
  <section class="view view-events hidden" data-view="events">
    <div class="events-filters">
      <button class="chip active" data-evt-filter="all">Todos</button>
      <button class="chip" data-evt-filter="price_drop">📉 Bajadas</button>
      <button class="chip" data-evt-filter="new">🆕 Nuevos</button>
      <button class="chip" data-evt-filter="price_rise">📈 Subidas</button>
      <button class="chip" data-evt-filter="removed">❌ Retirados</button>
      <button class="chip" data-evt-filter="relisted">♻️ Re-publicados</button>
    </div>
    <ol class="timeline" id="events-timeline"></ol>
  </section>

  <!-- ABOUT TAB -->
  <section class="view view-about hidden" data-view="about">
    <article class="prose">
      <h2>Cómo funciona</h2>
      <p>Este radar escanea Idealista, Fotocasa, Habitaclia y Pisos.com cada 30 minutos desde GitHub Actions. Detecta <strong>nuevos anuncios</strong>, <strong>bajadas de precio</strong>, <strong>subidas</strong> y <strong>retiradas</strong>. Los cambios se envían por Telegram al instante y se acumulan aquí para consulta.</p>
      <p>El estado vive en este mismo repositorio (<code>data/listings.db</code> + <code>data/listings.json</code>), así que el historial completo está en el git log.</p>
      <h2>Fuentes</h2>
      <ul>
        <li>Idealista · RSS + Playwright</li>
        <li>Fotocasa · Playwright</li>
        <li>Habitaclia · Playwright</li>
        <li>Pisos.com · Playwright</li>
      </ul>
      <p class="muted">Actualizado automáticamente en cada ciclo de scraping.</p>
    </article>
  </section>
</main>

<!-- DETAIL MODAL -->
<div class="modal hidden" id="modal">
  <div class="modal-backdrop"></div>
  <div class="modal-card">
    <button class="modal-close" id="modal-close">✕</button>
    <div id="modal-content"></div>
  </div>
</div>

<footer class="site-footer">
  <span class="mono muted">Scraper · GitHub Actions · <a href="https://github.com" target="_blank" rel="noopener">fuente</a></span>
</footer>

<script src="app.js"></script>
</body>
</html>
