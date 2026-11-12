import math
import os
import random
from PIL import Image, ImageDraw, ImageFont


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


def draw_bevel_rect(draw, box, fill, light=(255, 255, 255), dark=(40, 40, 40), thickness=3, inset=False):
    x0, y0, x1, y1 = box
    if fill is not None:
        draw.rectangle([x0, y0, x1, y1], fill=fill)
    tl_col = dark if inset else light
    br_col = light if inset else dark
    for i in range(thickness):
        # Top & Left
        draw.line([(x0 + i, y0 + i), (x1 - i, y0 + i)], fill=tl_col)
        draw.line([(x0 + i, y0 + i), (x0 + i, y1 - i)], fill=tl_col)
        # Bottom & Right
        draw.line([(x0 + i, y1 - i), (x1 - i, y1 - i)], fill=br_col)
        draw.line([(x1 - i, y0 + i), (x1 - i, y1 - i)], fill=br_col)


def draw_text_with_shadow(draw, pos, text, font, fill, shadow=(0, 0, 0), offset=(2, 2)):
    x, y = pos
    if shadow:
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def create_starfield(assets_dir):
    random.seed(1996)
    star_img = Image.new("RGB", (128, 128), (5, 5, 15))
    star_draw = ImageDraw.Draw(star_img)
    for _ in range(70):
        x = random.randint(0, 127)
        y = random.randint(0, 127)
        bright = random.randint(140, 255)
        color = random.choice([
            (bright, bright, bright),
            (bright, bright // 2, bright),
            (bright // 2, bright, bright),
            (bright, bright, bright // 2)
        ])
        star_draw.point((x, y), fill=color)
        if random.random() < 0.2:
            star_draw.point(((x + 1) % 128, y), fill=color)
            star_draw.point((x, (y + 1) % 128), fill=color)
    star_img.save(os.path.join(assets_dir, "stars_bg.png"))
    print("Created stars_bg.png")


def create_warning_strobe(assets_dir):
    """
    Create a crisp, bold animated 90s hazard triangle + security beacon strobe GIF (240x152).
    Never turns green: pulses between intense hazard yellow/gold and bright red/magenta strobe rings.
    """
    W, H = 240, 152
    frames = []
    f_small = load_font(["courbd.ttf", "consolab.ttf", "arialbd.ttf"], 13)

    for f in range(8):
        img = Image.new("RGB", (W, H), (8, 0, 6))
        d = ImageDraw.Draw(img)

        is_flash = (f % 2 == 0)
        phase = f / 8.0

        # Subtle background hazard grid
        grid_col = (35, 0, 20) if is_flash else (20, 0, 12)
        for gx in range(0, W, 16):
            d.line([(gx, 0), (gx, H)], fill=grid_col)
        for gy in range(0, H, 16):
            d.line([(0, gy), (W, gy)], fill=grid_col)

        cx, cy = W // 2, 90

        # Expanding radar / strobe rings behind the triangle
        for r_idx in range(3):
            rad = int(24 + ((phase * 30 + r_idx * 24) % 72))
            fade = max(0.0, 1.0 - (rad - 24) / 72.0)
            ring_col = (
                int(255 * fade),
                int(20 * fade),
                int((180 if r_idx % 2 == 0 else 40) * fade)
            )
            d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=ring_col, width=2)

        # Strobe light rays on flash frames
        if f in (0, 1, 4, 5):
            ray_col = (255, 40, 100) if f in (0, 4) else (220, 140, 0)
            for angle_deg in range(-160, 0, 25):
                ang = math.radians(angle_deg + (6 if f % 2 else 0))
                r1, r2 = 38, 68
                x1 = cx + int(math.cos(ang) * r1)
                y1 = cy + int(math.sin(ang) * r1)
                x2 = cx + int(math.cos(ang) * r2)
                y2 = cy + int(math.sin(ang) * r2)
                d.line([(x1, y1), (x2, y2)], fill=ray_col, width=2)

        # Top header strip for lamps & HUD label
        d.rectangle([2, 2, W - 3, 30], fill=(22, 0, 12), outline=(100, 0, 40))

        # Corner security strobe lamps
        lamp_left_on = (f < 4)
        lamp_right_on = (f >= 4)
        for lx, ly, is_on in [(20, 16, lamp_left_on), (W - 20, 16, lamp_right_on)]:
            if is_on:
                d.ellipse([lx - 10, ly - 10, lx + 10, ly + 10], fill=(120, 0, 40))
                d.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=(255, 0, 80), outline=(255, 200, 220))
                d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=(255, 255, 255))
            else:
                d.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=(55, 0, 20), outline=(110, 20, 50))

        # Top HUD label centered between lamps
        hud_txt = "ALERT // B-50"
        hb = d.textbbox((0, 0), hud_txt, font=f_small)
        hw = hb[2] - hb[0]
        hud_col = (255, 255, 0) if is_flash else (255, 80, 140)
        d.text(((W - hw) // 2, 9), hud_txt, font=f_small, fill=hud_col)

        # Large 3D Hazard Warning Triangle (clearly below the top header bar)
        top_pt = (cx, 36)
        left_pt = (cx - 58, 140)
        right_pt = (cx + 58, 140)

        # Red/magenta outer glow polygon on flash frames
        if is_flash:
            d.polygon(
                [(cx, 31), (cx - 63, 143), (cx + 63, 143)],
                outline=(255, 0, 80),
                fill=(90, 0, 30)
            )

        # Outer bright yellow rim
        d.polygon([top_pt, left_pt, right_pt], fill=(255, 225, 0), outline=(255, 255, 160))
        # 3D shading on right & bottom edges of outer triangle
        d.line([top_pt, right_pt], fill=(210, 140, 0), width=3)
        d.line([left_pt, right_pt], fill=(180, 110, 0), width=3)
        d.line([top_pt, left_pt], fill=(255, 255, 190), width=3)

        # Thick black inner hazard border triangle
        in1_top = (cx, 46)
        in1_left = (cx - 47, 133)
        in1_right = (cx + 47, 133)
        d.polygon([in1_top, in1_left, in1_right], fill=(15, 10, 0))

        # Inner glowing yellow/amber triangle core
        in2_top = (cx, 55)
        in2_left = (cx - 38, 127)
        in2_right = (cx + 38, 127)
        core_fill = (255, 230, 0) if is_flash else (245, 185, 0)
        d.polygon([in2_top, in2_left, in2_right], fill=core_fill)

        # Bold geometric Exclamation Mark (!) inside the triangle
        d.polygon([
            (cx - 7, 72),
            (cx + 7, 72),
            (cx + 4, 104),
            (cx - 4, 104)
        ], fill=(0, 0, 0))
        d.ellipse([cx - 7, 68, cx + 7, 77], fill=(0, 0, 0))
        # Bottom circular dot
        d.ellipse([cx - 6, 110, cx + 6, 122], fill=(0, 0, 0))

        # Outer border frame
        d.rectangle([0, 0, W - 1, H - 1], outline=(255, 0, 60) if is_flash else (160, 0, 40), width=2)

        frames.append(img)

    out_path = os.path.join(assets_dir, "warning_strobe.gif")
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0
    )
    print("Created warning_strobe.gif")


def draw_7seg_digit(draw, x, y, w, h, digit_char):
    """Draw an authentic 7-segment LED digit with dim unlit segments and bright glowing active segments."""
    # Segment map: a (top), b (top-right), c (bot-right), d (bot), e (bot-left), f (top-left), g (mid)
    segs = {
        '0': "abcdef",
        '1': "bc",
        '2': "abged",
        '3': "abgcd",
        '4': "fgbc",
        '5': "afgcd",
        '6': "afedcg",
        '7': "abc",
        '8': "abcdefg",
        '9': "abcdfg",
    }.get(digit_char, "")

    t = max(4, w // 5)  # segment thickness
    pad = 3
    mid_y = y + h // 2

    # Horizontal segment helper
    def h_poly(sx, sy, sw):
        ht = t // 2
        return [
            (sx + ht, sy - ht),
            (sx + sw - ht, sy - ht),
            (sx + sw, sy),
            (sx + sw - ht, sy + ht),
            (sx + ht, sy + ht),
            (sx, sy),
        ]

    # Vertical segment helper
    def v_poly(sx, sy, sh):
        ht = t // 2
        return [
            (sx, sy),
            (sx + ht, sy + ht),
            (sx + ht, sy + sh - ht),
            (sx, sy + sh),
            (sx - ht, sy + sh - ht),
            (sx - ht, sy + ht),
        ]

    top_y = y + pad + t // 2
    bot_y = y + h - pad - t // 2
    left_x = x + pad + t // 2
    right_x = x + w - pad - t // 2
    horz_w = right_x - left_x
    vert_h1 = mid_y - top_y
    vert_h2 = bot_y - mid_y

    polys = {
        'a': h_poly(left_x, top_y, horz_w),
        'g': h_poly(left_x, mid_y, horz_w),
        'd': h_poly(left_x, bot_y, horz_w),
        'f': v_poly(left_x, top_y, vert_h1),
        'b': v_poly(right_x, top_y, vert_h1),
        'e': v_poly(left_x, mid_y, vert_h2),
        'c': v_poly(right_x, mid_y, vert_h2),
    }

    # Draw unlit ghost segments first
    for k, poly in polys.items():
        if k not in segs:
            draw.polygon(poly, fill=(0, 38, 14))

    # Draw lit segments with bright CRT green glow
    for k, poly in polys.items():
        if k in segs:
            draw.polygon(poly, fill=(0, 255, 95), outline=(160, 255, 195))


def create_visitor_counter(assets_dir):
    """Create a full-column-width 7-segment LED odometer counter (392x86)."""
    W, H = 392, 86
    img = Image.new("RGB", (W, H), (20, 24, 22))
    d = ImageDraw.Draw(img)

    # Outer 3D metallic frame
    draw_bevel_rect(d, [0, 0, W - 1, H - 1], fill=(32, 36, 38), light=(150, 160, 165), dark=(12, 14, 16), thickness=4, inset=False)
    # Inner recessed display bezel
    draw_bevel_rect(d, [10, 8, W - 11, H - 9], fill=(4, 14, 6), light=(110, 120, 115), dark=(0, 0, 0), thickness=3, inset=True)

    digits = "001337"
    num_digits = len(digits)
    inner_x0, inner_y0 = 18, 14
    inner_w = (W - 36)
    cell_w = inner_w // num_digits
    cell_h = H - 28

    for i, ch in enumerate(digits):
        cx0 = inner_x0 + i * cell_w + 3
        cx1 = inner_x0 + (i + 1) * cell_w - 3
        cy0 = inner_y0
        cy1 = inner_y0 + cell_h
        # Individual recessed digit cell
        d.rectangle([cx0, cy0, cx1, cy1], fill=(2, 10, 4), outline=(18, 45, 24))
        draw_7seg_digit(d, cx0 + 6, cy0 + 4, (cx1 - cx0) - 12, (cy1 - cy0) - 8, ch)

    # Subtle CRT scanlines over the counter glass
    for sy in range(10, H - 10, 3):
        d.line([(13, sy), (W - 14, sy)], fill=(0, 18, 6))

    img.save(os.path.join(assets_dir, "counter.png"))
    print("Created counter.png")


def create_under_construction(assets_dir):
    """Create a full-column-width animated hazard banner (392x104) with bold readable text."""
    W, H = 392, 104
    frames = []
    f_main = load_font(["impact.ttf", "arialbd.ttf", "tahomabd.ttf"], 25)
    f_sub = load_font(["courbd.ttf", "consolab.ttf", "arialbd.ttf"], 14)

    stripe_w = 24
    for step in range(8):
        offset = (step * 6) % (stripe_w * 2)
        frame = Image.new("RGB", (W, H), (15, 12, 0))
        d = ImageDraw.Draw(frame)

        # Diagonal yellow & black hazard stripes across entire background
        for x in range(-H - stripe_w * 2, W + H + stripe_w * 2, stripe_w * 2):
            sx = x + offset
            d.polygon([
                (sx, 0),
                (sx + stripe_w, 0),
                (sx + stripe_w - H, H),
                (sx - H, H)
            ], fill=(255, 215, 0))

        # 3D bevel outer border
        d.rectangle([0, 0, W - 1, H - 1], outline=(255, 230, 0), width=2)

        # Center dark armored plate leaving bold hazard stripes on top/bottom/sides
        px0, py0, px1, py1 = 14, 18, W - 15, H - 19
        draw_bevel_rect(
            d,
            [px0, py0, px1, py1],
            fill=(10, 6, 8),
            light=(255, 230, 80),
            dark=(90, 60, 0),
            thickness=3,
            inset=False
        )
        d.rectangle([px0 + 4, py0 + 4, px1 - 4, py1 - 4], outline=(180, 0, 30), width=1)

        # Flashing red/yellow mini warning beacons on left & right of text
        blink_on = (step < 4)
        beacon_col = (255, 30, 30) if blink_on else (255, 200, 0)
        for bx in (px0 + 18, px1 - 18):
            by = H // 2
            d.polygon([(bx, by - 14), (bx - 12, by + 10), (bx + 12, by + 10)], fill=beacon_col, outline=(255, 255, 255))
            d.line([(bx, by - 6), (bx, by + 2)], fill=(0, 0, 0), width=2)
            d.point((bx, by + 6), fill=(0, 0, 0))

        # Line 1: "UNDER INVESTIGATION" centered
        txt1 = "UNDER INVESTIGATION"
        bbox1 = d.textbbox((0, 0), txt1, font=f_main)
        tw1 = bbox1[2] - bbox1[0]
        tx1 = (W - tw1) // 2
        draw_text_with_shadow(d, (tx1, 22), txt1, f_main, fill=(255, 235, 0), shadow=(160, 0, 0), offset=(2, 2))

        # Line 2: "// SECTOR B-50 SECURITY //" centered
        txt2 = "// SECTOR B-50 SECURITY //"
        bbox2 = d.textbbox((0, 0), txt2, font=f_sub)
        tw2 = bbox2[2] - bbox2[0]
        tx2 = (W - tw2) // 2
        sub_col = (255, 70, 70) if blink_on else (0, 255, 255)
        draw_text_with_shadow(d, (tx2, 56), txt2, f_sub, fill=sub_col, shadow=(0, 0, 0), offset=(1, 1))

        frames.append(frame)

    frames[0].save(
        os.path.join(assets_dir, "under_construction.gif"),
        save_all=True,
        append_images=frames[1:],
        duration=95,
        loop=0
    )
    print("Created under_construction.gif")


def create_badge_netscape(assets_dir):
    """
    Create a full-column-width (392x112) Netscape Now! 3.0 badge featuring the authentic
    90s Netscape Navigator emblem (starry night sky, curved glowing cyan horizon, ship's wheel
    spokes, and the iconic giant arching serif 'N' rising over the horizon).
    """
    W, H = 392, 112
    img = Image.new("RGB", (W, H), (0, 40, 70))
    d = ImageDraw.Draw(img)

    # Right background gradient (classic Netscape dark teal-navy)
    for y in range(H):
        t = y / float(H - 1)
        r = int(0 + 10 * t)
        g = int(42 + 45 * (1.0 - abs(t - 0.5) * 2))
        b = int(75 + 55 * (1.0 - t * 0.5))
        d.line([(0, y), (W - 1, y)], fill=(r, g, b))

    # Outer 3D Win95/Netscape button bevel
    draw_bevel_rect(d, [0, 0, W - 1, H - 1], fill=None, light=(190, 225, 235), dark=(0, 18, 36), thickness=4, inset=False)
    d.rectangle([4, 4, W - 5, H - 5], outline=(0, 110, 130), width=1)

    # Left Netscape Emblem Box (x: 10..110, y: 8..103 -> 100x95)
    lx0, ly0, lx1, ly1 = 10, 8, 110, 103
    lw, lh = lx1 - lx0, ly1 - ly0
    emblem = Image.new("RGB", (lw, lh), (0, 15, 35))
    ed = ImageDraw.Draw(emblem)

    # 1. Sky-to-horizon gradient inside emblem
    horizon_y = int(lh * 0.66)
    for y in range(lh):
        if y < horizon_y:
            t = y / float(horizon_y)
            # Deep space navy at top -> glowing teal-cyan near horizon
            r = int(0 + 20 * (t ** 2))
            g = int(16 + 165 * (t ** 1.7))
            b = int(42 + 165 * (t ** 1.4))
        else:
            t = (y - horizon_y) / float(lh - horizon_y)
            # Dark teal ocean below horizon
            r = 0
            g = int(110 * (1.0 - t * 0.75))
            b = int(135 * (1.0 - t * 0.65))
        ed.line([(0, y), (lw - 1, y)], fill=(r, g, b))

    # 2. Starfield + shooting star in upper sky
    stars = [(12, 12), (26, 8), (48, 14), (72, 10), (86, 18), (18, 28), (64, 24), (82, 34), (10, 44)]
    for sx, sy in stars:
        ed.point((sx, sy), fill=(220, 255, 255))
    # Twinkle cross star at top-right
    ed.line([(78, 14), (86, 14)], fill=(255, 255, 255))
    ed.line([(82, 10), (82, 18)], fill=(255, 255, 255))
    # Shooting comet trail
    ed.line([(14, 22), (36, 12)], fill=(120, 240, 255), width=1)
    ed.ellipse([34, 10, 38, 14], fill=(255, 255, 255))

    # 3. Subtle Netscape helm/compass spokes radiating from horizon center
    hcx, hcy = lw // 2, horizon_y + 6
    for ang_deg in range(-155, -20, 22):
        ang = math.radians(ang_deg)
        x2 = hcx + int(math.cos(ang) * 44)
        y2 = hcy + int(math.sin(ang) * 44)
        ed.line([(hcx, hcy), (x2, y2)], fill=(20, 140, 155), width=1)

    # 4. Curved planetary horizon glow arc & perspective sea grid
    ed.arc([-30, horizon_y - 8, lw + 30, horizon_y + 42], start=200, end=340, fill=(170, 255, 255), width=3)
    ed.arc([-30, horizon_y - 5, lw + 30, horizon_y + 45], start=200, end=340, fill=(0, 210, 210), width=2)
    for gx in range(-20, lw + 25, 16):
        ed.line([(hcx, horizon_y + 2), (gx, lh)], fill=(0, 125, 140), width=1)

    # 5. Iconic Giant Netscape Arching Serif 'N' rising from bottom across the horizon
    # Draw custom high-detail polygon for the classic Netscape 'N' with curved bridge & serifs
    def draw_netscape_n(ox, oy, col_main, col_hi=None):
        # Left pillar (slightly tilted inward like classic Netscape perspective 'N')
        ed.polygon([
            (18 + ox, 84 + oy),
            (31 + ox, 16 + oy),
            (42 + ox, 16 + oy),
            (30 + ox, 84 + oy)
        ], fill=col_main)
        # Right pillar
        ed.polygon([
            (66 + ox, 84 + oy),
            (76 + ox, 18 + oy),
            (86 + ox, 18 + oy),
            (76 + ox, 84 + oy)
        ], fill=col_main)
        # Diagonal stroke connecting top-left to bottom-right
        ed.polygon([
            (34 + ox, 16 + oy),
            (43 + ox, 16 + oy),
            (75 + ox, 80 + oy),
            (65 + ox, 84 + oy)
        ], fill=col_main)
        # Classic Netscape bottom-left and top-right serifs
        ed.polygon([(11 + ox, 84 + oy), (36 + ox, 84 + oy), (36 + ox, 79 + oy), (13 + ox, 79 + oy)], fill=col_main)
        ed.polygon([(24 + ox, 16 + oy), (44 + ox, 16 + oy), (43 + ox, 21 + oy), (24 + ox, 21 + oy)], fill=col_main)
        ed.polygon([(69 + ox, 18 + oy), (91 + ox, 18 + oy), (90 + ox, 23 + oy), (69 + ox, 23 + oy)], fill=col_main)
        if col_hi:
            ed.line([(31 + ox, 16 + oy), (18 + ox, 83 + oy)], fill=col_hi, width=2)
            ed.line([(35 + ox, 17 + oy), (67 + ox, 81 + oy)], fill=col_hi, width=2)
            ed.line([(76 + ox, 18 + oy), (66 + ox, 83 + oy)], fill=col_hi, width=2)

    # Deep 3D extrusion shadow
    draw_netscape_n(3, 3, (0, 22, 35))
    draw_netscape_n(2, 2, (0, 65, 80))
    # Main metallic teal-silver 'N'
    draw_netscape_n(0, 0, (195, 245, 250), col_hi=(255, 255, 255))

    # Paste emblem and frame it with a 3D inset bevel
    img.paste(emblem, (lx0, ly0))
    draw_bevel_rect(d, [lx0 - 2, ly0 - 2, lx1 + 1, ly1 + 1], fill=None, light=(180, 230, 240), dark=(0, 15, 30), thickness=2, inset=True)

    # Right Side Typography
    f_top = load_font(["arialbd.ttf", "tahomabd.ttf"], 13)
    f_big = load_font(["timesbi.ttf", "timesbd.ttf", "arialbd.ttf"], 32)
    f_sub = load_font(["arialbd.ttf", "tahomabd.ttf"], 21)
    f_tag = load_font(["arialbd.ttf", "tahomabd.ttf"], 12)

    rx = 122
    draw_text_with_shadow(d, (rx, 10), "BEST VIEWED WITH", f_top, fill=(120, 245, 255), shadow=(0, 15, 30), offset=(1, 1))
    draw_text_with_shadow(d, (rx, 26), "NETSCAPE", f_big, fill=(255, 255, 255), shadow=(0, 20, 40), offset=(3, 3))
    draw_text_with_shadow(d, (rx, 64), "NOW! 3.0", f_sub, fill=(255, 230, 0), shadow=(0, 20, 40), offset=(2, 2))

    # "NAVIGATOR" pill badge on bottom right
    px0, py0, px1, py1 = 264, 65, 376, 91
    draw_bevel_rect(d, [px0, py0, px1, py1], fill=(180, 130, 0), light=(255, 235, 120), dark=(80, 50, 0), thickness=2, inset=False)
    tag_txt = "NAVIGATOR"
    tb = d.textbbox((0, 0), tag_txt, font=f_tag)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    draw_text_with_shadow(d, (px0 + (px1 - px0 - tw) // 2, py0 + (py1 - py0 - th) // 2 - 2), tag_txt, f_tag, fill=(255, 255, 235), shadow=(60, 30, 0), offset=(1, 1))

    # Subtle bottom rule
    d.line([(rx, 96), (376, 96)], fill=(0, 190, 210), width=2)

    img.save(os.path.join(assets_dir, "badge_netscape.png"))
    print("Created badge_netscape.png")


def create_badge_povray(assets_dir):
    """
    Create a full-column-width (392x112) Rendered with POV-Ray badge featuring a raytraced
    reflective gold/amber sphere over a 3D perspective checkered floor.
    """
    W, H = 392, 112
    img = Image.new("RGB", (W, H), (10, 8, 24))
    d = ImageDraw.Draw(img)

    # Background deep raytracer midnight gradient
    for y in range(H):
        t = y / float(H - 1)
        d.line([(0, y), (W - 1, y)], fill=(int(12 + 18 * t), int(8 + 10 * t), int(28 + 30 * (1 - t))))

    draw_bevel_rect(d, [0, 0, W - 1, H - 1], fill=None, light=(190, 195, 225), dark=(15, 10, 35), thickness=4, inset=False)

    # Left 100x95 Raytraced Scene Viewport
    lx0, ly0, lx1, ly1 = 10, 8, 110, 103
    lw, lh = lx1 - lx0, ly1 - ly0
    vp = Image.new("RGB", (lw, lh), (8, 2, 18))
    px = vp.load()

    horiz = int(lh * 0.62)
    # Render sky + 3D perspective checkered plane + raytraced sphere per-pixel!
    scx, scy, srad = 50.0, 44.0, 27.0
    for y in range(lh):
        for x in range(lw):
            # Check sphere intersection first
            dx = x - scx
            dy = y - scy
            dist_sq = dx * dx + dy * dy
            if dist_sq <= srad * srad:
                dz = math.sqrt(srad * srad - dist_sq)
                nx, ny, nz = dx / srad, dy / srad, dz / srad
                # Light direction (from bottom-right-front & top-left rim)
                lx_dir, ly_dir, lz_dir = 0.42, 0.25, 0.87
                ndotl = max(0.0, nx * lx_dir + ny * ly_dir + nz * lz_dir)
                # Specular highlight
                spec = max(0.0, ndotl) ** 22
                # Purple floor bounce reflection on lower hemisphere
                bounce = max(0.0, ny) * 0.45
                r = min(255, int(45 + 195 * ndotl + 255 * spec + 110 * bounce))
                g = min(255, int(25 + 145 * ndotl + 250 * spec + 15 * bounce))
                b = min(255, int(20 + 55 * ndotl + 230 * spec + 150 * bounce))
                px[x, y] = (r, g, b)
            elif y < horiz:
                # Deep purple/indigo sky gradient
                t = y / float(horiz)
                px[x, y] = (int(8 + 30 * t), int(2 + 8 * t), int(18 + 45 * t))
            else:
                # 3D perspective checkerboard floor
                fy = (y - horiz + 1.5) / float(lh - horiz)
                z = 1.0 / fy
                u = (x - lw * 0.5) * z * 0.09
                v = z * 1.4
                checker = (int(math.floor(u)) + int(math.floor(v))) & 1
                fog = min(1.0, fy ** 0.55)
                # Cast shadow under sphere
                sh_dx = (x - 46.0) / 30.0
                sh_dy = (y - 71.0) / 9.0
                in_shadow = 0.38 if (sh_dx * sh_dx + sh_dy * sh_dy) < 1.0 else 1.0
                if checker:
                    r = int(175 * fog * in_shadow)
                    g = int(20 * fog * in_shadow)
                    b = int(225 * fog * in_shadow)
                else:
                    r = int(22 * fog * in_shadow)
                    g = int(5 * fog * in_shadow)
                    b = int(38 * fog * in_shadow)
                px[x, y] = (r, g, b)

    img.paste(vp, (lx0, ly0))
    draw_bevel_rect(d, [lx0 - 2, ly0 - 2, lx1 + 1, ly1 + 1], fill=None, light=(170, 175, 215), dark=(10, 5, 25), thickness=2, inset=True)

    # Right Side Typography
    f_top = load_font(["arialbd.ttf", "tahomabd.ttf"], 14)
    f_big = load_font(["arialbd.ttf", "tahomabd.ttf"], 34)
    f_sub = load_font(["courbd.ttf", "arialbd.ttf"], 13)

    rx = 122
    d.line([(rx, 10), (378, 10)], fill=(100, 130, 210), width=1)
    draw_text_with_shadow(d, (rx, 14), "RENDERED WITH", f_top, fill=(175, 205, 255), shadow=(0, 0, 0), offset=(2, 2))
    # 3D Gold POV-Ray title
    draw_text_with_shadow(d, (rx, 34), "POV-Ray", f_big, fill=(255, 210, 25), shadow=(80, 40, 0), offset=(3, 3))
    d.text((rx - 1, 33), "POV-Ray", font=f_big, fill=(255, 235, 90))
    draw_text_with_shadow(d, (rx, 79), "RAYTRACER v3.0 // B-50", f_sub, fill=(225, 120, 255), shadow=(0, 0, 0), offset=(1, 1))

    img.save(os.path.join(assets_dir, "badge_povray.png"))
    print("Created badge_povray.png")


def create_badge_sgi(assets_dir):
    """
    Create a full-column-width (392x112) Powered by SGI IRIX badge featuring the iconic
    Silicon Graphics 3D isometric tubular cube emblem.
    """
    W, H = 392, 112
    img = Image.new("RGB", (W, H), (55, 0, 90))
    d = ImageDraw.Draw(img)

    # Rich SGI Indigo/Crimson gradient
    for y in range(H):
        t = y / float(H - 1)
        r = int(75 - 35 * t)
        g = int(5 + 10 * (1 - t))
        b = int(125 - 45 * t)
        d.line([(0, y), (W - 1, y)], fill=(r, g, b))

    draw_bevel_rect(d, [0, 0, W - 1, H - 1], fill=None, light=(225, 150, 255), dark=(25, 0, 45), thickness=4, inset=False)

    # Left 100x95 SGI 3D Cube Emblem Viewport
    lx0, ly0, lx1, ly1 = 10, 8, 110, 103
    lw, lh = lx1 - lx0, ly1 - ly0
    vp = Image.new("RGB", (lw, lh), (18, 0, 34))
    vd = ImageDraw.Draw(vp)

    # Subtle isometric grid in background
    for g in range(-40, 140, 16):
        vd.line([(0, g), (lw, g + 30)], fill=(42, 8, 68), width=1)
        vd.line([(0, g + 30), (lw, g)], fill=(42, 8, 68), width=1)

    # Draw the iconic 3D SGI Isometric Cube with shaded glowing tubes
    cx, cy = lw // 2, lh // 2
    R = 36
    # Outer hexagon vertices of isometric cube
    hex_pts = []
    for i in range(6):
        ang = math.radians(-90 + i * 60)
        hex_pts.append((cx + int(math.cos(ang) * R), cy + int(math.sin(ang) * R)))

    def draw_tube(p1, p2, col_dark, col_mid, col_hi):
        vd.line([p1, p2], fill=(0, 0, 0), width=11)
        vd.line([p1, p2], fill=col_dark, width=9)
        vd.line([p1, p2], fill=col_mid, width=5)
        vd.line([p1, p2], fill=col_hi, width=2)

    # Back/outer edges
    for i in range(6):
        p1 = hex_pts[i]
        p2 = hex_pts[(i + 1) % 6]
        if i in (0, 1):
            draw_tube(p1, p2, (0, 120, 150), (0, 220, 255), (200, 255, 255))
        elif i in (2, 3):
            draw_tube(p1, p2, (140, 0, 140), (240, 40, 255), (255, 190, 255))
        else:
            draw_tube(p1, p2, (70, 20, 170), (140, 90, 255), (220, 200, 255))

    # Inner Y-junction ribs of the SGI cube
    draw_tube((cx, cy), hex_pts[1], (0, 130, 160), (0, 240, 255), (220, 255, 255))
    draw_tube((cx, cy), hex_pts[3], (150, 0, 130), (255, 60, 220), (255, 210, 245))
    draw_tube((cx, cy), hex_pts[5], (90, 30, 180), (170, 110, 255), (235, 220, 255))

    # Glowing node joints
    for pt in hex_pts + [(cx, cy)]:
        vd.ellipse([pt[0] - 4, pt[1] - 4, pt[0] + 4, pt[1] + 4], fill=(255, 255, 255), outline=(0, 220, 255))

    img.paste(vp, (lx0, ly0))
    draw_bevel_rect(d, [lx0 - 2, ly0 - 2, lx1 + 1, ly1 + 1], fill=None, light=(215, 140, 255), dark=(20, 0, 40), thickness=2, inset=True)

    # Right Side Typography
    f_top = load_font(["arialbd.ttf", "tahomabd.ttf"], 14)
    f_big = load_font(["arialbd.ttf", "tahomabd.ttf"], 33)
    f_sub = load_font(["courbd.ttf", "arialbd.ttf"], 13)

    rx = 122
    draw_text_with_shadow(d, (rx, 12), "POWERED BY 64-BIT", f_top, fill=(255, 215, 0), shadow=(25, 0, 40), offset=(2, 2))
    draw_text_with_shadow(d, (rx, 33), "SGI IRIX 6.2", f_big, fill=(0, 255, 255), shadow=(20, 0, 45), offset=(3, 3))
    draw_text_with_shadow(d, (rx, 77), "SILICON GRAPHICS INDIGO2", f_sub, fill=(255, 150, 255), shadow=(20, 0, 40), offset=(1, 1))

    img.save(os.path.join(assets_dir, "badge_sgi.png"))
    print("Created badge_sgi.png")


def create_badge_800x600(assets_dir):
    """
    Create a full-column-width (392x112) Best at 800x600 badge featuring a 90s SVGA CRT monitor icon.
    """
    W, H = 392, 112
    img = Image.new("RGB", (W, H), (0, 20, 8))
    d = ImageDraw.Draw(img)

    for y in range(H):
        t = y / float(H - 1)
        d.line([(0, y), (W - 1, y)], fill=(0, int(28 - 16 * t), int(10 - 6 * t)))

    draw_bevel_rect(d, [0, 0, W - 1, H - 1], fill=None, light=(80, 255, 120), dark=(0, 60, 20), thickness=4, inset=False)

    # Left 100x95 CRT Monitor Icon Box
    lx0, ly0, lx1, ly1 = 10, 8, 110, 103
    lw, lh = lx1 - lx0, ly1 - ly0
    vp = Image.new("RGB", (lw, lh), (0, 12, 4))
    vd = ImageDraw.Draw(vp)

    # Monitor swivel base & neck
    vd.polygon([(34, 88), (66, 88), (74, 93), (26, 93)], fill=(150, 150, 140), outline=(60, 60, 55))
    vd.rectangle([42, 76, 58, 88], fill=(120, 120, 112), outline=(50, 50, 45))

    # Monitor outer beige 3D casing
    draw_bevel_rect(vd, [12, 8, 88, 78], fill=(195, 192, 180), light=(245, 245, 235), dark=(90, 88, 80), thickness=3, inset=False)
    # Recessed dark CRT screen
    draw_bevel_rect(vd, [19, 15, 81, 66], fill=(0, 32, 12), light=(70, 70, 65), dark=(30, 30, 28), thickness=2, inset=True)

    # Glowing phosphor grid & diagonal resize arrows inside CRT screen
    for gx in range(24, 80, 10):
        vd.line([(gx, 17), (gx, 64)], fill=(0, 85, 30))
    for gy in range(20, 65, 9):
        vd.line([(21, gy), (79, gy)], fill=(0, 85, 30))

    # Diagonal dimension line with arrowheads
    vd.line([(25, 21), (75, 59)], fill=(0, 255, 100), width=2)
    vd.polygon([(23, 19), (33, 20), (24, 28)], fill=(180, 255, 200))
    vd.polygon([(77, 61), (67, 60), (76, 52)], fill=(180, 255, 200))

    # Green power LED on monitor bezel
    vd.rectangle([72, 70, 79, 74], fill=(0, 255, 80), outline=(0, 90, 20))

    img.paste(vp, (lx0, ly0))
    draw_bevel_rect(d, [lx0 - 2, ly0 - 2, lx1 + 1, ly1 + 1], fill=None, light=(0, 220, 90), dark=(0, 50, 15), thickness=2, inset=True)

    # Right Side Typography
    f_top = load_font(["courbd.ttf", "arialbd.ttf"], 14)
    f_big = load_font(["arialbd.ttf", "tahomabd.ttf"], 34)
    f_sub = load_font(["courbd.ttf", "arialbd.ttf"], 13)

    rx = 122
    draw_text_with_shadow(d, (rx, 12), "BEST VIEWED AT SVGA", f_top, fill=(0, 255, 100), shadow=(0, 0, 0), offset=(2, 2))
    draw_text_with_shadow(d, (rx, 32), "800 x 600", f_big, fill=(255, 255, 255), shadow=(0, 110, 40), offset=(3, 3))
    draw_text_with_shadow(d, (rx, 77), "256 COLORS // 60Hz CRT", f_sub, fill=(255, 235, 0), shadow=(0, 0, 0), offset=(1, 1))

    img.save(os.path.join(assets_dir, "badge_800x600.png"))
    print("Created badge_800x600.png")


def create_badge_notepad(assets_dir):
    """
    Create a full-column-width (392x112) Made with Notepad badge featuring the classic
    Windows 95 spiral-bound Notepad icon and crisp Win95 UI styling.
    """
    W, H = 392, 112
    img = Image.new("RGB", (W, H), (212, 208, 200))
    d = ImageDraw.Draw(img)

    # Classic Win95 3D button bevel
    draw_bevel_rect(d, [0, 0, W - 1, H - 1], fill=(224, 224, 224), light=(255, 255, 255), dark=(64, 64, 64), thickness=4, inset=False)
    d.rectangle([4, 4, W - 5, H - 5], outline=(160, 160, 160), width=1)

    # Left 100x95 Win95 Notepad Icon Box (on classic #008080 teal desktop background)
    lx0, ly0, lx1, ly1 = 10, 8, 110, 103
    lw, lh = lx1 - lx0, ly1 - ly0
    vp = Image.new("RGB", (lw, lh), (0, 128, 128))
    vd = ImageDraw.Draw(vp)

    # Drop shadow of notepad
    vd.rectangle([24, 16, 84, 90], fill=(0, 60, 60))
    # Teal/cyan notepad backing cover
    vd.rectangle([18, 12, 78, 86], fill=(0, 165, 165), outline=(0, 0, 0), width=2)
    # White paper pages
    vd.rectangle([22, 18, 74, 81], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
    # Blue horizontal ruled lines + simulated HTML tags on the page
    for ly in range(28, 76, 8):
        vd.line([(26, ly), (70, ly)], fill=(180, 215, 255), width=1)
    # Simulated dark code lines
    code_bars = [(27, 26, 52), (31, 34, 66), (31, 42, 60), (27, 50, 68), (31, 58, 55), (27, 66, 48)]
    for cx0, cy, cx1 in code_bars:
        vd.line([(cx0, cy), (cx1, cy)], fill=(0, 0, 140), width=2)
    # Blinking red cursor mark
    vd.rectangle([52, 63, 55, 69], fill=(255, 0, 0))

    # Classic top spiral wire bindings
    for sx in range(25, 73, 8):
        vd.rectangle([sx, 8, sx + 3, 19], fill=(80, 80, 90), outline=(0, 0, 0))
        vd.point((sx + 1, 11), fill=(255, 255, 255))

    img.paste(vp, (lx0, ly0))
    draw_bevel_rect(d, [lx0 - 2, ly0 - 2, lx1 + 1, ly1 + 1], fill=None, light=(255, 255, 255), dark=(64, 64, 64), thickness=2, inset=True)

    # Right Side Win95 Title Bar + Typography
    d.rectangle([118, 10, 380, 32], fill=(0, 0, 128))
    f_bar = load_font(["arialbd.ttf", "tahomabd.ttf"], 13)
    f_big = load_font(["arialbd.ttf", "tahomabd.ttf"], 31)
    f_sub = load_font(["courbd.ttf", "arialbd.ttf"], 13)

    d.text((125, 13), "100% HAND-CODED WITH", font=f_bar, fill=(255, 255, 255))
    draw_text_with_shadow(d, (122, 38), "NOTEPAD.EXE", f_big, fill=(210, 0, 0), shadow=(255, 255, 255), offset=(2, 2))
    d.text((122, 78), "PURE HTML 3.2 // WIN95", font=f_sub, fill=(0, 0, 128))

    img.save(os.path.join(assets_dir, "badge_notepad.png"))
    print("Created badge_notepad.png")


def create_retro_elements():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    assets_dir = os.path.join(project_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    create_starfield(assets_dir)
    create_warning_strobe(assets_dir)
    create_visitor_counter(assets_dir)
    create_under_construction(assets_dir)
    create_badge_netscape(assets_dir)
    create_badge_povray(assets_dir)
    create_badge_sgi(assets_dir)
    create_badge_800x600(assets_dir)
    create_badge_notepad(assets_dir)


if __name__ == "__main__":
    create_retro_elements()
