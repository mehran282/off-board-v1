'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useLocale, useTranslations } from 'next-intl';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

interface OfferCardProps {
  id: string;
  productName: string;
  brand?: string | null;
  currentPrice: number;
  oldPrice?: number | null;
  discountPercentage?: number | null;
  imageUrl?: string | null;
  retailer: {
    id: string;
    name: string;
    logoUrl?: string | null;
  };
  validUntil?: string | null;
}

export function OfferCard({
  id,
  productName,
  brand,
  currentPrice,
  oldPrice,
  discountPercentage,
  imageUrl,
  retailer,
  validUntil,
}: OfferCardProps) {
  const locale = useLocale();
  const t = useTranslations('offers');
  const tCommon = useTranslations('common');
  
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat(locale === 'de' ? 'de-DE' : 'en-US', {
      style: 'currency',
      currency: 'EUR',
    }).format(price);
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString(locale === 'de' ? 'de-DE' : 'en-US', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  return (
    <Link href={`/${locale}/offers/${id}`}>
      <Card className="h-full w-full hover:shadow-lg transition-shadow cursor-pointer overflow-hidden !py-0">
        <div className="relative w-full aspect-[3/3.12] bg-muted overflow-hidden">
            {imageUrl ? (
              <Image
                src={imageUrl}
                alt={productName}
                fill
                className="object-cover"
                sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, 20vw"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-muted-foreground text-xs sm:text-sm">
                {t('noImage')}
              </div>
            )}
            {discountPercentage && discountPercentage > 0 && (
              <Badge
                className="absolute top-1 right-1 bg-destructive text-destructive-foreground text-[10px] sm:text-xs px-1 sm:px-1.5 py-0.5"
                variant="destructive"
              >
                -{Math.round(discountPercentage)}%
              </Badge>
            )}
          </div>
        <CardContent className="p-1.5 sm:p-2">
          <div className="space-y-0.5 sm:space-y-1">
            {brand && (
              <p className="text-[10px] sm:text-xs text-muted-foreground truncate">{brand}</p>
            )}
            <h3 className="font-semibold text-xs sm:text-sm line-clamp-2 min-h-[2.5em]">{productName}</h3>
            <div className="flex items-center gap-1 flex-wrap">
              {oldPrice && oldPrice > currentPrice && (
                <span className="text-[10px] sm:text-xs text-muted-foreground line-through">
                  {formatPrice(oldPrice)}
                </span>
              )}
              <span className="text-sm sm:text-base font-bold">{formatPrice(currentPrice)}</span>
            </div>
            <div className="flex items-center gap-1 pt-0.5 sm:pt-1">
              <Avatar className="h-3 w-3 sm:h-4 sm:w-4">
                <AvatarImage src={retailer.logoUrl || undefined} alt={retailer.name} />
                <AvatarFallback className="text-[7px] sm:text-[9px]">
                  {retailer.name.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <span className="text-[10px] sm:text-xs text-muted-foreground truncate">{retailer.name}</span>
            </div>
            {validUntil && (
              <p className="text-[9px] sm:text-[10px] text-muted-foreground">
                {t('validUntil')}: {formatDate(validUntil)}
              </p>
            )}
          </div>
        </CardContent>
        <CardFooter className="p-1.5 sm:p-2 pt-0">
          <span className="text-[10px] sm:text-xs text-primary font-medium">{tCommon('details')} →</span>
        </CardFooter>
      </Card>
    </Link>
  );
}

