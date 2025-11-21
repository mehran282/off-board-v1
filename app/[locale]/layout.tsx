import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales, type Locale } from '@/i18n';
import { PWAInstaller } from '@/components/pwa-installer';
import '../globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  
  const metadata: Record<string, any> = {
    icons: {
      icon: '/icon.svg',
      shortcut: '/icon.svg',
      apple: '/icon.svg',
    },
    manifest: '/manifest.json',
  };

  if (locale === 'de') {
    metadata.title = {
      default: 'off-board - Angebote und Prospekte',
      template: '%s | off-board',
    };
    metadata.description = 'Finden Sie die besten Angebote und Prospekte von Händlern in Ihrer Nähe';
    metadata.keywords = ['Angebote', 'Prospekte', 'Rabatte', 'Händler', 'off-board'];
    metadata.openGraph = {
      type: 'website',
      locale: 'de_DE',
      url: 'https://off-board.com',
      siteName: 'off-board',
      title: 'off-board - Angebote und Prospekte',
      description: 'Finden Sie die besten Angebote und Prospekte von Händlern in Ihrer Nähe',
    };
  } else {
    metadata.title = {
      default: 'off-board - Offers and Flyers',
      template: '%s | off-board',
    };
    metadata.description = 'Find the best offers and flyers from retailers near you';
    metadata.keywords = ['offers', 'flyers', 'discounts', 'retailers', 'off-board'];
    metadata.openGraph = {
      type: 'website',
      locale: 'en_US',
      url: 'https://off-board.com',
      siteName: 'off-board',
      title: 'off-board - Offers and Flyers',
      description: 'Find the best offers and flyers from retailers near you',
    };
  }

  return metadata;
}

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!locales.includes(locale as Locale)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <NextIntlClientProvider messages={messages}>
          {children}
          <PWAInstaller />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

