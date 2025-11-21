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
      <main className="flex-1 container py-8 px-4">
        <Link href={`/${locale}/flyers`}>
          <Button variant="ghost" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('backToFlyers')}
          </Button>
        </Link>

        <div className="bg-card border rounded-lg p-6 mb-8">
          <div className="flex items-start gap-4 mb-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={flyer.retailer.logoUrl || undefined} alt={flyer.retailer.name} />
              <AvatarFallback className="text-xl">{flyer.retailer.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{flyer.title}</h1>
              <p className="text-lg text-muted-foreground">{flyer.retailer.name}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">{t('validFrom')}</p>
                <p className="font-semibold">{formatDate(flyer.validFrom)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">{t('validUntil')}</p>
                <p className="font-semibold">{formatDate(flyer.validUntil)}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">{t('pages')}</p>
                <p className="font-semibold">{flyer.pages}</p>
              </div>
            </div>
          </div>

          {flyer.pdfUrl && (
            <Link href={flyer.pdfUrl} target="_blank" rel="noopener noreferrer">
              <Button>
                <ExternalLink className="h-4 w-4 mr-2" />
                {t('openPdf')}
              </Button>
            </Link>
          )}
        </div>

        {flyer.offers.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold mb-4">
              {t('offersInFlyer')} ({flyer.offers.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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

