# ABOUTME: Generates batch.json with random theme assignments for all layouts.
# ABOUTME: Ensures all themes are used at least once as both front and back.

import json
import os
import random
import sys


def main():
    # Get all layouts
    layouts = sorted([f.replace('.json', '') for f in os.listdir('layouts') if f.endswith('.json')])

    # Get all themes
    themes = sorted([f.replace('.json', '') for f in os.listdir('themes') if f.endswith('.json')])

    if not layouts:
        print("No layouts found in layouts/")
        print("Run: python migrate_layouts.py")
        sys.exit(1)

    if not themes:
        print("No themes found in themes/")
        print("Run: python import_theme.py")
        sys.exit(1)

    print(f"Layouts: {len(layouts)}")
    print(f"Themes: {len(themes)}")

    # Calculate how many times to repeat themes to cover all layouts
    repeats = (len(layouts) + len(themes) - 1) // len(themes)

    # Create shuffled theme lists for front and back
    front_themes = (themes * repeats)[:len(layouts)]
    back_themes = (themes * repeats)[:len(layouts)]
    random.shuffle(front_themes)
    random.shuffle(back_themes)

    # Load existing batch.json to preserve paths, or create new
    if os.path.exists('batch.json'):
        with open('batch.json', 'r') as f:
            batch_data = json.load(f)
    else:
        batch_data = {
            "mode": "design",
            "image_path_landscape": None,
            "image_path_portrait": None,
            "text_path": None,
            "personal_note_path": None
        }

    # Build batch entries
    batch_entries = []
    for i, layout in enumerate(layouts):
        batch_entries.append({
            "layout": layout,
            "front_theme": front_themes[i],
            "back_theme": back_themes[i]
        })

    batch_data['batch'] = batch_entries

    # Write out
    with open('batch.json', 'w') as f:
        json.dump(batch_data, f, indent=2)

    print(f"\nGenerated {len(batch_entries)} batch entries in batch.json")

    # Verify coverage
    front_used = set(e['front_theme'] for e in batch_entries)
    back_used = set(e['back_theme'] for e in batch_entries)
    print(f"Unique front themes: {len(front_used)}")
    print(f"Unique back themes: {len(back_used)}")


if __name__ == '__main__':
    main()
