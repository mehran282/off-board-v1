import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { OfferCard } from '@/components/offer-card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import { Calendar, FileText, ExternalLink, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

async function getFlyer(id: string) {
  try {
    const flyer = await prisma.flyer.findUnique({
      where: { id },
      include: {
        retailer: true,
        offers: {
          include: {
            retailer: {
              select: {
                id: true,
                name: true,
                logoUrl: true,
              },
            },
          },
          orderBy: {
            discountPercentage: 'desc',
          },
        },
      },
    });
    return flyer;
  } catch (error) {
    console.error('Error fetching flyer:', error);
    return null;
  }
}

interface FlyerDetailPageProps {
  params: Promise<{ locale: string; id: string }>;
}

export async function generateMetadata({
  params,
}: FlyerDetailPageProps): Promise<Metadata> {
  try {
    const { locale, id } = await params;
    const flyer = await getFlyer(id);
    const t = await getTranslations({ locale, namespace: 'flyers' });

    if (!flyer) {
      return {
        title: t('notFound'),
      };
    }

    return {
      title: flyer.title,
      description: `${flyer.title} ${t('from')} ${flyer.retailer.name} - ${t('validUntil')} ${new Date(flyer.validUntil).toLocaleDateString(locale === 'de' ? 'de-DE' : 'en-US')}`,
    };
  } catch (error) {
    console.error('Error generating metadata for flyer:', error);
    return {
      title: 'Flyer',
    };
  }
}

export default async function FlyerDetailPage({ params }: FlyerDetailPageProps) {
  const { locale, id } = await params;
  const flyer = await getFlyer(id);
  const t = await getTranslations({ locale, namespace: 'flyers' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });

  if (!flyer) {
    notFound();
  }

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString(locale === 'de' ? 'de-DE' : 'en-US', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-4 md:py-8 px-2 sm:px-4">
        <Link href={`/${locale}/flyers`}>
          <Button variant="ghost" className="mb-4" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('backToFlyers')}
          </Button>
        </Link>

        <div className="bg-card border rounded-lg p-4 sm:p-6 mb-6 sm:mb-8">
          <div className="flex items-start gap-3 sm:gap-4 mb-4">
            <Avatar className="h-12 w-12 sm:h-16 sm:w-16">
              <AvatarImage src={flyer.retailer.logoUrl || undefined} alt={flyer.retailer.name} />
              <AvatarFallback className="text-base sm:text-xl">{flyer.retailer.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <h1 className="text-xl sm:text-2xl md:text-3xl font-bold mb-2 break-words">{flyer.title}</h1>
              <p className="text-sm sm:text-base md:text-lg text-muted-foreground truncate">{flyer.retailer.name}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground">{t('validFrom')}</p>
                <p className="text-sm sm:text-base font-semibold">{formatDate(flyer.validFrom)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground">{t('validUntil')}</p>
                <p className="text-sm sm:text-base font-semibold">{formatDate(flyer.validUntil)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground">{t('pages')}</p>
                <p className="text-sm sm:text-base font-semibold">{flyer.pages}</p>
              </div>
            </div>
          </div>

          {flyer.pdfUrl && (
            <Link href={flyer.pdfUrl} target="_blank" rel="noopener noreferrer">
              <Button size="sm" className="w-full sm:w-auto">
                <ExternalLink className="h-4 w-4 mr-2" />
                {t('openPdf')}
              </Button>
            </Link>
          )}
        </div>

        {flyer.offers.length > 0 && (
          <div>
            <h2 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4">
              {t('offersInFlyer')} ({flyer.offers.length})
            </h2>
            <div className="grid grid-cols-3 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-4 md:gap-6">
              {flyer.offers.map((offer: {
                id: string;
                productName: string;
                brand: string | null;
                currentPrice: number;
                oldPrice: number | null;
                discountPercentage: number | null;
                imageUrl: string | null;
                retailer: {
                  id: string;
                  name: string;
                  logoUrl: string | null;
                };
                validUntil: Date | null;
              }) => (
                <OfferCard
                  key={offer.id}
                  id={offer.id}
                  productName={offer.productName}
                  brand={offer.brand}
                  currentPrice={offer.currentPrice}
                  oldPrice={offer.oldPrice}
                  discountPercentage={offer.discountPercentage}
                  imageUrl={offer.imageUrl}
                  retailer={offer.retailer}
                  validUntil={offer.validUntil?.toISOString() || null}
                />
              ))}
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

