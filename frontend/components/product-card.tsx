import Link from 'next/link';
import Image from 'next/image';
import { Package } from 'lucide-react';
import type { Product } from '@/generated/prisma/client/client';

interface ProductCardProps {
  product: Product & {
    _count?: {
      offers: number;
    };
  };
  locale: string;
}

export function ProductCard({ product, locale }: ProductCardProps) {
  const offersCount = product._count?.offers || 0;

  return (
    <Link href={`/${locale}/products/${product.id}`}>
      <div className="group relative overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm transition-all hover:shadow-md">
        <div className="aspect-square relative bg-muted">
          {product.imageUrl ? (
            <Image
              src={product.imageUrl}
              alt={product.name}
              fill
              className="object-cover transition-transform group-hover:scale-105"
              sizes="(max-width: 640px) 33vw, (max-width: 1024px) 25vw, 20vw"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <Package className="h-12 w-12 text-muted-foreground" />
            </div>
          )}
        </div>
        <div className="p-4 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-sm sm:text-base line-clamp-2 group-hover:text-primary transition-colors">
              {product.name}
            </h3>
          </div>
          {product.brand && (
            <p className="text-xs sm:text-sm text-muted-foreground">
              {product.brand}
            </p>
          )}
          {product.category && (
            <span className="inline-block text-xs px-2 py-1 rounded-full bg-secondary text-secondary-foreground">
              {product.category}
            </span>
          )}
          {offersCount > 0 && (
            <p className="text-xs sm:text-sm text-muted-foreground">
              {offersCount} {offersCount === 1 ? 'offer' : 'offers'}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}

