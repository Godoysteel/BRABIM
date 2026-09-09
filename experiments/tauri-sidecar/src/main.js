import { Command } from '@tauri-apps/plugin-shell';

let logEl, splashEl, splashStatusEl;
let child = null;
let launchedAt = 0;
let ready = false;

function log(line) {
  logEl.textContent += line + "\n";
}

function hideSplash() {
  splashEl.classList.add('hidden');
}

async function startEngine() {
  const command = Command.sidecar("binaries/brabim-engine");
  command.stdout.on("data", (line) => {
    const elapsed = ((performance.now() - launchedAt) / 1000).toFixed(3);
    log(`[+${elapsed}s] stdout: ${line}`);
    if (!ready) {
      try {
        const parsed = JSON.parse(line);
        if (parsed.type === 'ready') {
          ready = true;
          hideSplash();
        }
      } catch {}
    }
  });
  command.stderr.on("data", (line) => log(`stderr: ${line}`));
  command.on("close", (data) => log(`process closed: ${JSON.stringify(data)}`));
  command.on("error", (error) => { log(`process error: ${error}`); splashStatusEl.textContent = 'Erro ao iniciar o motor.'; });
  launchedAt = performance.now();
  child = await command.spawn();
  log("sidecar spawned, pid " + child.pid);
}

async function sendRequest() {
  if (!child) return log("motor ainda não iniciado");
  await child.write(JSON.stringify({ id: Date.now() }) + "\n");
}

window.addEventListener("DOMContentLoaded", () => {
  logEl = document.querySelector("#log");
  splashEl = document.querySelector("#splash");
  splashStatusEl = document.querySelector("#splash-status");
  document.querySelector("#send").addEventListener("click", sendRequest);
  startEngine();
});
