import {createRoot} from 'react-dom/client';
import Home from '../app/page';
import Ensaios from '../app/ensaios/page';
import '../app/globals.css';
createRoot(document.getElementById('root')!).render(location.pathname.replace(/\/$/,'').endsWith('/ensaios') ? <Ensaios/> : <Home/>);
