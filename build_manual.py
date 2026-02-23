#!/usr/bin/env python3
"""Build Vehicle Forge PDF manual from the DOCX via LibreOffice.

Usage: python3 build_manual.py

Requires:
  - node + docx-js (npm install -g docx) for DOCX generation
  - LibreOffice for DOCX→PDF conversion

The DOCX is the single source of truth for all manual formatting.
The PDF is a pixel-identical derivative.
"""
import subprocess, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: Rebuild DOCX from live HTML data
print("Building DOCX from vehicle-forge.html...")
r = subprocess.run(['node', 'build_docx_manual.js'], capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode != 0:
    print("DOCX build failed:", r.stderr)
    sys.exit(1)

# Step 2: Convert DOCX → PDF via LibreOffice
print("Converting DOCX → PDF...")
r = subprocess.run([
    'python3', '/mnt/skills/public/docx/scripts/office/soffice.py',
    '--headless', '--convert-to', 'pdf', 'vehicle-forge-manual.docx'
], capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode != 0:
    print("PDF conversion failed:", r.stderr)
    sys.exit(1)

size = os.path.getsize('vehicle-forge-manual.pdf')
print(f"Vehicle Forge Companion Guide: {size:,} bytes")
