import 'dotenv/config';
import { defineConfig, env } from 'prisma/config';

// DATABASE_URL is optional during generate, only needed for migrations
const databaseUrl = process.env.DATABASE_URL || 'postgresql://placeholder:placeholder@localhost:5432/placeholder';

export default defineConfig({
  // the main entry for your schema
  schema: 'prisma/schema.prisma',
  // where migrations should be generated
  migrations: {
    path: 'prisma/migrations',
  },
  // The database URL
  datasource: {
    url: databaseUrl,
  },
});
