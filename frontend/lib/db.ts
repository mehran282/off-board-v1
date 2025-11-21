import { PrismaClient } from '@prisma/client';

let prisma: PrismaClient;

declare global {
  // eslint-disable-next-line no-var
  var __prisma: PrismaClient | undefined;
}

function getPrismaClient(): PrismaClient {
  const connectionString = process.env.DATABASE_URL;

  if (!connectionString) {
    throw new Error('DATABASE_URL environment variable is not set');
  }

  if (process.env.NODE_ENV === 'production') {
    if (!prisma) {
      prisma = new PrismaClient();
    }
    return prisma;
  } else {
    if (!global.__prisma) {
      global.__prisma = new PrismaClient({
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

