# JSON Configuration Documentation

PrintLayoutDesigner uses three types of JSON files:
- **batch.json** - Controls what gets generated (in `production/` or `test/`)
- **layouts/*.json** - Layout geometry definitions
- **themes/*.json** - Color themes

## Directory Structure

All paths are derived from the batch file location. Given `{dir}/batch.json`:
- Layouts: `{dir}/layouts/`
- Themes: `{dir}/themes/`
- Output: `{dir}/output/`

```
production/
  layouts/       # Production layouts
  themes/        # Production themes
  output/        # Production output (auto-created)
  batch.json     # Production batch file
test/
  layouts/       # Test layouts
  themes/        # Test themes
  output/        # Test output (auto-created)
  batch.json     # Test batch file
```

## batch.json

Controls which layouts to generate and with which themes.

### Root Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | string | No | Rendering mode: `"design"` or `"print"` (default: `"design"`) |
| `image_path_landscape` | string | No | Path to sample image for landscape layouts (img_w > img_h) |
| `image_path_portrait` | string | No | Path to sample image for portrait layouts (img_h >= img_w) |
| `text_path` | string | No | Path to sample text file for captions |
| `personal_note_path` | string | No | Path to personal note text file for back sides |
| `batch` | array | Yes | Array of batch entry objects |

### Batch Entry Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `layout` | string | Yes | Layout filename (e.g., `"01_ClassicMuseum.json"`) |
| `front_theme` | string | Yes | Theme filename for front side |
| `back_theme` | string | Yes | Theme filename for back side |

### Example batch.json

```json
{
  "mode": "design",
  "image_path_landscape": "/path/to/landscape.tif",
  "image_path_portrait": "/path/to/portrait.tif",
  "text_path": "/path/to/caption.md",
  "personal_note_path": "/path/to/note.md",
  "batch": [
    {
      "layout": "01_ClassicMuseum_Land_8-5x11.json",
      "front_theme": "Christmas_light.json",
      "back_theme": "Christmas_dark.json"
    }
  ]
}
```

---

## Layout Files (layouts/*.json)

Each layout file defines geometry only - no colors. Colors come from themes.

### Layout Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Layout identifier (matches filename) |
| `title` | string | Yes | Display name for title block |
| `paper_size` | object | Yes | Paper dimensions (see Dimensions Object) |
| `front` | object | Yes | Front side geometry |
| `back` | object | Yes | Back side geometry |
| `notes` | string | Yes | Installation notes for title block |

### Front Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `img_dims` | object | Yes | Image dimensions |
| `img_pos` | object | Yes | Image position |
| `caption_dims` | object | Yes | Caption dimensions |
| `caption_pos` | object | Yes | Caption position |
| `special` | string | No | Special mode: `"double_col"` for two-column caption |
| `gutter` | number | No | Gutter width between columns (inches) |
| `border_widths` | object | Yes | Border widths for front elements |

### Front Border Widths Object

| Field | Type | Description |
|-------|------|-------------|
| `paper` | number | Paper border width in inches |
| `img` | number | Image border width in inches |
| `caption` | number or null | Caption border width (null = no border) |

### Back Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `note_dims` | object | Yes | Note area dimensions |
| `note_pos` | string | Yes | Position: `"centered"` |
| `border_widths` | object | Yes | Border widths for back elements |

### Back Border Widths Object

| Field | Type | Description |
|-------|------|-------------|
| `paper` | number | Paper border width in inches |
| `note` | number | Note area border width in inches |

### Dimensions Object

| Field | Type | Description |
|-------|------|-------------|
| `width` | number | Width in inches |
| `height` | number | Height in inches |

### Position Object

| Field | Type | Description |
|-------|------|-------------|
| `left` | number | Distance from left edge of paper (inches) |
| `top` | number | Distance from top edge of paper (inches) |

### Example Layout File

```json
{
  "name": "01_ClassicMuseum_Land_8-5x11",
  "title": "Classic Museum - Landscape",
  "paper_size": {
    "width": 8.5,
    "height": 11
  },
  "front": {
    "img_dims": {"width": 6, "height": 4},
    "img_pos": {"left": 1.25, "top": 2},
    "caption_dims": {"width": 6, "height": 1.75},
    "caption_pos": {"left": 1.25, "top": 7.0},
    "special": null,
    "gutter": null,
    "border_widths": {
      "paper": 0.75,
      "img": 0.125,
      "caption": null
    }
  },
  "back": {
    "note_dims": {"width": 6, "height": 9},
    "note_pos": "centered",
    "border_widths": {
      "paper": 0.5,
      "note": 0.0625
    }
  },
  "notes": "Layout: Classic Museum\nPaper: 8-5x11\nOrientation: Landscape Img"
}
```

---

## Theme Files (themes/*.json)

Themes define colors and how they map to layout elements.

### Theme Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Theme name |
| `source` | string | No | Color source (e.g., `"adobe-color"`) |
| `mode` | string | Yes | `"light"` or `"dark"` |
| `colors` | object | Yes | Color palette |
| `styles` | object | Yes | Color role mappings |

### Colors Object

| Field | Type | Description |
|-------|------|-------------|
| `background` | string | Hex color for backgrounds |
| `base` | string | Hex color for primary elements |
| `secondary` | string | Hex color for secondary elements |
| `accent` | string | Hex color for accent/highlight |
| `text` | string | Hex color for text |

### Styles Object

Maps color roles to layout elements.

| Field | Type | Description |
|-------|------|-------------|
| `paper_background` | string | Color role for paper fill |
| `paper_border` | string | Color role for paper border |
| `img_background` | string | Color role for image box fill |
| `img_border` | string | Color role for image box border |
| `caption_background` | string | Color role for caption box fill |
| `caption_border` | string | Color role for caption box border |
| `note_background` | string | Color role for note area fill |
| `note_border` | string | Color role for note area border |
| `font_color` | string | Color role for text |

### Example Theme File

```json
{
  "name": "Christmas",
  "source": "adobe-color",
  "mode": "light",
  "colors": {
    "background": "#F2F2F2",
    "base": "#A69F3C",
    "secondary": "#F22E2E",
    "accent": "#D93829",
    "text": "#537334"
  },
  "styles": {
    "paper_background": "background",
    "paper_border": "base",
    "img_background": "secondary",
    "img_border": "accent",
    "caption_background": "secondary",
    "caption_border": "accent",
    "note_background": "secondary",
    "note_border": "accent",
    "font_color": "text"
  }
}
```

---

## Rendering Modes

| Mode | Canvas Size | Description |
|------|-------------|-------------|
| `design` | 18" x 24" | Full blueprint with dimension lines, title block, and labels |
| `print` | paper size | Paper-sized output for print-ready templates |

### Mode Comparison

| Element | design | print |
|---------|--------|-------|
| Canvas size | 18" x 24" | paper_size dimensions |
| Canvas border | Yes | No |
| Dimension lines | Yes | No |
| Title block | Yes | No |
| Box labels | Yes | No |
| Paper with styles | Yes | Yes |
| Image box with styles | Yes | Yes |
| Caption box with styles | Yes | Yes |

---

## Output Files

Each batch entry generates two PNG files:

```
{layout}_front_{theme}.png
{layout}_back_{theme}.png
```

Example:
```
01_ClassicMuseum_Land_8-5x11_front_Christmas_light.png
01_ClassicMuseum_Land_8-5x11_back_Christmas_dark.png
```

Files are written to `{dir}/output/` where `{dir}` is the directory containing the batch.json file. The output directory is created automatically if it doesn't exist.

---

## Border Behavior

- **Paper borders**: Drawn INSIDE the paper edge (inset, like a mat)
- **Image/caption/note borders**: Drawn OUTSIDE the box

---

## Utility Scripts

Scripts in `scripts/` directory:

| Script | Purpose |
|--------|---------|
| `generate_batch.py` | Generate batch.json with random theme assignments |
| `import_theme.py` | Import Adobe Color CSS palettes as theme files |
| `migrate_layouts.py` | Migrate from old layouts.json format |
