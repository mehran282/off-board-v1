import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { FlyerCard } from '@/components/flyer-card';
import { OfferCard } from '@/components/offer-card';
import { RetailerCard } from '@/components/retailer-card';
import { SearchBar } from '@/components/search-bar';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { FileText, Tag, ArrowRight, Store } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import Image from 'next/image';
import prisma from '@/lib/db';
import { getTranslations } from 'next-intl/server';

async function getRecentFlyers() {
  try {
    const flyers = await prisma.flyer.findMany({
      take: 3,
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
    });
    return flyers;
  } catch (error) {
    console.error('Error fetching recent flyers:', error);
    return [];
  }
}

async function getTopOffers() {
  try {
    const offers = await prisma.offer.findMany({
      take: 5,
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
    });
    return offers;
  } catch (error) {
    console.error('Error fetching top offers:', error);
    return [];
  }
}

async function getTopRetailers() {
  try {
    const retailers = await prisma.retailer.findMany({
      take: 5,
      include: {
        _count: {
          select: {
            flyers: true,
            offers: true,
            stores: true,
          },
        },
      },
      orderBy: {
        name: 'asc',
      },
    });
    return retailers;
  } catch (error) {
    console.error('Error fetching top retailers:', error);
    return [];
  }
}

async function getTopRetailersWithOffers() {
  try {
    // گرفتن همه فروشگاه‌ها با تعداد offers
    const allRetailers = await prisma.retailer.findMany({
      include: {
        _count: {
          select: {
            offers: true,
          },
        },
      },
    });

    // مرتب‌سازی بر اساس تعداد offers و گرفتن 2 تا برتر
    const retailers = allRetailers
      .sort((a, b) => b._count.offers - a._count.offers)
      .slice(0, 2);

    // برای هر فروشگاه، محصولات (offers) را بگیریم
    const retailersWithOffers = await Promise.all(
      retailers.map(async (retailer) => {
        const offers = await prisma.offer.findMany({
          where: {
            retailerId: retailer.id,
          },
          take: 8, // 8 محصول برای هر فروشگاه
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
        });

        return {
          ...retailer,
          offers,
        };
      })
    );

    return retailersWithOffers;
  } catch (error) {
    console.error('Error fetching top retailers with offers:', error);
    return [];
  }
}

interface HomePageProps {
  params: Promise<{ locale: string }>;
}

export default async function HomePage({ params }: HomePageProps) {
  const { locale } = await params;
  const t = await getTranslations('home');
  const tCommon = await getTranslations('common');
  const [recentFlyers, topOffers, topRetailers, topRetailersWithOffers] = await Promise.all([
    getRecentFlyers(),
    getTopOffers(),
    getTopRetailers(),
    getTopRetailersWithOffers(),
  ]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="w-full flex justify-center">
          <div className="w-full max-w-[60%]">
            {/* Hero Section */}
            <section className="py-6">
              <div className="text-center space-y-4 mb-4">
                <h1 className="text-4xl md:text-5xl font-bold">{t('title')}</h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                  {t('subtitle')}
                </p>
              </div>
              <div className="flex justify-center mb-6">
                <SearchBar />
              </div>
            </section>

            {/* Recent Flyers */}
            {recentFlyers.length > 0 && (
              <section className="py-4">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <FileText className="h-6 w-6" />
                    <h2 className="text-2xl font-bold">{t('recentFlyers')}</h2>
                  </div>
                  <Link href={`/${locale}/flyers`}>
                    <Button variant="outline">
                      {tCommon('showAll')}
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </div>
                <div className="grid grid-cols-3 gap-6">
                  {recentFlyers.map((flyer: {
                    id: string;
                    title: string;
                    pages: number;
                    validFrom: Date;
                    validUntil: Date;
                    pdfUrl: string | null;
                    thumbnailUrl: string | null;
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
                      pdfUrl={flyer.pdfUrl}
                      thumbnailUrl={flyer.thumbnailUrl}
                      offersCount={flyer._count.offers}
                    />
                  ))}
                </div>
              </section>
            )}

            {/* Top 2 Retailers with Offers */}
            {topRetailersWithOffers.length > 0 && (
              <section className="py-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {topRetailersWithOffers.slice(0, 2).map((retailer: {
                    id: string;
                    name: string;
                    logoUrl: string | null;
                    _count: {
                      offers: number;
                    };
                    offers: Array<{
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
                    }>;
                  }) => (
                    <div key={retailer.id} className="p-4 h-full flex flex-col">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-2">
                            {retailer.logoUrl && (
                              <div className="relative h-8 w-8">
                                <Image 
                                  src={retailer.logoUrl} 
                                  alt={retailer.name}
                                  fill
                                  className="object-contain"
                                  unoptimized
                                />
                              </div>
                            )}
                            <h2 className="text-xl font-bold">{retailer.name}</h2>
                          </div>
                          <Badge variant="secondary" className="text-sm">
                            {retailer._count.offers} {tCommon('offers')}
                          </Badge>
                        </div>
                        <Link href={`/${locale}/retailers/${retailer.id}`}>
                          <Button variant="outline" size="sm">
                            {tCommon('showAll')}
                            <ArrowRight className="h-4 w-4 ml-2" />
                          </Button>
                        </Link>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 flex-1">
                        {retailer.offers.slice(0, 8).map((offer: {
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
                          <div key={offer.id} className="w-full">
                            <OfferCard
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
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Top Offers */}
            {topOffers.length > 0 && (
              <section className="py-4">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Tag className="h-6 w-6" />
                    <h2 className="text-2xl font-bold">{t('topOffers')}</h2>
                  </div>
                  <Link href={`/${locale}/offers`}>
                    <Button variant="outline">
                      {tCommon('showAll')}
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </div>
                <div className="grid grid-cols-5 gap-2">
                  {topOffers.map((offer: {
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
                    <div key={offer.id} className="w-full">
                      <OfferCard
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
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Top Retailers */}
            {topRetailers.length > 0 && (
              <section className="py-4">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Store className="h-6 w-6" />
                    <h2 className="text-2xl font-bold">{tCommon('retailers')}</h2>
                  </div>
                  <Link href={`/${locale}/retailers`}>
                    <Button variant="outline">
                      {tCommon('showAll')}
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </div>
                <div className="grid grid-cols-5 gap-2">
                  {topRetailers.map((retailer: {
                    id: string;
                    name: string;
                    category: string;
                    logoUrl: string | null;
                    _count: {
                      flyers: number;
                      offers: number;
                      stores: number;
                    };
                  }) => (
                    <div key={retailer.id} className="w-full">
                      <RetailerCard
                        id={retailer.id}
                        name={retailer.name}
                        category={retailer.category}
                        logoUrl={retailer.logoUrl}
                        flyersCount={retailer._count.flyers}
                        offersCount={retailer._count.offers}
                        storesCount={retailer._count.stores}
                      />
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Empty State */}
            {recentFlyers.length === 0 && topOffers.length === 0 && topRetailers.length === 0 && (
              <section className="py-12 text-center">
                <p className="text-muted-foreground text-lg">{t('noData')}</p>
              </section>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

