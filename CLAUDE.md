# PrintLayoutDesigner

Generates technical blueprint-style diagrams showing print layout specifications for gallery/museum presentations.

## Key Concepts

- **Blueprint canvas** (BLUEPRINT_W x BLUEPRINT_H): The drawing surface, currently 18x24 inches
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

- Canvas size: Edit `BLUEPRINT_W` and `BLUEPRINT_H` constants in Python
- Layouts: Edit `layouts.json` to modify individual layout parameters
- `black_border`: Set per-layout in JSON (0 = no border, 0.125 = 1/8 inch black line around paper edge)

