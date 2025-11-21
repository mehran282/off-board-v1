import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const retailerId = searchParams.get('retailerId');
    const skip = (page - 1) * limit;

    const where = retailerId ? { retailerId } : {};

    const [flyers, total] = await Promise.all([
      prisma.flyer.findMany({
        where,
        include: {
          retailer: {
            select: {
              id: true,
              name: true,
              logoUrl: true,
            },
          },
          offers: {
            take: 5,
            select: {
              id: true,
              productName: true,
              currentPrice: true,
              oldPrice: true,
              imageUrl: true,
            },
          },
        },
        orderBy: {
          validUntil: 'desc',
        },
        skip,
        take: limit,
      }),
      prisma.flyer.count({ where }),
    ]);

    return NextResponse.json({
      flyers,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching flyers:', error);
    return NextResponse.json(
      { error: 'Failed to fetch flyers' },
      { status: 500 }
    );
  }
}

