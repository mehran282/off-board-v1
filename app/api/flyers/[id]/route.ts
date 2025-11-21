import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/db';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    const flyer = await prisma.flyer.findUnique({
      where: { id },
      include: {
        retailer: true,
        offers: {
          include: {
            product: true,
          },
          orderBy: {
            discountPercentage: 'desc',
          },
        },
      },
    });

    if (!flyer) {
      return NextResponse.json(
        { error: 'Flyer not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ flyer });
  } catch (error) {
    console.error('Error fetching flyer:', error);
    return NextResponse.json(
      { error: 'Failed to fetch flyer' },
      { status: 500 }
    );
  }
}

