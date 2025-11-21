'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';
import { useTranslations } from 'next-intl';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const pathname = usePathname();
  const locale = pathname.split('/')[1] || 'de';
  const t = useTranslations('errors');

  useEffect(() => {
    console.error(error);
  }, [error]);

  const homeUrl = `/${locale}`;

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center space-y-4 max-w-md">
        <AlertCircle className="h-12 w-12 mx-auto text-destructive" />
        <h2 className="text-2xl font-semibold">{t('errorOccurred')}</h2>
        <p className="text-muted-foreground">
          {error.message || t('unexpectedError')}
        </p>
        <div className="flex gap-2 justify-center">
          <Button onClick={reset}>{t('tryAgain')}</Button>
          <Button variant="outline" onClick={() => (window.location.href = homeUrl)}>
            {t('goHome')}
          </Button>
        </div>
      </div>
    </div>
  );
}

