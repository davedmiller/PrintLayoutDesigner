# layouts.json Documentation

This file defines all print layout configurations.

## Root Object

The JSON file is an object containing a global mode, sample content paths, and an array of layouts.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | string | No | Rendering mode for all layouts (default: `"design"`) |
| `image_path_landscape` | string | No | Path to sample image for landscape layouts (img_w > img_h). In design mode, renders the image instead of placeholder label. |
| `image_path_portrait` | string | No | Path to sample image for portrait layouts (img_h >= img_w). In design mode, renders the image instead of placeholder label. |
| `text_path` | string | No | Path to sample text file. In design mode, renders the text in caption boxes instead of placeholder label. |
| `layouts` | array | Yes | Array of layout objects |

When image or text paths are `null` or the files don't exist, placeholder labels are shown ("IMAGE WxH" and "CAPTION TEXT (Greeked)").

## Rendering Modes

The `mode` field controls how all layouts are rendered.

| Mode | Canvas Size | Description |
|------|-------------|-------------|
| `design` | 18" x 24" | Full blueprint canvas with dimension lines, title block, and labels inside image/text boxes. Used for reviewing and documenting layouts. |
| `print` | paper size | Paper-sized output with only the styled paper, image box, and text box. No dimension lines, no title block, no labels. Used for generating print-ready templates. |

### Mode Comparison

| Element | design | print |
|---------|--------|-------|
| Canvas size | 18" x 24" | paper_size dimensions |
| Canvas border | Yes | No |
| Dimension lines (D1-D16) | Yes | No |
| Title block | Yes | No |
| "IMAGE WxH" label | Yes | No |
| "CAPTION TEXT" label | Yes | No |
| Paper with styles | Yes | Yes |
| Image box with styles | Yes | Yes |
| Text box with styles | Yes | Yes |

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
| `paper_style` | object | No | Paper styling (see Style Object) |
| `img_style` | object | No | Image box styling (see Style Object) |
| `txt_style` | object | No | Text box styling (see Style Object) |
| `notes` | string | Yes | Installation notes displayed in title block |
| `special` | string | No | Special rendering mode: `"double_col"` splits caption into two columns |
| `gutter` | number | No | Width of gutter between columns for double_col mode (inches) |
| `font_color` | string | No | Hex color code for caption text (default: black) |

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

## Style Object

Controls the background and border styling for paper, image, and text areas.

| Field | Type | Description |
|-------|------|-------------|
| `background` | string | Hex color code for fill (e.g., `"#FFFFFF"`) or `null` for default |
| `border` | object | Border definition (see Border Object) or `null` for no border |

### Border Object (nested in Style)

| Field | Type | Description |
|-------|------|-------------|
| `color` | string | Hex color code for border (e.g., `"#CCCCCC"`) |
| `width` | number | Border width in inches |

### Style Behavior by Element

- **paper_style.border**: Drawn INSIDE the paper edge (inset effect, like a mat)
- **img_style.border**: Drawn OUTSIDE the image box
- **txt_style.border**: Drawn OUTSIDE the text box

## Special Modes

| Mode | Description |
|------|-------------|
| `double_col` | Caption split into two columns with gutter specified by `gutter` field |

## Example File

```json
{
  "mode": "design",
  "image_path_landscape": "/path/to/landscape_image.jpg",
  "image_path_portrait": "/path/to/portrait_image.jpg",
  "text_path": "/path/to/sample_text.md",
  "layouts": [
    {
      "file": "01_ClassicMuseum_Land_8-5x11.png",
      "title": "Classic Museum - Landscape",
      "paper_size": {"width": 8.5, "height": 11},
      "img_dims": {"width": 6, "height": 4},
      "img_pos": {"left": 1.25, "top": 2},
      "txt_dims": {"width": 6, "height": 1.75},
      "txt_pos": {"left": 1.25, "top": 7.0},
      "paper_style": {"background": "#FFFFFF", "border": {"color": "#CCCCCC", "width": 0.5}},
      "img_style": {"background": "#E8EFF5", "border": null},
      "txt_style": {"background": null, "border": null},
      "special": null,
      "gutter": null,
      "font_color": null,
      "notes": "Layout: Classic Museum\nPaper: 8-5x11\nOrientation: Landscape Img\nTop Margin: 2\"\nText Gap: 1\""
    }
  ]
}
```

This creates a layout in design mode with:
- 8.5x11 inch paper with white background and gray (#CCCCCC) border inset 0.5 inches
- 6x4 inch landscape image with light blue (#E8EFF5) background, positioned 1.25" left, 2" top
- 6x1.75 inch caption with default background, positioned 1.25" left, 7" top

To generate print-ready output instead, change `"mode": "design"` to `"mode": "print"`.
