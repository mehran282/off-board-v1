'use client';

import { useEffect, useState, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { Smartphone } from 'lucide-react';

export function PWAInstaller() {
  const t = useTranslations('common');
  const tPWA = useTranslations('pwa');
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const deferredPromptRef = useRef<any>(null);
  const [showInstallButton, setShowInstallButton] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if app is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration);
        })
        .catch((error) => {
          console.log('Service Worker registration failed:', error);
        });
    }

    // Show button by default
    setShowInstallButton(true);

    // Listen for beforeinstallprompt event
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      deferredPromptRef.current = e;
      console.log('beforeinstallprompt event received');
    };

    window.addEventListener('beforeinstallprompt', handler);

    // Also check if the event was already fired (some browsers fire it before we listen)
    // This is a workaround for browsers that fire the event immediately
    setTimeout(() => {
      // If still no prompt after 2 seconds, button will still work with instructions
      console.log('Waiting for install prompt...');
    }, 2000);

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
    };
  }, []);

  const handleInstallClick = async () => {
    // Check both state and ref for deferredPrompt
    const prompt = deferredPrompt || deferredPromptRef.current;
    
    // If deferredPrompt is available, use it immediately (like browser's install button)
    if (prompt) {
      try {
        // This will show the browser's native install prompt - exactly like the browser's install button
        await prompt.prompt();
        const { outcome } = await prompt.userChoice;
        
        if (outcome === 'accepted') {
          console.log('User accepted the install prompt');
          setShowInstallButton(false);
          setIsInstalled(true);
        } else {
          console.log('User dismissed the install prompt');
        }

        setDeferredPrompt(null);
        deferredPromptRef.current = null;
      } catch (error) {
        console.error('Error showing install prompt:', error);
        showInstallInstructions();
      }
      return;
    }

    // If no deferredPrompt yet, wait for it to become available
    // This handles cases where the event hasn't fired yet
    let attempts = 0;
    const maxAttempts = 20; // Wait up to 2 seconds (20 * 100ms)
    
    while (attempts < maxAttempts && !deferredPromptRef.current) {
      await new Promise(resolve => setTimeout(resolve, 100));
      attempts++;
    }

    // Try again if prompt became available
    if (deferredPromptRef.current) {
      handleInstallClick();
      return;
    }

    // If still no prompt after waiting, show instructions
    // This means the browser doesn't support automatic installation
    // or the PWA criteria aren't met (HTTPS, valid manifest, service worker, etc.)
    showInstallInstructions();
  };

  const showInstallInstructions = () => {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    const isChrome = /Chrome/.test(navigator.userAgent) && !/Edge|Edg/.test(navigator.userAgent);
    const isEdge = /Edge|Edg/.test(navigator.userAgent);
    const isFirefox = /Firefox/.test(navigator.userAgent);
    
    let message = '';
    if (isIOS) {
      message = tPWA('installInstructionsIOS');
    } else if (isAndroid) {
      if (isChrome) {
        message = tPWA('installInstructionsAndroidChrome');
      } else {
        message = tPWA('installInstructionsAndroidOther');
      }
    } else {
      // Desktop browsers
      if (isChrome) {
        message = tPWA('installInstructionsDesktopChrome');
      } else if (isEdge) {
        message = tPWA('installInstructionsDesktopEdge');
      } else if (isFirefox) {
        message = tPWA('installInstructionsDesktopFirefox');
      } else {
        message = tPWA('installInstructionsDesktopOther');
      }
    }
    
    alert(message);
  };

  // Don't show if app is already installed
  if (isInstalled) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={handleInstallClick}
        className="bg-black hover:bg-gray-900 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 transition-colors"
        aria-label={t('installAppAriaLabel')}
      >
        <Smartphone className="h-5 w-5" />
        {t('installApp')}
      </button>
    </div>
  );
}

