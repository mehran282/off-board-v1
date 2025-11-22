import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { ProductCard } from '@/components/product-card';
import { FilterPanel } from '@/components/filter-panel';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import Link from 'next/link';
import { Package, ChevronLeft, ChevronRight } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

async function getProducts(
  page: number,
  limit: number,
  category?: string | null,
  brand?: string | null,
  search?: string | null
) {
  try {
    const skip = (page - 1) * limit;
    const where: any = {};

    if (category) {
      where.category = category;
    }

    if (brand) {
      where.brand = brand;
    }

    if (search) {
      where.name = {
        contains: search,
        mode: 'insensitive',
      };
    }

    const [products, total, categories, brands] = await Promise.all([
      prisma.product.findMany({
        where,
        include: {
          _count: {
            select: {
              offers: true,
            },
          },
        },
        orderBy: {
          createdAt: 'desc',
        },
        skip,
        take: limit,
      }),
      prisma.product.count({ where }),
      prisma.product
        .groupBy({
          by: ['category'],
          where: { category: { not: null } },
          _count: {
            id: true,
          },
        })
        .then((cats) =>
          cats
            .filter((c): c is { category: string; _count: { id: number } } => c.category !== null)
            .map((c) => ({
              name: c.category!,
              count: c._count.id,
            }))
        ) as Promise<Array<{ name: string; count: number }>>,
      prisma.product
        .groupBy({
          by: ['brand'],
          where: { brand: { not: null } },
          _count: {
            id: true,
          },
        })
        .then((brands) =>
          brands
            .filter((b): b is { brand: string; _count: { id: number } } => b.brand !== null)
            .map((b) => ({
              name: b.brand!,
              count: b._count.id,
            }))
        ) as Promise<Array<{ name: string; count: number }>>,
    ]);

    return {
      products,
      total,
      totalPages: Math.ceil(total / limit),
      categories,
      brands,
    };
  } catch (error) {
    console.error('Error fetching products:', error);
    return {
      products: [],
      total: 0,
      totalPages: 0,
      categories: [],
      brands: [],
    };
  }
}

export async function generateMetadata({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'common' });

  return {
    title: t('products'),
    description: t('productsDescription') || 'Browse all products',
  };
}

export default async function ProductsPage({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const { locale } = await params;
  const resolvedSearchParams = await searchParams;
  const t = await getTranslations({ locale, namespace: 'common' });

  const page = Number(resolvedSearchParams.page) || 1;
  const limit = 24;
  const category = resolvedSearchParams.category as string | undefined;
  const brand = resolvedSearchParams.brand as string | undefined;
  const search = resolvedSearchParams.search as string | undefined;

  const { products, total, totalPages, categories, brands } = await getProducts(
    page,
    limit,
    category,
    brand,
    search
  );

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 w-full max-w-full lg:max-w-[60%] mx-auto px-4 py-6 sm:py-8">
        <div className="mb-6 sm:mb-8">
          <div className="flex items-center gap-2 mb-2">
            <Package className="h-6 w-6 sm:h-8 sm:w-8" />
            <h1 className="text-2xl sm:text-3xl font-bold">{t('products')}</h1>
          </div>
          {total > 0 && (
            <p className="text-sm sm:text-base text-muted-foreground">
              {total} {total === 1 ? 'product' : 'products'} found
            </p>
          )}
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          <aside className="lg:w-64 flex-shrink-0">
            <FilterPanel
              categories={categories}
              brands={brands}
              currentBrand={brand}
            />
          </aside>

          <div className="flex-1">
            {products.length > 0 ? (
              <>
                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3 sm:gap-4">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} locale={locale} />
                  ))}
                </div>

                {totalPages > 1 && (
                  <div className="mt-6 sm:mt-8 flex items-center justify-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      asChild
                      disabled={page === 1}
                    >
                      <Link
                        href={{
                          pathname: `/${locale}/products`,
                          query: {
                            ...resolvedSearchParams,
                            page: page > 1 ? page - 1 : 1,
                          },
                        }}
                      >
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        {t('previous')}
                      </Link>
                    </Button>

                    <span className="text-sm text-muted-foreground px-4">
                      {t('page')} {page} {t('of')} {totalPages}
                    </span>

                    <Button
                      variant="outline"
                      size="sm"
                      asChild
                      disabled={page >= totalPages}
                    >
                      <Link
                        href={{
                          pathname: `/${locale}/products`,
                          query: {
                            ...resolvedSearchParams,
                            page: page < totalPages ? page + 1 : totalPages,
                          },
                        }}
                      >
                        {t('next')}
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Link>
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-lg font-semibold mb-2">{t('noResults')}</p>
                <p className="text-sm text-muted-foreground">{t('tryOtherFilters')}</p>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

