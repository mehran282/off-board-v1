'use client';

import { useTranslations } from 'next-intl';

export function Footer() {
  const t = useTranslations('footer');

  return (
    <footer className="border-t bg-muted/50">
      <div className="w-full flex justify-center">
        <div className="w-full max-w-full lg:max-w-[60%] py-6 md:py-8 px-4 sm:px-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 md:gap-8">
            <div>
              <h3 className="font-semibold mb-4">{t('about')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('aboutDescription')}
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">{t('contact')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('contactDescription')}
              </p>
            </div>
          </div>
          <div className="mt-6 md:mt-8 pt-6 md:pt-8 border-t text-center text-xs sm:text-sm text-muted-foreground px-4">
            <p>&copy; {new Date().getFullYear()} off-board. {t('rights')}</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
