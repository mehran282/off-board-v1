'use client';

import Link from 'next/link';
import { useLocale, useTranslations } from 'next-intl';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Calendar, FileText } from 'lucide-react';
import Image from 'next/image';

interface FlyerCardProps {
  id: string;
  title: string;
  retailer: {
    id: string;
    name: string;
    logoUrl?: string | null;
  };
  validFrom: string;
  validUntil: string;
  pages: number;
  pdfUrl?: string | null;
  thumbnailUrl?: string | null;
  offersCount?: number;
}

export function FlyerCard({
  id,
  title,
  retailer,
  validFrom,
  validUntil,
  pages,
  pdfUrl,
  thumbnailUrl,
  offersCount = 0,
}: FlyerCardProps) {
  const locale = useLocale();
  const t = useTranslations('flyers');
  const tCommon = useTranslations('common');

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString(locale === 'de' ? 'de-DE' : 'en-US', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  // ساخت URL تصویر: اول thumbnailUrl، سپس از pdfUrl یک preview URL می‌سازیم
  let imageUrl: string | null = null;
  
  if (thumbnailUrl) {
    // اگر thumbnailUrl کامل است (با http شروع می‌شود)، استفاده می‌کنیم
    imageUrl = thumbnailUrl.startsWith('http') ? thumbnailUrl : `https:${thumbnailUrl}`;
  } else if (pdfUrl) {
    // اگر thumbnailUrl نبود، از pdfUrl یک preview URL می‌سازیم
    if (pdfUrl.includes('bonial.biz')) {
      // برای bonial.biz: جایگزین کردن /file.pdf با /preview.jpg
      if (pdfUrl.includes('/file.pdf')) {
        imageUrl = pdfUrl.replace('/file.pdf', '/preview.jpg');
      } else if (pdfUrl.endsWith('.pdf')) {
        imageUrl = pdfUrl.replace('.pdf', '/preview.jpg');
      } else {
        // اگر ساختار متفاوت است
        imageUrl = pdfUrl.replace(/\/[^/]+\.pdf$/, '/preview.jpg');
      }
    }
  }

  return (
    <Link href={`/${locale}/flyers/${id}`}>
      <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer overflow-hidden !py-0">
        {imageUrl ? (
          <div className="relative w-full aspect-[3/4] bg-muted overflow-hidden">
            <Image
              src={imageUrl}
              alt={title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              unoptimized={imageUrl.includes('bonial.biz')} // برای تصاویر خارجی
            />
          </div>
        ) : (
          <div className="relative w-full aspect-[3/4] bg-muted flex items-center justify-center">
            <FileText className="h-12 w-12 text-muted-foreground/50" />
          </div>
        )}
        <CardHeader className="p-3">
          <div className="flex items-center gap-2 mb-2">
            <Avatar className="h-8 w-8">
              <AvatarImage src={retailer.logoUrl || undefined} alt={retailer.name} />
              <AvatarFallback className="text-xs">{retailer.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-sm truncate">{title}</h3>
              <p className="text-xs text-muted-foreground truncate">{retailer.name}</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-3 pt-0">
          <div className="space-y-1.5">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span className="truncate">
                {formatDate(validFrom)} - {formatDate(validUntil)}
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <FileText className="h-3 w-3" />
              <span>{pages} {t('pages')}</span>
            </div>
            {offersCount > 0 && (
              <Badge variant="secondary" className="text-xs px-1.5 py-0">
                {offersCount} {t('offersCount')}
              </Badge>
            )}
          </div>
        </CardContent>
        <CardFooter className="p-3 pt-0">
          <span className="text-xs text-primary font-medium">{tCommon('details')} →</span>
        </CardFooter>
      </Card>
    </Link>
  );
}

