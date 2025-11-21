'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { SearchBar } from './search-bar';
import { LanguageSwitcher } from './language-switcher';
import { FileText, Tag, Store, Home } from 'lucide-react';

export function Header() {
  const t = useTranslations('common');
  const locale = useLocale();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="w-full flex justify-center">
        <div className="w-full max-w-[60%] flex h-16 items-center justify-between gap-4 px-4">
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href={`/${locale}`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
            >
              <Home className="h-4 w-4" />
              {t('home')}
            </Link>
            <Link
              href={`/${locale}/flyers`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
            >
              <FileText className="h-4 w-4" />
              {t('flyers')}
            </Link>
            <Link
              href={`/${locale}/offers`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
            >
              <Tag className="h-4 w-4" />
              {t('offers')}
            </Link>
            <Link
              href={`/${locale}/retailers`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
            >
              <Store className="h-4 w-4" />
              {t('retailers')}
            </Link>
          </nav>

          <div className="flex items-center gap-4 flex-1 justify-end">
            <div className="flex-1 max-w-md hidden lg:block">
              <SearchBar />
            </div>
            <LanguageSwitcher />
          </div>
        </div>
      </div>
    </header>
  );
}
