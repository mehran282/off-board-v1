# off-board Frontend

Frontend application for displaying catalogs and discounts from kaufDA.de scraper (off-board project).

## Tech Stack

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Styling
- **shadcn/ui** - UI components
- **Prisma** - Database ORM
- **PostgreSQL (Supabase)** - Database

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- PostgreSQL database (Supabase)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Set up environment variables:

Create a `.env.local` file in the root directory:

```env
DATABASE_URL="postgresql://postgres:password@db.project-ref.supabase.co:5432/postgres?sslmode=require"
NEXT_PUBLIC_SUPABASE_URL=https://project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for detailed setup instructions.

3. Generate Prisma Client:

```bash
npx prisma generate
```

4. Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── api/               # API routes
│   ├── flyers/            # Flyer pages
│   ├── offers/            # Offer pages
│   ├── retailers/         # Retailer pages
│   ├── search/            # Search page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── error.tsx          # Error boundary
│   ├── loading.tsx        # Loading state
│   └── not-found.tsx      # 404 page
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── flyer-card.tsx    # Flyer card component
│   ├── offer-card.tsx    # Offer card component
│   ├── retailer-card.tsx # Retailer card component
│   ├── search-bar.tsx    # Search bar component
│   ├── filter-panel.tsx  # Filter panel component
│   ├── header.tsx        # Header component
│   └── footer.tsx        # Footer component
├── lib/                  # Utilities
│   ├── db.ts             # Prisma client
│   └── utils.ts          # Utility functions
└── prisma/               # Prisma schema
    └── schema.prisma     # Database schema
```

## Features

- 🏠 **Home Page** - Display recent flyers and top offers
- 📄 **Flyers** - Browse and filter flyers by retailer
- 🏷️ **Offers** - Browse and filter offers with advanced filters
- 🏪 **Retailers** - Browse all retailers
- 🔍 **Search** - Search for products, brands, and categories
- 📱 **Responsive Design** - Mobile-friendly interface
- ⚡ **Server Components** - Optimized performance with Next.js
- 🎨 **Modern UI** - Beautiful interface with Tailwind CSS and shadcn/ui

## API Routes

- `GET /api/flyers` - List flyers with pagination
- `GET /api/flyers/[id]` - Get flyer details
- `GET /api/offers` - List offers with filters
- `GET /api/offers/[id]` - Get offer details
- `GET /api/retailers` - List retailers
- `GET /api/categories` - List categories

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Database

The application uses Prisma ORM with PostgreSQL (Supabase). Make sure the database schema is up to date:

```bash
npx prisma generate
```

## Docker Usage

### Build Image

```bash
docker build -t off-board-frontend:latest ./frontend
```

### Run Container

```bash
docker run --rm \
  -p 3040:3040 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/dbname" \
  off-board-frontend:latest
```

### Using GitHub Container Registry

```bash
# Pull image
docker pull ghcr.io/mehran282/off-board-frontend:latest

# Run with environment variables
docker run --rm \
  -p 3040:3040 \
  -e DATABASE_URL="your-database-url" \
  ghcr.io/mehran282/off-board-frontend:latest
```

### Using Docker Compose

```bash
cd frontend

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:pass@host:5432/dbname
NEXT_PUBLIC_DEFAULT_LOCALE=en
NEXT_PUBLIC_SUPPORTED_LOCALES=en,de
EOF

# Run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Deployment

### Docker Deployment

1. Build the Docker image:

```bash
docker build -t off-board-frontend:latest ./frontend
```

2. Run with environment variables:

```bash
docker run -d \
  -p 3040:3040 \
  -e DATABASE_URL="your-database-url" \
  --name off-board-frontend \
  off-board-frontend:latest
```

### Vercel/Netlify Deployment

1. Build the application:

```bash
npm run build
```

2. Set environment variables in your hosting platform
3. Deploy to Vercel, Netlify, or your preferred platform

### GitHub Actions

The project includes a GitHub Action workflow (`.github/workflows/build-frontend.yml`) that automatically builds and pushes Docker images to GitHub Container Registry (GHCR) on every push to `master` or `main` branch.

The image will be available at: `ghcr.io/mehran282/off-board-frontend:latest`

## License

MIT
