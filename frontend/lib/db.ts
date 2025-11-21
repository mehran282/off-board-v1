import { PrismaClient } from '@prisma/client';
import { withAccelerate } from '@prisma/extension-accelerate';

type PrismaClientWithAccelerate = ReturnType<typeof createPrismaClient>;

let prisma: PrismaClientWithAccelerate;

declare global {
  // eslint-disable-next-line no-var
  var __prisma: PrismaClientWithAccelerate | undefined;
}

function createPrismaClient() {
  return new PrismaClient().$extends(withAccelerate());
}

function getPrismaClient(): PrismaClientWithAccelerate {
  const databaseUrl = process.env.DATABASE_URL;

  if (!databaseUrl) {
    throw new Error('DATABASE_URL environment variable is not set');
  }

  if (process.env.NODE_ENV === 'production') {
    if (!prisma) {
      prisma = createPrismaClient();
    }
    return prisma;
  } else {
    if (!global.__prisma) {
      global.__prisma = createPrismaClient();
    }
    return global.__prisma;
  }
}

// Lazy initialization - only create client when actually used
const prismaProxy = new Proxy({} as PrismaClientWithAccelerate, {
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

