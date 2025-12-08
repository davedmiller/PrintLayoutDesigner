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
VERSION = "2.0.0"

# Canvas drawing size
CANVAS_W = 18
CANVAS_H = 24

# Print paper size (the actual paper being designed for printing)
PAPER_W = 8.5
PAPER_H = 11

DPI = 150  # High resolution for crisp text
BLUE = '#1E3D59'
CANVAS_COLOR = '#F2F2F2'

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
                   paper_w, paper_h, paper_style, img_style, txt_style,
                   img_w, img_h, img_margins,
                   txt_dims, txt_pos_desc,
                   notes, special_mode=None, gutter=None, mode="design",
                   image_path_landscape=None, image_path_portrait=None, text_path=None,
                   font_color=None):
    """
    Generates a single canvas image.
    paper_w, paper_h = dimensions of the print paper (e.g., 8.5x11 or 11x14)
    paper_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    img_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    txt_style = {'background': hex, 'border': {'color': hex, 'width': val}}
    img_margins = {'top': val, 'left': val, 'right': val}
    mode = 'design' (full canvas with dimensions) or 'print' (paper-sized, no annotations)
    image_path_landscape = path to sample image for landscape layouts (img_w > img_h)
    image_path_portrait = path to sample image for portrait layouts (img_h >= img_w)
    text_path = path to sample text file (design mode only, renders instead of label)
    (We calculate X/Y based on margins or centering logic)
    """
    # Setup canvas based on mode
    if mode == "print":
        # Print mode: canvas = paper size, paper at origin
        fig, ax = plt.subplots(figsize=(paper_w, paper_h), dpi=DPI)
        ax.set_xlim(0, paper_w)
        ax.set_ylim(0, paper_h)
        # Remove all margins so axes fills entire figure
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        paper_x, paper_y = 0, 0
        # Use paper background color for figure
        paper_bg = paper_style.get('background', '#FFFFFF') if paper_style else '#FFFFFF'
        fig.patch.set_facecolor(paper_bg)
        ax.set_facecolor(paper_bg)
    else:
        # Design mode: full canvas with dimensions and title block
        fig, ax = plt.subplots(figsize=(CANVAS_W, CANVAS_H), dpi=DPI)
        ax.set_xlim(-1, CANVAS_W - 1)
        ax.set_ylim(-1, CANVAS_H - 1)
        fig.patch.set_facecolor(CANVAS_COLOR)
        ax.set_facecolor(CANVAS_COLOR)

        # Draw canvas border (1/4 inch from edge)
        BORDER_MARGIN = 0.25
        canvas_border = patches.Rectangle((-1 + BORDER_MARGIN, -1 + BORDER_MARGIN),
                                         CANVAS_W - 2*BORDER_MARGIN,
                                         CANVAS_H - 2*BORDER_MARGIN,
                                         linewidth=1, edgecolor=BLUE, facecolor='none')
        ax.add_patch(canvas_border)

        # Title block dimensions (defined here so we can use for paper positioning)
        title_block_h = 2.5
        title_block_y = -1 + BORDER_MARGIN
        title_block_top = title_block_y + title_block_h

        # Calculate paper position - centered on canvas
        canvas_center_x = CANVAS_W/2 - 1
        paper_x = canvas_center_x - paper_w/2

        # Vertical: center between top of canvas and top of title block
        available_height = (CANVAS_H - 1) - title_block_top
        paper_y = title_block_top + (available_height - paper_h) / 2

    # Draw Print Paper with style
    paper_bg = paper_style.get('background', '#FFFFFF') if paper_style else '#FFFFFF'
    paper_border = paper_style.get('border') if paper_style else None

    if paper_border:
        # Draw inset border (border color at edges, background in center)
        draw_border_inset(ax, paper_x, paper_y, paper_w, paper_h, paper_border, paper_bg)
        # Add thin blue edge for canvas visibility (design mode only)
        if mode == "design":
            paper_edge = patches.Rectangle((paper_x, paper_y), paper_w, paper_h,
                                            linewidth=0.8, edgecolor=BLUE, facecolor='none')
            ax.add_patch(paper_edge)
    else:
        # No border - just draw paper with background
        edge_color = BLUE if mode == "design" else 'none'
        paper_rect = patches.Rectangle((paper_x, paper_y), paper_w, paper_h,
                                        linewidth=0.8, edgecolor=edge_color, facecolor=paper_bg)
        ax.add_patch(paper_rect)

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

    # Draw Image with style
    img_bg = img_style.get('background') if img_style else None
    img_border = img_style.get('border') if img_style else None

    # Draw outset border if specified
    draw_border_outset(ax, img_x, img_y, img_w, img_h, img_border)

    # Draw image rectangle with background
    img_fill = img_bg if img_bg else 'white'
    img_rect = patches.Rectangle((img_x, img_y), img_w, img_h,
                                 linewidth=0, edgecolor='none', facecolor=img_fill)
    ax.add_patch(img_rect)
    if mode == "design":
        # Select image based on orientation (landscape: width > height, portrait: height >= width)
        image_path = image_path_landscape if img_w > img_h else image_path_portrait
        if image_path and os.path.exists(image_path):
            # Render actual image, scaled to fit the image box
            try:
                sample_img = mpimg.imread(image_path)
                ax.imshow(sample_img, extent=[img_x, img_x + img_w, img_y, img_y + img_h],
                         aspect='auto', zorder=2)
            except Exception as e:
                # Fall back to label if image can't be loaded
                ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"",
                        ha='center', va='center', color='#666666', fontsize=10, fontweight='bold')
        else:
            ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"",
                    ha='center', va='center', color='#666666', fontsize=10, fontweight='bold')

    # --- CALCULATE TEXT POSITION (relative to paper) ---
    txt_w, txt_h = txt_dims

    # Text position from absolute left/top margins
    txt_x = paper_x + txt_pos_desc['left']
    txt_y = paper_y + paper_h - txt_pos_desc['top'] - txt_h

    # Draw Text Block(s) with style
    txt_bg = txt_style.get('background') if txt_style else None
    txt_border = txt_style.get('border') if txt_style else None
    txt_fill = txt_bg if txt_bg else 'white'

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

    if special_mode == 'double_col':
        # Split into two columns
        col_w = (txt_w - gutter) / 2
        # Draw outset borders for each column if specified
        draw_border_outset(ax, txt_x, txt_y, col_w, txt_h, txt_border)
        draw_border_outset(ax, txt_x + col_w + gutter, txt_y, col_w, txt_h, txt_border)
        # Draw column rectangles
        col_1 = patches.Rectangle((txt_x, txt_y), col_w, txt_h, lw=0, ec='none', fc=txt_fill)
        col_2 = patches.Rectangle((txt_x + col_w + gutter, txt_y), col_w, txt_h, lw=0, ec='none', fc=txt_fill)
        ax.add_patch(col_1)
        ax.add_patch(col_2)
        if mode == "design":
            if sample_text:
                # Wrap text for column width (approx 12 chars per inch at fontsize 7)
                chars_per_col = int(col_w * 12)
                wrapped = textwrap.fill(sample_text, width=chars_per_col)
                lines = wrapped.split('\n')
                # Split lines between columns
                mid = len(lines) // 2
                col1_text = '\n'.join(lines[:mid]) if mid > 0 else lines[0] if lines else ''
                col2_text = '\n'.join(lines[mid:]) if mid < len(lines) else ''
                ax.text(txt_x + 0.1, txt_y + txt_h - 0.1, col1_text,
                        ha='left', va='top', color=text_color, fontsize=7, wrap=True)
                ax.text(txt_x + col_w + gutter + 0.1, txt_y + txt_h - 0.1, col2_text,
                        ha='left', va='top', color=text_color, fontsize=7, wrap=True)
            else:
                ax.text(txt_x + col_w/2, txt_y + txt_h/2, "TXT", ha='center', va='center', color='#666666', fontsize=8, alpha=0.5)
                ax.text(txt_x + col_w + gutter + col_w/2, txt_y + txt_h/2, "TXT", ha='center', va='center', color='#666666', fontsize=8, alpha=0.5)
    else:
        # Draw outset border if specified
        draw_border_outset(ax, txt_x, txt_y, txt_w, txt_h, txt_border)
        # Draw text rectangle
        txt_rect = patches.Rectangle((txt_x, txt_y), txt_w, txt_h,
                                     linewidth=0, edgecolor='none', facecolor=txt_fill)
        ax.add_patch(txt_rect)
        if mode == "design":
            if sample_text:
                # Wrap text for box width (approx 12 chars per inch at fontsize 7)
                chars_per_line = int(txt_w * 12)
                wrapped = textwrap.fill(sample_text, width=chars_per_line)
                ax.text(txt_x + 0.1, txt_y + txt_h - 0.1, wrapped,
                        ha='left', va='top', color=text_color, fontsize=7)
            else:
                ax.text(txt_x + txt_w/2, txt_y + txt_h/2, "CAPTION TEXT\n(Greeked)",
                        ha='center', va='center', color='#666666', fontsize=8, alpha=0.6, style='italic')

    # --- TITLE BLOCK (Bottom of Canvas) - Design mode only ---
    if mode == "design":
        # title_block_h and title_block_y already defined above for paper positioning
        # Make title block edges touch the left and right canvas borders
        title_block_x = -1 + BORDER_MARGIN
        # Width spans from left border to right border
        # Right border is at: (CANVAS_W - 1 - BORDER_MARGIN)
        title_block_w = (CANVAS_W - 1 - BORDER_MARGIN) - (-1 + BORDER_MARGIN)

        # Draw title block border
        title_block_border = patches.Rectangle((title_block_x, title_block_y), title_block_w, title_block_h,
                                               linewidth=2, edgecolor=BLUE, facecolor='white')
        ax.add_patch(title_block_border)

        # Divide title block into two sections: title (left) and notes (right)
        divider_x = title_block_x + title_block_w * 0.6
        ax.plot([divider_x, divider_x], [title_block_y, title_block_y + title_block_h],
                color=BLUE, linewidth=1.5)

        # Title section (left side - 60%)
        ax.text(title_block_x + 0.2, title_block_y + title_block_h - 0.4, "LAYOUT",
                fontsize=8, fontweight='bold', color=BLUE)
        ax.text(title_block_x + 0.2, title_block_y + title_block_h - 0.8, title.upper(),
                fontsize=12, fontweight='bold', color=BLUE)
        ax.text(title_block_x + 0.2, title_block_y + 1.2, f"Paper Size: {paper_w}\" × {paper_h}\"",
                fontsize=8, color='#333333')

        # Style information
        font_color_display = font_color if font_color else "black"
        style_info = (
            f"{format_style_for_display(paper_style, 'paper')}\n"
            f"{format_style_for_display(img_style, 'img')}\n"
            f"{format_style_for_display(txt_style, 'txt')}, font={font_color_display}"
        )
        ax.text(title_block_x + 0.2, title_block_y + 0.9, style_info,
                fontsize=6, va='top', color='#333333', family='monospace')

        # Notes section (right side - 40%)
        ax.text(divider_x + 0.2, title_block_y + title_block_h - 0.4, "INSTALLATION DATA",
                fontsize=8, fontweight='bold', color=BLUE)
        ax.text(divider_x + 0.2, title_block_y + title_block_h - 0.7, notes,
                fontsize=7, va='top', color='#333333', wrap=True)

    # --- DIMENSIONS (Visual Aids) - Design mode only ---
    if mode == "design":
        # All dimension lines are positioned outside the paper
        # Calculate caption boundaries
        caption_top = txt_y + txt_h
        caption_bottom = txt_y
        caption_left = txt_x
        caption_right = txt_x + txt_w

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

        # D6: Text block height (vertical dimension of caption area)
        # Position: 0.5 inch right of paper edge (same line as D4)
        if txt_h > 0.1:  # Only show if there's a meaningful text height
            d6_x = paper_x + paper_w + 0.5
            draw_dim_line(ax, d6_x, caption_bottom, caption_top, f"{txt_h:.2f}\"", dim_id="D6")

        # D12: Bottom margin (from bottom of text block to bottom of paper)
        # Position: 0.5 inch right of paper edge (same line as D4, D6)
        bottom_margin = txt_y - paper_y
        if bottom_margin > 0.1:  # Only show if there's a meaningful margin
            d12_x = paper_x + paper_w + 0.5
            draw_dim_line(ax, d12_x, paper_y, txt_y, f"{bottom_margin:.2f}\"", dim_id="D12")

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

        # D9: Text box left edge position (from left edge of paper to left of text box)
        # Position: 0.5 inch below paper bottom
        txt_left_margin = txt_x - paper_x
        draw_horizontal_dim_line(ax, paper_y - 0.5, paper_x, txt_x, f"{txt_left_margin:.2f}\"", dim_id="D9")

        # D10: Text box width
        # Position: 0.5 inch below paper bottom (same line as D9)
        draw_horizontal_dim_line(ax, paper_y - 0.5, txt_x, txt_x + txt_w, f"{txt_w:.2f}\"", dim_id="D10")

        # D15: Text box right margin (from right edge of text box to right edge of paper)
        # Position: 0.5 inch below paper bottom (same line as D9, D10)
        txt_right_margin = (paper_x + paper_w) - (txt_x + txt_w)
        if txt_right_margin > 0.1:  # Only show if there's a meaningful margin
            draw_horizontal_dim_line(ax, paper_y - 0.5, txt_x + txt_w, paper_x + paper_w, f"{txt_right_margin:.2f}\"", dim_id="D15")

        # D11: Double column gutter width (only for double_col layouts)
        # Position: 1/2 inch above paper top (same line as D2/D3)
        if special_mode == 'double_col' and gutter:
            col_w = (txt_w - gutter) / 2
            gutter_x_start = txt_x + col_w
            gutter_x_end = txt_x + col_w + gutter
            draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, gutter_x_start, gutter_x_end, f"{gutter:.2f}\"", dim_id="D11")

        # D7: Overall paper width
        # Position: 1 inch below paper bottom
        draw_horizontal_dim_line(ax, paper_y - 1.0, paper_x, paper_x + paper_w, f"{paper_w}\"", dim_id="D7", offset=0)

        # D8: Overall paper height
        # Position: 1 inch right of paper edge
        draw_dim_line(ax, paper_x + paper_w + 1.0, paper_y, paper_y + paper_h, f"{paper_h}\"", dim_id="D8")

    # Clean up
    ax.axis('off')

    output_path = os.path.join('output', filename)
    if mode == "print":
        # Print mode: save exact figure size, no cropping
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    else:
        # Design mode: tight crop with padding for dimension lines
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Generated: {output_path}")

# ==========================================
# LOAD LAYOUTS FROM JSON
# ==========================================

def load_layouts(filename='layouts.json'):
    """Load layout definitions from a JSON file. Returns (layouts, mode, image_path_landscape, image_path_portrait, text_path)."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        # Handle both old array format and new object format
        if isinstance(data, list):
            return data, "design", None, None, None  # backwards compatible
        return (data.get('layouts', []),
                data.get('mode', 'design'),
                data.get('image_path_landscape'),
                data.get('image_path_portrait'),
                data.get('text_path'))
    except FileNotFoundError:
        print(f"Error: Could not find '{filename}'")
        print("Please ensure the layouts.json file exists in the same directory as this script.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}")
        sys.exit(1)

# Run Generator
if __name__ == "__main__":
    print(f"PrintLayoutDesigner v{VERSION}")

    layouts, mode, image_path_landscape, image_path_portrait, text_path = load_layouts()
    print(f"Generating {len(layouts)} layouts in {mode} mode...")
    for layout in layouts:
        draw_canvas(
            filename=layout['file'],
            title=layout['title'],
            layout_type="Standard",
            orientation="Portrait",
            paper_w=layout['paper_size']['width'],
            paper_h=layout['paper_size']['height'],
            paper_style=layout.get('paper_style', {}),
            img_style=layout.get('img_style', {}),
            txt_style=layout.get('txt_style', {}),
            img_w=layout['img_dims']['width'],
            img_h=layout['img_dims']['height'],
            img_margins={'left': layout['img_pos']['left'], 'top': layout['img_pos']['top']},
            txt_dims=[layout['txt_dims']['width'], layout['txt_dims']['height']],
            txt_pos_desc=layout['txt_pos'],
            notes=layout['notes'],
            special_mode=layout.get('special'),
            gutter=layout.get('gutter'),
            mode=mode,
            image_path_landscape=image_path_landscape,
            image_path_portrait=image_path_portrait,
            text_path=text_path,
            font_color=layout.get('font_color')
        )

    print("Done! Check your folder.")