'use client';

import Link from 'next/link';
import { useLocale, useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Store, FileText, Tag } from 'lucide-react';

interface RetailerCardProps {
  id: string;
  name: string;
  category: string;
  logoUrl?: string | null;
  flyersCount?: number;
  offersCount?: number;
  storesCount?: number;
}

// Generate a deterministic color based on the retailer name
function getColorForName(name: string): string {
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-red-500',
    'bg-yellow-500',
    'bg-teal-500',
    'bg-orange-500',
    'bg-cyan-500',
    'bg-rose-500',
    'bg-violet-500',
    'bg-emerald-500',
    'bg-amber-500',
    'bg-sky-500',
  ];

  // Simple hash function to get consistent color for same name
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % colors.length;
  return colors[index];
}

export function RetailerCard({
  id,
  name,
  category,
  logoUrl,
  flyersCount = 0,
  offersCount = 0,
  storesCount = 0,
}: RetailerCardProps) {
  const locale = useLocale();
  const t = useTranslations('retailers');
  const avatarColor = !logoUrl ? getColorForName(name) : '';
  
  return (
    <Link href={`/${locale}/retailers/${id}`}>
      <Card className="h-full w-full hover:shadow-lg transition-shadow cursor-pointer overflow-hidden !py-0">
        <CardHeader className="p-1.5">
          <div className="flex flex-col items-center gap-1 text-center">
            <Avatar className="h-8 w-8">
              <AvatarImage src={logoUrl || undefined} alt={name} />
              <AvatarFallback className={`text-[10px] text-white ${avatarColor}`}>
                {name.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <h3 className="font-semibold text-xs line-clamp-2">{name}</h3>
            <Badge variant="secondary" className="text-[8px] px-1 py-0">
              {category}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="p-1.5 pt-0">
          <div className="grid grid-cols-3 gap-1 text-center">
            <div>
              <FileText className="h-3 w-3 mx-auto mb-0.5 text-muted-foreground" />
              <p className="text-[10px] font-semibold">{flyersCount}</p>
              <p className="text-[8px] text-muted-foreground">{t('flyers')}</p>
            </div>
            <div>
              <Tag className="h-3 w-3 mx-auto mb-0.5 text-muted-foreground" />
              <p className="text-[10px] font-semibold">{offersCount}</p>
              <p className="text-[8px] text-muted-foreground">{t('offers')}</p>
            </div>
            <div>
              <Store className="h-3 w-3 mx-auto mb-0.5 text-muted-foreground" />
              <p className="text-[10px] font-semibold">{storesCount}</p>
              <p className="text-[8px] text-muted-foreground">{t('stores')}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

