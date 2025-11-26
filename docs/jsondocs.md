# layouts.json Documentation

This file defines all print layout configurations. Each layout is a JSON object in an array.

## Layout Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | string | Yes | Output filename (e.g., `"01_ClassicMuseum_Land_8-5x11.png"`) |
| `title` | string | Yes | Layout name displayed in title block |
| `paper_size` | [width, height] | Yes | Print paper dimensions in inches (e.g., `[8.5, 11]` or `[11, 14]`) |
| `black_border` | number | Yes | Width of black border around paper edge in inches (0 = no border) |
| `img` | [width, height] | Yes | Image dimensions in inches |
| `margins` | object | Yes | Image positioning (see Margins below) |
| `txt_dims` | [width, height] | Yes | Caption text box dimensions in inches |
| `txt_pos` | object | Yes | Caption text positioning (see Text Position below) |
| `notes` | string | Yes | Installation notes displayed in title block |
| `special` | string | No | Special rendering mode: `"double_col"` splits caption into two columns |
| `gutter` | number | No | Width of gutter between columns for double_col mode (inches) |

## Margins Object

Controls image placement on the paper.

| Field | Type | Description |
|-------|------|-------------|
| `top` | number | Distance from top of paper to top of image (inches) |
| `left` | number | Distance from left edge of paper to left of image |
| `right` | number | Distance from right edge of paper to right of image |
| `center_v` | boolean | If true, vertically center the image |

- If neither `left` nor `right` is specified, image is horizontally centered
- If neither `top` nor `center_v` is specified, image is vertically centered

## Text Position Object

Controls caption text box placement using absolute positioning from paper edges.

| Field | Type | Description |
|-------|------|-------------|
| `left` | number | Distance from left edge of paper to left edge of text box (inches) |
| `top` | number | Distance from top edge of paper to top edge of text box (inches) |

## Special Modes

| Mode | Description |
|------|-------------|
| `double_col` | Caption split into two columns with 0.5" gutter |

## Example Layout

```json
{
  "file": "01_ClassicMuseum_Land_8-5x11.png",
  "title": "Classic Museum - Landscape",
  "paper_size": [8.5, 11],
  "black_border": 0.25,
  "img": [6, 4],
  "margins": {"top": 2},
  "txt_dims": [6, 1.75],
  "txt_pos": {"left": 1.25, "top": 7.0},
  "notes": "Layout: Classic Museum\nPaper: 8-5x11\nOrientation: Landscape Img\nTop Margin: 2\"\nText Gap: 1\""
}
```

This creates a layout with:
- 8.5x11 inch paper with 1/4 inch black border
- 6x4 inch landscape image, 2 inches from top, horizontally centered
- 6x1.75 inch caption, 1.25 inches from left edge and 7 inches from top of paper
