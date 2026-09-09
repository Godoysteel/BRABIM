import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/postcss';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('.',import.meta.url));
export default defineConfig({
  root:root+'pages',
  base:'/',
  publicDir:root+'public',
  plugins:[react()],
  resolve:{alias:{'@':root}},
  define:{__BRABIM_BASE__:JSON.stringify('')},
  css:{postcss:{plugins:[tailwindcss()]}},
  server:{port:1420,strictPort:true},
  build:{outDir:root+'dist-tauri',emptyOutDir:true},
});
