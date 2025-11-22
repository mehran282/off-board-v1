import { PrismaClient } from '@/generated/prisma/client/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

let prisma: PrismaClient;
let adapter: PrismaPg;

declare global {
  // eslint-disable-next-line no-var
  var __prisma: PrismaClient | undefined;
  // eslint-disable-next-line no-var
  var __adapter: PrismaPg | undefined;
}

function getPrismaClient(): PrismaClient {
  const databaseUrl = process.env.DATABASE_URL;

  if (!databaseUrl) {
    throw new Error('DATABASE_URL environment variable is not set. Please set it in your .env file or environment variables.');
  }

  // Validate connection string format
  if (!databaseUrl.startsWith('postgres://') && !databaseUrl.startsWith('postgresql://')) {
    console.warn('Warning: DATABASE_URL should start with postgres:// or postgresql://');
  }

  // Create adapter with connection pool
  if (process.env.NODE_ENV === 'production') {
    if (!adapter) {
      const pool = new Pool({
        connectionString: databaseUrl,
        ssl: databaseUrl.includes('sslmode=require') ? { rejectUnauthorized: false } : undefined,
      });
      adapter = new PrismaPg(pool);
    }
    if (!prisma) {
      prisma = new PrismaClient({ adapter });
    }
    return prisma;
  } else {
    if (!global.__adapter) {
      const pool = new Pool({
        connectionString: databaseUrl,
        ssl: databaseUrl.includes('sslmode=require') ? { rejectUnauthorized: false } : undefined,
      });
      global.__adapter = new PrismaPg(pool);
    }
    if (!global.__prisma) {
      global.__prisma = new PrismaClient({ adapter: global.__adapter });
    }
    return global.__prisma;
  }
}

// Lazy initialization - only create client when actually used
const prismaProxy = new Proxy({} as PrismaClient, {
  get(_target, prop) {
    const client = getPrismaClient();
    const value = (client as any)[prop];
    if (typeof value === 'function') {
      return value.bind(client);
    }
    return value;
  },
});

export default prismaProxy;

