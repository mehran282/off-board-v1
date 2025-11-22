'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import { ShoppingCart } from 'lucide-react';

export function PageLoading() {
  const pathname = usePathname();
  const [loading, setLoading] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Check if mobile on mount and resize
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    // Show loading on mobile only when pathname changes
    if (!isMobile) {
      setLoading(false);
      return;
    }

    setLoading(true);
    
    // Hide loading after a short delay to allow page to render
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [pathname, isMobile]);

  if (!loading || !isMobile) return null;

  return (
    <div className="fixed inset-0 z-[9999] bg-background/80 backdrop-blur-sm flex items-center justify-center md:hidden">
      <div className="flex flex-col items-center gap-4">
        <ShoppingCart className="h-8 w-8 animate-cart-forward text-primary" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

