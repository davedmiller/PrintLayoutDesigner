import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for cleaner PNG output
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import os
import sys

# --- CONFIGURATION ---
# Blueprint drawing size (the canvas we're drawing on)
BLUEPRINT_W = 18
BLUEPRINT_H = 24

# Print paper size (the actual paper being designed for printing)
PAPER_W = 8.5
PAPER_H = 11

DPI = 150  # High resolution for crisp text
BLUE = '#1E3D59'
CANVAS_COLOR = '#F2F2F2'

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

def draw_blueprint(filename, title, layout_type, orientation,
                   paper_w, paper_h, black_border,
                   img_w, img_h, img_margins,
                   txt_dims, txt_pos_desc,
                   notes, special_mode=None):
    """
    Generates a single blueprint image.
    paper_w, paper_h = dimensions of the print paper (e.g., 8.5x11 or 11x14)
    img_margins = {'top': val, 'left': val, 'right': val}
    (We calculate X/Y based on margins or centering logic)
    """
    # Use BLUEPRINT size for canvas, PAPER size for the print paper border
    fig, ax = plt.subplots(figsize=(BLUEPRINT_W, BLUEPRINT_H), dpi=DPI)
    ax.set_xlim(-1, BLUEPRINT_W - 1)
    ax.set_ylim(-1, BLUEPRINT_H - 1)
    fig.patch.set_facecolor(CANVAS_COLOR)
    ax.set_facecolor(CANVAS_COLOR)

    # Draw canvas border (1/4 inch from edge)
    # The axes go from -1 to BLUEPRINT_W-1 and -1 to BLUEPRINT_H-1
    # So we need to account for the -1 offset
    BORDER_MARGIN = 0.25
    canvas_border = patches.Rectangle((-1 + BORDER_MARGIN, -1 + BORDER_MARGIN),
                                     BLUEPRINT_W - 2*BORDER_MARGIN,
                                     BLUEPRINT_H - 2*BORDER_MARGIN,
                                     linewidth=1, edgecolor=BLUE, facecolor='none')
    ax.add_patch(canvas_border)

    # Title block dimensions (defined here so we can use for paper positioning)
    title_block_h = 2.5
    # Position title block so its bottom edge touches the canvas border
    title_block_y = -1 + BORDER_MARGIN
    title_block_top = title_block_y + title_block_h

    # Calculate paper position
    # Horizontal: center on canvas
    # Coordinate space goes from -1 to (BLUEPRINT_W - 1)
    # Center is at: -1 + BLUEPRINT_W/2 = BLUEPRINT_W/2 - 1
    canvas_center_x = BLUEPRINT_W/2 - 1
    paper_x = canvas_center_x - paper_w/2

    # Vertical: center between top of canvas and top of title block
    # Top of coordinate space is at BLUEPRINT_H - 1
    available_height = (BLUEPRINT_H - 1) - title_block_top
    paper_y = title_block_top + (available_height - paper_h) / 2

    # Draw Print Paper Border
    border = patches.Rectangle((paper_x, paper_y), paper_w, paper_h, linewidth=3, edgecolor=BLUE, facecolor='white')
    ax.add_patch(border)

    # Draw optional black border around paper edge
    if black_border > 0:
        black_border_rect = patches.Rectangle((paper_x, paper_y), paper_w, paper_h,
                                              linewidth=black_border * DPI / 2,
                                              edgecolor='black', facecolor='none')
        ax.add_patch(black_border_rect)

    # --- CALCULATE IMAGE POSITION (relative to paper, not blueprint) ---
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

    # Draw Image
    img_rect = patches.Rectangle((img_x, img_y), img_w, img_h, 
                                 linewidth=1.5, edgecolor=BLUE, facecolor='#E8EFF5')
    ax.add_patch(img_rect)
    ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"", 
            ha='center', va='center', color=BLUE, fontsize=10, fontweight='bold')

    # --- CALCULATE TEXT POSITION (relative to paper) ---
    txt_w, txt_h = txt_dims

    # Text position from absolute left/top margins
    txt_x = paper_x + txt_pos_desc['left']
    txt_y = paper_y + paper_h - txt_pos_desc['top'] - txt_h

    # Draw Text Block(s)
    if special_mode == 'double_col':
        # Split into two columns
        col_w = (txt_w - 0.5) / 2
        col_1 = patches.Rectangle((txt_x, txt_y), col_w, txt_h, ls='--', lw=1, ec=BLUE, fc='none')
        col_2 = patches.Rectangle((txt_x + col_w + 0.5, txt_y), col_w, txt_h, ls='--', lw=1, ec=BLUE, fc='none')
        ax.add_patch(col_1)
        ax.add_patch(col_2)
        ax.text(txt_x + col_w/2, txt_y + txt_h/2, "TXT", ha='center', va='center', color=BLUE, fontsize=8, alpha=0.5)
        ax.text(txt_x + col_w + 0.5 + col_w/2, txt_y + txt_h/2, "TXT", ha='center', va='center', color=BLUE, fontsize=8, alpha=0.5)
    else:
        txt_rect = patches.Rectangle((txt_x, txt_y), txt_w, txt_h, 
                                     linestyle='--', linewidth=1, edgecolor=BLUE, facecolor='none')
        ax.add_patch(txt_rect)
        ax.text(txt_x + txt_w/2, txt_y + txt_h/2, "CAPTION TEXT\n(Greeked)", 
                ha='center', va='center', color=BLUE, fontsize=8, alpha=0.6, style='italic')

    # --- TITLE BLOCK (Bottom of Blueprint) ---
    # title_block_h and title_block_y already defined above for paper positioning
    # Make title block edges touch the left and right canvas borders
    title_block_x = -1 + BORDER_MARGIN
    # Width spans from left border to right border
    # Right border is at: (BLUEPRINT_W - 1 - BORDER_MARGIN)
    title_block_w = (BLUEPRINT_W - 1 - BORDER_MARGIN) - (-1 + BORDER_MARGIN)

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
    ax.text(title_block_x + 0.2, title_block_y + 0.4, f"Paper Size: {paper_w}\" × {paper_h}\"",
            fontsize=8, color='#333333')

    # Notes section (right side - 40%)
    ax.text(divider_x + 0.2, title_block_y + title_block_h - 0.4, "INSTALLATION DATA",
            fontsize=8, fontweight='bold', color=BLUE)
    ax.text(divider_x + 0.2, title_block_y + title_block_h - 0.7, notes,
            fontsize=7, va='top', color='#333333', wrap=True)

    # --- DIMENSIONS (Visual Aids) ---
    # All dimension lines are positioned outside the paper
    # Calculate caption boundaries
    caption_top = txt_y + txt_h
    caption_bottom = txt_y
    caption_left = txt_x
    caption_right = txt_x + txt_w

    # D1: Top Margin Dimension (from top of paper to top of image)
    # Position: 1/2 inch left of paper edge
    if 'top' in img_margins:
        d1_x = paper_x - 0.5
        draw_dim_line(ax, d1_x, paper_y + paper_h, img_y + img_h, f"{img_margins['top']}\"", dim_id="D1")

    # D5: Dimension between bottom of image and top of caption (gap)
    # Position: 1/2 inch left of paper edge (same line as D1)
    gap_distance = img_y - caption_top
    if gap_distance > 0.1:  # Only show if there's a meaningful gap
        d5_x = paper_x - 0.5
        draw_dim_line(ax, d5_x, img_y, caption_top, f"{gap_distance:.2f}\"", dim_id="D5")

    # D4: Dimension from top of paper to top of caption
    # Position: 1 inch left of paper edge
    distance_sheet_to_caption = (paper_y + paper_h) - caption_top
    d4_x = paper_x - 1.0
    draw_dim_line(ax, d4_x, paper_y + paper_h, caption_top, f"{distance_sheet_to_caption:.2f}\"", dim_id="D4")

    # D6: Caption left margin (from left edge of paper to left edge of caption)
    # Position: 1 inch left of paper edge (same line as D4)
    caption_left_margin = caption_left - paper_x
    if abs(caption_left_margin) > 0.1:  # Only show if there's a meaningful margin
        d6_x = paper_x - 1.0
        draw_dim_line(ax, d6_x, caption_bottom, caption_top, f"{caption_left_margin:.2f}\"", dim_id="D6")

    # D2: Left Margin Dimension (from left edge of paper to left of image)
    # Position: 1/2 inch above paper top
    left_margin = img_x - paper_x
    draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, paper_x, img_x, f"{left_margin:.2f}\"", dim_id="D2")

    # D3: Right Margin Dimension (from right of image to right edge of paper)
    # Position: 1/2 inch above paper top (same line as D2)
    right_margin = (paper_x + paper_w) - (img_x + img_w)
    draw_horizontal_dim_line(ax, paper_y + paper_h + 0.5, img_x + img_w, paper_x + paper_w, f"{right_margin:.2f}\"", dim_id="D3")

    # D9: Text box left edge position (from left edge of paper to left of text box)
    # Position: 1 inch above paper top
    txt_left_margin = txt_x - paper_x
    draw_horizontal_dim_line(ax, paper_y + paper_h + 1.0, paper_x, txt_x, f"{txt_left_margin:.2f}\"", dim_id="D9")

    # D10: Text box width
    # Position: 1 inch above paper top (same line as D9)
    draw_horizontal_dim_line(ax, paper_y + paper_h + 1.0, txt_x, txt_x + txt_w, f"{txt_w:.2f}\"", dim_id="D10")

    # D7: Overall paper width
    # Position: 1/2 inch below paper bottom
    draw_horizontal_dim_line(ax, paper_y - 0.5, paper_x, paper_x + paper_w, f"{paper_w}\"", dim_id="D7", offset=0)

    # D8: Overall paper height
    # Position: 1/2 inch right of paper edge
    draw_dim_line(ax, paper_x + paper_w + 0.5, paper_y, paper_y + paper_h, f"{paper_h}\"", dim_id="D8")

    # Clean up
    ax.axis('off')

    output_path = os.path.join('output', filename)
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Generated: {output_path}")

# ==========================================
# LOAD LAYOUTS FROM JSON
# ==========================================

def load_layouts(filename='layouts.json'):
    """Load layout definitions from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find '{filename}'")
        print("Please ensure the layouts.json file exists in the same directory as this script.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}")
        sys.exit(1)

# Run Generator
if __name__ == "__main__":
    layouts = load_layouts()
    print(f"Generating {len(layouts)} Layout Blueprints...")
    for layout in layouts:
        draw_blueprint(
            filename=layout['file'],
            title=layout['title'],
            layout_type="Standard",
            orientation="Portrait",
            paper_w=layout['paper_size'][0],
            paper_h=layout['paper_size'][1],
            black_border=layout.get('black_border', 0),
            img_w=layout['img'][0],
            img_h=layout['img'][1],
            img_margins=layout['margins'],
            txt_dims=layout['txt_dims'],
            txt_pos_desc=layout['txt_pos'],
            notes=layout['notes'],
            special_mode=layout.get('special')
        )
    print("Done! Check your folder.")