# layouts.json Documentation

This file defines all print layout configurations. Each layout is a JSON object in an array.

## Layout Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | string | Yes | Output filename (e.g., `"01_ClassicMuseum_Land_8-5x11.png"`) |
| `title` | string | Yes | Layout name displayed in title block |
| `paper_size` | object | Yes | Print paper dimensions (see Dimensions Object) |
| `img_dims` | object | Yes | Image dimensions (see Dimensions Object) |
| `img_pos` | object | Yes | Image position from paper edges (see Position Object) |
| `txt_dims` | object | Yes | Caption text box dimensions (see Dimensions Object) |
| `txt_pos` | object | Yes | Caption text position from paper edges (see Position Object) |
| `border` | object | Yes | Border style and width (see Border Object) |
| `notes` | string | Yes | Installation notes displayed in title block |
| `special` | string | No | Special rendering mode: `"double_col"` splits caption into two columns |
| `gutter` | number | No | Width of gutter between columns for double_col mode (inches) |

## Dimensions Object

Used for `paper_size`, `img_dims`, and `txt_dims`.

| Field | Type | Description |
|-------|------|-------------|
| `width` | number | Width in inches |
| `height` | number | Height in inches |

## Position Object

Used for `img_pos` and `txt_pos`. Specifies absolute position from paper edges.

| Field | Type | Description |
|-------|------|-------------|
| `left` | number | Distance from left edge of paper (inches) |
| `top` | number | Distance from top edge of paper (inches) |

## Border Object

Controls the border drawn around the paper.

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Border type: `"white"` (dashed inset line) or `"black"` (solid edge border) |
| `width` | number | Border width/inset in inches |

- `type: "white"` draws a dashed line inset from the paper edge by `width` inches
- `type: "black"` draws a solid border at the paper edge with `width` thickness

## Special Modes

| Mode | Description |
|------|-------------|
| `double_col` | Caption split into two columns with gutter specified by `gutter` field |

## Example Layout

```json
{
  "file": "01_ClassicMuseum_Land_8-5x11.png",
  "title": "Classic Museum - Landscape",
  "paper_size": {"width": 8.5, "height": 11},
  "img_dims": {"width": 6, "height": 4},
  "img_pos": {"left": 1.25, "top": 2},
  "txt_dims": {"width": 6, "height": 1.75},
  "txt_pos": {"left": 1.25, "top": 7.0},
  "border": {"type": "white", "width": 0.5},
  "special": null,
  "gutter": null,
  "notes": "Layout: Classic Museum\nPaper: 8-5x11\nOrientation: Landscape Img\nTop Margin: 2\"\nText Gap: 1\""
}
```

This creates a layout with:
- 8.5x11 inch paper with white border (dashed line 0.5 inches inset from edge)
- 6x4 inch landscape image positioned 1.25 inches from left and 2 inches from top
- 6x1.75 inch caption positioned 1.25 inches from left and 7 inches from top
