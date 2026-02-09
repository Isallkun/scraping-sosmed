"""
Script to organize output files into proper folders
Moves old output files to platform-specific folders
"""

import os
import sys
import shutil
from pathlib import Path
import json

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def organize_outputs():
    """Organize output files into platform folders"""
    print("📂 Organizing output files...")
    print("=" * 70)

    output_dir = Path("output")

    if not output_dir.exists():
        print("❌ Output directory not found")
        return

    # Create platform folders
    platforms = {
        'instagram': output_dir / 'instagram',
        'twitter': output_dir / 'twitter',
        'facebook': output_dir / 'facebook',
        'sentiment': output_dir / 'sentiment',
        'other': output_dir / 'other'
    }

    for platform_dir in platforms.values():
        platform_dir.mkdir(exist_ok=True)

    # Get all JSON files in output root
    json_files = list(output_dir.glob('*.json'))

    moved_count = 0

    for file_path in json_files:
        try:
            # Determine platform from filename or content
            platform = None

            if 'instagram' in file_path.name:
                platform = 'instagram'
            elif 'twitter' in file_path.name:
                platform = 'twitter'
            elif 'facebook' in file_path.name:
                platform = 'facebook'
            elif 'sentiment' in file_path.name:
                platform = 'sentiment'
            else:
                # Try to read file and determine from metadata
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'metadata' in data and 'platform' in data['metadata']:
                            platform = data['metadata']['platform']
                except:
                    platform = 'other'

            if platform:
                dest_dir = platforms.get(platform, platforms['other'])
                dest_path = dest_dir / file_path.name

                # Avoid overwriting
                counter = 1
                while dest_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                shutil.move(str(file_path), str(dest_path))
                print(f"✓ Moved: {file_path.name} -> {platform}/{dest_path.name}")
                moved_count += 1

        except Exception as e:
            print(f"✗ Error moving {file_path.name}: {e}")

    print()
    print("=" * 70)
    print(f"✅ Organization complete! Moved {moved_count} files")
    print()
    print("Folder structure:")
    for platform, path in platforms.items():
        file_count = len(list(path.glob('*.json')))
        if file_count > 0:
            print(f"  📁 {platform}: {file_count} files")

if __name__ == "__main__":
    organize_outputs()
