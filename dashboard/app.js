/* Radar Inmobiliario · Dashboard JS
   Vanilla, single file, no deps. Reads data/listings.json. */

const STATE = {
  data: null,
  view: "listings",
  listingsFilters: {
    portal: "",
    location: "",
    maxPrice: null,
    minRooms: null,
    sort: "newest",
    status: "active",
  },
  eventsFilter: "all",
};

// ---------------------------------------------------------------- bootstrap
(async function init() {
  try {
    const res = await fetch(`listings.json?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("listings.json not found");
    STATE.data = await res.json();
  } catch (e) {
    document.getElementById("listings-grid").innerHTML =
      `<p class="empty">No hay datos todavía. El primer scraping poblará este dashboard.<br><small>${e.message}</small></p>`;
    return;
  }
  hydrateFilters();
  renderAll();
  bindEvents();
})();

// ---------------------------------------------------------------- rendering
function renderAll() {
  renderHeaderMeta();
  renderStats();
  renderListings();
  renderEvents();
}

function renderHeaderMeta() {
  const when = new Date(STATE.data.updated_at);
  const fmt = when.toLocaleString("es-ES", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  });
  document.getElementById("updated-at").textContent = `Actualizado · ${fmt}`;
}

function renderStats() {
  const { listings, events, stats } = STATE.data;
  const active = listings.filter(l => l.is_active);

  // Nuevos 24h
  const day = Date.now() - 86400e3;
  const week = Date.now() - 7 * 86400e3;
  const new24 = events.filter(e => e.event_type === "new" && new Date(e.occurred_at).getTime() > day).length;
  const drops7 = events.filter(e => e.event_type === "price_drop" && new Date(e.occurred_at).getTime() > week).length;

  const prices = active.map(l => l.price).filter(Boolean);
  const avg = prices.length ? Math.round(prices.reduce((a,b)=>a+b,0) / prices.length) : null;

  const perm2s = active
    .filter(l => l.price && l.size_m2 && l.size_m2 > 0)
    .map(l => l.price / l.size_m2);
  const perm2Avg = perm2s.length ? (perm2s.reduce((a,b)=>a+b,0) / perm2s.length).toFixed(1) : null;

  document.getElementById("stat-active").textContent = stats.active_total ?? active.length;
  document.getElementById("stat-new24").textContent = new24;
  document.getElementById("stat-drops").textContent = drops7;
  document.getElementById("stat-avg").textContent = avg ? `${avg}€` : "—";
  document.getElementById("stat-perm2").textContent = perm2Avg ? `${perm2Avg}` : "—";
}

// ---------------------------------------------------------------- filters
function hydrateFilters() {
  const portals = [...new Set(STATE.data.listings.map(l => l.portal))].sort();
  const locations = [...new Set(STATE.data.listings.map(l => l.location).filter(Boolean))].sort();

  const pSel = document.getElementById("filter-portal");
  portals.forEach(p => {
    const o = document.createElement("option");
    o.value = p; o.textContent = p;
    pSel.appendChild(o);
  });
  const lSel = document.getElementById("filter-location");
  locations.forEach(l => {
    const o = document.createElement("option");
    o.value = l; o.textContent = l;
    lSel.appendChild(o);
  });
}

function currentListings() {
  const f = STATE.listingsFilters;
  let items = STATE.data.listings.slice();
  if (f.status === "active") items = items.filter(l => l.is_active);
  else if (f.status === "inactive") items = items.filter(l => !l.is_active);
  if (f.portal) items = items.filter(l => l.portal === f.portal);
  if (f.location) items = items.filter(l => l.location === f.location);
  if (f.maxPrice) items = items.filter(l => l.price <= f.maxPrice);
  if (f.minRooms) items = items.filter(l => (l.rooms || 0) >= f.minRooms);

  const sort = f.sort;
  if (sort === "price-asc") items.sort((a,b) => a.price - b.price);
  else if (sort === "price-desc") items.sort((a,b) => b.price - a.price);
  else if (sort === "size-desc") items.sort((a,b) => (b.size_m2||0) - (a.size_m2||0));
  else if (sort === "perm2") items.sort((a,b) => {
    const ax = a.size_m2 ? a.price/a.size_m2 : Infinity;
    const bx = b.size_m2 ? b.price/b.size_m2 : Infinity;
    return ax - bx;
  });
  else /* newest */ items.sort((a,b) => new Date(b.first_seen) - new Date(a.first_seen));
  return items;
}

function renderListings() {
  const items = currentListings();
  const grid = document.getElementById("listings-grid");
  const empty = document.getElementById("listings-empty");
  grid.innerHTML = "";
  if (items.length === 0) { empty.hidden = false; return; }
  empty.hidden = true;

  // Build badge set from recent events (24h)
  const day = Date.now() - 86400e3;
  const recentByUid = {};
  for (const e of STATE.data.events) {
    if (new Date(e.occurred_at).getTime() < day) continue;
    recentByUid[e.uid] = recentByUid[e.uid] || [];
    recentByUid[e.uid].push(e.event_type);
  }

  for (const l of items) {
    const el = document.createElement("article");
    el.className = "card" + (l.is_active ? "" : " inactive");
    el.dataset.uid = l.uid;

    const meta = [];
    if (l.rooms) meta.push(`${l.rooms} hab`);
    if (l.size_m2) meta.push(`${l.size_m2} m²`);
    if (l.size_m2 && l.price) meta.push(`${(l.price/l.size_m2).toFixed(1)} €/m²`);

    const badges = (recentByUid[l.uid] || []).map(t => {
      if (t === "new") return `<span class="card-badge badge-new">Nuevo</span>`;
      if (t === "price_drop") return `<span class="card-badge badge-drop">Bajó precio</span>`;
      return "";
    }).join("");

    el.innerHTML = `
      <div class="card-price">${l.price.toLocaleString("es-ES")}€<span style="font-size:13px;color:var(--ink-mute);"> /mes</span></div>
      <div class="card-meta">${meta.map(m => `<span>${m}</span>`).join("")}</div>
      <h3 class="card-title">${escapeHtml(l.title)}</h3>
      <div class="card-location">${escapeHtml(l.location || l.raw_location || "—")}</div>
      <div class="card-footer">
        <span class="portal-tag">${l.portal}</span>
        <span>${badges}</span>
      </div>
    `;
    el.addEventListener("click", () => openModal(l));
    grid.appendChild(el);
  }
}

function renderEvents() {
  const tl = document.getElementById("events-timeline");
  const filt = STATE.eventsFilter;
  const events = STATE.data.events.filter(e => filt === "all" || e.event_type === filt);
  tl.innerHTML = "";
  if (events.length === 0) {
    tl.innerHTML = `<li class="empty">Sin eventos todavía.</li>`;
    return;
  }
  for (const e of events.slice(0, 200)) {
    const li = document.createElement("li");
    li.className = "event " + e.event_type;
    const when = new Date(e.occurred_at).toLocaleString("es-ES", {
      day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit"
    });
    let price = "";
    if (e.event_type === "price_drop") {
      const delta = e.new_price - e.old_price;
      const pct = ((delta / e.old_price) * 100).toFixed(1);
      price = `<span class="event-price event-delta-down">${e.old_price}€ → ${e.new_price}€  (${delta}€, ${pct}%)</span>`;
    } else if (e.event_type === "price_rise") {
      const delta = e.new_price - e.old_price;
      const pct = ((delta / e.old_price) * 100).toFixed(1);
      price = `<span class="event-price event-delta-up">${e.old_price}€ → ${e.new_price}€  (+${delta}€, +${pct}%)</span>`;
    } else if (e.event_type === "new" || e.event_type === "relisted") {
      price = `<span class="event-price">${e.new_price}€</span>`;
    } else if (e.event_type === "removed") {
      price = `<span class="event-price">${e.old_price}€</span>`;
    }
    li.innerHTML = `
      <div class="event-head">
        <h4 class="event-title">${LABELS[e.event_type]}</h4>
        <span class="event-when">${when}</span>
      </div>
      <div class="event-meta">
        <a href="${e.url}" target="_blank" rel="noopener">${escapeHtml(e.title)}</a>
        — ${e.portal} · ${escapeHtml(e.location || "")}
        ${e.rooms ? `· ${e.rooms}hab` : ""}
        ${e.size_m2 ? `· ${e.size_m2}m²` : ""}
      </div>
      <div>${price}</div>
    `;
    tl.appendChild(li);
  }
}

const LABELS = {
  new: "Nuevo anuncio",
  price_drop: "Bajada de precio",
  price_rise: "Subida de precio",
  removed: "Retirado",
  relisted: "Re-publicado",
};

// ---------------------------------------------------------------- modal
function openModal(listing) {
  const modal = document.getElementById("modal");
  const content = document.getElementById("modal-content");
  const hist = STATE.data.price_history[listing.uid] || [];

  let chartHtml = "";
  if (hist.length > 1) {
    chartHtml = renderPriceChart(hist);
  }

  content.innerHTML = `
    <p class="muted mono" style="font-size:11px;letter-spacing:.12em;text-transform:uppercase;margin:0 0 8px;">${listing.portal} · ${escapeHtml(listing.location || "")}</p>
    <h2 style="font-family:var(--serif);font-size:24px;margin:0 0 12px;">${escapeHtml(listing.title)}</h2>
    <div class="mono" style="font-size:32px;font-weight:600;">${listing.price.toLocaleString("es-ES")}€<span style="font-size:14px;color:var(--ink-mute)"> /mes</span></div>
    <p class="muted" style="margin-top:8px;">
      ${listing.rooms ? `${listing.rooms} hab · ` : ""}
      ${listing.bathrooms ? `${listing.bathrooms} baños · ` : ""}
      ${listing.size_m2 ? `${listing.size_m2} m²` : ""}
    </p>
    ${listing.description ? `<p style="margin-top:16px;font-family:var(--serif);">${escapeHtml(listing.description)}</p>` : ""}
    ${chartHtml}
    <div style="margin-top:24px;">
      <a href="${listing.url}" target="_blank" rel="noopener" style="display:inline-block;padding:10px 18px;background:var(--ink);color:var(--bg);text-decoration:none;border-radius:2px;font-weight:500;font-size:14px;">
        Ver en ${listing.portal} ↗
      </a>
    </div>
    <p class="mono muted" style="font-size:11px;margin-top:20px;">
      Visto por primera vez: ${new Date(listing.first_seen).toLocaleString("es-ES")}<br>
      Última vez visto: ${new Date(listing.last_seen).toLocaleString("es-ES")}
    </p>
  `;
  modal.classList.remove("hidden");
}

function renderPriceChart(history) {
  const w = 540, h = 140, pad = 24;
  const prices = history.map(p => p.price);
  const min = Math.min(...prices), max = Math.max(...prices);
  const range = max - min || 1;
  const pts = history.map((p, i) => {
    const x = pad + (i / (history.length - 1)) * (w - 2*pad);
    const y = h - pad - ((p.price - min) / range) * (h - 2*pad);
    return [x, y, p];
  });
  const path = pts.map((pt, i) => (i === 0 ? "M" : "L") + pt[0].toFixed(1) + "," + pt[1].toFixed(1)).join(" ");
  const circles = pts.map(pt =>
    `<circle cx="${pt[0].toFixed(1)}" cy="${pt[1].toFixed(1)}" r="3" fill="var(--accent)"></circle>`
  ).join("");
  return `
    <div class="price-chart">
      <p class="price-chart-title">Historial de precio · ${history.length} puntos</p>
      <svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;">
        <path d="${path}" fill="none" stroke="var(--accent)" stroke-width="2" />
        ${circles}
        <text x="${pad}" y="14" font-size="11" font-family="var(--mono)" fill="var(--ink-mute)">${max}€</text>
        <text x="${pad}" y="${h - 4}" font-size="11" font-family="var(--mono)" fill="var(--ink-mute)">${min}€</text>
      </svg>
    </div>
  `;
}

// ---------------------------------------------------------------- events
function bindEvents() {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => switchView(tab.dataset.tab));
  });

  document.getElementById("filter-portal").addEventListener("change", e => {
    STATE.listingsFilters.portal = e.target.value; renderListings();
  });
  document.getElementById("filter-location").addEventListener("change", e => {
    STATE.listingsFilters.location = e.target.value; renderListings();
  });
  document.getElementById("filter-max-price").addEventListener("input", e => {
    STATE.listingsFilters.maxPrice = e.target.value ? parseInt(e.target.value) : null; renderListings();
  });
  document.getElementById("filter-min-rooms").addEventListener("input", e => {
    STATE.listingsFilters.minRooms = e.target.value ? parseInt(e.target.value) : null; renderListings();
  });
  document.getElementById("filter-sort").addEventListener("change", e => {
    STATE.listingsFilters.sort = e.target.value; renderListings();
  });
  document.getElementById("filter-status").addEventListener("change", e => {
    STATE.listingsFilters.status = e.target.value; renderListings();
  });

  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      STATE.eventsFilter = chip.dataset.evtFilter;
      renderEvents();
    });
  });

  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.querySelector(".modal-backdrop").addEventListener("click", closeModal);
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });
}

function switchView(name) {
  STATE.view = name;
  document.querySelectorAll(".tab").forEach(t => t.classList.toggle("active", t.dataset.tab === name));
  document.querySelectorAll(".view").forEach(v => v.classList.toggle("hidden", v.dataset.view !== name));
}

function closeModal() {
  document.getElementById("modal").classList.add("hidden");
}

function escapeHtml(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
