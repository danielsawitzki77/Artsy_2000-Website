import os
from PIL import Image, ImageDraw, ImageFont

def create_retro_elements():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    assets_dir = os.path.join(project_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Starfield background tile (64x64)
    import random
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
            star_draw.point(((x+1)%128, y), fill=color)
            star_draw.point((x, (y+1)%128), fill=color)
    star_img.save(os.path.join(assets_dir, "stars_bg.png"))
    print("Created stars_bg.png")

    # 2. 88x31 Badges:
    # Netscape Now
    ns_img = Image.new("RGB", (88, 31), (0, 0, 0))
    d = ImageDraw.Draw(ns_img)
    d.rectangle([0, 0, 87, 30], outline=(100, 100, 100))
    d.rectangle([1, 1, 86, 29], fill=(0, 50, 100))
    d.rectangle([2, 2, 28, 28], fill=(0, 120, 120))
    d.text((8, 6), "N", fill=(255, 255, 255))
    d.text((32, 4), "NETSCAPE", fill=(255, 255, 0))
    d.text((38, 16), "NOW 3.0", fill=(255, 255, 255))
    ns_img.save(os.path.join(assets_dir, "badge_netscape.png"))

    # Made with Notepad
    np_img = Image.new("RGB", (88, 31), (192, 192, 192))
    d = ImageDraw.Draw(np_img)
    d.rectangle([0, 0, 87, 30], outline=(0, 0, 0))
    d.rectangle([2, 2, 85, 28], fill=(255, 255, 255))
    d.text((6, 3), "MADE WITH", fill=(0, 0, 128))
    d.text((8, 15), "NOTEPAD", fill=(255, 0, 0))
    np_img.save(os.path.join(assets_dir, "badge_notepad.png"))

    # 800x600 Recommended
    res_img = Image.new("RGB", (88, 31), (0, 0, 0))
    d = ImageDraw.Draw(res_img)
    d.rectangle([0, 0, 87, 30], outline=(0, 255, 0))
    d.text((10, 4), "BEST AT", fill=(0, 255, 0))
    d.text((12, 16), "800 x 600", fill=(255, 255, 255))
    res_img.save(os.path.join(assets_dir, "badge_800x600.png"))

    # SGI Powered Badge
    sgi_img = Image.new("RGB", (88, 31), (80, 0, 120))
    d = ImageDraw.Draw(sgi_img)
    d.rectangle([0, 0, 87, 30], outline=(200, 100, 255))
    d.text((6, 4), "POWERED BY", fill=(255, 200, 0))
    d.text((18, 16), "SGI IRIX", fill=(0, 255, 255))
    sgi_img.save(os.path.join(assets_dir, "badge_sgi.png"))

    # 3. Animated Under Construction Bar (GIF)
    cons_frames = []
    width, height = 300, 40
    for offset in range(0, 20, 2):
        frame = Image.new("RGB", (width, height), (0, 0, 0))
        d = ImageDraw.Draw(frame)
        # Hazard stripes
        for x in range(-40, width + 40, 20):
            d.polygon([
                (x + offset, 0),
                (x + offset + 10, 0),
                (x + offset - 10, height),
                (x + offset - 20, height)
            ], fill=(255, 220, 0))
        # Black center box
        d.rectangle([30, 6, width - 30, height - 6], fill=(0, 0, 0), outline=(255, 255, 255))
        d.text((55, 12), "UNDER INVESTIGATION / B50", fill=(255, 50, 50))
        cons_frames.append(frame)

    cons_frames[0].save(
        os.path.join(assets_dir, "under_construction.gif"),
        save_all=True,
        append_images=cons_frames[1:],
        duration=100,
        loop=0
    )
    print("Created under_construction.gif")

    # 4. Animated Warning Beacon / Biohazard strobe (GIF)
    hazard_frames = []
    for f in range(8):
        h_img = Image.new("RGB", (48, 48), (0, 0, 0))
        d = ImageDraw.Draw(h_img)
        radius = 16 + (f % 4) * 3
        glow = 255 if f < 4 else 80
        color = (glow, 0, 0)
        d.ellipse([24 - radius, 24 - radius, 24 + radius, 24 + radius], outline=color, width=2)
        d.polygon([(24, 8), (40, 38), (8, 38)], outline=(255, 255, 0), fill=(200 if f < 4 else 50, 150, 0))
        d.text((22, 18), "!", fill=(0, 0, 0))
        hazard_frames.append(h_img)
    hazard_frames[0].save(
        os.path.join(assets_dir, "warning_strobe.gif"),
        save_all=True,
        append_images=hazard_frames[1:],
        duration=120,
        loop=0
    )
    print("Created warning_strobe.gif")

    # 5. Visitor Counter digits strip
    counter_img = Image.new("RGB", (120, 26), (10, 10, 10))
    d = ImageDraw.Draw(counter_img)
    d.rectangle([0, 0, 119, 25], outline=(100, 100, 100))
    digits = "0 0 1 3 3 7"
    d.text((16, 6), digits, fill=(0, 255, 100))
    counter_img.save(os.path.join(assets_dir, "counter.png"))
    print("Created counter.png")

if __name__ == "__main__":
    create_retro_elements()
