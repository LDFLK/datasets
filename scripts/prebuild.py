#!/usr/bin/env python3
"""
Prebuild orchestrator for Docusaurus site.
Runs all generators and copies necessary files.
Note: Data files are served directly via staticDirectories config.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_script(script_name: str, script_dir: Path) -> bool:
    """Run a Python script and return success status"""
    script_path = script_dir / script_name
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_dir.parent),
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False


def copy_assets(project_root: Path) -> bool:
    """Copy assets from docs/assets to website/static"""
    print(f"\n{'='*60}")
    print("Copying assets...")
    print('='*60)

    # Copy images
    src_images = project_root / "docs" / "assets" / "images"
    dst_images = project_root / "website" / "static" / "img"

    if src_images.exists():
        dst_images.mkdir(parents=True, exist_ok=True)
        for item in src_images.iterdir():
            if item.is_file():
                shutil.copy2(item, dst_images / item.name)
                print(f"  Copied {item.name} to static/img/")

    # Copy documents
    src_docs = project_root / "docs" / "assets" / "documents"
    dst_docs = project_root / "website" / "static" / "documents"

    if src_docs.exists():
        dst_docs.mkdir(parents=True, exist_ok=True)
        for item in src_docs.iterdir():
            if item.is_file():
                shutil.copy2(item, dst_docs / item.name)
                print(f"  Copied {item.name} to static/documents/")

    return True


def copy_existing_downloads(project_root: Path) -> bool:
    """Copy existing ZIP downloads if they exist"""
    print(f"\n{'='*60}")
    print("Checking for existing downloads...")
    print('='*60)

    src = project_root / "docs" / "downloads"
    dst = project_root / "website" / "static" / "downloads"

    if src.exists():
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.is_file() and item.suffix == '.zip':
                dst_file = dst / item.name
                if not dst_file.exists():
                    shutil.copy2(item, dst_file)
                    print(f"  Copied {item.name}")
                else:
                    print(f"  Skipped {item.name} (already exists)")

    return True


def main():
    """Main prebuild orchestrator"""
    print("="*60)
    print("PREBUILD ORCHESTRATOR")
    print("="*60)

    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    success = True

    # 1. Generate dataset index for React
    if not run_script("generate_data_index.py", script_dir):
        print("Warning: generate_data_index.py failed")
        success = False

    # 2. Generate ZIP files
    if not run_script("update_dataset_index.py", script_dir):
        print("Warning: update_dataset_index.py failed")
        success = False

    # 3. Copy assets (images, documents)
    if not copy_assets(project_root):
        print("Warning: Failed to copy assets")
        success = False

    # 5. Copy existing downloads
    copy_existing_downloads(project_root)

    # Note: Data files are served directly from ../data via staticDirectories

    print(f"\n{'='*60}")
    if success:
        print("PREBUILD COMPLETED SUCCESSFULLY")
    else:
        print("PREBUILD COMPLETED WITH WARNINGS")
    print("="*60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
