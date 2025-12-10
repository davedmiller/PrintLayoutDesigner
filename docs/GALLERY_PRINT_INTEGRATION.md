# Gallery Print Integration Guide

This document explains how to integrate PrintLayoutDesigner with PostCardMaker's "Gallery Print" feature.

## Overview

PrintLayoutDesigner provides:
- **Layouts**: JSON files defining geometry (positions, dimensions, borders)
- **Themes**: JSON files defining colors (backgrounds, borders, text)
- **API functions**: For discovering and using layouts/themes programmatically

PostCardMaker's Gallery Print feature can use these to generate print-ready PDF layouts.

## Project Location

PrintLayoutDesigner is located at:
```
/Users/dave/Documents/ClaudeApps/PrintLayoutDesigner
```

PostCardMaker can reference it as a sibling directory:
```
../PrintLayoutDesigner
```

## API Functions

### Importing

```python
import sys
sys.path.insert(0, '../PrintLayoutDesigner')

from PrintLayoutDesigner import (
    list_layouts,
    list_themes,
    get_layout_spec,
    get_html_template,
)
```

### Discovery Functions

```python
# List available layouts
layouts = list_layouts('/path/to/production')
# Returns: [{'name': '01_ClassicMuseum_Land_8-5x11', 'title': 'Classic Museum - Landscape', 'paper_size': {'width': 8.5, 'height': 11}}, ...]

# List available themes
themes = list_themes('/path/to/production')
# Returns: [{'name': 'Christmas_light', 'mode': 'light'}, ...]
```

### Option A: HTML Template with Placeholders

Use this when you want PrintLayoutDesigner to generate the HTML structure and you just fill in content:

```python
template = get_html_template(
    layout_name='01_ClassicMuseum_Land_8-5x11',
    front_theme_name='Christmas_light',
    back_theme_name='simple_light',
    base_dir='/path/to/production'
)

# Template contains placeholders:
# {{IMAGE}} - Replace with your image element
# {{CAPTION}} - Replace with caption HTML
# {{NOTE}} - Replace with personal note HTML
# {{FONT_FAMILY}} - Replace with WeasyPrint-compatible font

html = template.replace('{{IMAGE}}', my_image_html)
html = html.replace('{{CAPTION}}', my_processed_caption)
html = html.replace('{{NOTE}}', my_processed_note)
html = html.replace('{{FONT_FAMILY}}', 'DejaVu Sans, sans-serif')
```

### Option B: Layout Specification

Use this when you want full control over HTML generation:

```python
spec = get_layout_spec(
    layout_name='01_ClassicMuseum_Land_8-5x11',
    front_theme_name='Christmas_light',
    back_theme_name='simple_light',
    base_dir='/path/to/production'
)

# spec structure:
{
    'paper': {'width': 8.5, 'height': 11},
    'front': {
        'image': {'width': 6, 'height': 4, 'left': 1.25, 'top': 2, 'border_width': 0.125},
        'caption': {'width': 6, 'height': 1.75, 'left': 1.25, 'top': 7.0, 'border_width': 0},
        'paper_border_width': 0.75,
        'special': None,  # or 'double_col' for two-column caption
        'gutter': None,   # column gap in inches (for double_col)
        'colors': {
            'paper_bg': '#F2F2F2',
            'paper_border': '#A69F3C',
            'image_bg': '#F22E2E',
            'image_border': '#D93829',
            'caption_bg': '#F22E2E',
            'caption_border': '#D93829',
            'font': '#537334',
        },
        'text': {
            'align_h': 'left',  # left, center, right, justify
            'align_v': 'top',   # top, middle, bottom
            'font': 'Georgia, serif',
            'size': 10,
        },
    },
    'back': {
        'note': {'width': 6, 'height': 9, 'pos': 'centered', 'border_width': 0.0625},
        'paper_border_width': 0.5,
        'colors': {...},
        'text': {...},
    },
}

# Build your own HTML using these dimensions and colors
```

## Considerations for PostCardMaker

### Font Handling

WeasyPrint has specific font requirements. Options:

1. **Replace `{{FONT_FAMILY}}`** in the template with WeasyPrint-compatible fonts
2. **Add `@font-face` declarations** to the HTML head
3. **Use system fonts** that WeasyPrint can access

Common safe fonts:
- `DejaVu Sans, sans-serif`
- `DejaVu Serif, serif`
- `Liberation Sans, sans-serif`

### Emoji Handling

PrintLayoutDesigner uses Unicode emoji in its sample content. PostCardMaker should:

1. **Pre-process content** to convert emoji to `<img>` tags before inserting into placeholders
2. **Use the template approach** (Option A) so emoji replacement happens at the content level

Example:
```python
# PostCardMaker processes emoji before insertion
caption_with_img_emoji = convert_emoji_to_images(raw_caption)
html = template.replace('{{CAPTION}}', caption_with_img_emoji)
```

### Image Embedding

The template's `{{IMAGE}}` placeholder expects an HTML element. Options:

1. **File path**: `<img src="file:///path/to/image.jpg" alt="Photo">`
2. **Base64**: `<img src="data:image/jpeg;base64,..." alt="Photo">`
3. **Custom element**: Whatever PostCardMaker uses for WeasyPrint

### Paper Sizes

Available paper sizes in production layouts:
- **8.5" x 11"** (Letter) - most common
- **11" x 14"** - large format

Check `paper_size` in the layout spec or list_layouts() output.

### Two-Column Layouts

Some layouts have `special: 'double_col'` for two-column captions. The template handles this with CSS `column-count: 2`. The `gutter` value specifies the gap between columns.

## Testing

Run the API test script:
```bash
cd /path/to/PrintLayoutDesigner
python test/test_api.py
```

This verifies:
- Discovery functions find layouts and themes
- `get_layout_spec()` returns valid structure
- `get_html_template()` contains expected placeholders
- Template renders visually (writes to `test/output/template_test.html`)

## File Locations

- **Production layouts**: `PrintLayoutDesigner/production/layouts/`
- **Production themes**: `PrintLayoutDesigner/production/themes/`
- **Test layouts**: `PrintLayoutDesigner/test/layouts/`
- **JSON schema docs**: `PrintLayoutDesigner/docs/jsondocs.md`
