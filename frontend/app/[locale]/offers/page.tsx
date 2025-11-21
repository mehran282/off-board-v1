import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { OfferCard } from '@/components/offer-card';
import { FilterPanel } from '@/components/filter-panel';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import Link from 'next/link';
import { Tag, ChevronLeft, ChevronRight } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

async function getOffers(
  page: number,
  limit: number,
  retailerId?: string | null,
  category?: string | null,
  search?: string | null,
  minDiscount?: string | null
) {
  const skip = (page - 1) * limit;
  const where: any = {};

  if (retailerId) {
    where.retailerId = retailerId;
  }

  if (category) {
    where.category = category;
  }

  if (search) {
    where.productName = {
      contains: search,
      mode: 'insensitive',
    };
  }

  if (minDiscount) {
    where.discountPercentage = {
      gte: parseFloat(minDiscount),
    };
  }

  const [offers, total, categories, retailers] = await Promise.all([
    prisma.offer.findMany({
      where,
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
      skip,
      take: limit,
    }),
    prisma.offer.count({ where }),
    prisma.offer
      .groupBy({
        by: ['category'],
        _count: {
          id: true,
        },
        orderBy: {
          _count: {
            id: 'desc',
          },
        },
      })
      .then((cats: Array<{ category: string | null; _count: { id: number } }>) =>
        cats
          .filter((c: { category: string | null; _count: { id: number } }) => c.category !== null)
          .map((c: { category: string | null; _count: { id: number } }) => ({
            name: c.category!,
            count: c._count.id,
          }))
      ),
    prisma.retailer.findMany({
      select: {
        id: true,
        name: true,
      },
      orderBy: {
        name: 'asc',
      },
    }),
  ]);

  return { offers, total, categories, retailers };
}

interface OffersPageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{
    page?: string;
    retailerId?: string;
    category?: string;
    search?: string;
    minDiscount?: string;
  }>;
}

export async function generateMetadata({ params }: OffersPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'offers' });
  
  return {
    title: t('title'),
    description: t('description'),
  };
}

export default async function OffersPage({ params, searchParams }: OffersPageProps) {
  const { locale } = await params;
  const paramsSearch = await searchParams;
  const t = await getTranslations({ locale, namespace: 'offers' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });
  
  const page = parseInt(paramsSearch.page || '1');
  const limit = 20;
  const { offers, total, categories, retailers } = await getOffers(
    page,
    limit,
    paramsSearch.retailerId || null,
    paramsSearch.category || null,
    paramsSearch.search || null,
    paramsSearch.minDiscount || null
  );

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-8 px-4">
        <div className="flex items-center gap-2 mb-6">
          <Tag className="h-6 w-6" />
          <h1 className="text-3xl font-bold">{t('title')}</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <aside className="lg:col-span-1">
            <FilterPanel categories={categories} retailers={retailers} />
          </aside>

          <div className="lg:col-span-3">
            {offers.length > 0 ? (
              <>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-6">
                  {offers.map((offer: {
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

                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2">
                    <Link
                      href={`/${locale}/offers?page=${Math.max(1, page - 1)}${
                        paramsSearch.retailerId ? `&retailerId=${paramsSearch.retailerId}` : ''
                      }${paramsSearch.category ? `&category=${paramsSearch.category}` : ''}${
                        paramsSearch.search ? `&search=${paramsSearch.search}` : ''
                      }${paramsSearch.minDiscount ? `&minDiscount=${paramsSearch.minDiscount}` : ''}`}
                    >
                      <Button variant="outline" disabled={page === 1}>
                        <ChevronLeft className="h-4 w-4" />
                        {tCommon('previous')}
                      </Button>
                    </Link>
                    <span className="text-sm text-muted-foreground">
                      {t('pageInfo', { current: page, total: totalPages })}
                    </span>
                    <Link
                      href={`/${locale}/offers?page=${Math.min(totalPages, page + 1)}${
                        paramsSearch.retailerId ? `&retailerId=${paramsSearch.retailerId}` : ''
                      }${paramsSearch.category ? `&category=${paramsSearch.category}` : ''}${
                        paramsSearch.search ? `&search=${paramsSearch.search}` : ''
                      }${paramsSearch.minDiscount ? `&minDiscount=${paramsSearch.minDiscount}` : ''}`}
                    >
                      <Button variant="outline" disabled={page === totalPages}>
                        {tCommon('next')}
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground">
                  {t('noOffers')}
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

