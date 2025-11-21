'use client';

import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';

export function Footer() {
  const t = useTranslations('footer');
  const tCommon = useTranslations('common');
  const locale = useLocale();

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
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} off-board. {t('rights')}</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
