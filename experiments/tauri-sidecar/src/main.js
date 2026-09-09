import { Command } from '@tauri-apps/plugin-shell';

let splashEl, statusEl, planEl, widthEl, depthEl;
let child = null;
let ready = false;
let nextId = 1;
const pending = new Map();

function hideSplash() {
  splashEl.classList.add('hidden');
}

function renderPlan(meshes) {
  const svgNS = 'http://www.w3.org/2000/svg';
  planEl.innerHTML = '';
  for (const mesh of meshes) {
    const xs = mesh.vertices.map((v) => v[0]);
    const ys = mesh.vertices.map((v) => v[1]);
    const rect = document.createElementNS(svgNS, 'rect');
    rect.setAttribute('x', Math.min(...xs));
    rect.setAttribute('y', Math.min(...ys));
    rect.setAttribute('width', Math.max(...xs) - Math.min(...xs));
    rect.setAttribute('height', Math.max(...ys) - Math.min(...ys));
    rect.setAttribute('fill', '#657a88');
    planEl.appendChild(rect);
  }
}

function requestRoom() {
  if (!child) return;
  const id = nextId++;
  const room = { width: Number(widthEl.value), depth: Number(depthEl.value), height: 2.8, thickness: 0.2 };
  statusEl.textContent = 'calculando...';
  const t0 = performance.now();
  pending.set(id, t0);
  child.write(JSON.stringify({ id, room }) + '\n');
}

async function startEngine() {
  const command = Command.sidecar('binaries/brabim-engine');
  command.stdout.on('data', (line) => {
    let msg;
    try { msg = JSON.parse(line); } catch { return; }
    if (msg.type === 'ready') {
      ready = true;
      hideSplash();
      statusEl.textContent = 'pronto';
      requestRoom();
    } else if (msg.type === 'result') {
      const t0 = pending.get(msg.id) ?? performance.now();
      pending.delete(msg.id);
      const roundTrip = Math.round(performance.now() - t0);
      statusEl.textContent = `atualizado (${msg.elapsed_seconds}s motor, ${roundTrip}ms total)`;
      renderPlan(msg.meshes);
    } else if (msg.type === 'error') {
      statusEl.textContent = 'erro: ' + msg.message;
    }
  });
  command.stderr.on('data', (line) => console.error('stderr', line));
  command.on('error', (error) => { statusEl.textContent = 'erro ao iniciar motor'; console.error(error); });
  child = await command.spawn();
}

window.addEventListener('DOMContentLoaded', () => {
  splashEl = document.querySelector('#splash');
  statusEl = document.querySelector('#status');
  planEl = document.querySelector('#plan');
  widthEl = document.querySelector('#width');
  depthEl = document.querySelector('#depth');
  let debounce;
  const onChange = () => { clearTimeout(debounce); debounce = setTimeout(requestRoom, 300); };
  widthEl.addEventListener('input', onChange);
  depthEl.addEventListener('input', onChange);
  startEngine();
});
