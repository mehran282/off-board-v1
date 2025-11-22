'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Home } from 'lucide-react';
import { useLocale } from 'next-intl';
import { useTranslations } from 'next-intl';

export default function NotFound() {
  const locale = useLocale();
  const t = useTranslations('errors');
  
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-bold">404</h1>
        <h2 className="text-2xl font-semibold">{t('notFound')}</h2>
        <p className="text-muted-foreground">
          {t('notFoundDescription')}
        </p>
        <Link href={`/${locale}`}>
          <Button>
            <Home className="h-4 w-4 mr-2" />
            {t('goHome')}
          </Button>
        </Link>
      </div>
    </div>
  );
}

