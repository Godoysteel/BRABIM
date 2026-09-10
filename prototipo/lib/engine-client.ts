import type {IfcMesh} from '@/app/viewport';
import type {Room} from '@/lib/room';

// Talks to the IfcOpenShell sidecar (see experiments/desktop-sidecar,
// experiments/tauri-sidecar). Only available inside the Tauri desktop app;
// on the web prototype (GitHub Pages) this stays inert. Field names match
// Room exactly so the app's own room object can be sent as-is.
export type EngineRoomParams = Pick<Room,'width'|'depth'|'height'|'thickness'|'doorWidth'|'doorHeight'|'doorOffset'|'windowWidth'|'windowHeight'|'windowOffset'|'sill'>;

type Pending = {resolve: (meshes: IfcMesh[]) => void; reject: (error: Error) => void};

let childPromise: Promise<{write: (data: string) => Promise<void>}> | null = null;
let nextId = 1;
const pending = new Map<number, Pending>();

export function isEngineAvailable() {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

async function getChild() {
  if (!childPromise) {
    childPromise = (async () => {
      const {Command} = await import('@tauri-apps/plugin-shell');
      const command = Command.sidecar('binaries/brabim-engine');
      command.stdout.on('data', (line: string) => {
        let msg: any;
        try { msg = JSON.parse(line); } catch { return; }
        const entry = msg.id != null ? pending.get(msg.id) : undefined;
        if (!entry) return;
        pending.delete(msg.id);
        if (msg.type === 'result') entry.resolve(msg.meshes.map((m: any) => ({...m, height: 0})));
        else entry.reject(new Error(msg.message ?? 'Erro desconhecido do motor.'));
      });
      command.on('error', () => { childPromise = null; });
      command.on('close', () => { childPromise = null; });
      return command.spawn();
    })();
  }
  return childPromise;
}

export async function computeRoomMeshes(room: EngineRoomParams): Promise<IfcMesh[]> {
  const child = await getChild();
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, {resolve, reject});
    child.write(JSON.stringify({id, room}) + '\n').catch(reject);
  });
}
