import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/db';

/**
 * این API دیگر استفاده نمی‌شود چون thumbnail از سایت استخراج می‌شود
 * اما برای سازگاری با کدهای قدیمی نگه داشته شده است
 */
export async function POST(request: NextRequest) {
  try {
    const { flyerId } = await request.json();

    if (!flyerId) {
      return NextResponse.json({ error: 'Flyer ID is required' }, { status: 400 });
    }

    // Get flyer from database
    const flyer = await prisma.flyer.findUnique({
      where: { id: flyerId },
    });

    if (!flyer) {
      return NextResponse.json({ error: 'Flyer not found' }, { status: 404 });
    }

    // اگر thumbnailUrl موجود باشد، آن را برمی‌گردانیم
    if (flyer.thumbnailUrl) {
      return NextResponse.json({ 
        success: true, 
        thumbnailUrl: flyer.thumbnailUrl,
        message: 'Thumbnail from website' 
      });
    }

    // اگر thumbnailUrl نبود، پیام خطا برمی‌گردانیم
    // دیگر از PDF thumbnail نمی‌سازیم چون thumbnail باید از سایت استخراج شود
    return NextResponse.json({ 
      error: 'Thumbnail not available. Please ensure thumbnail is scraped from the website.' 
    }, { status: 404 });
  } catch (error) {
    console.error('Error in generate-thumbnail API:', error);
    return NextResponse.json(
      { error: 'Failed to get thumbnail' },
      { status: 500 }
    );
  }
}

