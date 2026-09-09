import { Command } from '@tauri-apps/plugin-shell';

let logEl;
let child = null;
let launchedAt = 0;

function log(line) {
  logEl.textContent += line + "\n";
}

async function startEngine() {
  const command = Command.sidecar("binaries/brabim-engine");
  command.stdout.on("data", (line) => {
    const elapsed = ((performance.now() - launchedAt) / 1000).toFixed(3);
    log(`[+${elapsed}s] stdout: ${line}`);
  });
  command.stderr.on("data", (line) => log(`stderr: ${line}`));
  command.on("close", (data) => log(`process closed: ${JSON.stringify(data)}`));
  command.on("error", (error) => log(`process error: ${error}`));
  launchedAt = performance.now();
  child = await command.spawn();
  log("sidecar spawned, pid " + child.pid);
}

async function sendRequest() {
  if (!child) return log("start the engine first");
  await child.write(JSON.stringify({ id: Date.now() }) + "\n");
}

window.addEventListener("DOMContentLoaded", () => {
  logEl = document.querySelector("#log");
  document.querySelector("#start").addEventListener("click", startEngine);
  document.querySelector("#send").addEventListener("click", sendRequest);
});
