import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for cleaner PNG output
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
import json
import os
import sys
import textwrap

# --- CONFIGURATION ---
VERSION = "3.0.0"

# Canvas drawing size
CANVAS_W = 18
CANVAS_H = 24

# Print paper size (the actual paper being designed for printing)
PAPER_W = 8.5
PAPER_H = 11

DPI = 150  # High resolution for crisp text
BLUE = '#1E3D59'
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
        print(f"Error: Theme not found: {theme_path}")
        sys.exit(1)


def load_layout(layout_path):
    """Load a layout from the given path."""
    try:
        with open(layout_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Layout not found: {layout_path}")
        sys.exit(1)


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


def load_batch(batch_path):
    """Load batch configuration from JSON file.

    Returns (batch_entries, mode, image_path_landscape, image_path_portrait, text_path, personal_note_path).
    """
    try:
        with open(batch_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Batch file not found: {batch_path}")
        sys.exit(1)

    return (
        data.get('batch', []),
        data.get('mode', 'design'),
        data.get('image_path_landscape'),
        data.get('image_path_portrait'),
        data.get('text_path'),
        data.get('personal_note_path')
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
    ax.text(x - 0.1, mid_y, label_text, ha='right', va='center', fontsize=7, color=BLUE, rotation=90)

def draw_horizontal_dim_line(ax, y, x_start, x_end, label, dim_id=None, offset=0):
    """Draws a horizontal dimension line with arrows and optional ID"""
    ax.annotate(text='', xy=(x_start, y), xytext=(x_end, y),
                arrowprops=dict(arrowstyle='<->', color=BLUE, lw=0.8))
    mid_x = (x_start + x_end) / 2
    if dim_id:
        label_text = f"{dim_id}: {label}"
    else:
        label_text = label
    ax.text(mid_x, y + 0.1 + offset, label_text, ha='center', va='bottom', fontsize=7, color=BLUE)

def draw_canvas(filename, title, layout_type, orientation,
                   paper_w, paper_h, paper_style, img_style, caption_style,
                   img_w, img_h, img_margins,
                   caption_dims, caption_pos,
                   notes, special_mode=None, gutter=None, mode="design",
                   image_path_landscape=None, image_path_portrait=None, text_path=None,
                   font_color=None, theme_name=None, output_dir='output'):
    """
    Generates a single canvas image.
    paper_w, paper_h = dimensions of the print paper (e.g., 8.5x11 or 11x14)
    paper_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    img_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    caption_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    img_margins = {'top': val, 'left': val, 'right': val}
    mode = 'design' (full canvas with dimensions) or 'print' (paper-sized, no annotations)
    image_path_landscape = path to sample image for landscape layouts (img_w > img_h)
    image_path_portrait = path to sample image for portrait layouts (img_h >= img_w)
    text_path = path to sample text file (design mode only, renders instead of label)
    (We calculate X/Y based on margins or centering logic)
    """
    # Setup canvas and paper
    fig, ax, paper_x, paper_y, title_block_top = setup_canvas(paper_w, paper_h, paper_style, mode)
    draw_paper(ax, paper_x, paper_y, paper_w, paper_h, paper_style, mode)

    # --- CALCULATE IMAGE POSITION (relative to paper, not canvas) ---
    # Default: Center Horizontal if 'left'/'right' not specified in margins
    if 'left' in img_margins:
        img_x = paper_x + img_margins['left']
    elif 'right' in img_margins:
        img_x = paper_x + paper_w - img_margins['right'] - img_w
    else:
        img_x = paper_x + (paper_w - img_w) / 2

    # Calculate Y based on Top Margin or Vertical Centering
    if 'top' in img_margins:
        img_y = paper_y + paper_h - img_margins['top'] - img_h
    elif 'center_v' in img_margins:
        img_y = paper_y + (paper_h - img_h) / 2
    else:
        img_y = paper_y + (paper_h - img_h) / 2 # Default fallback

    # Draw Image with style using draw_content_block
    def render_image():
        if mode == "design":
            image_path = image_path_landscape if img_w > img_h else image_path_portrait
            if image_path and os.path.exists(image_path):
                try:
                    sample_img = mpimg.imread(image_path)
                    ax.imshow(sample_img, extent=[img_x, img_x + img_w, img_y, img_y + img_h],
                             aspect='auto', zorder=2)
                except Exception:
                    ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"",
                            ha='center', va='center', color='#666666', fontsize=10, fontweight='bold')
            else:
                ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"",
                        ha='center', va='center', color='#666666', fontsize=10, fontweight='bold')

    draw_content_block(ax, img_x, img_y, img_w, img_h, img_style, render_image)

    # --- CALCULATE CAPTION POSITION (relative to paper) ---
    caption_w, caption_h = caption_dims

    # Caption position from absolute left/top margins
    caption_x = paper_x + caption_pos['left']
    caption_y = paper_y + paper_h - caption_pos['top'] - caption_h

    # Load sample text if path provided
    sample_text = None
    if text_path and os.path.exists(text_path):
        try:
            with open(text_path, 'r') as f:
                sample_text = f.read().strip()
        except Exception:
            sample_text = None

    # Text color for sample text (default to black)
    text_color = font_color if font_color else '#000000'

    # Draw Caption Block(s) with style using draw_content_block
    if special_mode == 'double_col':
        col_w = (caption_w - gutter) / 2
        col1_x = caption_x
        col2_x = caption_x + col_w + gutter

        # Prepare text for columns
        col1_text, col2_text = '', ''
        if mode == "design" and sample_text:
            chars_per_col = int(col_w * 12)
            wrapped = textwrap.fill(sample_text, width=chars_per_col)
            lines = wrapped.split('\n')
            mid = len(lines) // 2
            col1_text = '\n'.join(lines[:mid]) if mid > 0 else lines[0] if lines else ''
            col2_text = '\n'.join(lines[mid:]) if mid < len(lines) else ''

        def render_col1():
            if mode == "design":
                if sample_text:
                    ax.text(col1_x + 0.1, caption_y + caption_h - 0.1, col1_text,
                            ha='left', va='top', color=text_color, fontsize=7, wrap=True)
                else:
                    ax.text(col1_x + col_w/2, caption_y + caption_h/2, "CAPTION",
                            ha='center', va='center', color='#666666', fontsize=8, alpha=0.5)

        def render_col2():
            if mode == "design":
                if sample_text:
                    ax.text(col2_x + 0.1, caption_y + caption_h - 0.1, col2_text,
                            ha='left', va='top', color=text_color, fontsize=7, wrap=True)
                else:
                    ax.text(col2_x + col_w/2, caption_y + caption_h/2, "CAPTION",
                            ha='center', va='center', color='#666666', fontsize=8, alpha=0.5)

        draw_content_block(ax, col1_x, caption_y, col_w, caption_h, caption_style, render_col1)
        draw_content_block(ax, col2_x, caption_y, col_w, caption_h, caption_style, render_col2)
    else:
        def render_caption():
            if mode == "design":
                if sample_text:
                    chars_per_line = int(caption_w * 12)
                    wrapped = textwrap.fill(sample_text, width=chars_per_line)
                    ax.text(caption_x + 0.1, caption_y + caption_h - 0.1, wrapped,
                            ha='left', va='top', color=text_color, fontsize=7)
                else:
                    ax.text(caption_x + caption_w/2, caption_y + caption_h/2, "CAPTION TEXT\n(Greeked)",
                            ha='center', va='center', color='#666666', fontsize=8, alpha=0.6, style='italic')

        draw_content_block(ax, caption_x, caption_y, caption_w, caption_h, caption_style, render_caption)

    # --- TITLE BLOCK (Bottom of Canvas) - Design mode only ---
    if mode == "design":
        title_block_y = title_block_top - TITLE_BLOCK_H
        title_block_x = -1 + BORDER_MARGIN
        title_block_w = (CANVAS_W - 1 - BORDER_MARGIN) - (-1 + BORDER_MARGIN)

        # Draw title block border
        title_block_border = patches.Rectangle((title_block_x, title_block_y), title_block_w, TITLE_BLOCK_H,
                                               linewidth=2, edgecolor=BLUE, facecolor='white')
        ax.add_patch(title_block_border)

        # Divide title block into two sections: title (left) and notes (right)
        divider_x = title_block_x + title_block_w * 0.6
        ax.plot([divider_x, divider_x], [title_block_y, title_block_y + TITLE_BLOCK_H],
                color=BLUE, linewidth=1.5)

        # Title section (left side - 60%)
        ax.text(title_block_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.4, f"{title.upper()} - FRONT",
                fontsize=12, fontweight='bold', color=BLUE)
        if theme_name:
            ax.text(title_block_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.8, theme_name.upper(),
                    fontsize=12, fontweight='bold', color=BLUE)
        ax.text(title_block_x + 0.2, title_block_y + 1.2, f"Paper Size: {paper_w}\" × {paper_h}\"",
                fontsize=8, color='#333333')

        # Style information
        font_color_display = font_color if font_color else "black"
        style_info = (
            f"{format_style_for_display(paper_style, 'paper')}\n"
            f"{format_style_for_display(img_style, 'img')}\n"
            f"{format_style_for_display(caption_style, 'caption')}, font={font_color_display}"
        )
        ax.text(title_block_x + 0.2, title_block_y + 0.9, style_info,
                fontsize=6, va='top', color='#333333', family='monospace')

        # Notes section (right side - 40%)
        ax.text(divider_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.4, "INSTALLATION DATA",
                fontsize=8, fontweight='bold', color=BLUE)
        ax.text(divider_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.7, notes,
                fontsize=7, va='top', color='#333333', wrap=True)

    # --- DIMENSIONS (Visual Aids) - Design mode only ---
    if mode == "design":
        # All dimension lines are positioned outside the paper
        # Calculate caption boundaries
        caption_top = caption_y + caption_h
        caption_bottom = caption_y
        caption_left = caption_x
        caption_right = caption_x + caption_w

        # D1: Top Margin Dimension (from top of paper to top of image)
        # Position: 1 inch left of paper edge
        if 'top' in img_margins:
            d1_x = paper_x - 1.0
            draw_dim_line(ax, d1_x, paper_y + paper_h, img_y + img_h, f"{img_margins['top']}\"", dim_id="D1")

        # D13: Image height
        # Position: 1 inch left of paper edge (same line as D1)
        d13_x = paper_x - 1.0
        draw_dim_line(ax, d13_x, img_y, img_y + img_h, f"{img_h:.2f}\"", dim_id="D13")

        # D14: Bottom of image to bottom of paper
        # Position: 1 inch left of paper edge (same line as D1, D13)
        img_bottom_margin = img_y - paper_y
        if img_bottom_margin > 0.1:  # Only show if there's a meaningful margin
            d14_x = paper_x - 1.0
            draw_dim_line(ax, d14_x, paper_y, img_y, f"{img_bottom_margin:.2f}\"", dim_id="D14")

        # D5: Dimension between bottom of image and top of caption (gap)
        # Position: 1/2 inch left of paper edge (same line as D1)
        gap_distance = img_y - caption_top
        if gap_distance > 0.1:  # Only show if there's a meaningful gap
            d5_x = paper_x - 0.5
            draw_dim_line(ax, d5_x, img_y, caption_top, f"{gap_distance:.2f}\"", dim_id="D5")

        # D4: Dimension from top of paper to top of caption
        # Position: 0.5 inch right of paper edge
        distance_sheet_to_caption = (paper_y + paper_h) - caption_top
        d4_x = paper_x + paper_w + 0.5
        draw_dim_line(ax, d4_x, paper_y + paper_h, caption_top, f"{distance_sheet_to_caption:.2f}\"", dim_id="D4")

        # D6: Caption block height (vertical dimension of caption area)
        # Position: 0.5 inch right of paper edge (same line as D4)
        if caption_h > 0.1:  # Only show if there's a meaningful caption height
            d6_x = paper_x + paper_w + 0.5
            draw_dim_line(ax, d6_x, caption_bottom, caption_top, f"{caption_h:.2f}\"", dim_id="D6")

        # D12: Bottom margin (from bottom of caption block to bottom of paper)
        # Position: 0.5 inch right of paper edge (same line as D4, D6)
        bottom_margin = caption_y - paper_y
        if bottom_margin > 0.1:  # Only show if there's a meaningful margin
            d12_x = paper_x + paper_w + 0.5
            draw_dim_line(ax, d12_x, paper_y, caption_y, f"{bottom_margin:.2f}\"", dim_id="D12")

        # D2: Left Margin Dimension (from left edge of paper to left of image)
        # Position: 1/2 inch above paper top
        left_margin = img_x - paper_x
        draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, paper_x, img_x, f"{left_margin:.2f}\"", dim_id="D2")

        # D16: Image width
        # Position: 1/2 inch above paper top (same line as D2)
        draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, img_x, img_x + img_w, f"{img_w:.2f}\"", dim_id="D16")

        # D3: Right Margin Dimension (from right of image to right edge of paper)
        # Position: 1/2 inch above paper top (same line as D2)
        right_margin = (paper_x + paper_w) - (img_x + img_w)
        draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, img_x + img_w, paper_x + paper_w, f"{right_margin:.2f}\"", dim_id="D3")

        # D9: Caption box left edge position (from left edge of paper to left of caption box)
        # Position: 0.5 inch below paper bottom
        caption_left_margin = caption_x - paper_x
        draw_horizontal_dim_line(ax, paper_y - 0.5, paper_x, caption_x, f"{caption_left_margin:.2f}\"", dim_id="D9")

        # D10: Caption box width
        # Position: 0.5 inch below paper bottom (same line as D9)
        draw_horizontal_dim_line(ax, paper_y - 0.5, caption_x, caption_x + caption_w, f"{caption_w:.2f}\"", dim_id="D10")

        # D15: Caption box right margin (from right edge of caption box to right edge of paper)
        # Position: 0.5 inch below paper bottom (same line as D9, D10)
        caption_right_margin = (paper_x + paper_w) - (caption_x + caption_w)
        if caption_right_margin > 0.1:  # Only show if there's a meaningful margin
            draw_horizontal_dim_line(ax, paper_y - 0.5, caption_x + caption_w, paper_x + paper_w, f"{caption_right_margin:.2f}\"", dim_id="D15")

        # D11: Double column gutter width (only for double_col layouts)
        # Position: 1/2 inch above paper top (same line as D2/D3)
        if special_mode == 'double_col' and gutter:
            col_w = (caption_w - gutter) / 2
            gutter_x_start = caption_x + col_w
            gutter_x_end = caption_x + col_w + gutter
            draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, gutter_x_start, gutter_x_end, f"{gutter:.2f}\"", dim_id="D11")

        # D7: Overall paper width
        # Position: 1 inch below paper bottom
        draw_horizontal_dim_line(ax, paper_y - 1.0, paper_x, paper_x + paper_w, f"{paper_w}\"", dim_id="D7", offset=0)

        # D8: Overall paper height
        # Position: 1 inch right of paper edge
        draw_dim_line(ax, paper_x + paper_w + 1.0, paper_y, paper_y + paper_h, f"{paper_h}\"", dim_id="D8")

    # Clean up
    ax.axis('off')

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    if mode == "print":
        # Print mode: save exact figure size, no cropping
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    else:
        # Design mode: tight crop with padding for dimension lines
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Generated: {output_path}")

def draw_back(filename, title, paper_w, paper_h, paper_style, note_style,
              note_dims, note_font_color, mode, personal_note_path, theme_name=None, output_dir='output'):
    """Generate back side with centered personal note.

    paper_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    note_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    note_dims = [width, height] - dimensions of note area (default 6x9)
    note_font_color = hex color for note text
    """
    # Setup canvas and paper
    fig, ax, paper_x, paper_y, title_block_top = setup_canvas(paper_w, paper_h, paper_style, mode)
    draw_paper(ax, paper_x, paper_y, paper_w, paper_h, paper_style, mode)

    # Calculate note position (centered on paper)
    note_w, note_h = note_dims
    note_x = paper_x + (paper_w - note_w) / 2
    note_y = paper_y + (paper_h - note_h) / 2

    # Load personal note text if path provided
    note_text = None
    if personal_note_path and os.path.exists(personal_note_path):
        try:
            with open(personal_note_path, 'r') as f:
                note_text = f.read().strip()
        except Exception:
            note_text = None

    # Text color for note (default to black)
    text_color = note_font_color if note_font_color else '#000000'

    # Draw note block using draw_content_block
    def render_note():
        if mode == "design":
            if note_text:
                chars_per_line = int(note_w * 12)
                wrapped = textwrap.fill(note_text, width=chars_per_line)
                ax.text(note_x + 0.1, note_y + note_h - 0.1, wrapped,
                        ha='left', va='top', color=text_color, fontsize=7)
            else:
                ax.text(note_x + note_w/2, note_y + note_h/2, "PERSONAL NOTE\n(Greeked)",
                        ha='center', va='center', color='#666666', fontsize=8, alpha=0.6, style='italic')

    draw_content_block(ax, note_x, note_y, note_w, note_h, note_style, render_note)

    # --- TITLE BLOCK (Bottom of Canvas) - Design mode only ---
    if mode == "design":
        title_block_y = title_block_top - TITLE_BLOCK_H
        title_block_x = -1 + BORDER_MARGIN
        title_block_w = (CANVAS_W - 1 - BORDER_MARGIN) - (-1 + BORDER_MARGIN)

        # Draw title block border
        title_block_border = patches.Rectangle((title_block_x, title_block_y), title_block_w, TITLE_BLOCK_H,
                                               linewidth=2, edgecolor=BLUE, facecolor='white')
        ax.add_patch(title_block_border)

        # Divide title block into two sections
        divider_x = title_block_x + title_block_w * 0.6
        ax.plot([divider_x, divider_x], [title_block_y, title_block_y + TITLE_BLOCK_H],
                color=BLUE, linewidth=1.5)

        # Title section (left side - 60%)
        ax.text(title_block_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.4, f"{title.upper()} - BACK",
                fontsize=12, fontweight='bold', color=BLUE)
        if theme_name:
            ax.text(title_block_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.8, theme_name.upper(),
                    fontsize=12, fontweight='bold', color=BLUE)
        ax.text(title_block_x + 0.2, title_block_y + 1.2, f"Paper Size: {paper_w}\" × {paper_h}\"",
                fontsize=8, color='#333333')

        # Style information
        font_color_display = note_font_color if note_font_color else "black"
        style_info = (
            f"{format_style_for_display(paper_style, 'paper')}\n"
            f"{format_style_for_display(note_style, 'note')}, font={font_color_display}"
        )
        ax.text(title_block_x + 0.2, title_block_y + 0.9, style_info,
                fontsize=6, va='top', color='#333333', family='monospace')

        # Notes section (right side - 40%)
        ax.text(divider_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.4, "BACK SIDE",
                fontsize=8, fontweight='bold', color=BLUE)
        note_info = f"Note Area: {note_w}\" × {note_h}\"\nCentered on paper"
        ax.text(divider_x + 0.2, title_block_y + TITLE_BLOCK_H - 0.7, note_info,
                fontsize=7, va='top', color='#333333', wrap=True)

    # --- DIMENSIONS (Visual Aids) - Design mode only ---
    if mode == "design":
        # Calculate margins
        left_margin = note_x - paper_x
        right_margin = (paper_x + paper_w) - (note_x + note_w)
        top_margin = (paper_y + paper_h) - (note_y + note_h)
        bottom_margin = note_y - paper_y

        # D1: Top margin (from top of paper to top of note)
        d1_x = paper_x - 0.5
        draw_dim_line(ax, d1_x, paper_y + paper_h, note_y + note_h, f"{top_margin:.2f}\"", dim_id="D1")

        # D2: Note height
        d2_x = paper_x - 0.5
        draw_dim_line(ax, d2_x, note_y, note_y + note_h, f"{note_h:.2f}\"", dim_id="D2")

        # D3: Bottom margin (from bottom of note to bottom of paper)
        d3_x = paper_x - 0.5
        draw_dim_line(ax, d3_x, paper_y, note_y, f"{bottom_margin:.2f}\"", dim_id="D3")

        # D4: Left margin
        draw_horizontal_dim_line(ax, paper_y - 0.5, paper_x, note_x, f"{left_margin:.2f}\"", dim_id="D4")

        # D5: Note width
        draw_horizontal_dim_line(ax, paper_y - 0.5, note_x, note_x + note_w, f"{note_w:.2f}\"", dim_id="D5")

        # D6: Right margin
        draw_horizontal_dim_line(ax, paper_y - 0.5, note_x + note_w, paper_x + paper_w, f"{right_margin:.2f}\"", dim_id="D6")

        # D7: Overall paper width
        draw_horizontal_dim_line(ax, paper_y - 1.0, paper_x, paper_x + paper_w, f"{paper_w}\"", dim_id="D7", offset=0)

        # D8: Overall paper height
        draw_dim_line(ax, paper_x + paper_w + 0.5, paper_y, paper_y + paper_h, f"{paper_h}\"", dim_id="D8")

    # Clean up
    ax.axis('off')

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    if mode == "print":
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    else:
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Generated: {output_path}")

# Run Generator
if __name__ == "__main__":
    print(f"PrintLayoutDesigner v{VERSION}")

    batch_path = sys.argv[1] if len(sys.argv) > 1 else 'production/batch.json'
    batch_dir = os.path.dirname(batch_path) or '.'
    output_dir = os.path.join(batch_dir, 'output')

    batch_entries, mode, image_path_landscape, image_path_portrait, text_path, personal_note_path = load_batch(batch_path)

    if not batch_entries:
        print(f"Error: No entries in {batch_path} batch list.")
        sys.exit(1)

    print(f"Generating {len(batch_entries)} batch entries (front + back) in {mode} mode...")
    print(f"Output directory: {output_dir}")
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

        # Build styles from theme + layout
        paper_style, img_style, caption_style, font_color = build_front_styles(layout, front_theme)
        back_paper_style, back_note_style, back_font_color = build_back_styles(layout, back_theme)

        # Extract geometry from layout
        front = layout.get('front', {})
        back = layout.get('back', {})

        # Generate filenames: layout_side_theme.png
        front_filename = f"{layout_name}_front_{front_theme_name}.png"
        back_filename = f"{layout_name}_back_{back_theme_name}.png"

        # Generate front side
        draw_canvas(
            filename=front_filename,
            title=layout.get('title', layout_name),
            layout_type="Standard",
            orientation="Portrait",
            paper_w=layout['paper_size']['width'],
            paper_h=layout['paper_size']['height'],
            paper_style=paper_style,
            img_style=img_style,
            caption_style=caption_style,
            img_w=front['img_dims']['width'],
            img_h=front['img_dims']['height'],
            img_margins={'left': front['img_pos']['left'], 'top': front['img_pos']['top']},
            caption_dims=[front['caption_dims']['width'], front['caption_dims']['height']],
            caption_pos=front['caption_pos'],
            notes=layout.get('notes', ''),
            special_mode=front.get('special'),
            gutter=front.get('gutter'),
            mode=mode,
            image_path_landscape=image_path_landscape,
            image_path_portrait=image_path_portrait,
            text_path=text_path,
            font_color=font_color,
            theme_name=front_theme_name,
            output_dir=output_dir
        )

        # Generate back side
        note_dims = back.get('note_dims', {'width': 6, 'height': 9})
        draw_back(
            filename=back_filename,
            title=layout.get('title', layout_name),
            paper_w=layout['paper_size']['width'],
            paper_h=layout['paper_size']['height'],
            paper_style=back_paper_style,
            note_style=back_note_style,
            note_dims=[note_dims['width'], note_dims['height']],
            note_font_color=back_font_color,
            mode=mode,
            personal_note_path=personal_note_path,
            theme_name=back_theme_name,
            output_dir=output_dir
        )

    print("Done! Check your folder.")