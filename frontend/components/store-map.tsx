'use client';

import { useEffect, useRef } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { Feature } from 'ol';
import { Point } from 'ol/geom';
import { fromLonLat } from 'ol/proj';
import { Style, Icon } from 'ol/style';

interface StoreLocation {
  id: string;
  address: string;
  city: string;
  postalCode: string;
  latitude: number | null;
  longitude: number | null;
  name?: string;
}

interface StoreMapProps {
  stores: StoreLocation[];
  retailerName?: string;
  className?: string;
}

export function StoreMap({ stores, retailerName, className = '' }: StoreMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Filter stores with valid coordinates
    const validStores = stores.filter(
      (store) => store.latitude !== null && store.longitude !== null && 
                 !isNaN(store.latitude) && !isNaN(store.longitude)
    );

    if (validStores.length === 0) {
      // Show message if no valid coordinates
      mapRef.current.innerHTML = '<div class="flex items-center justify-center h-full text-muted-foreground text-sm">No location data available</div>';
      return;
    }

    // Create vector source for markers
    const vectorSource = new VectorSource();

    // Add markers for each store
    validStores.forEach((store) => {
      const feature = new Feature({
        geometry: new Point(fromLonLat([store.longitude!, store.latitude!])),
        name: store.name || `${store.address}, ${store.postalCode} ${store.city}`,
        address: store.address,
        city: store.city,
        postalCode: store.postalCode,
      });

      // Create marker style
      feature.setStyle(
        new Style({
          image: new Icon({
            anchor: [0.5, 1],
            src: 'data:image/svg+xml;base64,' + btoa(`
              <svg width="32" height="40" viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 0C7.163 0 0 7.163 0 16C0 24.837 16 40 16 40C16 40 32 24.837 32 16C32 7.163 24.837 0 16 0Z" fill="#dc2626"/>
                <circle cx="16" cy="16" r="6" fill="white"/>
              </svg>
            `),
            scale: 1,
          }),
        })
      );

      vectorSource.addFeature(feature);
    });

    // Calculate center and zoom
    const lons = validStores.map((s) => s.longitude!);
    const lats = validStores.map((s) => s.latitude!);
    const centerLon = (Math.min(...lons) + Math.max(...lons)) / 2;
    const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;

    // Calculate zoom level based on bounds
    const lonDiff = Math.max(...lons) - Math.min(...lons);
    const latDiff = Math.max(...lats) - Math.min(...lats);
    const maxDiff = Math.max(lonDiff, latDiff);
    let zoom = 13;
    if (maxDiff > 0.1) zoom = 10;
    else if (maxDiff > 0.05) zoom = 11;
    else if (maxDiff > 0.02) zoom = 12;
    else if (maxDiff > 0.01) zoom = 13;
    else zoom = 14;

    // Create map
    const map = new Map({
      target: mapRef.current,
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
        new VectorLayer({
          source: vectorSource,
        }),
      ],
      view: new View({
        center: fromLonLat([centerLon, centerLat]),
        zoom: zoom,
      }),
    });

    mapInstanceRef.current = map;

    // Cleanup
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.setTarget(undefined);
        mapInstanceRef.current = null;
      }
    };
  }, [stores, retailerName]);

  return (
    <div className={`w-full h-[400px] sm:h-[500px] rounded-lg overflow-hidden border ${className}`}>
      <div ref={mapRef} className="w-full h-full" />
    </div>
  );
}

