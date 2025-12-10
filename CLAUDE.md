# PrintLayoutDesigner

Generates technical diagrams showing print layout specifications for gallery/museum presentations.

## Key Concepts

- **Canvas** (18x24 inches in design mode): The drawing surface for blueprints
- **Print paper** (paper_size in layout JSON): The actual paper being designed for (8.5x11 or 11x14)
- **Layouts** define geometry (positions, dimensions, border widths)
- **Themes** define colors (backgrounds, borders, text)

## Directory Structure

All paths are derived from batch file location. Given `{dir}/batch.json`:
- Layouts: `{dir}/layouts/`
- Themes: `{dir}/themes/`
- Output: `{dir}/output/` (auto-created)

```
production/
  layouts/            # Production layout JSON files
  themes/             # Production theme JSON files
  output/             # Production output (auto-created)
  batch.json          # Production batch configuration
test/
  layouts/            # Test layout JSON files
  themes/             # Test theme JSON files
  output/             # Test output (auto-created)
  batch.json          # Test batch configuration
  assets/             # Test images and text files
palettes/             # Adobe Color CSS files (source for themes)
scripts/              # Utility scripts
```

## Running

```bash
source venv/bin/activate
python PrintLayoutDesigner.py                       # Uses production/batch.json
python PrintLayoutDesigner.py production/batch.json # Explicit production
python PrintLayoutDesigner.py test/batch.json       # Run test batch
```

## Configuration

- **batch.json**: Specifies layout/theme pairs (filenames only), rendering mode, and asset paths
- **layouts/*.json**: Edit to modify geometry (positions, dimensions, border widths)
- **themes/*.json**: Edit to modify colors

See `docs/jsondocs.md` for complete JSON documentation.

## API Functions

For use as an importable module:

```python
from PrintLayoutDesigner import (
    list_layouts,        # Discovery: list available layouts
    list_themes,         # Discovery: list available themes
    get_layout_spec,     # Returns structured dict with geometry and colors
    get_html_template,   # Returns HTML with {{IMAGE}}, {{CAPTION}}, {{NOTE}}, {{FONT_FAMILY}} placeholders
)
```

See `docs/GALLERY_PRINT_INTEGRATION.md` for integration details.

## Utility Scripts

```bash
python scripts/generate_batch.py    # Generate batch.json with random themes
python scripts/import_theme.py      # Import Adobe Color CSS as themes
python scripts/migrate_layouts.py   # Migrate from old layouts.json format
```
