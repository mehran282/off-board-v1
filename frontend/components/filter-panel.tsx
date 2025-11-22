'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

interface FilterPanelProps {
  categories?: Array<{ name: string; count: number }>;
  retailers?: Array<{ id: string; name: string }>;
  brands?: Array<{ name: string; count: number }>;
  currentBrand?: string | null;
}

export function FilterPanel({ categories = [], retailers = [], brands = [], currentBrand }: FilterPanelProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const locale = useLocale();
  const t = useTranslations('filters');
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);
  const [selectedRetailer, setSelectedRetailer] = useState<string | undefined>(undefined);
  const [selectedBrand, setSelectedBrand] = useState<string | undefined>(undefined);
  const [minDiscount, setMinDiscount] = useState<string | undefined>(undefined);

  useEffect(() => {
    const category = searchParams.get('category');
    const retailer = searchParams.get('retailerId');
    const brand = searchParams.get('brand');
    const discount = searchParams.get('minDiscount');
    setSelectedCategory(category || undefined);
    setSelectedRetailer(retailer || undefined);
    setSelectedBrand(brand || currentBrand || undefined);
    setMinDiscount(discount || undefined);
  }, [searchParams, currentBrand]);

  const updateFilters = (key: string, value: string | undefined) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.set('page', '1');
    router.push(`${pathname}?${params.toString()}`);
  };

  const clearFilters = () => {
    router.push(pathname);
  };

  const hasActiveFilters = selectedCategory || selectedRetailer || selectedBrand || minDiscount;

  return (
    <div className="space-y-3 md:space-y-4 p-3 md:p-4 border rounded-lg bg-card">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{t('title')}</h3>
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="h-8"
          >
            <X className="h-4 w-4 mr-1" />
            {t('reset')}
          </Button>
        )}
      </div>

      <div className="space-y-3">
        {categories.length > 0 && (
          <div>
            <label className="text-sm font-medium mb-2 block">{t('category')}</label>
            <Select
              value={selectedCategory}
              onValueChange={(value) => {
                setSelectedCategory(value);
                updateFilters('category', value);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder={t('allCategories')} />
              </SelectTrigger>
              <SelectContent>
                {categories.map((cat) => (
                  <SelectItem key={cat.name} value={cat.name}>
                    {cat.name} ({cat.count})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {retailers.length > 0 && (
          <div>
            <label className="text-sm font-medium mb-2 block">{t('retailer')}</label>
            <Select
              value={selectedRetailer}
              onValueChange={(value) => {
                setSelectedRetailer(value);
                updateFilters('retailerId', value);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder={t('allRetailers')} />
              </SelectTrigger>
              <SelectContent>
                {retailers.map((retailer) => (
                  <SelectItem key={retailer.id} value={retailer.id}>
                    {retailer.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {brands.length > 0 && (
          <div>
            <label className="text-sm font-medium mb-2 block">{t('brand')}</label>
            <Select
              value={selectedBrand}
              onValueChange={(value) => {
                setSelectedBrand(value);
                updateFilters('brand', value);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder={t('allBrands')} />
              </SelectTrigger>
              <SelectContent>
                {brands.map((brand) => (
                  <SelectItem key={brand.name} value={brand.name}>
                    {brand.name} ({brand.count})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div>
          <label className="text-sm font-medium mb-2 block">
            {t('minDiscount')}
          </label>
          <Select
            value={minDiscount}
            onValueChange={(value) => {
              setMinDiscount(value);
              updateFilters('minDiscount', value);
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder={t('noMinimum')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10% {t('orMore')}</SelectItem>
              <SelectItem value="20">20% {t('orMore')}</SelectItem>
              <SelectItem value="30">30% {t('orMore')}</SelectItem>
              <SelectItem value="50">50% {t('orMore')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 pt-2">
          {selectedCategory && (
            <Badge variant="secondary" className="gap-1">
              {t('category')}: {selectedCategory}
              <button
                onClick={() => {
                  setSelectedCategory(undefined);
                  updateFilters('category', undefined);
                }}
                className="ml-1 hover:bg-destructive/20 rounded-full p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {selectedRetailer && (
            <Badge variant="secondary" className="gap-1">
              {t('retailer')}: {retailers.find((r) => r.id === selectedRetailer)?.name}
              <button
                onClick={() => {
                  setSelectedRetailer(undefined);
                  updateFilters('retailerId', undefined);
                }}
                className="ml-1 hover:bg-destructive/20 rounded-full p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {selectedBrand && (
            <Badge variant="secondary" className="gap-1">
              {t('brand')}: {selectedBrand}
              <button
                onClick={() => {
                  setSelectedBrand(undefined);
                  updateFilters('brand', undefined);
                }}
                className="ml-1 hover:bg-destructive/20 rounded-full p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {minDiscount && (
            <Badge variant="secondary" className="gap-1">
              {t('minDiscount').split('(')[0].trim()}: {minDiscount}%+
              <button
                onClick={() => {
                  setMinDiscount(undefined);
                  updateFilters('minDiscount', undefined);
                }}
                className="ml-1 hover:bg-destructive/20 rounded-full p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}

