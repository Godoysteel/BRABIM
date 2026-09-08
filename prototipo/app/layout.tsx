import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'BRABIM · Estudo de paredes', description: 'Protótipo de edição de paredes em planta e 3D.' };
export default function RootLayout({ children }: {children: React.ReactNode}) { return <html lang="pt-BR"><body>{children}</body></html>; }
