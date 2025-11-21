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
        <div className="relative w-full aspect-[3/2] bg-muted overflow-hidden">
            {imageUrl ? (
              <Image
                src={imageUrl}
                alt={productName}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                {t('noImage')}
              </div>
            )}
            {discountPercentage && discountPercentage > 0 && (
              <Badge
                className="absolute top-1 right-1 bg-destructive text-destructive-foreground text-xs px-1.5 py-0.5"
                variant="destructive"
              >
                -{Math.round(discountPercentage)}%
              </Badge>
            )}
          </div>
        <CardContent className="p-1.5">
          <div className="space-y-0.5">
            {brand && (
              <p className="text-[10px] text-muted-foreground">{brand}</p>
            )}
            <h3 className="font-semibold text-xs line-clamp-2">{productName}</h3>
            <div className="flex items-center gap-1 flex-wrap">
              {oldPrice && oldPrice > currentPrice && (
                <span className="text-[10px] text-muted-foreground line-through">
                  {formatPrice(oldPrice)}
                </span>
              )}
              <span className="text-base font-bold">{formatPrice(currentPrice)}</span>
            </div>
            <div className="flex items-center gap-1 pt-0.5">
              <Avatar className="h-3 w-3">
                <AvatarImage src={retailer.logoUrl || undefined} alt={retailer.name} />
                <AvatarFallback className="text-[7px]">
                  {retailer.name.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <span className="text-[10px] text-muted-foreground">{retailer.name}</span>
            </div>
            {validUntil && (
              <p className="text-[9px] text-muted-foreground">
                {t('validUntil')}: {formatDate(validUntil)}
              </p>
            )}
          </div>
        </CardContent>
        <CardFooter className="p-1.5 pt-0">
          <span className="text-[10px] text-primary font-medium">{tCommon('details')} →</span>
        </CardFooter>
      </Card>
    </Link>
  );
}

