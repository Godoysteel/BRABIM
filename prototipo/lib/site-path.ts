declare const __BRABIM_BASE__: string;
export const sitePath = (path: string) => (typeof __BRABIM_BASE__ === 'string' ? __BRABIM_BASE__ : '') + path;
