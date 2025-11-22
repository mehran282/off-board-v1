'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { useState } from 'react';
import { SearchBar } from './search-bar';
import { LanguageSwitcher } from './language-switcher';
import { Button } from '@/components/ui/button';
import { FileText, Tag, Store, Home, Menu, X, Search } from 'lucide-react';

export function Header() {
  const t = useTranslations('common');
  const locale = useLocale();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="w-full flex justify-center">
        <div className="w-full max-w-full lg:max-w-[60%] flex h-16 items-center justify-between gap-4 px-4">
          {/* Desktop Navigation */}
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

          {/* Mobile Menu - Left side when menu is open */}
          {mobileMenuOpen && (
            <div className="md:hidden flex-1">
              <nav className="flex flex-row items-center justify-start gap-3 sm:gap-4 overflow-x-auto">
                <Link
                  href={`/${locale}`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Home className="h-5 w-5" />
                  <span>{t('home')}</span>
                </Link>
                <Link
                  href={`/${locale}/flyers`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <FileText className="h-5 w-5" />
                  <span>{t('flyers')}</span>
                </Link>
                <Link
                  href={`/${locale}/offers`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Tag className="h-5 w-5" />
                  <span>{t('offers')}</span>
                </Link>
                <Link
                  href={`/${locale}/retailers`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Store className="h-5 w-5" />
                  <span>{t('retailers')}</span>
                </Link>
              </nav>
            </div>
          )}

          <div className={`flex items-center gap-2 md:gap-4 ${mobileMenuOpen ? 'justify-end' : 'flex-1 justify-end'}`}>
            {/* Mobile Search Button */}
            {!mobileMenuOpen && (
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => {
                  setMobileSearchOpen(!mobileSearchOpen);
                  setMobileMenuOpen(false); // Close menu when opening search
                }}
                aria-label="Toggle search"
              >
                <Search className="h-5 w-5" />
              </Button>
            )}

            {/* Desktop Search Bar */}
            <div className="flex-1 max-w-md hidden lg:block">
              <SearchBar />
            </div>
            {!mobileMenuOpen && <LanguageSwitcher />}

            {/* Mobile Menu Button - Right side */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Search Bar */}
        {mobileSearchOpen && !mobileMenuOpen && (
          <div className="w-full max-w-full lg:max-w-[60%] mx-auto px-4 pb-4 lg:hidden">
            <SearchBar />
          </div>
        )}

      </div>
    </header>
  );
}
