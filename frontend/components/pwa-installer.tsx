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
  
  // Safe translation getters with fallbacks
  const getInstallAppAriaLabel = () => {
    try {
      return t('installAppAriaLabel');
    } catch {
      return 'Install app';
    }
  };
  
  const getInstallAppText = () => {
    try {
      return t('installApp');
    } catch {
      return 'Install App';
    }
  };
  
  const installAppAriaLabel = getInstallAppAriaLabel();
  const installAppText = getInstallAppText();

  useEffect(() => {
    // Check if app is already installed (multiple methods for different platforms)
    const checkIfInstalled = () => {
      // Method 1: Check display mode (works for most browsers)
    if (window.matchMedia('(display-mode: standalone)').matches) {
        return true;
      }
      
      // Method 2: Check for iOS standalone mode
      if ((window.navigator as any).standalone === true) {
        return true;
      }
      
      // Method 3: Check if running in standalone mode via user agent
      if (window.matchMedia('(display-mode: fullscreen)').matches) {
        return true;
      }
      
      // Method 4: Check if document is in fullscreen (PWA mode)
      if (document.referrer.includes('android-app://')) {
        return true;
      }
      
      return false;
    };

    // Check immediately
    if (checkIfInstalled()) {
      setIsInstalled(true);
      return;
    }

    // Also check on window load and focus events
    const handleVisibilityChange = () => {
      if (checkIfInstalled()) {
        setIsInstalled(true);
      }
    };

    window.addEventListener('load', handleVisibilityChange);
    document.addEventListener('visibilitychange', handleVisibilityChange);

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

    // Show button by default (only if not installed)
    if (!checkIfInstalled()) {
    setShowInstallButton(true);
    }

    // Listen for beforeinstallprompt event
    const handler = (e: Event) => {
      // Only prevent default if we're going to use the prompt
      // This prevents the warning about preventDefault() without prompt()
      const beforeInstallPrompt = e as any;
      if (beforeInstallPrompt && typeof beforeInstallPrompt.prompt === 'function') {
      e.preventDefault();
        setDeferredPrompt(beforeInstallPrompt);
        deferredPromptRef.current = beforeInstallPrompt;
      console.log('beforeinstallprompt event received');
      }
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
      window.removeEventListener('load', handleVisibilityChange);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
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

  // Don't show if app is already installed or button shouldn't be shown
  if (isInstalled || !showInstallButton) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={handleInstallClick}
        className="bg-black hover:bg-gray-900 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 transition-colors"
        aria-label={installAppAriaLabel}
      >
        <Smartphone className="h-5 w-5" />
        {installAppText}
      </button>
    </div>
  );
}

