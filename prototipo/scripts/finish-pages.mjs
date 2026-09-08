import {copyFile,mkdir,writeFile} from 'node:fs/promises';
await mkdir('dist-pages/ensaios',{recursive:true});
await copyFile('dist-pages/index.html','dist-pages/ensaios/index.html');
await writeFile('dist-pages/.nojekyll','');
