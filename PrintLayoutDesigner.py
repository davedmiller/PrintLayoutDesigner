import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for cleaner PNG output
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import glob
import json
import markdown
import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
import webbrowser

# --- CONFIGURATION ---
VERSION = "4.1.0"

# Canvas drawing size (combined blueprint: front + back side-by-side)
PANEL_W = 18      # Width of each panel (front or back)
PANEL_GAP = 0     # Gap between panels
CANVAS_W = PANEL_W * 2 + PANEL_GAP  # 36 inches total
CANVAS_H = 24

# Print paper size (the actual paper being designed for printing)
PAPER_W = 8.5
PAPER_H = 11

DPI = 150  # High resolution for crisp text
BLUE = '#4A90D9'
CANVAS_COLOR = '#F2F2F2'
BORDER_MARGIN = 0.25  # Canvas border margin
TITLE_BLOCK_H = 2.5  # Title block height

# --- THEME AND LAYOUT LOADING ---

def load_theme(theme_path):
    """Load a theme from the given path."""
    try:
        with open(theme_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Theme not found: {theme_path}")


def load_layout(layout_path):
    """Load a layout from the given path."""
    try:
        with open(layout_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Layout not found: {layout_path}")


# --- API: DISCOVERY FUNCTIONS ---

def list_layouts(base_dir):
    """Return list of available layouts with metadata.

    Args:
        base_dir: Path to directory containing 'layouts' subdirectory

    Returns:
        List of dicts with 'name', 'title', 'paper_size' keys
    """
    layouts_dir = Path(base_dir) / 'layouts'
    result = []
    for f in sorted(layouts_dir.glob('*.json')):
        data = json.loads(f.read_text())
        result.append({
            'name': f.stem,
            'title': data.get('title', f.stem),
            'paper_size': data.get('paper_size', {}),
        })
    return result


def list_themes(base_dir):
    """Return list of available themes with metadata.

    Args:
        base_dir: Path to directory containing 'themes' subdirectory

    Returns:
        List of dicts with 'name', 'mode' keys
    """
    themes_dir = Path(base_dir) / 'themes'
    result = []
    for f in sorted(themes_dir.glob('*.json')):
        data = json.loads(f.read_text())
        result.append({
            'name': f.stem,
            'mode': data.get('mode', 'unknown'),
        })
    return result


# --- API: LAYOUT SPEC ---

def get_layout_spec(layout_name, front_theme_name, back_theme_name, base_dir):
    """Return structured dict with geometry and colors for a layout.

    Args:
        layout_name: Name of layout file (without .json extension)
        front_theme_name: Name of front theme file (without .json extension)
        back_theme_name: Name of back theme file (without .json extension)
        base_dir: Path to directory containing 'layouts' and 'themes' subdirectories

    Returns:
        Dict with paper, front, back, and text specifications
    """
    base = Path(base_dir)
    layout = load_layout(base / 'layouts' / f'{layout_name}.json')
    front_theme = load_theme(base / 'themes' / f'{front_theme_name}.json')
    back_theme = load_theme(base / 'themes' / f'{back_theme_name}.json')

    front = layout.get('front', {})
    back = layout.get('back', {})
    front_borders = front.get('border_widths', {})
    back_borders = back.get('border_widths', {})
    front_text = front.get('text_style', {})
    back_text = back.get('text_style', {})

    def get_color(theme, style_key):
        color_role = theme['styles'].get(style_key)
        return theme['colors'].get(color_role) if color_role else None

    return {
        'paper': layout.get('paper_size', {'width': 8.5, 'height': 11}),
        'front': {
            'image': {
                **front.get('img_dims', {}),
                **front.get('img_pos', {}),
                'border_width': front_borders.get('img', 0),
            },
            'caption': {
                **front.get('caption_dims', {}),
                **front.get('caption_pos', {}),
                'border_width': front_borders.get('caption', 0),
            },
            'paper_border_width': front_borders.get('paper', 0),
            'special': front.get('special'),
            'gutter': front.get('gutter'),
            'colors': {
                'paper_bg': get_color(front_theme, 'paper_background'),
                'paper_border': get_color(front_theme, 'paper_border'),
                'image_bg': get_color(front_theme, 'img_background'),
                'image_border': get_color(front_theme, 'img_border'),
                'caption_bg': get_color(front_theme, 'caption_background'),
                'caption_border': get_color(front_theme, 'caption_border'),
                'font': get_color(front_theme, 'font_color'),
            },
            'text': {
                'align_h': front_text.get('align_h', 'left'),
                'align_v': front_text.get('align_v', 'top'),
                'font': front_text.get('font', 'Georgia, serif'),
                'size': front_text.get('size', 10),
            },
        },
        'back': {
            'note': {
                **back.get('note_dims', {}),
                'pos': back.get('note_pos', 'centered'),
                'border_width': back_borders.get('note', 0),
            },
            'paper_border_width': back_borders.get('paper', 0),
            'colors': {
                'paper_bg': get_color(back_theme, 'paper_background'),
                'paper_border': get_color(back_theme, 'paper_border'),
                'note_bg': get_color(back_theme, 'note_background'),
                'note_border': get_color(back_theme, 'note_border'),
                'font': get_color(back_theme, 'font_color'),
            },
            'text': {
                'align_h': back_text.get('align_h', 'left'),
                'align_v': back_text.get('align_v', 'top'),
                'font': back_text.get('font', 'Georgia, serif'),
                'size': back_text.get('size', 10),
            },
        },
    }


# --- API: HTML TEMPLATE ---

def get_html_template(layout_name, front_theme_name, back_theme_name, base_dir):
    """Return HTML template with placeholders for content injection.

    Args:
        layout_name: Name of layout file (without .json extension)
        front_theme_name: Name of front theme file (without .json extension)
        back_theme_name: Name of back theme file (without .json extension)
        base_dir: Path to directory containing 'layouts' and 'themes' subdirectories

    Returns:
        HTML string with placeholders:
        - {{IMAGE}} - image element placeholder
        - {{CAPTION}} - caption HTML content placeholder
        - {{NOTE}} - note HTML content placeholder
        - {{FONT_FAMILY}} - font-family CSS value placeholder
    """
    base = Path(base_dir)
    layout = load_layout(base / 'layouts' / f'{layout_name}.json')
    front_theme = load_theme(base / 'themes' / f'{front_theme_name}.json')
    back_theme = load_theme(base / 'themes' / f'{back_theme_name}.json')

    paper_w = layout['paper_size']['width']
    paper_h = layout['paper_size']['height']
    front = layout.get('front', {})
    back = layout.get('back', {})

    # Build styles
    paper_style, img_style, caption_style, font_color = build_front_styles(layout, front_theme)
    back_paper_style, back_note_style, back_font_color = build_back_styles(layout, back_theme)

    # Get text styles
    front_text_style = front.get('text_style', {})
    back_text_style = back.get('text_style', {})
    front_css = get_css_text_alignment(front_text_style)
    back_css = get_css_text_alignment(back_text_style)

    # Image position and size
    img_w = front['img_dims']['width']
    img_h = front['img_dims']['height']
    img_left = front['img_pos']['left']
    img_top_margin = front['img_pos']['top']
    img_y = paper_h - img_top_margin - img_h

    # Caption position and size
    caption_w = front['caption_dims']['width']
    caption_h = front['caption_dims']['height']
    caption_left = front['caption_pos']['left']
    caption_top_margin = front['caption_pos']['top']
    caption_y = paper_h - caption_top_margin - caption_h

    # Note position and size
    note_dims = back.get('note_dims', {'width': 6, 'height': 9})
    note_w = note_dims['width']
    note_h = note_dims['height']
    note_left = (paper_w - note_w) / 2
    note_y = (paper_h - note_h) / 2

    # Generate CSS
    front_paper_bg = paper_style.get('background', '#FFFFFF') if paper_style else '#FFFFFF'
    back_paper_bg = back_paper_style.get('background', '#FFFFFF') if back_paper_style else '#FFFFFF'

    front_paper_border = paper_style.get('border') if paper_style else None
    back_paper_border = back_paper_style.get('border') if back_paper_style else None

    def get_paper_border_css(border):
        if border and border.get('width') and border.get('color'):
            w = border['width']
            c = border['color']
            return f"box-shadow: inset 0 0 0 {w}in {c};"
        return ""

    front_border_css = get_paper_border_css(front_paper_border)
    back_border_css = get_paper_border_css(back_paper_border)

    img_css = generate_box_css(img_left, img_y, img_w, img_h, img_style, paper_h)
    caption_css = generate_box_css(caption_left, caption_y, caption_w, caption_h, caption_style, paper_h)
    note_css = generate_box_css(note_left, note_y, note_w, note_h, back_note_style, paper_h)

    # Handle special double-column layout
    special_mode = front.get('special')
    gutter = front.get('gutter', 0.25)

    if special_mode == 'double_col':
        caption_border = caption_style.get('border', {}) if caption_style else {}
        rule_color = caption_border.get('color', '#000000')
        caption_block_html = f'''
            <div class="caption-box" style="{caption_css} overflow: hidden; padding: 0.1in; column-count: 2; column-gap: {gutter}in; column-fill: auto; column-rule: 1px solid {rule_color}; text-align: {front_css['text_align']}; font-family: {{{{FONT_FAMILY}}}}; font-size: {front_css['font_size']}pt; color: {font_color or '#000000'};">{{{{CAPTION}}}}</div>'''
    else:
        caption_block_html = f'''
            <div class="caption-box" style="{caption_css} display: flex; flex-direction: column; justify-content: {front_css['align_items']}; overflow: hidden; padding: 0.1in;">
                <div style="text-align: {front_css['text_align']}; font-family: {{{{FONT_FAMILY}}}}; font-size: {front_css['font_size']}pt; color: {font_color or '#000000'};">{{{{CAPTION}}}}</div>
            </div>'''

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{layout_name}</title>
    <style>
        @page {{
            size: {paper_w}in {paper_h}in;
            margin: 0;
        }}
        @media print {{
            body {{ margin: 0; }}
            .page {{ page-break-after: always; }}
            .page:last-child {{ page-break-after: auto; }}
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: {{{{FONT_FAMILY}}}};
        }}
        .page {{
            width: {paper_w}in;
            height: {paper_h}in;
            position: relative;
            overflow: hidden;
        }}
        .image-box img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        p {{
            margin: 0 0 0.5em 0;
        }}
        p:last-child {{
            margin-bottom: 0;
        }}
    </style>
</head>
<body>
    <!-- Front Page -->
    <div class="page" style="background: {front_paper_bg}; {front_border_css}">
        <div class="image-box" style="{img_css} overflow: hidden;">
            {{{{IMAGE}}}}
        </div>
        {caption_block_html}
    </div>

    <!-- Back Page -->
    <div class="page" style="background: {back_paper_bg}; {back_border_css}">
        <div class="note-box" style="{note_css} display: flex; flex-direction: column; justify-content: {back_css['align_items']}; overflow: hidden; padding: 0.1in;">
            <div style="text-align: {back_css['text_align']}; font-family: {{{{FONT_FAMILY}}}}; font-size: {back_css['font_size']}pt; color: {back_font_color or '#000000'};">{{{{NOTE}}}}</div>
        </div>
    </div>
</body>
</html>'''

    return html


def resolve_color(theme, style_key):
    """Resolve a color from theme using the style mapping."""
    color_role = theme['styles'].get(style_key)
    if color_role:
        return theme['colors'].get(color_role)
    return None


def build_style(theme, bg_style_key, border_style_key, border_width):
    """Build a style object from theme colors and layout border width."""
    bg_color = resolve_color(theme, bg_style_key)
    border_color = resolve_color(theme, border_style_key)

    style = {"background": bg_color}
    if border_width and border_color:
        style["border"] = {"color": border_color, "width": border_width}
    else:
        style["border"] = None

    return style


def build_front_styles(layout, theme):
    """Build front side style objects from layout geometry and theme colors."""
    front = layout.get('front', {})
    border_widths = front.get('border_widths', {})

    paper_style = build_style(
        theme,
        'paper_background', 'paper_border',
        border_widths.get('paper')
    )
    img_style = build_style(
        theme,
        'img_background', 'img_border',
        border_widths.get('img')
    )
    caption_style = build_style(
        theme,
        'caption_background', 'caption_border',
        border_widths.get('caption')
    )
    font_color = resolve_color(theme, 'font_color')

    return paper_style, img_style, caption_style, font_color


def build_back_styles(layout, theme):
    """Build back side style objects from layout geometry and theme colors."""
    back = layout.get('back', {})
    border_widths = back.get('border_widths', {})

    paper_style = build_style(
        theme,
        'paper_background', 'paper_border',
        border_widths.get('paper')
    )
    note_style = build_style(
        theme,
        'note_background', 'note_border',
        border_widths.get('note')
    )
    font_color = resolve_color(theme, 'font_color')

    return paper_style, note_style, font_color


# --- HTML GENERATION ---

def render_markdown_to_html(text):
    """Convert markdown text to HTML."""
    if not text:
        return ''
    return markdown.markdown(text, extensions=['nl2br'])


def get_text_style_defaults():
    """Return default text style values."""
    return {
        'align_h': 'left',
        'align_v': 'top',
        'font': 'Georgia, serif',
        'size': 10
    }


def get_css_text_alignment(text_style):
    """Convert text_style to CSS properties for text alignment."""
    defaults = get_text_style_defaults()
    align_h = text_style.get('align_h', defaults['align_h'])
    align_v = text_style.get('align_v', defaults['align_v'])
    font = text_style.get('font', defaults['font'])
    size = text_style.get('size', defaults['size'])

    # Horizontal alignment maps directly to CSS text-align
    css_text_align = align_h if align_h in ('left', 'center', 'right', 'justify') else 'left'

    # Vertical alignment via flexbox
    css_align_items = {'top': 'flex-start', 'middle': 'center', 'bottom': 'flex-end'}.get(align_v, 'flex-start')

    return {
        'text_align': css_text_align,
        'align_items': css_align_items,
        'font_family': font,
        'font_size': size
    }


def generate_box_css(x, y, w, h, style, paper_h):
    """Generate CSS for a positioned box with optional border."""
    # Convert from bottom-left origin to top-left origin
    top = paper_h - y - h

    bg = style.get('background', '#FFFFFF') if style else '#FFFFFF'
    border = style.get('border') if style else None

    css = f"position: absolute; left: {x}in; top: {top}in; width: {w}in; height: {h}in; "
    css += f"background: {bg}; box-sizing: border-box; "

    if border and border.get('width') and border.get('color'):
        border_width = border['width']
        border_color = border['color']
        css += f"border: {border_width}in solid {border_color}; "

    return css


def generate_html_output(batch_entry, layout, front_theme, back_theme,
                         image_path, text_content, note_content,
                         layout_name, output_dir, blueprint_png=None):
    """Generate HTML file for print mode output."""

    paper_w = layout['paper_size']['width']
    paper_h = layout['paper_size']['height']
    front = layout.get('front', {})
    back = layout.get('back', {})

    # Build styles
    paper_style, img_style, caption_style, font_color = build_front_styles(layout, front_theme)
    back_paper_style, back_note_style, back_font_color = build_back_styles(layout, back_theme)

    # Get text styles with defaults
    front_text_style = front.get('text_style', {})
    back_text_style = back.get('text_style', {})
    front_css = get_css_text_alignment(front_text_style)
    back_css = get_css_text_alignment(back_text_style)

    # Image position and size
    img_w = front['img_dims']['width']
    img_h = front['img_dims']['height']
    img_left = front['img_pos']['left']
    img_top_margin = front['img_pos']['top']
    img_y = paper_h - img_top_margin - img_h  # Convert to bottom-left origin

    # Caption position and size
    caption_w = front['caption_dims']['width']
    caption_h = front['caption_dims']['height']
    caption_left = front['caption_pos']['left']
    caption_top_margin = front['caption_pos']['top']
    caption_y = paper_h - caption_top_margin - caption_h

    # Note position and size (centered)
    note_dims = back.get('note_dims', {'width': 6, 'height': 9})
    note_w = note_dims['width']
    note_h = note_dims['height']
    note_left = (paper_w - note_w) / 2
    note_y = (paper_h - note_h) / 2

    # Render markdown content
    caption_html = render_markdown_to_html(text_content) if text_content else ''
    note_html = render_markdown_to_html(note_content) if note_content else ''

    # Generate CSS for each element
    front_paper_bg = paper_style.get('background', '#FFFFFF') if paper_style else '#FFFFFF'
    back_paper_bg = back_paper_style.get('background', '#FFFFFF') if back_paper_style else '#FFFFFF'

    # Paper border (inset) - rendered as box-shadow inset
    front_paper_border = paper_style.get('border') if paper_style else None
    back_paper_border = back_paper_style.get('border') if back_paper_style else None

    def get_paper_border_css(border):
        if border and border.get('width') and border.get('color'):
            w = border['width']
            c = border['color']
            # Inset box-shadow simulates border drawn inside the paper
            # Include both the inset border AND the drop shadow for screen display
            return f"box-shadow: inset 0 0 0 {w}in {c}, 0 0 10px rgba(0,0,0,0.3);"
        return ""

    front_border_css = get_paper_border_css(front_paper_border)
    back_border_css = get_paper_border_css(back_paper_border)

    img_css = generate_box_css(img_left, img_y, img_w, img_h, img_style, paper_h)
    caption_css = generate_box_css(caption_left, caption_y, caption_w, caption_h, caption_style, paper_h)
    note_css = generate_box_css(note_left, note_y, note_w, note_h, back_note_style, paper_h)

    # Handle special double-column layout
    special_mode = front.get('special')
    gutter = front.get('gutter', 0.25)

    if special_mode == 'double_col':
        caption_border = caption_style.get('border', {}) if caption_style else {}
        rule_color = caption_border.get('color', '#000000')
        caption_block_html = f'''
            <div class="caption-box" style="{caption_css} overflow: hidden; padding: 0.1in; column-count: 2; column-gap: {gutter}in; column-fill: auto; column-rule: 1px solid {rule_color}; text-align: {front_css['text_align']}; font-family: {front_css['font_family']}; font-size: {front_css['font_size']}pt; color: {font_color or '#000000'};">{caption_html}</div>'''
    else:
        caption_block_html = f'''
            <div class="caption-box" style="{caption_css} display: flex; flex-direction: column; justify-content: {front_css['align_items']}; overflow: hidden; padding: 0.1in;">
                <div style="text-align: {front_css['text_align']}; font-family: {front_css['font_family']}; font-size: {front_css['font_size']}pt; color: {font_color or '#000000'};">{caption_html}</div>
            </div>'''

    # Build the HTML document
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{layout_name}</title>
    <style>
        @page {{
            size: {paper_w}in {paper_h}in;
            margin: 0;
        }}
        @media print {{
            body {{ margin: 0; }}
            .page {{ page-break-after: always; }}
            .page:last-child {{ page-break-after: auto; }}
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: Georgia, serif;
        }}
        .page {{
            width: {paper_w}in;
            height: {paper_h}in;
            position: relative;
            overflow: hidden;
        }}
        .pages-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            padding: 20px;
        }}
        @media screen {{
            .page {{
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
                flex-shrink: 0;
            }}
        }}
        @media print {{
            .pages-container {{
                display: block;
                padding: 0;
            }}
        }}
        .image-box img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        p {{
            margin: 0 0 0.5em 0;
        }}
        p:last-child {{
            margin-bottom: 0;
        }}
        .blueprint {{
            margin: 20px auto;
            text-align: center;
            max-width: 100%;
        }}
        .blueprint h3 {{
            margin: 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .blueprint img {{
            max-width: 100%;
            height: auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }}
        @media print {{
            .blueprint {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="pages-container">
        <!-- Front Page -->
        <div class="page" style="width: {paper_w}in; height: {paper_h}in; background: {front_paper_bg}; {front_border_css}">
            <div class="image-box" style="{img_css} overflow: hidden;">
                <img src="{image_path}" alt="Image">
            </div>
            {caption_block_html}
        </div>

        <!-- Back Page -->
        <div class="page" style="width: {paper_w}in; height: {paper_h}in; background: {back_paper_bg}; {back_border_css}">
            <div class="note-box" style="{note_css} display: flex; flex-direction: column; justify-content: {back_css['align_items']}; overflow: hidden; padding: 0.1in;">
                <div style="text-align: {back_css['text_align']}; font-family: {back_css['font_family']}; font-size: {back_css['font_size']}pt; color: {back_font_color or '#000000'};">{note_html}</div>
            </div>
        </div>
    </div>

    <!-- Blueprint -->
    {f'<div class="blueprint"><h3>Blueprint</h3><img src="{blueprint_png}" alt="Blueprint"></div>' if blueprint_png else ''}
</body>
</html>
'''

    # Write HTML file
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{layout_name}.html"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {output_path}")
    return output_path


def load_batch(batch_path):
    """Load batch configuration from JSON file.

    Returns (batch_entries, mode, image_path_landscape, image_path_portrait, text_path, personal_note_path, show_blueprints).
    """
    try:
        with open(batch_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Batch file not found: {batch_path}")

    return (
        data.get('batch', []),
        data.get('mode', 'design'),
        data.get('image_path_landscape'),
        data.get('image_path_portrait'),
        data.get('text_path'),
        data.get('personal_note_path'),
        data.get('show_blueprints', True)
    )


def draw_border_inset(ax, x, y, w, h, border, fill_color):
    """Draw inset border: filled rect at outer size, then fill_color rect inset."""
    if not border:
        return
    color = border.get('color', '#000000')
    width = border.get('width', 0)
    if width <= 0:
        return
    outer = patches.Rectangle((x, y), w, h, facecolor=color, edgecolor='none')
    ax.add_patch(outer)
    inner = patches.Rectangle((x + width, y + width), w - 2*width, h - 2*width,
                               facecolor=fill_color, edgecolor='none')
    ax.add_patch(inner)

def draw_border_outset(ax, x, y, w, h, border):
    """Draw outset border: filled rect expanded by width. Content drawn on top."""
    if not border:
        return
    color = border.get('color', '#000000')
    width = border.get('width', 0)
    if width <= 0:
        return
    rect = patches.Rectangle((x - width, y - width), w + 2*width, h + 2*width,
                              facecolor=color, edgecolor='none')
    ax.add_patch(rect)

def draw_content_block(ax, x, y, w, h, style, content_renderer=None):
    """Draw a content block with border, background, and optional content.

    Used for image blocks, caption blocks, and personal note blocks.
    The content_renderer is a callable that renders content inside the block.
    """
    border = style.get('border') if style else None
    draw_border_outset(ax, x, y, w, h, border)

    bg = style.get('background') if style else None
    fill = bg if bg else 'white'
    rect = patches.Rectangle((x, y), w, h, lw=0, ec='none', fc=fill)
    ax.add_patch(rect)

    if content_renderer:
        content_renderer()

def setup_canvas(paper_w, paper_h, paper_style, mode):
    """Setup figure and axes for rendering.

    Returns (fig, ax, paper_x, paper_y, title_block_top) where title_block_top
    is None in print mode.
    """
    if mode == "print":
        fig, ax = plt.subplots(figsize=(paper_w, paper_h), dpi=DPI)
        ax.set_xlim(0, paper_w)
        ax.set_ylim(0, paper_h)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        paper_x, paper_y = 0, 0
        paper_bg = paper_style.get('background', '#FFFFFF') if paper_style else '#FFFFFF'
        fig.patch.set_facecolor(paper_bg)
        ax.set_facecolor(paper_bg)
        return fig, ax, paper_x, paper_y, None
    else:
        fig, ax = plt.subplots(figsize=(CANVAS_W, CANVAS_H), dpi=DPI)
        ax.set_xlim(-1, CANVAS_W - 1)
        ax.set_ylim(-1, CANVAS_H - 1)
        fig.patch.set_facecolor(CANVAS_COLOR)
        ax.set_facecolor(CANVAS_COLOR)

        canvas_border = patches.Rectangle((-1 + BORDER_MARGIN, -1 + BORDER_MARGIN),
                                         CANVAS_W - 2*BORDER_MARGIN,
                                         CANVAS_H - 2*BORDER_MARGIN,
                                         linewidth=1, edgecolor=BLUE, facecolor='none')
        ax.add_patch(canvas_border)

        title_block_y = -1 + BORDER_MARGIN
        title_block_top = title_block_y + TITLE_BLOCK_H

        canvas_center_x = CANVAS_W/2 - 1
        paper_x = canvas_center_x - paper_w/2

        available_height = (CANVAS_H - 1) - title_block_top
        paper_y = title_block_top + (available_height - paper_h) / 2

        return fig, ax, paper_x, paper_y, title_block_top

def draw_paper(ax, paper_x, paper_y, paper_w, paper_h, paper_style, mode):
    """Draw the paper rectangle with background and optional inset border."""
    paper_bg = paper_style.get('background', '#FFFFFF') if paper_style else '#FFFFFF'
    paper_border = paper_style.get('border') if paper_style else None

    if paper_border:
        draw_border_inset(ax, paper_x, paper_y, paper_w, paper_h, paper_border, paper_bg)
        if mode == "design":
            paper_edge = patches.Rectangle((paper_x, paper_y), paper_w, paper_h,
                                            linewidth=0.8, edgecolor=BLUE, facecolor='none')
            ax.add_patch(paper_edge)
    else:
        edge_color = BLUE if mode == "design" else 'none'
        paper_rect = patches.Rectangle((paper_x, paper_y), paper_w, paper_h,
                                        linewidth=0.8, edgecolor=edge_color, facecolor=paper_bg)
        ax.add_patch(paper_rect)

def format_style_for_display(style, name):
    """Format a style object for display in the title block."""
    if style is None:
        return f"{name}: null"
    bg = style.get('background')
    border = style.get('border')
    parts = []
    if bg:
        parts.append(f"bg={bg}")
    else:
        parts.append("bg=null")
    if border:
        parts.append(f"border={border.get('color')} {border.get('width')}\"")
    else:
        parts.append("border=null")
    return f"{name}: {', '.join(parts)}"

def draw_dim_line(ax, x, y_start, y_end, label, dim_id=None):
    """Draws a vertical dimension line with arrows and optional ID"""
    ax.annotate(text='', xy=(x, y_start), xytext=(x, y_end),
                arrowprops=dict(arrowstyle='<->', color=BLUE, lw=0.8))
    mid_y = (y_start + y_end) / 2
    if dim_id:
        label_text = f"{dim_id}: {label}"
    else:
        label_text = label
    ax.text(x - 0.1, mid_y, label_text, ha='right', va='center', fontsize=12, color=BLUE, rotation=90)

def draw_horizontal_dim_line(ax, y, x_start, x_end, label, dim_id=None, offset=0):
    """Draws a horizontal dimension line with arrows and optional ID"""
    ax.annotate(text='', xy=(x_start, y), xytext=(x_end, y),
                arrowprops=dict(arrowstyle='<->', color=BLUE, lw=0.8))
    mid_x = (x_start + x_end) / 2
    if dim_id:
        label_text = f"{dim_id}: {label}"
    else:
        label_text = label
    ax.text(mid_x, y + 0.1 + offset, label_text, ha='center', va='bottom', fontsize=12, color=BLUE)


def draw_combined_blueprint(filename, layout, front_theme, back_theme,
                            image_path_landscape, image_path_portrait,
                            text_path, personal_note_path, output_dir):
    """Generate combined front+back blueprint as single PNG."""

    # Extract layout info
    title = layout.get('title', 'Layout')
    paper_w = layout['paper_size']['width']
    paper_h = layout['paper_size']['height']
    front = layout.get('front', {})
    back = layout.get('back', {})
    notes = layout.get('notes', '')

    # Build styles
    paper_style, img_style, caption_style, font_color = build_front_styles(layout, front_theme)
    back_paper_style, back_note_style, back_font_color = build_back_styles(layout, back_theme)

    # Create combined canvas
    fig, ax = plt.subplots(figsize=(CANVAS_W, CANVAS_H), dpi=DPI)
    ax.set_xlim(-1, CANVAS_W - 1)
    ax.set_ylim(-1, CANVAS_H - 1)
    fig.patch.set_facecolor(CANVAS_COLOR)
    ax.set_facecolor(CANVAS_COLOR)

    # Draw canvas border
    canvas_border = patches.Rectangle((-1 + BORDER_MARGIN, -1 + BORDER_MARGIN),
                                       CANVAS_W - 2*BORDER_MARGIN,
                                       CANVAS_H - 2*BORDER_MARGIN,
                                       linewidth=1, edgecolor=BLUE, facecolor='none')
    ax.add_patch(canvas_border)

    # Title block dimensions
    title_block_y = -1 + BORDER_MARGIN
    title_block_top = title_block_y + TITLE_BLOCK_H
    available_height = (CANVAS_H - 1) - title_block_top

    # Calculate panel centers and paper positions
    # Left panel: center at PANEL_W/2 - 1 = 8
    # Right panel: center at PANEL_W + PANEL_GAP + PANEL_W/2 - 1 = 28
    left_center = PANEL_W / 2 - 1
    right_center = PANEL_W + PANEL_GAP + PANEL_W / 2 - 1

    front_paper_x = left_center - paper_w / 2
    back_paper_x = right_center - paper_w / 2
    paper_y = title_block_top + (available_height - paper_h) / 2

    # ===== DRAW FRONT PANEL (LEFT) =====
    paper_bg = paper_style.get('background', '#FFFFFF') if paper_style else '#FFFFFF'
    paper_border = paper_style.get('border') if paper_style else None

    # Draw front paper
    if paper_border:
        draw_border_inset(ax, front_paper_x, paper_y, paper_w, paper_h, paper_border, paper_bg)
        paper_edge = patches.Rectangle((front_paper_x, paper_y), paper_w, paper_h,
                                        linewidth=0.8, edgecolor=BLUE, facecolor='none')
        ax.add_patch(paper_edge)
    else:
        paper_rect = patches.Rectangle((front_paper_x, paper_y), paper_w, paper_h,
                                        linewidth=0.8, edgecolor=BLUE, facecolor=paper_bg)
        ax.add_patch(paper_rect)

    # Front image position
    img_w = front['img_dims']['width']
    img_h = front['img_dims']['height']
    img_left = front['img_pos']['left']
    img_top_margin = front['img_pos']['top']
    img_x = front_paper_x + img_left
    img_y = paper_y + paper_h - img_top_margin - img_h

    # Draw front image
    image_path = image_path_landscape if img_w > img_h else image_path_portrait
    def render_front_image():
        if image_path and os.path.exists(image_path):
            try:
                sample_img = mpimg.imread(image_path)
                ax.imshow(sample_img, extent=[img_x, img_x + img_w, img_y, img_y + img_h],
                         aspect='auto', zorder=2)
            except Exception:
                ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"",
                        ha='center', va='center', color='#666666', fontsize=15, fontweight='bold')
        else:
            ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"",
                    ha='center', va='center', color='#666666', fontsize=15, fontweight='bold')
    draw_content_block(ax, img_x, img_y, img_w, img_h, img_style, render_front_image)

    # Front caption position
    caption_w = front['caption_dims']['width']
    caption_h = front['caption_dims']['height']
    caption_x = front_paper_x + front['caption_pos']['left']
    caption_y = paper_y + paper_h - front['caption_pos']['top'] - caption_h

    # Load sample text
    sample_text = None
    if text_path and os.path.exists(text_path):
        try:
            with open(text_path, 'r') as f:
                sample_text = f.read().strip()
        except Exception:
            pass

    text_color = font_color if font_color else '#000000'
    special_mode = front.get('special')
    gutter = front.get('gutter', 0.25)

    # Draw front caption
    if special_mode == 'double_col':
        col_w = (caption_w - gutter) / 2
        col1_x = caption_x
        col2_x = caption_x + col_w + gutter
        rule_x = caption_x + col_w + gutter / 2  # Center of gutter

        # Get border color for column rule
        caption_border = caption_style.get('border', {}) if caption_style else {}
        rule_color = caption_border.get('color', '#000000')

        col1_text, col2_text = '', ''
        if sample_text:
            chars_per_col = int(col_w * 7)
            wrapped = textwrap.fill(sample_text, width=chars_per_col)
            lines = wrapped.split('\n')
            mid = len(lines) // 2
            col1_text = '\n'.join(lines[:mid]) if mid > 0 else lines[0] if lines else ''
            col2_text = '\n'.join(lines[mid:]) if mid < len(lines) else ''

        def render_double_col():
            # Draw column rule (vertical line in center of gutter)
            ax.plot([rule_x, rule_x], [caption_y, caption_y + caption_h],
                    color=rule_color, linewidth=0.5, zorder=5)
            if sample_text:
                ax.text(col1_x + 0.1, caption_y + caption_h - 0.1, col1_text,
                        ha='left', va='top', color=text_color, fontsize=12, wrap=True)
                ax.text(col2_x + 0.1, caption_y + caption_h - 0.1, col2_text,
                        ha='left', va='top', color=text_color, fontsize=12, wrap=True)
            else:
                ax.text(caption_x + caption_w/2, caption_y + caption_h/2, "CAPTION",
                        ha='center', va='center', color='#666666', fontsize=13, alpha=0.5)

        draw_content_block(ax, caption_x, caption_y, caption_w, caption_h, caption_style, render_double_col)
    else:
        def render_caption():
            if sample_text:
                chars_per_line = int(caption_w * 7)
                wrapped = textwrap.fill(sample_text, width=chars_per_line)
                ax.text(caption_x + 0.1, caption_y + caption_h - 0.1, wrapped,
                        ha='left', va='top', color=text_color, fontsize=12)
            else:
                ax.text(caption_x + caption_w/2, caption_y + caption_h/2, "CAPTION TEXT\n(Greeked)",
                        ha='center', va='center', color='#666666', fontsize=13, alpha=0.6, style='italic')
        draw_content_block(ax, caption_x, caption_y, caption_w, caption_h, caption_style, render_caption)

    # Front dimensions
    caption_top = caption_y + caption_h
    if 'top' in front['img_pos']:
        d1_x = front_paper_x - 1.0
        draw_dim_line(ax, d1_x, paper_y + paper_h, img_y + img_h, f"{img_top_margin}\"", dim_id="D1")
    draw_dim_line(ax, front_paper_x - 1.0, img_y, img_y + img_h, f"{img_h:.2f}\"", dim_id="D13")
    img_bottom_margin = img_y - paper_y
    if img_bottom_margin > 0.1:
        draw_dim_line(ax, front_paper_x - 1.0, paper_y, img_y, f"{img_bottom_margin:.2f}\"", dim_id="D14")
    gap_distance = img_y - caption_top
    if gap_distance > 0.1:
        draw_dim_line(ax, front_paper_x - 0.5, img_y, caption_top, f"{gap_distance:.2f}\"", dim_id="D5")
    draw_dim_line(ax, front_paper_x + paper_w + 0.5, paper_y + paper_h, caption_top,
                  f"{(paper_y + paper_h) - caption_top:.2f}\"", dim_id="D4")
    if caption_h > 0.1:
        draw_dim_line(ax, front_paper_x + paper_w + 0.5, caption_y, caption_top, f"{caption_h:.2f}\"", dim_id="D6")
    bottom_margin = caption_y - paper_y
    if bottom_margin > 0.1:
        draw_dim_line(ax, front_paper_x + paper_w + 0.5, paper_y, caption_y, f"{bottom_margin:.2f}\"", dim_id="D12")
    left_margin = img_x - front_paper_x
    draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, front_paper_x, img_x, f"{left_margin:.2f}\"", dim_id="D2")
    draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, img_x, img_x + img_w, f"{img_w:.2f}\"", dim_id="D16")
    right_margin = (front_paper_x + paper_w) - (img_x + img_w)
    draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, img_x + img_w, front_paper_x + paper_w, f"{right_margin:.2f}\"", dim_id="D3")
    draw_horizontal_dim_line(ax, paper_y - 0.5, front_paper_x, caption_x, f"{caption_x - front_paper_x:.2f}\"", dim_id="D9")
    draw_horizontal_dim_line(ax, paper_y - 0.5, caption_x, caption_x + caption_w, f"{caption_w:.2f}\"", dim_id="D10")
    caption_right_margin = (front_paper_x + paper_w) - (caption_x + caption_w)
    if caption_right_margin > 0.1:
        draw_horizontal_dim_line(ax, paper_y - 0.5, caption_x + caption_w, front_paper_x + paper_w, f"{caption_right_margin:.2f}\"", dim_id="D15")
    draw_horizontal_dim_line(ax, paper_y - 1.0, front_paper_x, front_paper_x + paper_w, f"{paper_w}\"", dim_id="D7")
    draw_dim_line(ax, front_paper_x + paper_w + 1.0, paper_y, paper_y + paper_h, f"{paper_h}\"", dim_id="D8")

    # ===== DRAW BACK PANEL (RIGHT) =====
    back_paper_bg = back_paper_style.get('background', '#FFFFFF') if back_paper_style else '#FFFFFF'
    back_paper_border = back_paper_style.get('border') if back_paper_style else None

    # Draw back paper
    if back_paper_border:
        draw_border_inset(ax, back_paper_x, paper_y, paper_w, paper_h, back_paper_border, back_paper_bg)
        paper_edge = patches.Rectangle((back_paper_x, paper_y), paper_w, paper_h,
                                        linewidth=0.8, edgecolor=BLUE, facecolor='none')
        ax.add_patch(paper_edge)
    else:
        paper_rect = patches.Rectangle((back_paper_x, paper_y), paper_w, paper_h,
                                        linewidth=0.8, edgecolor=BLUE, facecolor=back_paper_bg)
        ax.add_patch(paper_rect)

    # Back note position (centered)
    note_dims = back.get('note_dims', {'width': 6, 'height': 9})
    note_w = note_dims['width']
    note_h = note_dims['height']
    note_x = back_paper_x + (paper_w - note_w) / 2
    note_y = paper_y + (paper_h - note_h) / 2

    # Load personal note
    note_text = None
    if personal_note_path and os.path.exists(personal_note_path):
        try:
            with open(personal_note_path, 'r') as f:
                note_text = f.read().strip()
        except Exception:
            pass

    back_text_color = back_font_color if back_font_color else '#000000'

    def render_note():
        if note_text:
            chars_per_line = int(note_w * 7)
            wrapped = textwrap.fill(note_text, width=chars_per_line)
            ax.text(note_x + 0.1, note_y + note_h - 0.1, wrapped,
                    ha='left', va='top', color=back_text_color, fontsize=12)
        else:
            ax.text(note_x + note_w/2, note_y + note_h/2, "PERSONAL NOTE\n(Greeked)",
                    ha='center', va='center', color='#666666', fontsize=13, alpha=0.6, style='italic')
    draw_content_block(ax, note_x, note_y, note_w, note_h, back_note_style, render_note)

    # Back dimensions
    left_margin_back = note_x - back_paper_x
    right_margin_back = (back_paper_x + paper_w) - (note_x + note_w)
    top_margin_back = (paper_y + paper_h) - (note_y + note_h)
    bottom_margin_back = note_y - paper_y
    draw_dim_line(ax, back_paper_x - 0.5, paper_y + paper_h, note_y + note_h, f"{top_margin_back:.2f}\"", dim_id="D1")
    draw_dim_line(ax, back_paper_x - 0.5, note_y, note_y + note_h, f"{note_h:.2f}\"", dim_id="D2")
    draw_dim_line(ax, back_paper_x - 0.5, paper_y, note_y, f"{bottom_margin_back:.2f}\"", dim_id="D3")
    draw_horizontal_dim_line(ax, paper_y - 0.5, back_paper_x, note_x, f"{left_margin_back:.2f}\"", dim_id="D4")
    draw_horizontal_dim_line(ax, paper_y - 0.5, note_x, note_x + note_w, f"{note_w:.2f}\"", dim_id="D5")
    draw_horizontal_dim_line(ax, paper_y - 0.5, note_x + note_w, back_paper_x + paper_w, f"{right_margin_back:.2f}\"", dim_id="D6")
    draw_horizontal_dim_line(ax, paper_y - 1.0, back_paper_x, back_paper_x + paper_w, f"{paper_w}\"", dim_id="D7")
    draw_dim_line(ax, back_paper_x + paper_w + 0.5, paper_y, paper_y + paper_h, f"{paper_h}\"", dim_id="D8")

    # ===== SHARED TITLE BLOCK =====
    title_block_x = -1 + BORDER_MARGIN
    title_block_w = CANVAS_W - 2 * BORDER_MARGIN

    title_block_border = patches.Rectangle((title_block_x, title_block_y), title_block_w, TITLE_BLOCK_H,
                                           linewidth=2, edgecolor=BLUE, facecolor='white')
    ax.add_patch(title_block_border)

    # Divide into 3 sections: Front info | Notes | Back info
    section_w = title_block_w / 3
    divider1_x = title_block_x + section_w
    divider2_x = title_block_x + section_w * 2
    ax.plot([divider1_x, divider1_x], [title_block_y, title_block_y + TITLE_BLOCK_H], color=BLUE, linewidth=1.5)
    ax.plot([divider2_x, divider2_x], [title_block_y, title_block_y + TITLE_BLOCK_H], color=BLUE, linewidth=1.5)

    # Front section (left)
    front_theme_name = front_theme.get('name', 'Theme')
    ax.text(title_block_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.4, f"{title.upper()} - FRONT",
            fontsize=16, fontweight='bold', color=BLUE)
    ax.text(title_block_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.8, front_theme_name.upper(),
            fontsize=15, fontweight='bold', color=BLUE)
    font_color_display = font_color if font_color else "black"
    front_style_info = (
        f"{format_style_for_display(paper_style, 'paper')}\n"
        f"{format_style_for_display(img_style, 'img')}\n"
        f"{format_style_for_display(caption_style, 'caption')}, font={font_color_display}"
    )
    ax.text(title_block_x + 0.2, title_block_y + 0.9, front_style_info,
            fontsize=10, va='top', color='#333333', family='monospace')

    # Notes section (center)
    ax.text(divider1_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.4, "INSTALLATION DATA",
            fontsize=13, fontweight='bold', color=BLUE)
    ax.text(divider1_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.7, notes,
            fontsize=11, va='top', color='#333333', wrap=True)
    ax.text(divider1_x + 0.2, title_block_y + 0.5, f"Paper Size: {paper_w}\" × {paper_h}\"",
            fontsize=12, color='#333333')

    # Back section (right)
    back_theme_name = back_theme.get('name', 'Theme')
    ax.text(divider2_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.4, f"{title.upper()} - BACK",
            fontsize=16, fontweight='bold', color=BLUE)
    ax.text(divider2_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.8, back_theme_name.upper(),
            fontsize=15, fontweight='bold', color=BLUE)
    back_font_display = back_font_color if back_font_color else "black"
    back_style_info = (
        f"{format_style_for_display(back_paper_style, 'paper')}\n"
        f"{format_style_for_display(back_note_style, 'note')}, font={back_font_display}"
    )
    ax.text(divider2_x + 0.2, title_block_y + 0.9, back_style_info,
            fontsize=10, va='top', color='#333333', family='monospace')

    # Add panel labels
    ax.text(left_center, paper_y + paper_h + 1.5, "FRONT", ha='center', fontsize=19, fontweight='bold', color=BLUE)
    ax.text(right_center, paper_y + paper_h + 1.5, "BACK", ha='center', fontsize=19, fontweight='bold', color=BLUE)

    # Clean up and save
    ax.axis('off')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Generated: {output_path}")
    return output_path


def generate_combined_html(html_files, output_dir):
    """Generate an all.html with all layouts in continuous scrollable sequence."""
    import re

    all_pages = []

    for path in html_files:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract layout name from filename
        layout_name = os.path.splitext(os.path.basename(path))[0]

        # Extract the pages-container content (greedy match to get all nested divs)
        match = re.search(r'<div class="pages-container">(.*)</div>\s*\n\s*<!-- Blueprint -->', content, re.DOTALL)
        # Extract the blueprint image
        blueprint_match = re.search(r'<div class="blueprint">.*?<img src="([^"]+)"', content, re.DOTALL)
        blueprint_img = blueprint_match.group(1) if blueprint_match else None

        if match:
            pages_content = match.group(1)
            blueprint_html = f'<div class="blueprint"><img src="{blueprint_img}" alt="Blueprint"></div>' if blueprint_img else ''
            # Add a section header for this layout
            all_pages.append(f'''
    <!-- {layout_name} -->
    <div class="layout-section" id="{layout_name}">
        <div class="layout-header">{layout_name}</div>
        <div class="pages-row">
            {pages_content}
        </div>
        {blueprint_html}
    </div>''')

    combined_pages = '\n'.join(all_pages)

    # Build navigation
    nav_items = '\n'.join([
        f'<a href="#{os.path.splitext(os.path.basename(p))[0]}" class="nav-link">{os.path.splitext(os.path.basename(p))[0]}</a>'
        for p in html_files
    ])

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>All Layouts - Continuous Scroll</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #ecf0f1;
            padding: 20px;
        }}
        .layout-section {{
            margin-bottom: 40px;
            scroll-margin-top: 20px;
        }}
        .layout-header {{
            background: #2c3e50;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 4px 4px 0 0;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .pages-row {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            background: #ddd;
            border-radius: 0 0 4px 4px;
        }}
        .page {{
            position: relative;
            overflow: hidden;
            flex-shrink: 0;
        }}
        .image-box img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        p {{
            margin: 0 0 0.5em 0;
        }}
        p:last-child {{
            margin-bottom: 0;
        }}
        .nav-sidebar {{
            position: fixed;
            right: 20px;
            top: 20px;
            background: rgba(44, 62, 80, 0.9);
            padding: 10px;
            border-radius: 4px;
            max-height: 90vh;
            overflow-y: auto;
            z-index: 100;
            font-size: 11px;
        }}
        .nav-link {{
            display: block;
            color: #ecf0f1;
            text-decoration: none;
            padding: 4px 8px;
            border-radius: 2px;
        }}
        .nav-link:hover {{
            background: #3498db;
        }}
        .blueprint {{
            text-align: center;
            padding: 20px;
            background: #ccc;
            margin-top: 10px;
        }}
        .blueprint img {{
            max-width: 100%;
            height: auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div class="nav-sidebar">
        <strong style="color: white; display: block; margin-bottom: 8px;">Jump to:</strong>
        {nav_items}
    </div>
    {combined_pages}
</body>
</html>
'''

    all_path = os.path.join(output_dir, 'all.html')
    with open(all_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated: {all_path}")
    return all_path


# Run Generator
if __name__ == "__main__":
    print(f"PrintLayoutDesigner v{VERSION}")

    batch_path = sys.argv[1] if len(sys.argv) > 1 else 'production/batch.json'
    batch_dir = os.path.dirname(batch_path) or '.'
    output_dir = os.path.join(batch_dir, 'output')

    # Clear output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    batch_entries, mode, image_path_landscape, image_path_portrait, text_path, personal_note_path, show_blueprints = load_batch(batch_path)

    if not batch_entries:
        print(f"Error: No entries in {batch_path} batch list.")
        sys.exit(1)

    # Load text content for HTML output
    text_content = None
    note_content = None
    if text_path and os.path.exists(text_path):
        with open(text_path, 'r') as f:
            text_content = f.read().strip()
    if personal_note_path and os.path.exists(personal_note_path):
        with open(personal_note_path, 'r') as f:
            note_content = f.read().strip()

    output_types = "PNG + HTML" if show_blueprints else "HTML only"
    print(f"Generating {len(batch_entries)} batch entries ({output_types})...")
    print(f"Output directory: {output_dir}")

    html_files = []

    for entry in batch_entries:
        layout_path = os.path.join(batch_dir, 'layouts', entry['layout'])
        front_theme_path = os.path.join(batch_dir, 'themes', entry['front_theme'])
        back_theme_path = os.path.join(batch_dir, 'themes', entry['back_theme'])

        # Extract names from paths for filenames (remove directory and .json extension)
        layout_name = os.path.splitext(os.path.basename(layout_path))[0]
        front_theme_name = os.path.splitext(os.path.basename(front_theme_path))[0]
        back_theme_name = os.path.splitext(os.path.basename(back_theme_path))[0]

        # Load layout and themes
        layout = load_layout(layout_path)
        front_theme = load_theme(front_theme_path)
        back_theme = load_theme(back_theme_path)

        # --- Generate combined PNG blueprint (if enabled) ---
        blueprint_filename = None
        if show_blueprints:
            blueprint_filename = f"{layout_name}_{front_theme_name}_blueprint.png"
            draw_combined_blueprint(
                filename=blueprint_filename,
                layout=layout,
                front_theme=front_theme,
                back_theme=back_theme,
                image_path_landscape=image_path_landscape,
                image_path_portrait=image_path_portrait,
                text_path=text_path,
                personal_note_path=personal_note_path,
                output_dir=output_dir
            )

        # --- Generate HTML (print preview) ---
        front = layout.get('front', {})
        img_w = front['img_dims']['width']
        img_h = front['img_dims']['height']
        image_path = image_path_landscape if img_w > img_h else image_path_portrait

        html_path = generate_html_output(
            batch_entry=entry,
            layout=layout,
            front_theme=front_theme,
            back_theme=back_theme,
            image_path=image_path,
            text_content=text_content,
            note_content=note_content,
            layout_name=f"{layout_name}_{front_theme_name}",
            output_dir=output_dir,
            blueprint_png=blueprint_filename
        )
        html_files.append(html_path)

    # Generate combined all.html
    all_path = generate_combined_html(html_files, output_dir)

    print("Done!")

    # Open all.html in browser (continuous scroll view)
    webbrowser.open('file://' + os.path.abspath(all_path))