'use client';

import dynamic from 'next/dynamic';

const PWAInstaller = dynamic(() => import('@/components/pwa-installer').then(mod => ({ default: mod.PWAInstaller })), {
  ssr: false,
});

export function PWAInstallerWrapper() {
  return <PWAInstaller />;
}

