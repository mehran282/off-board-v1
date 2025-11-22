import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { RetailerCard } from '@/components/retailer-card';
import { FilterPanel } from '@/components/filter-panel';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import Link from 'next/link';
import { Store, ChevronLeft, ChevronRight } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

async function getRetailers(
  page: number,
  limit: number,
  category?: string | null,
  search?: string | null
) {
  try {
    const skip = (page - 1) * limit;
    const where: any = {};

    if (category) {
      where.category = category;
    }

    if (search) {
      where.name = {
        contains: search,
        mode: 'insensitive',
      };
    }

    const [retailers, total, categories] = await Promise.all([
      prisma.retailer.findMany({
        where,
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
        skip,
        take: limit,
      }),
    prisma.retailer.count({ where }),
    (prisma.retailer
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
    ]);

    return { retailers, total, categories };
  } catch (error) {
    console.error('Error fetching retailers:', error);
    return { retailers: [], total: 0, categories: [] };
  }
}

interface RetailersPageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{
    page?: string;
    category?: string;
    search?: string;
  }>;
}

export async function generateMetadata({ params }: RetailersPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'retailers' });
  
  return {
    title: t('title'),
    description: t('description'),
  };
}

export default async function RetailersPage({ params, searchParams }: RetailersPageProps) {
  const { locale } = await params;
  const paramsSearch = await searchParams;
  const t = await getTranslations({ locale, namespace: 'retailers' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });
  
  const page = parseInt(paramsSearch.page || '1');
  const limit = 20;
  const { retailers, total, categories } = await getRetailers(
    page,
    limit,
    paramsSearch.category || null,
    paramsSearch.search || null
  );

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-4 md:py-8 px-2 sm:px-4">
        <div className="flex items-center gap-2 mb-4 md:mb-6">
          <Store className="h-5 w-5 md:h-6 md:w-6" />
          <h1 className="text-2xl md:text-3xl font-bold">{t('title')}</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 md:gap-6">
          <aside className="lg:col-span-1 order-2 lg:order-1">
            <FilterPanel categories={categories} />
          </aside>

          <div className="lg:col-span-3 order-1 lg:order-2">
            {retailers.length > 0 ? (
              <>
                <div className="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 md:gap-3 mb-4 md:mb-6">
                  {retailers.map((retailer: {
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
                    <RetailerCard
                      key={retailer.id}
                      id={retailer.id}
                      name={retailer.name}
                      category={retailer.category}
                      logoUrl={retailer.logoUrl}
                      flyersCount={retailer._count.flyers}
                      offersCount={retailer._count.offers}
                      storesCount={retailer._count.stores}
                    />
                  ))}
                </div>

                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2">
                    <Link
                      href={`/${locale}/retailers?page=${Math.max(1, page - 1)}${
                        paramsSearch.category ? `&category=${paramsSearch.category}` : ''
                      }${paramsSearch.search ? `&search=${paramsSearch.search}` : ''}`}
                    >
                      <Button variant="outline" disabled={page === 1}>
                        <ChevronLeft className="h-4 w-4" />
                        {tCommon('previous')}
                      </Button>
                    </Link>
                    <span className="text-sm text-muted-foreground">
                      {tCommon('page')} {page} {tCommon('of')} {totalPages}
                    </span>
                    <Link
                      href={`/${locale}/retailers?page=${Math.min(totalPages, page + 1)}${
                        paramsSearch.category ? `&category=${paramsSearch.category}` : ''
                      }${paramsSearch.search ? `&search=${paramsSearch.search}` : ''}`}
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
                  {t('noRetailers')}
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

