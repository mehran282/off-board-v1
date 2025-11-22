'use client';

import { useEffect, useState, useRef } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { Smartphone } from 'lucide-react';

export function PWAInstaller() {
  const t = useTranslations('common');
  const tPWA = useTranslations('pwa');
  const locale = useLocale();
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
    // Only register service worker in production (not in development)
    // Check if we're in development by checking the hostname
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.port === '3040';
    
    if ('serviceWorker' in navigator && !isDevelopment) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration);
        })
        .catch((error) => {
          console.log('Service Worker registration failed:', error);
        });
    } else if (isDevelopment) {
      // Unregister any existing service workers in development
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        registrations.forEach((registration) => {
          registration.unregister();
        });
      });
    }

    // Show button by default (only if not installed)
    if (!checkIfInstalled()) {
      setShowInstallButton(true);
    }

    // Listen for beforeinstallprompt event
    // This event is fired when the browser thinks the PWA is installable
    // It may not fire if:
    // 1. PWA criteria aren't met (HTTPS, manifest, service worker)
    // 2. User already dismissed the prompt
    // 3. App is already installed
    // 4. Event fired before we started listening
    const handler = (e: Event) => {
      // Only prevent default if we're going to use the prompt
      // This prevents the warning about preventDefault() without prompt()
      const beforeInstallPrompt = e as any;
      if (beforeInstallPrompt && typeof beforeInstallPrompt.prompt === 'function') {
        e.preventDefault();
        setDeferredPrompt(beforeInstallPrompt);
        deferredPromptRef.current = beforeInstallPrompt;
        console.log('✅ beforeinstallprompt event received - install prompt available');
      }
    };

    // Add listener immediately
    window.addEventListener('beforeinstallprompt', handler);

    // Also check if event was already fired (some browsers fire it very early)
    // This is a workaround for browsers that fire the event before React mounts
    // We can't actually capture it if it already fired, but we can log it
    console.log('🔍 Listening for beforeinstallprompt event...');
    
    // Check periodically if prompt becomes available (for debugging)
    const checkInterval = setInterval(() => {
      if (deferredPromptRef.current) {
        console.log('✅ Install prompt is available');
        clearInterval(checkInterval);
      }
    }, 1000);

    // Clear interval after 10 seconds
    setTimeout(() => {
      clearInterval(checkInterval);
      if (!deferredPromptRef.current) {
        console.log('⚠️ Install prompt not received after 10 seconds. Possible reasons:');
        console.log('  - PWA criteria not met (HTTPS, manifest, service worker)');
        console.log('  - User already dismissed the prompt');
        console.log('  - App already installed');
        console.log('  - Browser doesn\'t support beforeinstallprompt');
      }
    }, 10000);

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
        console.log('🚀 Showing install prompt...');
        // This will show the browser's native install prompt - exactly like the browser's install button
        await prompt.prompt();
        const { outcome } = await prompt.userChoice;
        
        if (outcome === 'accepted') {
          console.log('✅ User accepted the install prompt');
          setShowInstallButton(false);
          setIsInstalled(true);
        } else {
          console.log('❌ User dismissed the install prompt');
        }

        // Clear the prompt after use (it can only be used once)
        setDeferredPrompt(null);
        deferredPromptRef.current = null;
      } catch (error) {
        console.error('❌ Error showing install prompt:', error);
        // If prompt() fails, show manual instructions
        showInstallInstructions();
      }
      return;
    }

    // If no deferredPrompt yet, wait for it to become available
    // This handles cases where the event hasn't fired yet or fired before we listened
    console.log('⏳ Install prompt not available, waiting...');
    let attempts = 0;
    const maxAttempts = 30; // Wait up to 3 seconds (30 * 100ms)
    
    while (attempts < maxAttempts && !deferredPromptRef.current) {
      await new Promise(resolve => setTimeout(resolve, 100));
      attempts++;
    }

    // Try again if prompt became available
    if (deferredPromptRef.current) {
      console.log('✅ Install prompt became available, retrying...');
      handleInstallClick();
      return;
    }

    // If still no prompt after waiting, show instructions
    // This means:
    // 1. The browser doesn't support automatic installation (iOS Safari, some mobile browsers)
    // 2. PWA criteria aren't met (HTTPS, valid manifest, service worker, etc.)
    // 3. User already dismissed the prompt (browser won't fire event again)
    // 4. App is already installed
    console.log('⚠️ Install prompt not available. Showing manual instructions...');
    showInstallInstructions();
  };

  const showInstallInstructions = () => {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    const isChrome = /Chrome/.test(navigator.userAgent) && !/Edge|Edg/.test(navigator.userAgent);
    const isEdge = /Edge|Edg/.test(navigator.userAgent);
    const isFirefox = /Firefox/.test(navigator.userAgent);
    
    // English messages
    const enMessages: Record<string, string> = {
      installInstructionsIOS: 'Please tap the share icon (□↑) and select "Add to Home Screen"',
      installInstructionsAndroidChrome: 'Please tap the menu (⋮) in the top right and select "Add to Home Screen" or "Install App"',
      installInstructionsAndroidOther: 'Please use your browser menu and select "Add to Home Screen"',
      installInstructionsDesktopChrome: 'Please click the install icon (⊕) in the address bar or use the menu (⋮) > "Install App"',
      installInstructionsDesktopEdge: 'Please click the install icon (⊕) in the address bar or use the menu (⋯) > "Apps" > "Install this website as an app"',
      installInstructionsDesktopFirefox: 'Please use the menu (☰) > "This Page" > "Add to Home Screen"',
      installInstructionsDesktopOther: 'Please use your browser menu and look for "Install App" or "Add to Home Screen"',
    };
    
    let messageKey = '';
    if (isIOS) {
      messageKey = 'installInstructionsIOS';
    } else if (isAndroid) {
      if (isChrome) {
        messageKey = 'installInstructionsAndroidChrome';
      } else {
        messageKey = 'installInstructionsAndroidOther';
      }
    } else {
      // Desktop browsers
      if (isChrome) {
        messageKey = 'installInstructionsDesktopChrome';
      } else if (isEdge) {
        messageKey = 'installInstructionsDesktopEdge';
      } else if (isFirefox) {
        messageKey = 'installInstructionsDesktopFirefox';
      } else {
        messageKey = 'installInstructionsDesktopOther';
      }
    }
    
    const currentMessage = tPWA(messageKey);
    const englishMessage = enMessages[messageKey] || '';
    
    // Show both messages if locale is German, otherwise show only current message
    let finalMessage = currentMessage;
    if (locale === 'de' && englishMessage) {
      finalMessage = `${currentMessage}\n\n--- English ---\n${englishMessage}`;
    }
    
    alert(finalMessage);
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


