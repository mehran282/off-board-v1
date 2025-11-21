'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Play, Loader2 } from 'lucide-react';

export function Footer() {
  const t = useTranslations('footer');
  const tCommon = useTranslations('common');
  const locale = useLocale();
  const [isScraping, setIsScraping] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState<string | null>(null);

  const handleRunScraper = async () => {
    setIsScraping(true);
    setScrapeStatus('Starting scraper...');
    
    try {
      const response = await fetch('/api/scrape', {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        setScrapeStatus('Scraper started successfully! Running in background...');
      } else {
        setScrapeStatus(`Error: ${data.message || data.error}`);
      }
    } catch (error) {
      setScrapeStatus(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsScraping(false);
      // Clear status after 5 seconds
      setTimeout(() => setScrapeStatus(null), 5000);
    }
  };

  return (
    <footer className="border-t bg-muted/50">
      <div className="w-full flex justify-center">
        <div className="w-full max-w-[60%] py-8 px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold mb-4">{t('about')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('aboutDescription')}
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">{t('navigation')}</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href={`/${locale}`} className="text-muted-foreground hover:text-foreground">
                    {tCommon('home')}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${locale}/flyers`}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    {tCommon('flyers')}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${locale}/offers`}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    {tCommon('offers')}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${locale}/retailers`}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    {tCommon('retailers')}
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">{t('contact')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('contactDescription')}
              </p>
            </div>
          </div>
          {/* Temporary Scraper Button */}
          <div className="mt-6 pt-6 border-t">
            <div className="flex flex-col items-center gap-2">
              <Button
                onClick={handleRunScraper}
                disabled={isScraping}
                variant="outline"
                size="sm"
                className="w-full max-w-xs"
              >
                {isScraping ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Scraper...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Run Scraper (Temporary)
                  </>
                )}
              </Button>
              {scrapeStatus && (
                <p className="text-xs text-muted-foreground text-center">
                  {scrapeStatus}
                </p>
              )}
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} off-board. {t('rights')}</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
