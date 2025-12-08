# ABOUTME: Imports Adobe Color CSS files and generates theme JSONs.
# ABOUTME: Creates light and dark mode themes with WCAG-based color role assignment.

import json
import os
import re
import sys
from glob import glob


def relative_luminance(hex_color):
    """WCAG relative luminance (0-1 scale, perceptually weighted)."""
    r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)]

    # Apply gamma correction (sRGB to linear)
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color1, color2):
    """WCAG contrast ratio (1:1 to 21:1)."""
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


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

    # Remaining colors become secondary and accent
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
    else:
        # Edge case: base and/or text might have consumed remaining
        # Use base for both
        secondary = base
        accent = base

    return {
        "background": background,
        "base": base,
        "secondary": secondary,
        "accent": accent,
        "text": text
    }


def parse_adobe_css(css_content):
    """Parse Adobe Color CSS and extract theme name and colors."""
    # Find hex color section and extract colors
    # Pattern: .ThemeName-N-hex { color: #XXXXXX; }
    pattern = r'\.([A-Za-z0-9_-]+)-(\d)-hex\s*\{\s*color:\s*(#[A-Fa-f0-9]{6})\s*;\s*\}'
    matches = re.findall(pattern, css_content)

    if len(matches) < 5:
        return None, []

    # Theme name from first match (strip the number suffix)
    theme_name = matches[0][0]

    # Extract colors in order (1-5)
    colors = [''] * 5
    for name, index, color in matches:
        idx = int(index) - 1  # Convert to 0-based
        if 0 <= idx < 5:
            colors[idx] = color.upper()

    # Verify we have all 5 colors
    if any(c == '' for c in colors):
        return None, []

    return theme_name, colors


def create_theme(name, colors, mode):
    """Create a theme JSON structure."""
    roles = assign_roles(colors, mode)

    return {
        "name": name,
        "source": "adobe-color",
        "mode": mode,
        "colors": roles,
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


def import_palette(css_path):
    """Import a single CSS palette file and create light/dark themes."""
    with open(css_path, 'r') as f:
        css_content = f.read()

    _, colors = parse_adobe_css(css_content)

    if not colors:
        print(f"Warning: Could not parse {css_path}")
        return []

    # Use filename (without path/extension) as theme name
    theme_name = os.path.splitext(os.path.basename(css_path))[0]

    os.makedirs('themes', exist_ok=True)
    created = []

    for mode in ['light', 'dark']:
        theme = create_theme(theme_name, colors, mode)
        filename = f"themes/{theme_name}_{mode}.json"

        with open(filename, 'w') as f:
            json.dump(theme, f, indent=2)

        print(f"Created: {filename}")
        created.append(filename)

    return created


def main():
    if len(sys.argv) > 1:
        # Import specific file(s)
        css_files = sys.argv[1:]
    else:
        # Import all CSS files in palettes/
        css_files = glob('palettes/*.css')

    if not css_files:
        print("No CSS files found in palettes/")
        print("Usage: python import_theme.py [path/to/palette.css ...]")
        return

    total_created = []
    for css_file in css_files:
        print(f"\nProcessing: {css_file}")
        created = import_palette(css_file)
        total_created.extend(created)

    print(f"\n{len(total_created)} theme files created in themes/")


if __name__ == '__main__':
    main()
