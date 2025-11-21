import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { FlyerCard } from '@/components/flyer-card';
import { FilterPanel } from '@/components/filter-panel';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import Link from 'next/link';
import { FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

async function getFlyers(
  page: number,
  limit: number,
  retailerId?: string | null
) {
  const skip = (page - 1) * limit;
  const where = retailerId ? { retailerId } : {};

  const [flyers, total, retailers] = await Promise.all([
    prisma.flyer.findMany({
      where,
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
      skip,
      take: limit,
    }),
    prisma.flyer.count({ where }),
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

  return { flyers, total, retailers };
}

interface FlyersPageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{
    page?: string;
    retailerId?: string;
  }>;
}

export async function generateMetadata({ params }: FlyersPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'flyers' });
  
  return {
    title: t('title'),
    description: t('description'),
  };
}

export default async function FlyersPage({ params, searchParams }: FlyersPageProps) {
  const { locale } = await params;
  const paramsSearch = await searchParams;
  const t = await getTranslations({ locale, namespace: 'flyers' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });
  
  const page = parseInt(paramsSearch.page || '1');
  const limit = 20;
  const { flyers, total, retailers } = await getFlyers(
    page,
    limit,
    paramsSearch.retailerId || null
  );

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-8 px-4">
        <div className="flex items-center gap-2 mb-6">
          <FileText className="h-6 w-6" />
          <h1 className="text-3xl font-bold">{t('title')}</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <aside className="lg:col-span-1">
            <FilterPanel retailers={retailers} />
          </aside>

          <div className="lg:col-span-3">
            {flyers.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  {flyers.map((flyer) => (
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

                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2">
                    <Link
                      href={`/${locale}/flyers?page=${Math.max(1, page - 1)}${
                        paramsSearch.retailerId ? `&retailerId=${paramsSearch.retailerId}` : ''
                      }`}
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
                      href={`/${locale}/flyers?page=${Math.min(totalPages, page + 1)}${
                        paramsSearch.retailerId ? `&retailerId=${paramsSearch.retailerId}` : ''
                      }`}
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
                  {t('noFlyers')}
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

