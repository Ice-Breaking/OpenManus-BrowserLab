// Preload guard (Node CLI only):
// lottie-web is pulled in transitively via @visactor/vmind -> @visactor/vrender-kits.
// Its UMD wrapper executes a side-effect IIFE whenever `typeof navigator !== "undefined"`,
// and that IIFE calls document.createElement() at import time. Node 22 defines a global
// `navigator` but no DOM, which crashes the whole pipeline before any chart is generated.
// vrender's Lottie graphic already early-returns unless vglobal.env === "browser", so the
// runtime never needs lottie here. Making `navigator` undefined during import keeps the
// exact same modules/versions while skipping the browser-only side effect.
try {
  Object.defineProperty(globalThis, "navigator", {
    value: undefined,
    configurable: true,
    writable: true,
  });
} catch (_e) {
  // non-fatal: if undefined, fall back to deleting
  try {
    // @ts-ignore
    delete (globalThis as any).navigator;
  } catch (_e2) {}
}
export {};
