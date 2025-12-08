# PrintLayoutDesigner

Generates technical diagrams showing print layout specifications for gallery/museum presentations.

## Key Concepts

- **Canvas** (CANVAS_W x CANVAS_H): The drawing surface, currently 18x24 inches
- **Print paper** (paper_size in JSON): The actual paper being designed for (8.5x11 or 11x14)
- **Dimension lines** (D1-D10): Labeled measurement lines positioned outside the paper

## Files

- `PrintLayoutDesigner.py` - Main generator script
- `layouts.json` - Layout definitions (paper size, margins, image/text positions, black_border width)

## Running

```bash
source venv/bin/activate
python PrintLayoutDesigner.py
```

## Configuration

- Canvas size: Edit `CANVAS_W` and `CANVAS_H` constants in Python
- Layouts: Edit `layouts.json` to modify individual layout parameters
- Styling: Each layout can define `paper_style`, `img_style`, and `txt_style` objects with:
  - `background`: Hex color code (e.g., `"#FFFFFF"`) or `null`
  - `border`: Object with `color` and `width`, or `null` for no border
  - Paper borders are drawn inset; image and text borders are drawn outset

