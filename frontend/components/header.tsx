'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { SearchBar } from './search-bar';
import { LanguageSwitcher } from './language-switcher';
import { Button } from '@/components/ui/button';
import { FileText, Tag, Store, Home, Menu, X, Package, Loader2 } from 'lucide-react';

export function Header() {
  const t = useTranslations('common');
  const locale = useLocale();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [loadingLink, setLoadingLink] = useState<string | null>(null);

  // Reset loading state when pathname changes
  useEffect(() => {
    setLoadingLink(null);
  }, [pathname]);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="w-full flex justify-center">
        <div className="w-full max-w-full lg:max-w-[60%] flex h-16 items-center justify-between gap-4 px-4">
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href={`/${locale}`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
              onClick={() => setLoadingLink(`/${locale}`)}
            >
              {loadingLink === `/${locale}` && pathname !== `/${locale}` ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Home className="h-4 w-4" />
              )}
              {t('home')}
            </Link>
            <Link
              href={`/${locale}/flyers`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
              onClick={() => setLoadingLink(`/${locale}/flyers`)}
            >
              {loadingLink === `/${locale}/flyers` && pathname !== `/${locale}/flyers` ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileText className="h-4 w-4" />
              )}
              {t('flyers')}
            </Link>
            <Link
              href={`/${locale}/offers`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
              onClick={() => setLoadingLink(`/${locale}/offers`)}
            >
              {loadingLink === `/${locale}/offers` && pathname !== `/${locale}/offers` ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Tag className="h-4 w-4" />
              )}
              {t('offers')}
            </Link>
            <Link
              href={`/${locale}/retailers`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
              onClick={() => setLoadingLink(`/${locale}/retailers`)}
            >
              {loadingLink === `/${locale}/retailers` && pathname !== `/${locale}/retailers` ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Store className="h-4 w-4" />
              )}
              {t('retailers')}
            </Link>
            <Link
              href={`/${locale}/products`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
              onClick={() => setLoadingLink(`/${locale}/products`)}
            >
              {loadingLink === `/${locale}/products` && pathname !== `/${locale}/products` ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Package className="h-4 w-4" />
              )}
              {t('products')}
            </Link>
          </nav>

          {/* Mobile Home Link - Always visible */}
          <div className="md:hidden">
            <Link
              href={`/${locale}`}
              className="text-sm font-medium transition-colors hover:text-primary flex items-center gap-1"
              onClick={() => setLoadingLink(`/${locale}`)}
            >
              {loadingLink === `/${locale}` && pathname !== `/${locale}` ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Home className="h-5 w-5" />
              )}
              <span>{t('home')}</span>
            </Link>
          </div>

          {/* Mobile Menu - Left side when menu is open */}
          {mobileMenuOpen && (
            <div className="md:hidden flex-1">
              <nav className="flex flex-row items-center justify-start gap-3 sm:gap-4 overflow-x-auto">
                <Link
                  href={`/${locale}/flyers`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    setLoadingLink(`/${locale}/flyers`);
                  }}
                >
                  {loadingLink === `/${locale}/flyers` && pathname !== `/${locale}/flyers` ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <FileText className="h-5 w-5" />
                  )}
                  <span>{t('flyers')}</span>
                </Link>
                <Link
                  href={`/${locale}/offers`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    setLoadingLink(`/${locale}/offers`);
                  }}
                >
                  {loadingLink === `/${locale}/offers` && pathname !== `/${locale}/offers` ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Tag className="h-5 w-5" />
                  )}
                  <span>{t('offers')}</span>
                </Link>
                <Link
                  href={`/${locale}/retailers`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    setLoadingLink(`/${locale}/retailers`);
                  }}
                >
                  {loadingLink === `/${locale}/retailers` && pathname !== `/${locale}/retailers` ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Store className="h-5 w-5" />
                  )}
                  <span>{t('retailers')}</span>
                </Link>
                <Link
                  href={`/${locale}/products`}
                  className="text-sm font-medium transition-colors hover:text-primary flex flex-col items-center gap-1 py-2 px-2 min-w-fit"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    setLoadingLink(`/${locale}/products`);
                  }}
                >
                  {loadingLink === `/${locale}/products` && pathname !== `/${locale}/products` ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Package className="h-5 w-5" />
                  )}
                  <span>{t('products')}</span>
                </Link>
              </nav>
            </div>
          )}

          <div className={`flex items-center gap-2 md:gap-4 ${mobileMenuOpen ? 'justify-end' : 'flex-1 justify-end'}`}>
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
      </div>
    </header>
  );
}
