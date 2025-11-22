import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import { ExternalLink, ArrowLeft, Calendar } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

async function getOffer(id: string) {
  try {
    const offer = await prisma.offer.findUnique({
      where: { id },
      include: {
        retailer: true,
        flyer: true,
        product: true,
      },
    });
    return offer;
  } catch (error) {
    console.error('Error fetching offer:', error);
    return null;
  }
}

interface OfferDetailPageProps {
  params: Promise<{ locale: string; id: string }>;
}

export async function generateMetadata({
  params,
}: OfferDetailPageProps): Promise<Metadata> {
  try {
    const { locale, id } = await params;
    const offer = await getOffer(id);
    const t = await getTranslations({ locale, namespace: 'offers' });

    if (!offer) {
      return {
        title: t('notFound'),
      };
    }

    return {
      title: offer.productName,
      description: `${offer.productName} ${t('from')} ${offer.retailer.name} - ${offer.currentPrice}€${offer.discountPercentage ? ` (${Math.round(offer.discountPercentage)}% ${t('discount')})` : ''}`,
    };
  } catch (error) {
    console.error('Error generating metadata for offer:', error);
    return {
      title: 'Offer',
    };
  }
}

export default async function OfferDetailPage({ params }: OfferDetailPageProps) {
  const { locale, id } = await params;
  const offer = await getOffer(id);
  const t = await getTranslations({ locale, namespace: 'offers' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });

  if (!offer) {
    notFound();
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat(locale === 'de' ? 'de-DE' : 'en-US', {
      style: 'currency',
      currency: 'EUR',
    }).format(price);
  };

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
        <Link href={`/${locale}/offers`}>
          <Button variant="ghost" className="mb-4" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('backToOffers')}
          </Button>
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-8">
          <div>
            {offer.imageUrl ? (
              <div className="relative w-full aspect-square bg-muted rounded-lg overflow-hidden mb-4">
                <Image
                  src={offer.imageUrl}
                  alt={offer.productName}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 50vw"
                />
              </div>
            ) : (
              <div className="w-full aspect-square bg-muted rounded-lg flex items-center justify-center mb-4">
                <p className="text-sm sm:text-base text-muted-foreground">{t('noImage')}</p>
              </div>
            )}
          </div>

          <div>
            <div className="flex items-start gap-3 sm:gap-4 mb-4">
              <Avatar className="h-10 w-10 sm:h-12 sm:w-12">
                <AvatarImage
                  src={offer.retailer.logoUrl || undefined}
                  alt={offer.retailer.name}
                />
                <AvatarFallback className="text-sm sm:text-base">{offer.retailer.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-xs sm:text-sm text-muted-foreground truncate">{offer.retailer.name}</p>
                {offer.brand && (
                  <p className="text-xs sm:text-sm text-muted-foreground truncate">{offer.brand}</p>
                )}
              </div>
            </div>

            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold mb-3 sm:mb-4">{offer.productName}</h1>

            {offer.category && (
              <Badge variant="secondary" className="mb-3 sm:mb-4 text-xs sm:text-sm">
                {offer.category}
              </Badge>
            )}

            <div className="space-y-3 sm:space-y-4 mb-4 sm:mb-6">
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground mb-1">{t('currentPrice')}</p>
                <p className="text-2xl sm:text-3xl md:text-4xl font-bold">{formatPrice(offer.currentPrice)}</p>
              </div>

              {offer.oldPrice && offer.oldPrice > offer.currentPrice && (
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground mb-1">{t('oldPrice')}</p>
                  <p className="text-lg sm:text-xl md:text-2xl line-through text-muted-foreground">
                    {formatPrice(offer.oldPrice)}
                  </p>
                </div>
              )}

              {offer.discountPercentage && offer.discountPercentage > 0 && (
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground mb-1">{t('discount')}</p>
                  <Badge variant="destructive" className="text-sm sm:text-base md:text-lg px-2 sm:px-3 py-1">
                    -{Math.round(offer.discountPercentage)}%
                  </Badge>
                </div>
              )}

              {offer.unitPrice && (
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground">{t('unitPrice')}</p>
                  <p className="text-sm sm:text-base font-semibold">{offer.unitPrice}</p>
                </div>
              )}

              {offer.validUntil && (
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
                  <div>
                    <p className="text-xs sm:text-sm text-muted-foreground">{t('validUntil')}</p>
                    <p className="text-sm sm:text-base font-semibold">{formatDate(offer.validUntil)}</p>
                  </div>
                </div>
              )}
            </div>

            {offer.flyer && (
              <div className="mb-4 sm:mb-6 p-3 sm:p-4 border rounded-lg">
                <p className="text-xs sm:text-sm text-muted-foreground mb-2">{t('fromFlyer')}</p>
                <Link
                  href={`/${locale}/flyers/${offer.flyer.id}`}
                  className="text-sm sm:text-base text-primary hover:underline font-medium break-words"
                >
                  {offer.flyer.title}
                </Link>
              </div>
            )}

            <Link href={offer.url} target="_blank" rel="noopener noreferrer">
              <Button className="w-full sm:w-auto" size="sm">
                <ExternalLink className="h-4 w-4 mr-2" />
                {t('viewOffer')}
              </Button>
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

