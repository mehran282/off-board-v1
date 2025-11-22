import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { FlyerCard } from '@/components/flyer-card';
import { OfferCard } from '@/components/offer-card';
import { StoreMap } from '@/components/store-map';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import { Store, ArrowLeft, FileText, Tag, MapPin } from 'lucide-react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

async function getRetailer(id: string) {
  try {
    const retailer = await prisma.retailer.findUnique({
      where: { id },
      include: {
        flyers: {
          take: 6,
          include: {
            retailer: {
              select: {
                id: true,
                name: true,
                logoUrl: true,
              },
            },
            _count: {
              select: {
                offers: true,
              },
            },
          },
          orderBy: {
            validUntil: 'desc',
          },
        },
        offers: {
          take: 6,
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
        stores: {
          take: 50,
          select: {
            id: true,
            address: true,
            city: true,
            postalCode: true,
            latitude: true,
            longitude: true,
            phone: true,
          },
        },
        _count: {
          select: {
            flyers: true,
            offers: true,
            stores: true,
          },
        },
      },
    });
    return retailer;
  } catch (error) {
    console.error('Error fetching retailer:', error);
    return null;
  }
}

interface RetailerDetailPageProps {
  params: Promise<{ locale: string; id: string }>;
}

export async function generateMetadata({
  params,
}: RetailerDetailPageProps): Promise<Metadata> {
  try {
    const { locale, id } = await params;
    const retailer = await getRetailer(id);
    const t = await getTranslations({ locale, namespace: 'retailers' });

    if (!retailer) {
      return {
        title: t('notFound'),
      };
    }

    return {
      title: retailer.name,
      description: `${retailer.name} - ${retailer.category} ${t('with')} ${retailer._count.offers} ${t('offers')} ${t('and')} ${retailer._count.flyers} ${t('flyers')}`,
    };
  } catch (error) {
    console.error('Error generating metadata for retailer:', error);
    return {
      title: 'Retailer',
    };
  }
}

export default async function RetailerDetailPage({
  params,
}: RetailerDetailPageProps) {
  const { locale, id } = await params;
  const retailer = await getRetailer(id);
  const t = await getTranslations({ locale, namespace: 'retailers' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });

  if (!retailer) {
    notFound();
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-4 md:py-8 px-2 sm:px-4">
        <Link href={`/${locale}/retailers`}>
          <Button variant="ghost" className="mb-4" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('backToRetailers')}
          </Button>
        </Link>

        <div className="bg-card border rounded-lg p-4 sm:p-6 mb-6 sm:mb-8">
          <div className="flex items-start gap-3 sm:gap-4 mb-4">
            <Avatar className="h-16 w-16 sm:h-20 sm:w-20">
              <AvatarImage src={retailer.logoUrl || undefined} alt={retailer.name} />
              <AvatarFallback className="text-xl sm:text-2xl">{retailer.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <h1 className="text-xl sm:text-2xl md:text-3xl font-bold mb-2 break-words">{retailer.name}</h1>
              <Badge variant="secondary" className="text-xs sm:text-sm md:text-base">
                {retailer.category}
              </Badge>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground">{t('flyers')}</p>
                <p className="text-sm sm:text-base font-semibold">{retailer._count.flyers}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Tag className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground">{t('offers')}</p>
                <p className="text-sm sm:text-base font-semibold">{retailer._count.offers}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground">{t('stores')}</p>
                <p className="text-sm sm:text-base font-semibold">{retailer._count.stores}</p>
              </div>
            </div>
          </div>
        </div>

        {retailer.stores.length > 0 && (
          <div className="mb-6 sm:mb-8">
            <h2 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 flex items-center gap-2">
              <MapPin className="h-5 w-5 sm:h-6 sm:w-6" />
              {t('storeLocations')} ({retailer.stores.length})
            </h2>
            
            {/* Map - Always show, component handles empty coordinates */}
            <div className="mb-4 sm:mb-6">
              <StoreMap 
                stores={retailer.stores.map((store: any) => ({
                  id: store.id,
                  address: store.address,
                  city: store.city,
                  postalCode: store.postalCode,
                  latitude: store.latitude,
                  longitude: store.longitude,
                  name: retailer.name,
                }))}
                retailerName={retailer.name}
              />
            </div>

            {/* Store List */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              {retailer.stores.map((store: {
                id: string;
                address: string;
                city: string;
                postalCode: string;
                phone: string | null;
              }) => (
                <div key={store.id} className="border rounded-lg p-3 sm:p-4">
                  <p className="text-sm sm:text-base font-semibold mb-1 break-words">{store.address}</p>
                  <p className="text-xs sm:text-sm text-muted-foreground">
                    {store.postalCode} {store.city}
                  </p>
                  {store.phone && (
                    <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                      {t('phone')}: {store.phone}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {retailer.flyers.length > 0 && (
          <div className="mb-6 sm:mb-8">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0 mb-3 sm:mb-4">
              <h2 className="text-xl sm:text-2xl font-bold flex items-center gap-2">
                <FileText className="h-5 w-5 sm:h-6 sm:w-6" />
                {t('flyers')} ({retailer._count.flyers})
              </h2>
              <Link href={`/${locale}/flyers?retailerId=${retailer.id}`}>
                <Button variant="outline" size="sm" className="w-full sm:w-auto">
                  {tCommon('showAll')}
                </Button>
              </Link>
            </div>
            <div className="grid grid-cols-3 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-4 md:gap-6">
              {retailer.flyers.map((flyer: {
                id: string;
                title: string;
                pages: number;
                validFrom: Date;
                validUntil: Date;
                retailer: {
                  id: string;
                  name: string;
                  logoUrl: string | null;
                };
                _count: {
                  offers: number;
                };
              }) => (
                <FlyerCard
                  key={flyer.id}
                  id={flyer.id}
                  title={flyer.title}
                  retailer={flyer.retailer}
                  validFrom={flyer.validFrom.toISOString()}
                  validUntil={flyer.validUntil.toISOString()}
                  pages={flyer.pages}
                  offersCount={flyer._count.offers}
                />
              ))}
            </div>
          </div>
        )}

        {retailer.offers.length > 0 && (
          <div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0 mb-3 sm:mb-4">
              <h2 className="text-xl sm:text-2xl font-bold flex items-center gap-2">
                <Tag className="h-5 w-5 sm:h-6 sm:w-6" />
                {t('offers')} ({retailer._count.offers})
              </h2>
              <Link href={`/${locale}/offers?retailerId=${retailer.id}`}>
                <Button variant="outline" size="sm" className="w-full sm:w-auto">
                  {tCommon('showAll')}
                </Button>
              </Link>
            </div>
            <div className="grid grid-cols-3 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-4 md:gap-6">
              {retailer.offers.map((offer: {
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

