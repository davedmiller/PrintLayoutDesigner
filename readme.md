# PrintLayoutDesigner

A Python tool that generates print layouts for gallery photography with technical blueprint diagrams.

## Purpose

PrintLayoutDesigner creates two-sided print layouts (front with image + caption, back with personal note) and generates technical blueprint diagrams showing precise dimensions for printing and framing.

## Features

- **Separate layouts and themes**: Geometry (layouts) and colors (themes) are defined in separate JSON files
- **Batch processing**: Generate multiple layouts with different theme combinations
- **HTML output**: Print-ready HTML layouts for browser viewing/printing
- **Blueprint diagrams**: Technical PNG diagrams with dimension annotations
- **API for integration**: Can be imported as a module by other Python projects

## Directory Structure

```
PrintLayoutDesigner/
├── PrintLayoutDesigner.py    # Main script
├── batch.json                # Batch configuration (what to generate)
├── layouts/                  # Layout JSON files (geometry)
├── themes/                   # Theme JSON files (colors)
├── production/               # Production layouts and themes
│   ├── layouts/
│   └── themes/
├── test/                     # Test layouts and assets
│   ├── layouts/
│   ├── assets/
│   └── batch.json
├── output/                   # Generated output
└── docs/                     # Documentation
```

## Installation

```bash
pip install matplotlib markdown
```

## Usage

### Command Line

```bash
# Generate from default batch.json
python PrintLayoutDesigner.py

# Generate from specific batch file
python PrintLayoutDesigner.py path/to/batch.json
```

### As a Module (API)

```python
from PrintLayoutDesigner import (
    list_layouts,
    list_themes,
    get_layout_spec,
    get_html_template,
)

# Discover available layouts and themes
layouts = list_layouts('/path/to/production')
themes = list_themes('/path/to/production')

# Get structured layout specification
spec = get_layout_spec(
    layout_name='01_ClassicMuseum_Land_8-5x11',
    front_theme_name='Christmas_light',
    back_theme_name='simple_light',
    base_dir='/path/to/production'
)

# Get HTML template with placeholders
template = get_html_template(
    layout_name='01_ClassicMuseum_Land_8-5x11',
    front_theme_name='Christmas_light',
    back_theme_name='simple_light',
    base_dir='/path/to/production'
)
# Returns HTML with {{IMAGE}}, {{CAPTION}}, {{NOTE}}, {{FONT_FAMILY}} placeholders
```

## Configuration

### batch.json

Controls what gets generated:

```json
{
  "mode": "design",
  "show_blueprints": true,
  "image_path_landscape": "/path/to/landscape.jpg",
  "image_path_portrait": "/path/to/portrait.jpg",
  "text_path": "/path/to/caption.md",
  "personal_note_path": "/path/to/note.md",
  "batch": [
    {
      "layout": "01_ClassicMuseum_Land_8-5x11.json",
      "front_theme": "Christmas_light.json",
      "back_theme": "simple_light.json"
    }
  ]
}
```

### Layouts (layouts/*.json)

Define geometry: paper size, image/caption positions and dimensions, border widths, text alignment.

### Themes (themes/*.json)

Define colors: paper background, borders, caption background, font colors.

See `docs/jsondocs.md` for complete JSON schema documentation.

## Utility Scripts

```bash
python scripts/generate_batch.py    # Generate batch.json with random theme combinations
python scripts/import_theme.py      # Import Adobe Color CSS as themes
python scripts/migrate_layouts.py   # Migrate from old layouts format
```

## Output

- **HTML files**: Print-ready layouts viewable in browser
- **Blueprint PNGs**: Technical diagrams with dimension annotations
- **all.html**: Combined view of all generated layouts

## Documentation

- `docs/jsondocs.md` - JSON schema for layouts and themes
- `docs/GALLERY_PRINT_INTEGRATION.md` - Integration guide for PostCardMaker
