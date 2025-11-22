import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { OfferCard } from '@/components/offer-card';
import { Button } from '@/components/ui/button';
import prisma from '@/lib/db';
import Link from 'next/link';
import { Package, ArrowLeft, Tag } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import { notFound } from 'next/navigation';
import Image from 'next/image';
import type { Metadata } from 'next';

async function getProduct(id: string) {
  try {
    const product = await prisma.product.findUnique({
      where: { id },
      include: {
        offers: {
          include: {
            retailer: {
              select: {
                id: true,
                name: true,
                logoUrl: true,
              },
            },
            flyer: {
              select: {
                id: true,
                title: true,
                thumbnailUrl: true,
              },
            },
          },
          orderBy: {
            currentPrice: 'asc',
          },
          take: 50,
        },
        _count: {
          select: {
            offers: true,
          },
        },
      },
    });

    return product;
  } catch (error) {
    console.error('Error fetching product:', error);
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}): Promise<Metadata> {
  const { id, locale } = await params;
  const t = await getTranslations({ locale, namespace: 'common' });
  const product = await getProduct(id);

  if (!product) {
    return {
      title: t('notFound'),
    };
  }

  return {
    title: product.name,
    description: product.description || `${product.name} - ${product.brand || ''}`,
  };
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id, locale } = await params;
  const t = await getTranslations({ locale, namespace: 'common' });
  const product = await getProduct(id);

  if (!product) {
    notFound();
  }

  const offersCount = product._count?.offers || 0;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 w-full max-w-full lg:max-w-[60%] mx-auto px-4 py-6 sm:py-8">
        <div className="mb-6">
          <Button variant="ghost" size="sm" asChild className="mb-4">
            <Link href={`/${locale}/products`}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              {t('back')}
            </Link>
          </Button>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 mb-8">
            <div className="aspect-square relative bg-muted rounded-lg overflow-hidden">
              {product.imageUrl ? (
                <Image
                  src={product.imageUrl}
                  alt={product.name}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 50vw"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <Package className="h-24 w-24 text-muted-foreground" />
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold mb-2">{product.name}</h1>
                {product.brand && (
                  <p className="text-lg sm:text-xl text-muted-foreground mb-2">
                    {product.brand}
                  </p>
                )}
                {product.category && (
                  <span className="inline-block text-sm px-3 py-1 rounded-full bg-secondary text-secondary-foreground mb-4">
                    {product.category}
                  </span>
                )}
              </div>

              {product.description && (
                <div>
                  <h2 className="text-lg font-semibold mb-2">Description</h2>
                  <p className="text-sm sm:text-base text-muted-foreground whitespace-pre-line">
                    {product.description}
                  </p>
                </div>
              )}

              {offersCount > 0 && (
                <div className="flex items-center gap-2 text-sm sm:text-base">
                  <Tag className="h-4 w-4 sm:h-5 sm:w-5" />
                  <span>
                    {offersCount} {offersCount === 1 ? 'offer' : 'offers'} available
                  </span>
                </div>
              )}
            </div>
          </div>

          {product.offers.length > 0 && (
            <div>
              <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">
                Available Offers ({product.offers.length})
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {product.offers.map((offer) => (
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
                    validUntil={offer.validUntil?.toISOString()}
                  />
                ))}
              </div>
            </div>
          )}

          {product.offers.length === 0 && (
            <div className="text-center py-12">
              <Tag className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-lg font-semibold mb-2">No offers available</p>
              <p className="text-sm text-muted-foreground">
                There are currently no offers for this product.
              </p>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}

