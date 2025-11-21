import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { OfferCard } from '@/components/offer-card';
import { SearchBar } from '@/components/search-bar';
import prisma from '@/lib/db';
import { Search } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';

interface SearchPageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{
    q?: string;
  }>;
}

export async function generateMetadata({ params }: SearchPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'search' });
  
  return {
    title: t('title'),
    description: t('description'),
  };
}

async function searchOffers(query: string) {
  try {
    const offers = await prisma.offer.findMany({
      where: {
        OR: [
          {
            productName: {
              contains: query,
              mode: 'insensitive',
            },
          },
          {
            brand: {
              contains: query,
              mode: 'insensitive',
            },
          },
          {
            category: {
              contains: query,
              mode: 'insensitive',
            },
          },
        ],
      },
      select: {
        id: true,
        productName: true,
        brand: true,
        currentPrice: true,
        oldPrice: true,
        discountPercentage: true,
        imageUrl: true,
        validUntil: true,
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
      take: 50,
    });

    return offers;
  } catch (error) {
    console.error('Error searching offers:', error);
    return [];
  }
}

export default async function SearchPage({ params, searchParams }: SearchPageProps) {
  const { locale } = await params;
  const paramsSearch = await searchParams;
  const t = await getTranslations({ locale, namespace: 'search' });
  const tCommon = await getTranslations({ locale, namespace: 'common' });
  
  const query = paramsSearch.q || '';
  const offers = query ? await searchOffers(query) : [];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-8 px-4">
        <div className="flex items-center gap-2 mb-6">
          <Search className="h-6 w-6" />
          <h1 className="text-3xl font-bold">{t('title')}</h1>
        </div>

        <div className="mb-6">
          <SearchBar />
        </div>

        {query && (
          <p className="text-muted-foreground mb-6">
            {offers.length} {offers.length === 1 ? t('result') : t('results')} {t('for')} &quot;{query}&quot;
          </p>
        )}

        {offers.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            {(offers as unknown as Array<{
              id: string;
              productName: string;
              brand: string | null;
              currentPrice: number;
              oldPrice: number | null;
              discountPercentage: number | null;
              imageUrl: string | null;
              validUntil: Date | null;
              retailer: {
                id: string;
                name: string;
                logoUrl: string | null;
              };
            }>).map((offer) => (
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
        ) : query ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              {t('noResults')} &quot;{query}&quot; {t('found')}.
            </p>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              {t('enterSearchTerm')}
            </p>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

