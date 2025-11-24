import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURATION ---
FIG_W = 8.5
FIG_H = 11
DPI = 150  # High resolution for crisp text
BLUE = '#1E3D59'
PAPER_COLOR = '#FDFBF7'

def draw_dim_line(ax, x, y_start, y_end, label):
    """Draws a vertical dimension line with arrows"""
    ax.annotate(text='', xy=(x, y_start), xytext=(x, y_end),
                arrowprops=dict(arrowstyle='<->', color=BLUE, lw=0.8))
    mid_y = (y_start + y_end) / 2
    ax.text(x - 0.1, mid_y, label, ha='right', va='center', fontsize=7, color=BLUE, rotation=90)

def draw_blueprint(filename, title, layout_type, orientation, 
                   img_w, img_h, img_margins, 
                   txt_dims, txt_pos_desc, 
                   notes, special_mode=None):
    """
    Generates a single blueprint image.
    img_margins = {'top': val, 'left': val, 'right': val} 
    (We calculate X/Y based on margins or centering logic)
    """
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, FIG_H)
    fig.patch.set_facecolor(PAPER_COLOR)
    ax.set_facecolor(PAPER_COLOR)
    
    # Draw Paper Border
    border = patches.Rectangle((0, 0), FIG_W, FIG_H, linewidth=3, edgecolor=BLUE, facecolor='none')
    ax.add_patch(border)

    # --- CALCULATE IMAGE POSITION ---
    # Default: Center Horizontal if 'left'/'right' not specified in margins
    if 'left' in img_margins:
        img_x = img_margins['left']
    elif 'right' in img_margins:
        img_x = FIG_W - img_margins['right'] - img_w
    else:
        img_x = (FIG_W - img_w) / 2

    # Calculate Y based on Top Margin or Vertical Centering
    if 'top' in img_margins:
        img_y = FIG_H - img_margins['top'] - img_h
    elif 'center_v' in img_margins:
        img_y = (FIG_H - img_h) / 2
    else:
        img_y = (FIG_H - img_h) / 2 # Default fallback

    # Draw Image
    img_rect = patches.Rectangle((img_x, img_y), img_w, img_h, 
                                 linewidth=1.5, edgecolor=BLUE, facecolor='#E8EFF5')
    ax.add_patch(img_rect)
    ax.text(img_x + img_w/2, img_y + img_h/2, f"IMAGE\n{img_w}\" x {img_h}\"", 
            ha='center', va='center', color=BLUE, fontsize=10, fontweight='bold')

    # --- CALCULATE TEXT POSITION ---
    txt_w, txt_h = txt_dims
    
    # Text X Logic
    if special_mode == 'broadside':
        txt_x = FIG_W - 0.75 - txt_w # Right margin 0.75 specific
    elif special_mode == 'asym':
        txt_x = img_x # Align flush left with image
    elif 'left' in img_margins and 'Art Book' in title:
        txt_x = 1 # Specific for Art Book Bottom Left
    elif 'Art Book' in title: # Landscape Art book
        txt_x = 1
    else:
        txt_x = (FIG_W - txt_w) / 2 # Default Center

    # Text Y Logic
    if 'gap' in txt_pos_desc:
        gap = txt_pos_desc['gap']
        txt_y = img_y - gap - txt_h
    elif 'bottom_margin' in txt_pos_desc:
        txt_y = txt_pos_desc['bottom_margin']
    elif special_mode == 'broadside':
        txt_y = img_y # Align top with image for magazine look
    else:
        txt_y = 2 # Fallback

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

    # --- ANNOTATIONS (NOTES SIDEBAR) ---
    note_w = 2.5
    note_h = 3.5
    note_x = FIG_W - note_w - 0.5
    note_y = 0.5
    
    # White box for notes
    note_bg = patches.Rectangle((note_x, note_y), note_w, note_h, lw=1, ec=BLUE, fc='white')
    ax.add_patch(note_bg)
    
    ax.text(note_x + 0.1, note_y + note_h - 0.3, "INSTALLATION DATA", 
            fontsize=9, fontweight='bold', color=BLUE)
    ax.text(note_x + 0.1, note_y + note_h - 0.6, notes, 
            fontsize=7, va='top', color='#333333', wrap=True)

    # --- TITLE ---
    ax.text(FIG_W/2, FIG_H - 0.5, title.upper(), ha='center', fontsize=14, fontweight='bold', color=BLUE)

    # --- DIMENSIONS (Visual Aids) ---
    # Top Margin Dimension
    if 'top' in img_margins:
        draw_dim_line(ax, img_x - 0.3, FIG_H, FIG_H - img_margins['top'], f"{img_margins['top']}\"")
    
    # Clean up
    ax.axis('off')
    
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"Generated: {filename}")

# ==========================================
# DEFINING THE 12 LAYOUTS
# ==========================================

layouts = [
    {
        "file": "01_ClassicMuseum_Land.png", "title": "Classic Museum - Landscape",
        "img": (6, 4), "margins": {'top': 2},
        "txt_dims": (6, 1.75), "txt_pos": {'gap': 1},
        "notes": "Layout: Classic Museum\nPaper: 8.5x11\nOrientation: Landscape Img\nTop Margin: 2\"\nText Gap: 1\""
    },
    {
        "file": "02_ClassicMuseum_Port.png", "title": "Classic Museum - Portrait",
        "img": (4, 6), "margins": {'top': 1.5},
        "txt_dims": (4, 2.5), "txt_pos": {'gap': 0.75},
        "notes": "Layout: Classic Museum\nPaper: 8.5x11\nOrientation: Portrait Img\nTop Margin: 1.5\"\nText Gap: 0.75\""
    },
    {
        "file": "03_ArtBook_Land.png", "title": "Art Book - Landscape",
        "img": (6, 4), "margins": {'top': 2, 'right': 1},
        "txt_dims": (5, 2), "txt_pos": {'bottom_margin': 2},
        "notes": "Layout: Art Book\nImg: Top Right (2\" Top, 1\" Right)\nTxt: Bottom Left (2\" Bottom, 1\" Left)"
    },
    {
        "file": "04_ArtBook_Port.png", "title": "Art Book - Portrait",
        "img": (4, 6), "margins": {'top': 1.5, 'right': 1},
        "txt_dims": (5, 2.5), "txt_pos": {'bottom_margin': 1.5},
        "notes": "Layout: Art Book\nImg: Top Right (1.5\" Top, 1\" Right)\nTxt: Bottom Left (1.5\" Bottom, 1\" Left)"
    },
    {
        "file": "05_Footer_Land.png", "title": "Footer - Landscape",
        "img": (6, 4), "margins": {'top': 2.5},
        "txt_dims": (7.5, 1), "txt_pos": {'bottom_margin': 1},
        "notes": "Layout: Footer\nImg: Optical Center\nText: Wide Footer (7.5\") anchored 1\" from bottom."
    },
    {
        "file": "06_Footer_Port.png", "title": "Footer - Portrait",
        "img": (4, 6), "margins": {'top': 2},
        "txt_dims": (7.5, 1), "txt_pos": {'bottom_margin': 1},
        "notes": "Layout: Footer\nImg: Optical Center\nText: Wide Footer (7.5\") anchored 1\" from bottom."
    },
    {
        "file": "07_Broadside_Port.png", "title": "Broadside - Portrait",
        "img": (4, 6), "margins": {'left': 0.75, 'center_v': True},
        "txt_dims": (2.5, 6), "txt_pos": {}, # Computed in special logic
        "special": "broadside",
        "notes": "Layout: Broadside\nImg: Left (0.75\" Margin)\nTxt: Right Column (2.5\" Wide)\nMagazine spread look."
    },
    {
        "file": "08_DoubleCol_Land.png", "title": "Double Column - Landscape",
        "img": (6, 4), "margins": {'top': 2},
        "txt_dims": (6, 2), "txt_pos": {'gap': 0.75},
        "special": "double_col",
        "notes": "Layout: Double Column\nImg: Centered Top\nTxt: Two 2.75\" columns with 0.5\" gutter."
    },
    {
        "file": "09_VisualAnchor_Land.png", "title": "Visual Anchor - Landscape",
        "img": (6, 4), "margins": {'top': 2.5},
        "txt_dims": (6, 1.75), "txt_pos": {'gap': 1},
        "notes": "Layout: Visual Anchor\nImg: Centered Top (2.5\")\nText: Matches image width."
    },
    {
        "file": "10_VisualAnchor_Port.png", "title": "Visual Anchor - Portrait",
        "img": (4, 6), "margins": {'top': 2},
        "txt_dims": (4, 2), "txt_pos": {'gap': 0.75},
        "notes": "Layout: Visual Anchor\nImg: Centered Top (2\")\nText: Matches image width."
    },
    {
        "file": "11_HighGallery_Land.png", "title": "High Gallery - Landscape",
        "img": (6, 4), "margins": {'top': 1.5},
        "txt_dims": (6, 1), "txt_pos": {'bottom_margin': 1.5},
        "notes": "Layout: High Gallery\nImg: High Center\nTxt: Low Center\nNote the large void in middle."
    },
    {
        "file": "12_HighGallery_Port.png", "title": "High Gallery - Portrait",
        "img": (4, 6), "margins": {'top': 1.5},
        "txt_dims": (4, 1), "txt_pos": {'bottom_margin': 1.5},
        "notes": "Layout: High Gallery\nImg: High Center\nTxt: Low Center\nNote the vertical pause."
    },
    {
        "file": "13_AsymOffset_Land.png", "title": "Asym Offset - Landscape",
        "img": (6, 4), "margins": {'right': 1, 'center_v': True},
        "txt_dims": (6, 1.5), "txt_pos": {'gap': 0.5},
        "special": "asym",
        "notes": "Layout: Asym Offset\nImg: Pushed Right (1\" margin)\nTxt: Flush Left with Image."
    },
    {
        "file": "14_AsymOffset_Port.png", "title": "Asym Offset - Portrait",
        "img": (4, 6), "margins": {'right': 1.5, 'center_v': True},
        "txt_dims": (4, 2), "txt_pos": {'gap': 0.5},
        "special": "asym",
        "notes": "Layout: Asym Offset\nImg: Pushed Right (1.5\" margin)\nTxt: Flush Left with Image."
    }
]

# Run Generator
if __name__ == "__main__":
    print("Generating 14 Layout Blueprints...")
    for layout in layouts:
        draw_blueprint(
            filename=layout['file'],
            title=layout['title'],
            layout_type="Standard",
            orientation="Portrait",
            img_w=layout['img'][0],
            img_h=layout['img'][1],
            img_margins=layout['margins'],
            txt_dims=layout['txt_dims'],
            txt_pos_desc=layout['txt_pos'],
            notes=layout['notes'],
            special_mode=layout.get('special')
        )
    print("Done! Check your folder.")