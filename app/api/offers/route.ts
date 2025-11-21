import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const retailerId = searchParams.get('retailerId');
    const category = searchParams.get('category');
    const search = searchParams.get('search');
    const minDiscount = searchParams.get('minDiscount');
    const skip = (page - 1) * limit;

    const where: any = {};

    if (retailerId) {
      where.retailerId = retailerId;
    }

    if (category) {
      where.category = category;
    }

    if (search) {
      where.productName = {
        contains: search,
        mode: 'insensitive',
      };
    }

    if (minDiscount) {
      where.discountPercentage = {
        gte: parseFloat(minDiscount),
      };
    }

    const [offers, total] = await Promise.all([
      prisma.offer.findMany({
        where,
        include: {
          retailer: {
            select: {
              id: true,
              name: true,
              logoUrl: true,
            },
          },
          flyer: {
            select: {
              id: true,
              title: true,
              url: true,
            },
          },
        },
        orderBy: {
          discountPercentage: 'desc',
        },
        skip,
        take: limit,
      }),
      prisma.offer.count({ where }),
    ]);

    return NextResponse.json({
      offers,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching offers:', error);
    return NextResponse.json(
      { error: 'Failed to fetch offers' },
      { status: 500 }
    );
  }
}

