import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { RetailerCard } from '@/components/retailer-card';
import { SearchBar } from '@/components/search-bar';
import prisma from '@/lib/db';
import { Store } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Händler',
  description: 'Durchsuchen Sie alle verfügbaren Händler und ihre Angebote',
};

async function getRetailers(category?: string | null, search?: string | null) {
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

  const retailers = await prisma.retailer.findMany({
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
  });

  return retailers;
}

interface RetailersPageProps {
  searchParams: Promise<{
    category?: string;
    search?: string;
  }>;
}

export default async function RetailersPage({ searchParams }: RetailersPageProps) {
  const params = await searchParams;
  const retailers = await getRetailers(
    params.category || null,
    params.search || null
  );

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-8 px-4">
        <div className="flex items-center gap-2 mb-6">
          <Store className="h-6 w-6" />
          <h1 className="text-3xl font-bold">Händler</h1>
        </div>

        <div className="mb-6">
          <SearchBar />
        </div>

        {retailers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {retailers.map((retailer) => (
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
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              Keine Händler gefunden. Bitte versuchen Sie eine andere Suche.
            </p>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
