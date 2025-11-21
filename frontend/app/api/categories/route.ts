import { NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function GET() {
  try {
    const categories = await prisma.offer.groupBy({
      by: ['category'],
      where: {
        category: {
          not: null,
        },
      },
      _count: {
        id: true,
      },
      orderBy: {
        _count: {
          id: 'desc',
        },
      },
    });

    return NextResponse.json({
      categories: (categories as unknown as Array<{ category: string | null; _count: { id: number } }>)
        .filter((c) => c.category !== null)
        .map((c) => ({
          name: c.category!,
          count: c._count.id,
        })),
    });
  } catch (error) {
    console.error('Error fetching categories:', error);
    return NextResponse.json(
      { error: 'Failed to fetch categories' },
      { status: 500 }
    );
  }
}

