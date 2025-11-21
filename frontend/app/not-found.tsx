import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-bold">404</h1>
        <h2 className="text-2xl font-semibold">Page Not Found / Seite nicht gefunden</h2>
        <p className="text-muted-foreground">
          The requested page could not be found. / Die angeforderte Seite konnte nicht gefunden werden.
        </p>
        <Link href="/de">
          <Button>
            <Home className="h-4 w-4 mr-2" />
            Go to Home / Zur Startseite
          </Button>
        </Link>
      </div>
    </div>
  );
}

