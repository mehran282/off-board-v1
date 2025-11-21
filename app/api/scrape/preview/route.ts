import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';

const execAsync = promisify(exec);

export async function GET() {
  try {
    // Get project root
    const projectRoot = process.cwd().replace(/\\frontend$/, '').replace(/\/frontend$/, '');
    const scraperPath = join(projectRoot, 'scraper');
    const scriptPath = join(scraperPath, 'scripts', 'preview.py');

    // Execute Python script
    const { stdout, stderr } = await execAsync(`python ${scriptPath}`, {
      cwd: scraperPath,
      timeout: 60000,
    });

    if (stderr && !stdout) {
      throw new Error(stderr);
    }

    const result = JSON.parse(stdout.trim());
    
    // Convert hex to base64 if needed
    if (result.success && result.screenshot) {
      if (typeof result.screenshot === 'string' && !result.screenshot.startsWith('data:')) {
        // Assume it's hex, convert to base64
        const buffer = Buffer.from(result.screenshot, 'hex');
        result.screenshot = buffer.toString('base64');
      }
    }
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error fetching preview:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
