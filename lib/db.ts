import { PrismaClient } from '@prisma/client';
import { Pool } from 'pg';
import { PrismaPg } from '@prisma/adapter-pg';

let prisma: PrismaClient;

declare global {
  // eslint-disable-next-line no-var
  var __prisma: PrismaClient | undefined;
  // eslint-disable-next-line no-var
  var __prismaPool: Pool | undefined;
  // eslint-disable-next-line no-var
  var __prismaAdapter: PrismaPg | undefined;
}

function getPrismaClient(): PrismaClient {
  const connectionString = process.env.DATABASE_URL;

  if (!connectionString) {
    throw new Error('DATABASE_URL environment variable is not set');
  }

  if (process.env.NODE_ENV === 'production') {
    if (!prisma) {
      const pool = new Pool({ connectionString });
      const adapter = new PrismaPg(pool);
      prisma = new PrismaClient({ adapter });
    }
    return prisma;
  } else {
    if (!global.__prisma) {
      if (!global.__prismaPool) {
        global.__prismaPool = new Pool({ connectionString });
      }
      if (!global.__prismaAdapter) {
        global.__prismaAdapter = new PrismaPg(global.__prismaPool);
      }
      global.__prisma = new PrismaClient({
        adapter: global.__prismaAdapter,
        log: ['error', 'warn'],
      });
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

