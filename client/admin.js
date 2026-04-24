// ========================
// QuakeComm — admin.js
// ========================

const API_URL = 'https://quakecomm-production.up.railway.app';

let map;
let markers = [];
let currentView = 'certainty';
let currentLang = 'en';

// --- Translations ---
const TRANSLATIONS = {
  en: {
    rescue_center: 'RESCUE COMMAND CENTER',
    certainty: 'CERTAINTY',
    uncertainty: 'UNCERTAINTY',
    total: 'TOTAL',
    critical: 'CRITICAL',
    trapped: 'TRAPPED',
    safe: 'SAFE',
    priority_list: '// PRIORITY LIST',
    refresh: '↻ REFRESH',
    no_signals: 'NO SIGNALS',
    navigate: '→ NAVIGATE',
    score: 'SCORE',
    conflicts: 'CONFLICT(S) DETECTED'
  },
  tr: {
    rescue_center: 'KURTARMA KOMUTA MERKEZİ',
    certainty: 'KESİNLİK',
    uncertainty: 'BELİRSİZLİK',
    total: 'TOPLAM',
    critical: 'KRİTİK',
    trapped: 'MAHSUR',
    safe: 'GÜVENLİ',
    priority_list: '// ÖNCELİK LİSTESİ',
    refresh: '↻ YENİLE',
    no_signals: 'SİNYAL YOK',
    navigate: '→ YÖNLENDİR',
    score: 'SKOR',
    conflicts: 'ÇAKIŞMA TESPİT EDİLDİ'
  },
  de: {
    rescue_center: 'RETTUNGSLEITSTELLE',
    certainty: 'SICHERHEIT',
    uncertainty: 'UNSICHERHEIT',
    total: 'GESAMT',
    critical: 'KRITISCH',
    trapped: 'EINGESCHLOSSEN',
    safe: 'SICHER',
    priority_list: '// PRIORITÄTSLISTE',
    refresh: '↻ AKTUALISIEREN',
    no_signals: 'KEINE SIGNALE',
    navigate: '→ NAVIGIEREN',
    score: 'PUNKTZAHL',
    conflicts: 'KONFLIKTE ERKANNT'
  },
  el: {
    rescue_center: 'ΚΕΝΤΡΟ ΔΙΑΣΩΣΗΣ',
    certainty: 'ΒΕΒΑΙΟΤΗΤΑ',
    uncertainty: 'ΑΒΕΒΑΙΟΤΗΤΑ',
    total: 'ΣΥΝΟΛΟ',
    critical: 'ΚΡΙΣΙΜΟ',
    trapped: 'ΠΑΓΙΔΕΥΜΕΝΟΣ',
    safe: 'ΑΣΦΑΛΗΣ',
    priority_list: '// ΛΙΣΤΑ ΠΡΟΤΕΡΑΙΟΤΗΤΑΣ',
    refresh: '↻ ΑΝΑΝΕΩΣΗ',
    no_signals: 'ΔΕΝ ΥΠΑΡΧΟΥΝ ΣΗΜΑΤΑ',
    navigate: '→ ΠΛΟΗΓΗΣΗ',
    score: 'ΣΚΟΡ',
    conflicts: 'ΕΝΤΟΠΙΣΜΟΣ ΣΥΓΚΡΟΥΣΕΩΝ'
  },
  it: {
    rescue_center: 'CENTRO DI COMANDO SOCCORSO',
    certainty: 'CERTEZZA',
    uncertainty: 'INCERTEZZA',
    total: 'TOTALE',
    critical: 'CRITICO',
    trapped: 'INTRAPPOLATO',
    safe: 'SICURO',
    priority_list: '// LISTA PRIORITÀ',
    refresh: '↻ AGGIORNA',
    no_signals: 'NESSUN SEGNALE',
    navigate: '→ NAVIGA',
    score: 'PUNTEGGIO',
    conflicts: 'CONFLITTI RILEVATI'
  }
};

// --- Apply Language ---
function applyLang(lang) {
  currentLang = lang;
  const t = TRANSLATIONS[lang];

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });

  loadData();
}

// --- Init Map ---
function initMap() {
  map = L.map('map', {
    center: [39.0, 35.0],
    zoom: 6,
    zoomControl: true
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);
}

// --- Clear Markers ---
function clearMarkers() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
}

// --- Status Color ---
function statusColor(status) {
  if (status === 'critical') return '#ff2020';
  if (status === 'trapped')  return '#ff8800';
  return '#00e676';
}

// --- Format Time ---
function formatTime(timestamp) {
  let ts = timestamp;
  if (ts > 1e10) ts = ts / 1000;
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString();
}

// --- Add Marker ---
function addMarker(signal, isConflict = false) {
  const t = TRANSLATIONS[currentLang];
  const color = isConflict ? '#ff8800' : statusColor(signal.status);
  const radius = signal.status === 'critical' ? 10 : 8;

  const circle = L.circleMarker([parseFloat(signal.lat), parseFloat(signal.lon)], {
    radius,
    fillColor: color,
    color,
    weight: 2,
    opacity: 0.9,
    fillOpacity: 0.7
  });

  const popupContent = `
    <div style="font-family: monospace; font-size: 12px; color: #fff; background: #111; padding: 8px; border-radius: 2px;">
      <strong style="color: ${color}">${signal.status.toUpperCase()}</strong><br/>
      ${t.score}: ${signal.priority_score}<br/>
      ${signal.note ? `Note: ${signal.note}<br/>` : ''}
      ${formatTime(signal.timestamp)}<br/>
      <a href="https://www.google.com/maps?q=${signal.lat},${signal.lon}" 
         target="_blank" 
         style="color: #00c853;">${t.navigate}</a>
    </div>
  `;

  circle.bindPopup(popupContent);
  circle.addTo(map);
  markers.push(circle);
}

// --- Update Stats ---
function updateStats(signals) {
  document.getElementById('stat-total').textContent    = signals.length;
  document.getElementById('stat-critical').textContent = signals.filter(s => s.status === 'critical').length;
  document.getElementById('stat-trapped').textContent  = signals.filter(s => s.status === 'trapped').length;
  document.getElementById('stat-safe').textContent     = signals.filter(s => s.status === 'safe').length;
}

// --- Update Signal List ---
function updateList(signals) {
  const t = TRANSLATIONS[currentLang];
  const list = document.getElementById('signal-list');
  list.innerHTML = '';

  if (signals.length === 0) {
    list.innerHTML = `<p style="color: #444; font-size: 0.7rem; font-family: monospace; padding: 12px;">${t.no_signals}</p>`;
    return;
  }

  signals.forEach(s => {
    const card = document.createElement('div');
    card.className = `signal-card ${s.status}`;

    card.innerHTML = `
      <div class="card-top">
        <span class="card-status ${s.status}">${s.status.toUpperCase()}</span>
        <span class="card-score mono">${t.score}: ${s.priority_score}</span>
      </div>
      <div class="card-coords mono">${s.lat}, ${s.lon}</div>
      ${s.note ? `<div class="card-note">${s.note}</div>` : ''}
      <div class="card-time mono">${formatTime(s.timestamp)}</div>
      <a class="card-nav" href="https://www.google.com/maps?q=${s.lat},${s.lon}" target="_blank">${t.navigate}</a>
    `;

    card.addEventListener('click', () => {
      map.setView([parseFloat(s.lat), parseFloat(s.lon)], 15);
    });

    list.appendChild(card);
  });
}

// --- Load Data ---
async function loadData() {
  const t = TRANSLATIONS[currentLang];
  try {
    const [signalsRes, conflictsRes] = await Promise.all([
      fetch(`${API_URL}/api/signals`),
      fetch(`${API_URL}/api/conflicts`)
    ]);

    const signalsData   = await signalsRes.json();
    const conflictsData = await conflictsRes.json();

    const signals   = signalsData.signals || [];
    const conflicts = conflictsData.conflicts || [];

    clearMarkers();
    updateStats(signals);

    const conflictUUIDs = new Set();
    conflicts.forEach(c => {
      conflictUUIDs.add(c.signal_1);
      conflictUUIDs.add(c.signal_2);
    });

    const badge = document.getElementById('conflict-badge');
    if (conflicts.length > 0) {
      badge.style.display = 'inline';
      badge.textContent = `⚠ ${conflicts.length} ${t.conflicts}`;
    } else {
      badge.style.display = 'none';
    }

    if (currentView === 'certainty') {
      const certain = signals.filter(s => !conflictUUIDs.has(s.uuid));
      certain.forEach(s => addMarker(s, false));
      updateList(certain);
    } else {
      const uncertain = signals.filter(s => conflictUUIDs.has(s.uuid));
      uncertain.forEach(s => addMarker(s, true));
      updateList(uncertain);
    }

    if (signals.length > 0) {
      const lats = signals.map(s => parseFloat(s.lat));
      const lons = signals.map(s => parseFloat(s.lon));
      const bounds = [
        [Math.min(...lats) - 0.01, Math.min(...lons) - 0.01],
        [Math.max(...lats) + 0.01, Math.max(...lons) + 0.01]
      ];
      map.fitBounds(bounds);
    }

  } catch (err) {
    console.error('Load error:', err);
  }
}

// --- Toggle View ---
document.getElementById('btn-certainty').addEventListener('click', () => {
  currentView = 'certainty';
  document.getElementById('btn-certainty').classList.add('active');
  document.getElementById('btn-uncertainty').classList.remove('active');
  loadData();
});

document.getElementById('btn-uncertainty').addEventListener('click', () => {
  currentView = 'uncertainty';
  document.getElementById('btn-uncertainty').classList.add('active');
  document.getElementById('btn-certainty').classList.remove('active');
  loadData();
});

// --- Lang Buttons ---
document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', () => applyLang(btn.dataset.lang));
});

// --- Auto Refresh ---
setInterval(loadData, 30000);

// --- Init ---
initMap();
applyLang('en');