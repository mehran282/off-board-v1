'use client';

import { FileText } from 'lucide-react';

interface PdfThumbnailProps {
  pdfUrl: string;
  alt?: string;
  className?: string;
}

export function PdfThumbnail({ pdfUrl, alt = 'PDF Preview', className = '' }: PdfThumbnailProps) {
  // Use iframe to display PDF preview
  // Note: Some PDFs may have X-Frame-Options that prevent embedding
  return (
    <div className={`relative w-full h-full bg-muted overflow-hidden ${className}`}>
      <iframe
        src={`${pdfUrl}#page=1&zoom=50`}
        className="w-full h-full border-0"
        title={alt}
        loading="lazy"
        onError={() => {
          // Fallback to placeholder if iframe fails
        }}
      />
      {/* Fallback placeholder - shown if iframe fails to load */}
      <div className="absolute inset-0 bg-muted flex flex-col items-center justify-center pointer-events-none">
        <FileText className="h-8 w-8 text-muted-foreground mb-2 opacity-50" />
        <span className="text-muted-foreground text-xs text-center px-2 opacity-50">PDF Preview</span>
      </div>
    </div>
  );
}

