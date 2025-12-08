# Plan: Theme Architecture with Adobe Color Integration

## Goal
Separate color/style information from layout geometry. Import color palettes from Adobe Color CSS exports and auto-map colors to semantic roles based on computed properties (lightness, contrast).

## Architecture Overview

```
batch.json                  # Global settings + batch list (master file)
palettes/                   # Adobe Color CSS files (user drops files here)
  CLEAN-LOOK-x-DG.css
  simple-grayscale.css
themes/                     # Generated theme JSONs (light + dark per palette)
  CLEAN-LOOK-x-DG_light.json
  CLEAN-LOOK-x-DG_dark.json
  simple-grayscale_light.json
  simple-grayscale_dark.json
layouts/                    # Geometry only (positions, dimensions)
  ClassicMuseum_Land_8-5x11.json
  ClassicMuseum_Port_8-5x11.json
```

## Adobe Color CSS Import

**Input format (CSS from Adobe Color):**
```css
/* Color Theme Swatches in Hex */
.CLEAN-LOOK-x-DG-1-hex { color: #D98B48; }
.CLEAN-LOOK-x-DG-2-hex { color: #A6634B; }
.CLEAN-LOOK-x-DG-3-hex { color: #D9A38F; }
.CLEAN-LOOK-x-DG-4-hex { color: #BF5A50; }
.CLEAN-LOOK-x-DG-5-hex { color: #F2F2F2; }
```

**Parsing:** Extract theme name from class prefix, extract 5 hex values via regex.

## Color Role Assignment Algorithm

Given 5 colors, compute and assign semantic roles based on `mode`:

### Light Mode (mode: "light") - default
1. **base** = Adobe index 3 (middle color, typically the "key" color)
2. **background** = lightest color (max luminance)
3. **text** = highest contrast to background (darkest)
4. **secondary** = lighter of the remaining two
5. **accent** = darker of the remaining two

### Dark Mode (mode: "dark")
1. **base** = Adobe index 3 (middle color, typically the "key" color)
2. **background** = darkest color (min luminance)
3. **text** = highest contrast to background (lightest)
4. **secondary** = darker of the remaining two
5. **accent** = lighter of the remaining two

### WCAG Relative Luminance

The WCAG (Web Content Accessibility Guidelines) formula accounts for gamma correction in sRGB, providing perceptually accurate lightness values:

```python
def relative_luminance(hex_color):
    """WCAG relative luminance (0-1 scale, perceptually weighted)"""
    r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)]

    # Apply gamma correction (sRGB to linear)
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

    return 0.2126 * r + 0.7152 * g + 0.0722 * b
```

### WCAG Contrast Ratio

Contrast ratio ranges from 1:1 (identical) to 21:1 (black/white). WCAG recommends 4.5:1 minimum for normal text.

```python
def contrast_ratio(color1, color2):
    """WCAG contrast ratio (1:1 to 21:1)"""
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
```

### Assignment Process

```python
def assign_roles(colors, mode="light"):
    """Assign semantic roles to 5 colors based on mode."""
    base = colors[2]  # index 3 in 1-based = index 2 in 0-based

    if mode == "light":
        # Background = lightest
        background = max(colors, key=relative_luminance)
    else:  # dark mode
        # Background = darkest
        background = min(colors, key=relative_luminance)

    # Text = highest contrast to background
    remaining = [c for c in colors if c != background]
    text = max(remaining, key=lambda c: contrast_ratio(c, background))

    # Remaining two become secondary and accent
    remaining = [c for c in remaining if c not in [base, text]]
    if len(remaining) == 2:
        if mode == "light":
            # Light mode: secondary=lighter, accent=darker
            secondary = max(remaining, key=relative_luminance)
            accent = min(remaining, key=relative_luminance)
        else:
            # Dark mode: secondary=darker, accent=lighter
            secondary = min(remaining, key=relative_luminance)
            accent = max(remaining, key=relative_luminance)
    elif len(remaining) == 1:
        secondary = remaining[0]
        accent = base  # fallback

    return {
        "background": background,
        "base": base,
        "secondary": secondary,
        "accent": accent,
        "text": text
    }
```

## Theme JSON Structure

One theme = one Adobe Color palette = one set of 5 colors. For different front/back palettes, use two different theme files.

```json
{
  "name": "CLEAN-LOOK-x-DG",
  "source": "adobe-color",
  "mode": "light",
  "colors": {
    "background": "#F2F2F2",
    "base": "#D9A38F",
    "secondary": "#D98B48",
    "accent": "#BF5A50",
    "text": "#A6634B"
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

When rendering:
- **Front** uses `front_theme.colors` + styles for: `paper_background`, `paper_border`, `img_background`, `img_border`, `caption_background`, `caption_border`, `font_color`
- **Back** uses `back_theme.colors` + styles for: `paper_background`, `paper_border`, `note_background`, `note_border`, `font_color`

Example: Use `CLEAN-LOOK-x-DG` for front (colorful) and `simple-grayscale` for back (minimal ink). Each is a separate theme file with its own colors.

The `mode` field controls color role assignment:
- `"light"` (default): lightest color → background, secondary lighter than accent
- `"dark"`: darkest color → background, secondary darker than accent

Specify mode when importing: `python import_theme.py palette.css --mode dark`
Or edit the theme JSON directly after import.

## Layout JSON Structure (Geometry Only)

```json
{
  "name": "ClassicMuseum_Land",
  "paper_size": {"width": 8.5, "height": 11},
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
      "paper": null,
      "note": 0.0625
    }
  }
}
```

Paper size applies to both sides. The `note_pos: "centered"` is the default; could also specify `{"left": x, "top": y}` for custom positioning.

## batch.json Structure (Master File)

```json
{
  "mode": "design",
  "image_path_landscape": "/path/to/landscape.tif",
  "image_path_portrait": "/path/to/portrait.tif",
  "text_path": "/path/to/lorem.md",
  "personal_note_path": "/path/to/note.md",
  "batch": [
    {
      "layout": "ClassicMuseum_Land",
      "front_theme": "CLEAN-LOOK-x-DG",
      "back_theme": "simple-grayscale"
    },
    {
      "layout": "ClassicMuseum_Port",
      "front_theme": "CLEAN-LOOK-x-DG",
      "back_theme": "simple-grayscale"
    },
    {
      "layout": "ArtBook_Land",
      "front_theme": "warm-palette",
      "back_theme": "warm-palette"
    }
  ]
}
```

Each batch entry specifies separate themes for front and back. Use the same theme for both if desired, or a simpler/grayscale theme for the back to save ink.

## Implementation Steps

### Phase 1: Directory Structure
Create the new directory structure:
```
palettes/                   # Drop Adobe Color CSS files here
  CLEAN-LOOK-x-DG.css
  simple-grayscale.css
themes/                     # Generated theme JSONs (light + dark per palette)
layouts/                    # Individual layout geometry files
```

### Phase 2: Layout Migration Script
Create `migrate_layouts.py` to extract layouts from current `layouts.json`:

**Input:** `layouts.json` (current file with 28 layouts)

**Output:** Individual files in `layouts/` directory:
- `ClassicMuseum_Land_8-5x11.json`
- `ClassicMuseum_Port_8-5x11.json`
- `ArtBook_Land_8-5x11.json`
- ... (28 total)

**Process:**
1. Read current layouts.json
2. For each layout, extract geometry fields only:
   - paper_size, front (img_dims, img_pos, caption_dims, caption_pos, special, gutter, border_widths), back (note_dims, note_pos, border_widths)
3. Derive border_widths from existing style objects (extract width values)
4. Write individual JSON file using layout name (sanitized for filename)
5. Generate starter `batch.json` with globals + empty batch list

### Phase 3: Theme Importer
Create `import_theme.py` script:

**Input:** CSS file from `palettes/` directory

**Output:** Two theme files in `themes/` directory:
- `{palette_name}_light.json`
- `{palette_name}_dark.json`

**Process:**
1. Scan `palettes/` for CSS files
2. For each CSS file:
   - Parse to extract theme name + 5 hex colors
   - Generate light mode theme (background=lightest)
   - Generate dark mode theme (background=darkest)
   - Write both to `themes/` directory

**Usage:**
```bash
# Import all palettes in palettes/ directory
python import_theme.py

# Import specific palette
python import_theme.py palettes/CLEAN-LOOK-x-DG.css
```

### Phase 4: Update PrintLayoutDesigner
- Load batch.json for global settings and batch list
- For each batch entry: load layout from `layouts/` + theme from `themes/`, merge into render parameters
- Generate output files named: `{layout}_{theme}_front.png` and `{layout}_{theme}_back.png`

### Phase 5: Testing
- Run migration script on current layouts.json
- Drop a test Adobe CSS file in palettes/
- Run theme importer
- Create test batch.json entries
- Run PrintLayoutDesigner and verify output

## Files to Create/Modify

### New Directories
- `palettes/` - user drops Adobe Color CSS files here
- `themes/` - generated theme JSON files
- `layouts/` - individual layout geometry files

### New Scripts
- `migrate_layouts.py` - one-time migration from layouts.json → layouts/*.json
- `import_theme.py` - converts palettes/*.css → themes/*_light.json + themes/*_dark.json

### New Config
- `batch.json` - master file with globals + batch list

### Modified
- `PrintLayoutDesigner.py` - refactor to use new architecture
- `docs/jsondocs.md` - update documentation

### Deprecated (after migration)
- `layouts.json` - replaced by batch.json + layouts/*.json

## Open Questions
1. ~~Border widths: keep in layout (geometry) or move to theme (style)?~~ **Resolved: keep in layout**
2. Output naming convention for layout+theme combinations?
