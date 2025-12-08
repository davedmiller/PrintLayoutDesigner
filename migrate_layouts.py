# ABOUTME: Migrates layouts.json to new architecture with individual layout files.
# ABOUTME: Creates layouts/*.json geometry files and batch.json master file.

import json
import os
import re

def extract_border_width(style_obj, key='border'):
    """Extract border width from style object, handling null values."""
    if style_obj is None:
        return None
    border = style_obj.get(key)
    if border is None:
        return None
    return border.get('width')

def sanitize_filename(name):
    """Convert layout name to safe filename."""
    # Remove file extension if present
    name = re.sub(r'\.png$', '', name)
    return name

def migrate_layout(layout):
    """Extract geometry-only data from a layout definition."""
    # Derive layout name from file field
    name = sanitize_filename(layout['file'])

    # Extract front border widths from style objects
    paper_border_width = extract_border_width(layout.get('paper_style'))
    img_border_width = extract_border_width(layout.get('img_style'))
    caption_border_width = extract_border_width(layout.get('caption_style'))

    # Extract back border widths
    back_paper_border_width = extract_border_width(layout.get('back_paper_style'))
    back_note_border_width = extract_border_width(layout.get('back_note_style'))

    # Calculate default back note dimensions if not specified
    paper_size = layout['paper_size']
    back_note_dims = layout.get('back_note_dims')
    if back_note_dims is None:
        # Default: 6" x 9" for 8.5x11, 7" x 10" for 11x14
        if paper_size['width'] == 8.5:
            back_note_dims = {"width": 6, "height": 9}
        else:
            back_note_dims = {"width": 7, "height": 10}

    return {
        "name": name,
        "title": layout.get('title', name),
        "paper_size": paper_size,
        "front": {
            "img_dims": layout['img_dims'],
            "img_pos": layout['img_pos'],
            "caption_dims": layout['caption_dims'],
            "caption_pos": layout['caption_pos'],
            "special": layout.get('special'),
            "gutter": layout.get('gutter'),
            "border_widths": {
                "paper": paper_border_width,
                "img": img_border_width,
                "caption": caption_border_width
            }
        },
        "back": {
            "note_dims": back_note_dims,
            "note_pos": "centered",
            "border_widths": {
                "paper": back_paper_border_width,
                "note": back_note_border_width
            }
        },
        "notes": layout.get('notes')
    }

def main():
    # Read current layouts.json
    with open('layouts.json', 'r') as f:
        data = json.load(f)

    # Create layouts directory if needed
    os.makedirs('layouts', exist_ok=True)

    # Migrate each layout to individual file
    layout_names = []
    for layout in data['layouts']:
        migrated = migrate_layout(layout)
        filename = f"layouts/{migrated['name']}.json"

        with open(filename, 'w') as f:
            json.dump(migrated, f, indent=2)

        print(f"Created: {filename}")
        layout_names.append(migrated['name'])

    # Create batch.json with globals
    batch = {
        "mode": data.get('mode', 'design'),
        "image_path_landscape": data.get('image_path_landscape'),
        "image_path_portrait": data.get('image_path_portrait'),
        "text_path": data.get('text_path'),
        "personal_note_path": data.get('personal_note_path'),
        "batch": []  # Empty batch list - user will populate
    }

    with open('batch.json', 'w') as f:
        json.dump(batch, f, indent=2)

    print(f"\nCreated: batch.json")
    print(f"\nMigrated {len(layout_names)} layouts to layouts/")
    print("\nTo use a layout, add entries to batch.json like:")
    print(json.dumps({
        "layout": layout_names[0],
        "front_theme": "theme_name_light",
        "back_theme": "theme_name_light"
    }, indent=2))

if __name__ == '__main__':
    main()
