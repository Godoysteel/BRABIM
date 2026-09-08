import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/postcss';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('.',import.meta.url));
export default defineConfig({root:root+'pages',base:'/BRABIM/',publicDir:root+'public',plugins:[react()],resolve:{alias:{'@':root}},define:{__BRABIM_BASE__:JSON.stringify('/BRABIM')},css:{postcss:{plugins:[tailwindcss()]}},build:{outDir:root+'dist-pages',emptyOutDir:true}});
