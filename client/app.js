// ========================
// QuakeComm — app.js
// ========================

const API_URL = 'https://quakecomm-production.up.railway.app';

// --- State ---
let selectedStatus = null;
let currentPosition = null;

// --- DOM Elements ---
const buttons = document.querySelectorAll('.status-btn');
const noteEl = document.getElementById('note');
const sendBtn = document.getElementById('send-btn');
const feedback = document.getElementById('feedback');
const gpsStatus = document.getElementById('gps-status');
const modeStatus = document.getElementById('mode-status');

// --- Button Selection ---
buttons.forEach(btn => {
  btn.addEventListener('click', () => {
    buttons.forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedStatus = btn.dataset.status;
  });
});

// --- GPS ---
function getLocation() {
  if (!navigator.geolocation) {
    gpsStatus.textContent = 'NOT SUPPORTED';
    gpsStatus.style.color = 'var(--critical)';
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      currentPosition = {
        lat: pos.coords.latitude.toFixed(6),
        lon: pos.coords.longitude.toFixed(6)
      };
      gpsStatus.textContent = 'ACQUIRED';
      gpsStatus.style.color = 'var(--safe)';
    },
    (err) => {
      gpsStatus.textContent = 'UNAVAILABLE';
      gpsStatus.style.color = 'var(--critical)';
      currentPosition = null;
    }
  );
}

getLocation();

// --- UUID Generator ---
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// --- Checksum ---
function generateChecksum(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash).toString(16).slice(0, 6).toUpperCase();
}

// --- Build Message Packet ---
function buildPacket(status, lat, lon, note) {
  const uuid = generateUUID();
  const timestamp = Date.now();
  const noteClean = note.replace(/\|/g, '').slice(0, 100);
  const core = `QK|${uuid}|${timestamp}|${lat}|${lon}|${status}|${noteClean}`;
  const checksum = generateChecksum(core);
  return `${core}|${checksum}`;
}

// --- Local Queue ---
function saveToQueue(packet) {
  const queue = JSON.parse(localStorage.getItem('qc_queue') || '[]');
  queue.push({ packet, timestamp: Date.now() });
  localStorage.setItem('qc_queue', JSON.stringify(queue));
}

// --- Network Check ---
function isOnline() {
  return navigator.onLine;
}

// --- Send Logic ---
async function sendPacket(packet) {
  if (isOnline()) {
    modeStatus.textContent = 'ONLINE';
    modeStatus.style.color = 'var(--safe)';
    try {
      const res = await fetch(`${API_URL}/api/signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ packet })
      });
      if (res.ok) return true;
    } catch (e) {
      // fallback to queue
    }
  }

  modeStatus.textContent = 'OFFLINE';
  modeStatus.style.color = 'var(--critical)';
  saveToQueue(packet);
  return false;
}

// --- Send Button ---
sendBtn.addEventListener('click', async () => {
  if (!selectedStatus) {
    feedback.textContent = 'SELECT A STATUS FIRST';
    feedback.style.color = 'var(--critical)';
    return;
  }

  const lat = currentPosition ? currentPosition.lat : 'UNKNOWN';
  const lon = currentPosition ? currentPosition.lon : 'UNKNOWN';
  const note = noteEl.value.trim();

  const packet = buildPacket(selectedStatus, lat, lon, note);

  sendBtn.disabled = true;
  feedback.textContent = 'TRANSMITTING...';
  feedback.style.color = 'var(--muted)';

  const sent = await sendPacket(packet);

  if (sent) {
    feedback.textContent = 'SIGNAL TRANSMITTED';
    feedback.style.color = 'var(--safe)';
  } else {
    feedback.textContent = 'QUEUED — WILL SEND WHEN CONNECTED';
    feedback.style.color = 'var(--trapped)';
  }

  sendBtn.disabled = false;
});

// --- Online/Offline Events ---
window.addEventListener('online', () => {
  modeStatus.textContent = 'ONLINE';
  modeStatus.style.color = 'var(--safe)';
  flushQueue();
});

window.addEventListener('offline', () => {
  modeStatus.textContent = 'OFFLINE';
  modeStatus.style.color = 'var(--critical)';
});

// --- Flush Queue When Online ---
async function flushQueue() {
  const queue = JSON.parse(localStorage.getItem('qc_queue') || '[]');
  if (queue.length === 0) return;

  const remaining = [];
  for (const item of queue) {
    try {
      const res = await fetch(`${API_URL}/api/signal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ packet: item.packet })
      });
      if (!res.ok) remaining.push(item);
    } catch {
      remaining.push(item);
    }
  }
  localStorage.setItem('qc_queue', JSON.stringify(remaining));
}

// --- Register Service Worker ---
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(() => console.log('SW registered'))
      .catch((err) => console.log('SW failed:', err));
  });
}