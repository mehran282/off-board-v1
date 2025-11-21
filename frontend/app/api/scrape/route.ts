import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { join } from 'path';

export async function POST() {
  try {
    // Get the parent directory (project root)
    const projectRoot = process.cwd().replace(/\\frontend$/, '').replace(/\/frontend$/, '');
    const scraperPath = join(projectRoot, 'scraper');
    const scriptPath = join(scraperPath, 'scripts', 'scrape_all.py');
    
    // Start the Python scraper process (non-blocking)
    const scraperProcess = spawn('python', [scriptPath], {
      cwd: scraperPath,
      shell: true,
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let output = '';
    let errorOutput = '';

    scraperProcess.stdout?.on('data', (data) => {
      output += data.toString();
    });

    scraperProcess.stderr?.on('data', (data) => {
      errorOutput += data.toString();
    });

    // Wait a bit to see if it starts successfully
    await new Promise(resolve => setTimeout(resolve, 2000));

    return NextResponse.json({
      success: true,
      message: 'Scraping started in background',
      pid: scraperProcess.pid,
      output: output.substring(0, 500), // First 500 chars
      error: errorOutput.substring(0, 500),
    });
  } catch (error: any) {
    console.error('Scraping error:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to start scraping',
        error: error.message || 'Unknown error',
      },
      { status: 500 }
    );
  }
}

