import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { OfferCard } from '@/components/offer-card';
import { FilterPanel } from '@/components/filter-panel';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import Link from 'next/link';
import { Tag, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Angebote',
  description: 'Entdecken Sie die besten Angebote und Rabatte von verschiedenen Händlern',
};

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
    (prisma.offer
      .groupBy({
        by: ['category'],
        where: {
          category: {
            not: null,
          },
        },
        _count: {
          id: true,
        },
        orderBy: {
          _count: {
            id: 'desc',
          },
        },
      }) as unknown as Promise<Array<{ category: string | null; _count: { id: number } }>>)
      .then((cats) =>
        cats
          .filter((c): c is { category: string; _count: { id: number } } => c.category !== null)
          .map((c) => ({
            name: c.category,
            count: c._count.id,
          }))
      )
      .catch(() => []),
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
  searchParams: Promise<{
    page?: string;
    retailerId?: string;
    category?: string;
    search?: string;
    minDiscount?: string;
  }>;
}

export default async function OffersPage({ searchParams }: OffersPageProps) {
  const params = await searchParams;
  const page = parseInt(params.page || '1');
  const limit = 20;
  const { offers, total, categories, retailers } = await getOffers(
    page,
    limit,
    params.retailerId || null,
    params.category || null,
    params.search || null,
    params.minDiscount || null
  );

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-8 px-4">
        <div className="flex items-center gap-2 mb-6">
          <Tag className="h-6 w-6" />
          <h1 className="text-3xl font-bold">Angebote</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <aside className="lg:col-span-1">
            <FilterPanel categories={categories} retailers={retailers} />
          </aside>

          <div className="lg:col-span-3">
            {offers.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                  {offers.map((offer) => (
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
                      href={`/offers?page=${Math.max(1, page - 1)}${
                        params.retailerId ? `&retailerId=${params.retailerId}` : ''
                      }${params.category ? `&category=${params.category}` : ''}${
                        params.search ? `&search=${params.search}` : ''
                      }${params.minDiscount ? `&minDiscount=${params.minDiscount}` : ''}`}
                    >
                      <Button variant="outline" disabled={page === 1}>
                        <ChevronLeft className="h-4 w-4" />
                        Zurück
                      </Button>
                    </Link>
                    <span className="text-sm text-muted-foreground">
                      Seite {page} von {totalPages}
                    </span>
                    <Link
                      href={`/offers?page=${Math.min(totalPages, page + 1)}${
                        params.retailerId ? `&retailerId=${params.retailerId}` : ''
                      }${params.category ? `&category=${params.category}` : ''}${
                        params.search ? `&search=${params.search}` : ''
                      }${params.minDiscount ? `&minDiscount=${params.minDiscount}` : ''}`}
                    >
                      <Button variant="outline" disabled={page === totalPages}>
                        Weiter
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground">
                  Keine Angebote gefunden. Bitte versuchen Sie andere Filter.
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
