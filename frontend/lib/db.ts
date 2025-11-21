import { PrismaClient } from '@prisma/client';
import { withAccelerate } from '@prisma/extension-accelerate';

let prisma: ReturnType<typeof createPrismaClient>;

declare global {
  // eslint-disable-next-line no-var
  var __prisma: ReturnType<typeof createPrismaClient> | undefined;
}

function createPrismaClient() {
  const accelerateUrl = process.env.DATABASE_URL;

  if (!accelerateUrl) {
    throw new Error('DATABASE_URL environment variable is not set');
  }

  return new PrismaClient({
    accelerateUrl,
  }).$extends(withAccelerate());
}

function getPrismaClient() {
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
const prismaProxy = new Proxy({} as ReturnType<typeof createPrismaClient>, {
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

