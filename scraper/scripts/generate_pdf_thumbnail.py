#!/usr/bin/env python3
"""Generate thumbnail from PDF first page"""
import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from pdf2image import convert_from_path
    from PIL import Image
    import requests
except ImportError:
    print(json.dumps({"error": "Required packages not installed: pdf2image, Pillow, requests"}))
    sys.exit(1)


def generate_thumbnail(pdf_url: str, flyer_id: str) -> dict:
    """Generate thumbnail from PDF first page"""
    try:
        # Download PDF
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        # Save PDF temporarily (use tempfile for cross-platform)
        temp_dir = tempfile.gettempdir()
        temp_pdf_path = os.path.join(temp_dir, f"flyer_{flyer_id}.pdf")
        with open(temp_pdf_path, 'wb') as f:
            f.write(response.content)
        
        # Convert first page to image
        # Try to find poppler path (common locations)
        poppler_path = None
        if os.name == 'nt':  # Windows
            # Common poppler paths on Windows
            localappdata = os.environ.get('LOCALAPPDATA', '')
            possible_paths = [
                os.path.join(localappdata, 'poppler', 'poppler-24.08.0', 'Library', 'bin'),
                os.path.join(localappdata, 'poppler', 'Library', 'bin'),
                os.path.join(localappdata, 'poppler', 'bin'),
                r'C:\poppler\Library\bin',
                r'C:\Program Files\poppler\bin',
                r'C:\Program Files (x86)\poppler\bin',
            ]
            for path in possible_paths:
                pdftoppm_exe = os.path.join(path, 'pdftoppm.exe')
                if os.path.exists(path) and os.path.exists(pdftoppm_exe):
                    poppler_path = path
                    break
        
        try:
            if poppler_path:
                images = convert_from_path(temp_pdf_path, first_page=1, last_page=1, dpi=150, poppler_path=poppler_path)
            else:
                # Try without path first (if poppler is in PATH)
                images = convert_from_path(temp_pdf_path, first_page=1, last_page=1, dpi=150)
        except Exception as e:
            error_msg = str(e)
            if "poppler" in error_msg.lower() or "pdftoppm" in error_msg.lower():
                return {"error": f"Poppler not found. Please install poppler. Searched paths: {possible_paths if os.name == 'nt' else 'N/A'}"}
            return {"error": f"Failed to convert PDF: {error_msg}"}
        
        if not images:
            return {"error": "Failed to convert PDF to image"}
        
        # Resize image to thumbnail size (max 800px width, maintain aspect ratio)
        img = images[0]
        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save thumbnail
        thumbnail_dir = Path(__file__).parent.parent.parent / "frontend" / "public" / "thumbnails"
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        
        thumbnail_path = thumbnail_dir / f"{flyer_id}.jpg"
        img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
        
        # Clean up temp PDF
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        
        # Return thumbnail URL
        thumbnail_url = f"/thumbnails/{flyer_id}.jpg"
        return {"thumbnailUrl": thumbnail_url}
        
    except Exception as e:
        error_msg = str(e)
        # Provide helpful error messages
        if "poppler" in error_msg.lower() or "pdftoppm" in error_msg.lower():
            error_msg = "Poppler is not installed. Please install poppler-utils. On Windows, download from: https://github.com/oschwartz10612/poppler-windows/releases"
        return {"error": error_msg}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: generate_pdf_thumbnail.py <pdf_url> <flyer_id>"}))
        sys.exit(1)
    
    pdf_url = sys.argv[1]
    flyer_id = sys.argv[2]
    
    result = generate_thumbnail(pdf_url, flyer_id)
    print(json.dumps(result))
    
    if "error" in result:
        sys.exit(1)

