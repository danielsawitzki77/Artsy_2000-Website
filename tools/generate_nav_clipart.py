import math
import os
from PIL import Image, ImageDraw, ImageFont


S = 160  # Supersampled drawing canvas size (downsampled cleanly to 40x40 RGBA)
OUT_SIZE = 40
OL = (0, 0, 0, 255)


def new_canvas():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def load_font(names, size):
    if isinstance(names, str):
        names = [names]
    fonts_dir = r"C:\Windows\Fonts"
    for name in names:
        p = os.path.join(fonts_dir, name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_starburst(d, cx, cy, outer_r, inner_r, points, fill, outline=OL, width=5):
    pts = []
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        r = outer_r if (i % 2 == 0) else inner_r
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


def draw_home_icon():
    """Classic 90s GeoCities red-roofed house with chimney smoke & lawn."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Cute chimney smoke puffs behind chimney
    d.ellipse([108, 12, 134, 34], fill=(235, 240, 245, 255), outline=OL, width=5)
    d.ellipse([118, 2, 146, 24], fill=(255, 255, 255, 255), outline=OL, width=5)

    # Brick chimney
    d.rectangle([104, 28, 126, 70], fill=(185, 55, 35, 255), outline=OL, width=6)
    d.rectangle([100, 24, 130, 36], fill=(210, 75, 50, 255), outline=OL, width=5)

    # House main body (warm sunny yellow) + right side shading
    d.rectangle([28, 72, 132, 140], fill=(255, 232, 105, 255), outline=OL, width=6)
    d.rectangle([110, 74, 129, 137], fill=(228, 190, 60, 255))

    # Window on right
    d.rectangle([82, 86, 118, 118], fill=(95, 210, 255, 255), outline=OL, width=5)
    d.line([(100, 86), (100, 118)], fill=OL, width=4)
    d.line([(82, 102), (118, 102)], fill=OL, width=4)
    d.line([(88, 92), (96, 98)], fill=(255, 255, 255, 255), width=4)

    # Brown front door on left
    d.rectangle([44, 92, 72, 140], fill=(150, 75, 30, 255), outline=OL, width=5)
    d.ellipse([60, 114, 68, 122], fill=(255, 220, 0, 255), outline=OL, width=2)

    # Vivid cherry-red pitched roof
    roof = [(12, 78), (80, 22), (148, 78), (134, 82), (80, 38), (26, 82)]
    d.polygon([(14, 78), (80, 22), (146, 78)], fill=(230, 30, 35, 255), outline=OL, width=6)
    # Roof highlight
    d.line([(28, 72), (80, 30)], fill=(255, 115, 110, 255), width=6)
    d.line(roof[:3], fill=OL, width=7, joint="curve")

    # Bright 90s grass strip along base
    d.rectangle([14, 134, 146, 150], fill=(30, 195, 55, 255), outline=OL, width=6)
    return img


def draw_vance_icon():
    """Classic 90s bust of Dr. Brad Vance: comb-over, oversized gold aviators, lab coat & red tie."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # White lab coat shoulders
    coat = [(16, 150), (24, 114), (56, 104), (104, 104), (136, 114), (144, 150)]
    d.polygon(coat, fill=(245, 248, 255, 255), outline=OL, width=6)
    # Coat shadow + V shirt collar + bold red necktie
    d.polygon([(62, 106), (98, 106), (80, 148)], fill=(175, 225, 255, 255), outline=OL, width=5)
    d.polygon([(74, 110), (86, 110), (92, 148), (68, 148)], fill=(225, 20, 35, 255), outline=OL, width=5)

    # Neck
    d.rectangle([66, 90, 94, 112], fill=(245, 190, 150, 255), outline=OL, width=5)

    # Ears
    d.ellipse([28, 56, 48, 82], fill=(250, 195, 155, 255), outline=OL, width=5)
    d.ellipse([112, 56, 132, 82], fill=(250, 195, 155, 255), outline=OL, width=5)

    # Face oval
    d.ellipse([36, 20, 124, 102], fill=(255, 212, 175, 255), outline=OL, width=6)

    # 1990s comb-over hair wave
    hair = [(36, 50), (34, 28), (54, 12), (102, 10), (126, 24), (124, 46), (106, 34), (62, 32), (44, 44)]
    d.polygon(hair, fill=(118, 66, 28, 255), outline=OL, width=6)
    d.arc([50, 16, 116, 36], start=190, end=350, fill=(165, 105, 50, 255), width=5)

    # Cheerful Dr. Vance toothy grin (clean chin space underneath)
    d.chord([58, 70, 102, 89], start=0, end=180, fill=(255, 255, 255, 255), outline=OL, width=4)

    # Oversized gold aviator sunglasses
    # Nose bridge
    d.line([(72, 48), (88, 48)], fill=(255, 210, 0, 255), width=8)
    d.rectangle([40, 42, 76, 72], fill=(255, 215, 0, 255), outline=OL, width=5)
    d.rectangle([84, 42, 120, 72], fill=(255, 215, 0, 255), outline=OL, width=5)
    # Dark teal/navy lenses inside gold frames
    d.polygon([(44, 46), (72, 46), (71, 66), (47, 66)], fill=(18, 52, 105, 255), outline=OL, width=3)
    d.polygon([(88, 46), (116, 46), (113, 66), (89, 66)], fill=(18, 52, 105, 255), outline=OL, width=3)
    # Crisp lens glare streaks
    d.line([(48, 50), (58, 62)], fill=(140, 240, 255, 255), width=5)
    d.line([(92, 50), (102, 62)], fill=(140, 240, 255, 255), width=5)
    return img


def draw_founder_icon():
    """Classic 90s shadowy Fedora Architect icon with glowing red eyes."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # High-collared trenchcoat shoulders (lighter charcoal so it pops cleanly on both grey and dark navy)
    coat = [(16, 150), (26, 106), (62, 96), (98, 96), (134, 106), (144, 150)]
    d.polygon(coat, fill=(66, 72, 94, 255), outline=OL, width=6)
    # Popped lapels framing shadowed face
    d.polygon([(38, 104), (56, 86), (78, 146), (56, 146)], fill=(96, 104, 132, 255), outline=OL, width=5)
    d.polygon([(122, 104), (104, 86), (82, 146), (104, 146)], fill=(96, 104, 132, 255), outline=OL, width=5)
    # Crimson inner collar shadow
    d.polygon([(66, 98), (94, 98), (80, 142)], fill=(145, 0, 55, 255), outline=OL, width=4)

    # Shadowed head oval
    d.ellipse([44, 46, 116, 108], fill=(22, 18, 32, 255), outline=OL, width=6)

    # Glowing crimson / yellow-core cybernetic eyes peeking from under fedora brim
    d.polygon([(52, 74), (72, 78), (68, 86), (54, 84)], fill=(255, 35, 55, 255))
    d.polygon([(108, 74), (88, 78), (92, 86), (106, 84)], fill=(255, 35, 55, 255))
    d.ellipse([58, 76, 66, 83], fill=(255, 240, 100, 255))
    d.ellipse([94, 76, 102, 83], fill=(255, 240, 100, 255))

    # Detective Fedora crown + bright magenta band + wide tilted brim
    crown = [(44, 54), (52, 14), (78, 22), (106, 14), (116, 54)]
    d.polygon(crown, fill=(78, 46, 115, 255), outline=OL, width=6)
    d.polygon([(45, 42), (115, 42), (116, 54), (44, 54)], fill=(220, 0, 140, 255), outline=OL, width=4)
    # Brim
    brim = [(16, 58), (80, 48), (144, 58), (134, 72), (80, 64), (26, 72)]
    d.polygon(brim, fill=(94, 58, 138, 255), outline=OL, width=6)
    return img


def draw_dossiers_icon():
    """Classic 90s Manila File Folder with papers, mugshot ID card & red CONFIDENTIAL band."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Folder back & tab
    d.polygon([(18, 24), (74, 24), (86, 40), (138, 40), (138, 140), (18, 140)],
              fill=(228, 165, 50, 255), outline=OL, width=6)

    # White documents peeking out top
    d.polygon([(30, 32), (124, 26), (128, 112), (34, 112)],
              fill=(255, 255, 255, 255), outline=OL, width=5)
    # Blue report lines on document
    for ly in (42, 52):
        d.line([(42, ly), (114, ly - 2)], fill=(0, 80, 200, 255), width=4)

    # Manila folder front flap (tilted forward slightly)
    d.polygon([(18, 60), (146, 60), (138, 142), (18, 142)],
              fill=(255, 215, 85, 255), outline=OL, width=6)

    # ID Polaroid mugshot pinned on lower left of flap
    d.rectangle([30, 72, 68, 116], fill=(255, 255, 255, 255), outline=OL, width=4)
    d.rectangle([34, 76, 64, 104], fill=(0, 210, 240, 255), outline=OL, width=2)
    d.ellipse([42, 80, 56, 94], fill=(40, 45, 70, 255))
    d.chord([37, 94, 61, 112], start=180, end=360, fill=(40, 45, 70, 255))

    # Vivid red SECRET stripe on right of folder
    d.polygon([(74, 84), (132, 74), (134, 96), (76, 106)],
              fill=(225, 20, 25, 255), outline=OL, width=4)
    d.line([(84, 94), (124, 86)], fill=(255, 255, 255, 255), width=5)
    return img


def draw_tour_icon():
    """Classic 90s 35mm Camera with yellow starburst flash."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Top viewfinder hump & shutter button
    d.polygon([(48, 48), (62, 28), (102, 28), (114, 48)], fill=(65, 70, 82, 255), outline=OL, width=6)
    d.rectangle([24, 38, 44, 52], fill=(225, 30, 35, 255), outline=OL, width=5)  # Red shutter button

    # Main camera body (charcoal bottom, metallic silver upper band)
    d.rectangle([16, 48, 144, 134], fill=(55, 60, 72, 255), outline=OL, width=6)
    d.rectangle([16, 48, 144, 72], fill=(205, 212, 222, 255), outline=OL, width=6)

    # Large central camera lens
    d.ellipse([44, 58, 116, 130], fill=(175, 185, 200, 255), outline=OL, width=6)
    d.ellipse([54, 68, 106, 120], fill=(15, 25, 45, 255), outline=OL, width=5)
    d.ellipse([62, 76, 98, 112], fill=(35, 130, 235, 255), outline=(120, 235, 255, 255), width=4)
    # Lens glare dot
    d.ellipse([68, 82, 82, 96], fill=(255, 255, 255, 255))

    # Bright 90s golden flash starburst at top-right flash unit
    d.rectangle([110, 52, 134, 66], fill=(255, 240, 120, 255), outline=OL, width=4)
    draw_starburst(d, 128, 40, outer_r=30, inner_r=11, points=8,
                   fill=(255, 230, 0, 255), outline=OL, width=5)
    d.ellipse([120, 32, 136, 48], fill=(255, 255, 255, 255))
    return img


def draw_protocols_icon():
    """Classic 90s Atari/PC Arcade Joystick with red ball top & fire buttons."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Perspective black/grey joystick base
    top_plate = [(18, 92), (56, 70), (142, 92), (104, 118)]
    front_face = [(18, 92), (104, 118), (104, 146), (18, 118)]
    right_face = [(104, 118), (142, 92), (142, 118), (104, 146)]
    d.polygon(front_face, fill=(45, 48, 58, 255), outline=OL, width=6)
    d.polygon(right_face, fill=(32, 34, 42, 255), outline=OL, width=6)
    d.polygon(top_plate, fill=(75, 82, 96, 255), outline=OL, width=6)

    # Two chunky arcade fire buttons (red & yellow)
    d.ellipse([34, 86, 56, 102], fill=(255, 220, 0, 255), outline=OL, width=4)
    d.ellipse([104, 90, 126, 106], fill=(235, 30, 35, 255), outline=OL, width=4)

    # Rubber stick boot
    d.ellipse([66, 80, 96, 98], fill=(25, 25, 30, 255), outline=OL, width=4)

    # Chrome joystick shaft
    d.polygon([(74, 42), (88, 42), (86, 88), (76, 88)], fill=(185, 195, 210, 255), outline=OL, width=5)

    # Big glossy red arcade ball-top
    d.ellipse([54, 12, 108, 66], fill=(235, 20, 30, 255), outline=OL, width=6)
    d.arc([60, 18, 100, 58], start=15, end=110, fill=(140, 0, 10, 255), width=6)
    d.ellipse([66, 20, 82, 34], fill=(255, 180, 180, 255))
    d.ellipse([69, 22, 77, 29], fill=(255, 255, 255, 255))
    return img


def draw_povray_icon():
    """Classic 90s POV-Ray glossy chrome-cyan sphere floating over checkered floor."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Perspective checkerboard floor at bottom
    rows = 3
    cols = 4
    y_top, y_bot = 104, 148
    x_top_l, x_top_r = 34, 126
    x_bot_l, x_bot_r = 10, 150
    for r in range(rows):
        t0, t1 = r / rows, (r + 1) / rows
        y0 = y_top + (y_bot - y_top) * t0
        y1 = y_top + (y_bot - y_top) * t1
        xl0 = x_top_l + (x_bot_l - x_top_l) * t0
        xr0 = x_top_r + (x_bot_r - x_top_r) * t0
        xl1 = x_top_l + (x_bot_l - x_top_l) * t1
        xr1 = x_top_r + (x_bot_r - x_top_r) * t1
        for c in range(cols):
            u0, u1 = c / cols, (c + 1) / cols
            quad = [
                (xl0 + (xr0 - xl0) * u0, y0),
                (xl0 + (xr0 - xl0) * u1, y0),
                (xl1 + (xr1 - xl1) * u1, y1),
                (xl1 + (xr1 - xl1) * u0, y1),
            ]
            col = (245, 245, 255, 255) if ((r + c) % 2 == 0) else (75, 0, 140, 255)
            d.polygon(quad, fill=col)
    # Bold black frame around checkerboard plane
    d.polygon([(x_top_l, y_top), (x_top_r, y_top), (x_bot_r, y_bot), (x_bot_l, y_bot)],
              fill=None, outline=OL, width=6)

    # Dark cast shadow under floating sphere
    d.ellipse([48, 114, 114, 134], fill=(15, 0, 35, 195))

    # Raytraced chrome sphere (sky + horizon + purple/cyan reflection)
    cx, cy, R = 80, 62, 46
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(35, 75, 200, 255), outline=OL, width=6)
    # Lower horizon chrome bounce
    d.chord([cx - R + 5, cy - R + 5, cx + R - 5, cy + R - 5], start=10, end=170, fill=(25, 20, 75, 255))
    # Bright cyan horizon band across middle of sphere
    d.chord([cx - R + 5, cy - 18, cx + R - 5, cy + 28], start=180, end=360, fill=(0, 225, 255, 255))
    # Magenta retro reflection rim
    d.arc([cx - R + 9, cy - R + 9, cx + R - 9, cy + R - 9], start=25, end=155, fill=(255, 0, 200, 255), width=7)
    # Specular star highlight upper-left
    d.ellipse([50, 28, 72, 48], fill=(220, 250, 255, 255))
    draw_starburst(d, 58, 36, outer_r=15, inner_r=5, points=4, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255), width=2)
    # Crisp outer rim
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=None, outline=OL, width=6)
    return img


def draw_perks_icon():
    """Classic 90s Dollar Cash Voucher + Cheesy Pepperoni Pizza Slice."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Bright green $ banknote / voucher angled behind
    bill = [(14, 46), (104, 16), (124, 72), (34, 102)]
    d.polygon(bill, fill=(45, 185, 75, 255), outline=OL, width=6)
    inner_bill = [(24, 50), (98, 25), (112, 67), (38, 92)]
    d.polygon(inner_bill, fill=(115, 230, 125, 255), outline=(15, 95, 30, 255), width=4)
    # Bold "$" sign on left of banknote
    f_dollar = load_font(["arialbd.ttf", "tahomabd.ttf"], 36)
    d.text((34, 40), "$", font=f_dollar, fill=(0, 85, 20, 255))

    # Big iconic 90s pepperoni pizza slice in foreground
    # Melted yellow cheese wedge
    slice_pts = [(54, 144), (72, 48), (146, 104)]
    d.polygon(slice_pts, fill=(255, 215, 25, 255), outline=OL, width=6)
    # Molten cheese drip edge
    d.ellipse([70, 96, 86, 114], fill=(255, 215, 25, 255))
    # Golden baked crust strip along top-right back edge
    crust = [(68, 44), (150, 104), (138, 120), (58, 60)]
    d.polygon(crust, fill=(215, 130, 40, 255), outline=OL, width=6)
    # 3 vivid red pepperoni circles
    for px, py, pr in [(86, 78, 12), (110, 98, 12), (76, 110, 11)]:
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(220, 25, 30, 255), outline=OL, width=4)
    # Re-stroke cheese triangle outline cleanly
    d.line([(72, 56), (54, 144), (138, 114)], fill=OL, width=6, joint="curve")

    # Shiny gold coin at lower-left ($1.50 vibe!)
    d.ellipse([14, 100, 56, 142], fill=(255, 210, 0, 255), outline=OL, width=5)
    d.ellipse([21, 107, 49, 135], fill=(255, 235, 90, 255), outline=(185, 125, 0, 255), width=3)
    return img


def draw_volunteer_icon():
    """Classic 90s Subject Application Clipboard with bright checkmark & pencil."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Brown masonite clipboard board
    d.rounded_rectangle([24, 24, 126, 148], radius=10, fill=(185, 110, 42, 255), outline=OL, width=6)

    # Crisp white registration form sheet
    d.rectangle([36, 40, 114, 136], fill=(255, 255, 255, 255), outline=OL, width=5)

    # Silver clipboard clip at top
    d.rounded_rectangle([54, 12, 96, 36], radius=6, fill=(195, 205, 218, 255), outline=OL, width=5)
    d.ellipse([69, 15, 81, 27], fill=(120, 130, 145, 255), outline=OL, width=3)

    # Blue form lines + bold red checkbox square
    d.rectangle([45, 52, 61, 68], fill=(255, 255, 255, 255), outline=OL, width=4)
    d.line([(68, 60), (105, 60)], fill=(0, 75, 195, 255), width=5)
    d.rectangle([45, 78, 61, 94], fill=(255, 255, 255, 255), outline=OL, width=4)
    d.line([(68, 86), (105, 86)], fill=(0, 75, 195, 255), width=5)
    d.line([(45, 112), (95, 112)], fill=(0, 75, 195, 255), width=5)

    # Big vibrant green checkmark stamped across the boxes
    chk = [(42, 66), (56, 84), (92, 46)]
    d.line(chk, fill=(0, 0, 0, 255), width=16, joint="curve")
    d.line(chk, fill=(25, 220, 55, 255), width=9, joint="curve")

    # Classic yellow #2 pencil angled on bottom-right
    d.polygon([(94, 114), (138, 70), (150, 82), (106, 126)], fill=(255, 205, 0, 255), outline=OL, width=5)
    # Pink eraser
    d.polygon([(134, 74), (144, 64), (156, 76), (146, 86)], fill=(255, 115, 155, 255), outline=OL, width=5)
    # Sharpened tip
    d.polygon([(86, 134), (94, 114), (106, 126)], fill=(245, 210, 160, 255), outline=OL, width=5)
    return img


def draw_terminal_icon():
    """Classic 90s Beige CRT Computer Workstation with bright green terminal screen."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Monitor outer beige housing
    d.rounded_rectangle([22, 16, 138, 102], radius=8, fill=(228, 220, 194, 255), outline=OL, width=6)
    # Right/bottom beige shadow strip
    d.line([(132, 22), (132, 96)], fill=(175, 165, 140, 255), width=6)

    # Dark CRT monitor bezel
    d.rectangle([32, 26, 128, 90], fill=(45, 50, 56, 255), outline=OL, width=4)
    # Phosphor dark-green screen
    d.rectangle([36, 30, 124, 86], fill=(4, 34, 14, 255), outline=(12, 70, 30, 255), width=3)

    # Bright terminal prompt lines + block cursor
    d.line([(44, 42), (62, 42)], fill=(50, 255, 95, 255), width=6)
    d.line([(68, 42), (104, 42)], fill=(255, 240, 50, 255), width=6)
    d.line([(44, 56), (92, 56)], fill=(50, 255, 95, 255), width=6)
    d.line([(44, 70), (70, 70)], fill=(50, 255, 95, 255), width=6)
    d.rectangle([76, 65, 88, 76], fill=(255, 255, 60, 255))

    # Monitor pedestal neck
    d.rectangle([58, 100, 102, 114], fill=(175, 165, 140, 255), outline=OL, width=5)

    # Desktop SGI/PC chassis base underneath
    d.rectangle([14, 112, 146, 146], fill=(228, 220, 194, 255), outline=OL, width=6)
    # Floppy disk drive slot + glowing green LED
    d.rectangle([78, 124, 128, 134], fill=(45, 45, 52, 255), outline=OL, width=3)
    d.rectangle([28, 125, 40, 135], fill=(0, 245, 70, 255), outline=OL, width=3)
    return img


def draw_guestbook_icon():
    """Classic 90s GeoCities Open Guestbook with feather quill pen."""
    img = new_canvas()
    d = ImageDraw.Draw(img)

    # Open burgundy-leather hardcover backing (distinct on both #c0c0c0 grey and #000080 navy)
    d.polygon([(12, 60), (80, 72), (146, 60), (142, 138), (80, 148), (16, 138)],
              fill=(170, 32, 52, 255), outline=OL, width=6)

    # Left crisp white curved page
    d.polygon([(22, 48), (78, 60), (78, 134), (20, 124)],
              fill=(255, 252, 232, 255), outline=OL, width=5)
    # Right crisp white curved page
    d.polygon([(78, 60), (136, 48), (138, 124), (78, 134)],
              fill=(255, 255, 255, 255), outline=OL, width=5)
    # Blue ink handwriting squiggles on left & right pages
    for ly in (72, 88, 104):
        d.line([(32, ly - 4), (68, ly + 2)], fill=(30, 85, 210, 255), width=4)
        d.line([(88, ly + 2), (124, ly - 4)], fill=(30, 85, 210, 255), width=4)

    # Center gold bookmark ribbon hanging out bottom
    d.polygon([(74, 132), (86, 132), (86, 152), (80, 144), (74, 152)],
              fill=(255, 200, 0, 255), outline=OL, width=4)

    # Classic diagonal gold & cyan feather quill signing the right page
    quill = [(88, 102), (102, 56), (136, 14), (150, 26), (134, 72), (102, 98)]
    d.polygon(quill, fill=(255, 210, 35, 255), outline=OL, width=6)
    # Cyan feather highlight stripe & dark pen nib
    d.line([(98, 92), (140, 22)], fill=(255, 135, 0, 255), width=5)
    d.polygon([(82, 110), (90, 92), (102, 100)], fill=(35, 45, 70, 255), outline=OL, width=4)
    return img


ICON_BUILDERS = [
    ("nav_home.png", "HOME & DISPATCH", draw_home_icon),
    ("nav_vance.png", "MEET DR. VANCE", draw_vance_icon),
    ("nav_founder.png", "THE FOUNDER", draw_founder_icon),
    ("nav_dossiers.png", "TERMINAL DOSSIERS", draw_dossiers_icon),
    ("nav_tour.png", "FACILITY TOUR", draw_tour_icon),
    ("nav_protocols.png", "PROTOCOLS (GAMES)", draw_protocols_icon),
    ("nav_povray.png", "POV-RAY Studio", draw_povray_icon),
    ("nav_perks.png", "PERKS & VOUCHERS", draw_perks_icon),
    ("nav_volunteer.png", "BECOME A SUBJECT", draw_volunteer_icon),
    ("nav_terminal.png", "B50 TERMINAL", draw_terminal_icon),
    ("nav_guestbook.png", "SIGN GUESTBOOK", draw_guestbook_icon),
]


def create_nav_clipart_icons(assets_dir=None):
    if assets_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(base_dir), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    for filename, _label, builder in ICON_BUILDERS:
        hi_img = builder()
        out_img = hi_img.resize((OUT_SIZE, OUT_SIZE), Image.Resampling.LANCZOS)
        out_path = os.path.join(assets_dir, filename)
        out_img.save(out_path, "PNG")
        print(f"Created {filename} ({OUT_SIZE}x{OUT_SIZE})")


if __name__ == "__main__":
    create_nav_clipart_icons()
