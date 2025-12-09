# Plan: HTML Print Mode

## Summary

Simplify output modes:
- **PNG** = design mode only (technical blueprint diagrams with measurements)
- **HTML** = print mode only (actual print-ready output with all features)

---

## Batch.json Changes

```json
{
  "mode": "design",    // "design" → PNG blueprint, "print" → HTML output
  ...
}
```

No `output_format` field needed - mode determines format automatically.

---

## Layout JSON Changes (text_style)

Add optional `text_style` to front/back sections:

```json
"front": {
  "caption_dims": {"width": 6, "height": 1.75},
  "caption_pos": {"left": 1.25, "top": 7.0},
  "text_style": {                    // NEW - optional, HTML only
    "align_h": "left",               // left|center|right|justified
    "align_v": "top",                // top|middle|bottom
    "font": "Georgia, serif",        // CSS font-family
    "size": 10                       // font size in points
  }
}

"back": {
  "note_dims": {"width": 6, "height": 9},
  "text_style": {                    // NEW - optional, HTML only
    "align_h": "left",
    "align_v": "top",
    "font": "Georgia, serif",
    "size": 10
  }
}
```

### Defaults (if not specified)
- `align_h`: "left"
- `align_v`: "top"
- `font`: "Georgia, serif"
- `size`: 10

---

## HTML Output Features

### Structure (per layout)

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    @page { size: 8.5in 11in; margin: 0; }
    @media print { body { margin: 0; } }
    .page { width: 8.5in; height: 11in; position: relative; page-break-after: always; }
    /* Element positioning via inline styles */
  </style>
</head>
<body>
  <!-- Front page -->
  <div class="page" style="background: #theme-color;">
    <div class="image-box" style="position: absolute; ...">
      <img src="path/to/image.jpg" />
    </div>
    <div class="caption-box" style="position: absolute; text-align: left; ...">
      <p>Rendered markdown content</p>
    </div>
  </div>

  <!-- Back page -->
  <div class="page" style="background: #theme-color;">
    <div class="note-box" style="position: absolute; ...">
      <p>Rendered markdown content</p>
    </div>
  </div>
</body>
</html>
```

### CSS Features
- `@page` for paper size
- Absolute positioning in inches
- Theme colors as inline styles
- Native `text-align` (including `justify`)
- `vertical-align` via flexbox
- Emoji works natively

### Markdown Support
- Use Python `markdown` library to convert `.md` → HTML
- Supports: **bold**, *italic*, lists, links, headers, etc.

### Image Handling
- Reference actual image files via `<img src="...">`
- Images display at full resolution (no matplotlib scaling)

---

## PNG Output (Design Mode)

Unchanged from current behavior:
- Technical blueprint showing measurements
- Blue reference lines and dimension annotations
- Placeholder boxes for images
- Plain text rendering (no markdown)
- No text_style options (always uses defaults)

---

## Implementation

### New Functions
- `generate_html(batch_item, layout, front_theme, back_theme, ...)` - main HTML generator
- `render_markdown(text)` - convert .md content to HTML
- `get_css_alignment(text_style)` - convert text_style to CSS properties

### Modified Functions
- `main()` - route to PNG or HTML based on mode
- Remove print mode from PNG generation path

### Files Modified
- `PrintLayoutDesigner.py` - HTML generation, simplify PNG to design-only
- `docs/jsondocs.md` - document text_style options and mode behavior
- `requirements.txt` - add `markdown` dependency

---

## Execution Order

1. Install markdown dependency
2. Add HTML generation functions
3. Add markdown rendering
4. Simplify PNG to design-mode only
5. Test design mode (PNG) still works
6. Test print mode (HTML) with markdown
7. Update documentation
