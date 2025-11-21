import { NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function GET() {
  try {
    // Get the latest scraping log
    const latestLog = await prisma.scrapingLog.findFirst({
      orderBy: {
        startedAt: 'desc',
      },
      take: 1,
    });

    if (!latestLog) {
      return NextResponse.json({
        status: 'idle',
        message: 'No scraping activity found',
      });
    }

    return NextResponse.json({
      status: latestLog.status,
      itemsScraped: latestLog.itemsScraped,
      errors: latestLog.errors ? JSON.parse(latestLog.errors) : [],
      startedAt: latestLog.startedAt,
      completedAt: latestLog.completedAt,
    });
  } catch (error) {
    console.error('Error fetching scraping status:', error);
    return NextResponse.json(
      {
        status: 'error',
        message: 'Failed to fetch scraping status',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

