Here is a clean, professional `README.md` file summarizing the purpose and usage of the Python script we created. You can place this file in the same folder as your script.

-----

# Gallery Layout Generator

A Python utility that generates precise, to-scale technical diagrams for photography printing and framing.

This tool was created to replace AI image generation for technical diagrams, ensuring that all dimensions, margins, and alignments are mathematically accurate rather than "hallucinated."

## 📋 Purpose

This script generates **14 distinct layout variations** for printing photography on **8.5" x 11" (Letter)** paper. It visualizes how a 6x4" (Landscape) or 4x6" (Portrait) image pairs with a 100-word caption block.

The output images are styled as **technical diagrams** (dark blue lines on off-white canvas) and include:

  * To-scale visual representations of the image and text block.
  * Dimension arrows indicating margins.
  * A "Notes" sidebar with specific installation and typography instructions.
  * Paper borders and cut lines.

## 🛠️ Technologies

  * **Python 3**
  * **Matplotlib:** Used here not for data plotting, but for coordinate-based technical drawing and rendering high-DPI images.

## 📦 Installation

1.  Ensure you have Python installed.
2.  Install the required dependency:

<!-- end list -->

```bash
pip install matplotlib
```

## 🚀 Usage

1.  Save the script as `generate_layouts.py`.
2.  Run the script from your terminal:

<!-- end list -->

```bash
python generate_layouts.py
```

3.  The script will generate **14 PNG files** in the same directory.

## 📂 Included Layout Styles

The script generates Landscape (6x4 image) and Portrait (4x6 image) versions of the following design styles:

| Style | Description |
| :--- | :--- |
| **Classic Museum** | The standard gallery look. Image centered with a text block centered directly below. |
| **Art Book** | Asymmetrical layout. Image pushed to Top-Right; Text pushed to Bottom-Left for diagonal flow. |
| **Footer** | Image centered optically; Text stretches wide across the bottom of the page. |
| **Broadside** | (Portrait only) Magazine-style layout with image on left and text column on right. |
| **Double Column** | (Landscape only) Academic style. Text split into two narrow columns below the image. |
| **Visual Anchor** | Similar to Museum, but with a heavier top margin (2.5") for a "hanging" feel. |
| **High Gallery** | Image placed high, text placed low, creating a large deliberate void/pause in the middle. |
| **Asymmetrical Offset** | Image pushed to the right margin; Text aligns flush-left with the image edge. |

## ⚙️ Customization

You can modify the `layouts` list at the bottom of the script to adjust:

  * **Margins:** Change `top`, `left`, or `right` values in inches.
  * **Paper Size:** Modify `FIG_W` and `FIG_H` constants at the top of the script.
  * **Colors:** Change `BLUE` and `CANVAS_COLOR` constants to alter the aesthetic.

## 📄 Output Example

Each file is saved at **150 DPI**, suitable for screen viewing or reference printing.

  * `01_ClassicMuseum_Land.png`
  * `02_ClassicMuseum_Port.png`
  * ...and so on.