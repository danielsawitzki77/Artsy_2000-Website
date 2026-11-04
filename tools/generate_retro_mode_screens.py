import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_blueprint_screen(out_path):
    width, height = 640, 480
    img = Image.new("RGB", (width, height), (10, 30, 60))
    draw = ImageDraw.Draw(img)
    
    # 1. Blueprint Grid
    grid_size = 20
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=(18, 50, 95), width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=(18, 50, 95), width=1)

    # Major grid lines every 100px
    for x in range(0, width, 100):
        draw.line([(x, 0), (x, height)], fill=(28, 75, 140), width=1)
    for y in range(0, height, 100):
        draw.line([(0, y), (width, y)], fill=(28, 75, 140), width=1)

    # 2. Border & Title Block
    draw.rectangle([10, 10, width - 10, height - 10], outline=(100, 200, 255), width=2)
    draw.rectangle([14, 14, width - 14, height - 14], outline=(50, 130, 200), width=1)

    # Title block bottom right
    tb_w, tb_h = 240, 70
    draw.rectangle([width - 10 - tb_w, height - 10 - tb_h, width - 10, height - 10], fill=(5, 20, 45), outline=(100, 200, 255), width=2)
    draw.text((width - 10 - tb_w + 8, height - 10 - tb_h + 6), "BUCK FIFTY ARCHITECTURAL DWG", fill=(200, 240, 255))
    draw.text((width - 10 - tb_w + 8, height - 10 - tb_h + 22), "PROJECT: SUITE G BLUEPRINT LABYRINTH", fill=(130, 200, 255))
    draw.text((width - 10 - tb_w + 8, height - 10 - tb_h + 38), "DWG NO: B50-CAD-0666  REV: 0.1", fill=(100, 180, 240))
    draw.text((width - 10 - tb_w + 8, height - 10 - tb_h + 52), "POV-RAY EXPORT: READY [KEY E]", fill=(0, 255, 200))

    # Top Header
    draw.text((24, 20), "=== BUCK FIFTY CAD-2000 ARCHITECTURAL BLUEPRINT SCHEMATIC ===", fill=(100, 220, 255))
    draw.text((24, 36), "SCORE: 084500   STEP COST: -50 PTS   PEN CATCH BONUS: +150 PTS", fill=(255, 255, 100))

    # 3. Draw Maze Walls in Cyan drafting double lines
    maze_ox, maze_oy = 40, 60
    mw, mh = 22, 16
    cs = 18

    # A simple labyrinth layout
    walls = [
        # outer box
        (0, 0, mw, 0), (mw, 0, mw, mh), (mw, mh, 0, mh), (0, mh, 0, 0),
        # internal walls
        (0, 4, 8, 4), (8, 4, 8, 8), (4, 8, 12, 8), (12, 2, 12, 8), (12, 2, 18, 2),
        (18, 2, 18, 7), (14, 7, 22, 7), (4, 10, 4, 14), (4, 12, 10, 12), (10, 10, 10, 15),
        (14, 10, 14, 14), (14, 12, 18, 12), (18, 9, 18, 14), (8, 14, 16, 14), (20, 10, 20, 15)
    ]

    for (x1, y1, x2, y2) in walls:
        px1 = maze_ox + x1 * cs
        py1 = maze_oy + y1 * cs
        px2 = maze_ox + x2 * cs
        py2 = maze_oy + y2 * cs
        # Obsidian fill wall
        draw.line([(px1, py1), (px2, py2)], fill=(120, 220, 255), width=4)
        draw.line([(px1, py1), (px2, py2)], fill=(20, 80, 140), width=2)

    # 4. Draw Scanning Pen Heads (Cyan circles with sweep arcs)
    pens = [(maze_ox + 5 * cs, maze_oy + 4 * cs), (maze_ox + 12 * cs, maze_oy + 5 * cs), (maze_ox + 16 * cs, maze_oy + 11 * cs)]
    for px, py in pens:
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(0, 200, 255), outline=(255, 255, 255), width=2)
        # Scanline cone
        draw.line([(px, py), (px + 25, py - 12)], fill=(0, 255, 255), width=1)
        draw.line([(px, py), (px + 25, py + 12)], fill=(0, 255, 255), width=1)
        draw.arc([px + 10, py - 14, px + 30, py + 14], -30, 30, fill=(150, 255, 255), width=2)

    # 5. Wandering Rubberstamp Square (Charcoal/ink stamp box with crosshair)
    rx, ry = maze_ox + 12 * cs, maze_oy + 5 * cs  # perfectly overlapping pen head for the catch!
    draw.rectangle([rx - 14, ry - 14, rx + 14, ry + 14], fill=None, outline=(255, 220, 50), width=3)
    draw.line([(rx - 10, ry), (rx + 10, ry)], fill=(255, 220, 50), width=2)
    draw.line([(rx, ry - 10), (rx, ry + 10)], fill=(255, 220, 50), width=2)

    # Catch alert notification bubble
    draw.rectangle([rx + 18, ry - 20, rx + 180, ry + 14], fill=(255, 240, 200), outline=(200, 100, 0), width=2)
    draw.text((rx + 24, ry - 16), "PEN HIT! +150 PTS", fill=(180, 40, 0))
    draw.text((rx + 24, ry - 2), "[SPACE / GAMEPAD A]", fill=(0, 80, 180))

    # Exit Diamond
    ex, ey = maze_ox + 21 * cs, maze_oy + 15 * cs
    draw.polygon([(ex, ey - 10), (ex + 10, ey), (ex, ey + 10), (ex - 10, ey)], fill=(0, 255, 100), outline=(255, 255, 255))
    draw.text((ex - 14, ey + 14), "EXIT", fill=(0, 255, 100))

    # Bottom Legend
    draw.rectangle([20, height - 52, width - 260, height - 16], fill=(0, 15, 35), outline=(50, 120, 180), width=1)
    draw.text((28, height - 46), "CONTROLS: ARROWS/WASD: Move Cursor | SPACE/A: Catch Scanning Pen (+150 PTS)", fill=(200, 240, 255))
    draw.text((28, height - 30), "KEY E: Export POV-Ray Turntable Scene | ESC/B: Return to Intake Terminal", fill=(130, 200, 255))

    img.save(out_path)
    print("Saved blueprint screen:", out_path)


def create_the_rise_screen(out_path):
    width, height = 640, 480
    img = Image.new("RGB", (width, height), (5, 8, 18))
    draw = ImageDraw.Draw(img)

    # 1. Perspective Checkerboard Floor
    horizon_y = 190
    vp_x = width // 2

    # Sky gradient / stars
    for y in range(0, horizon_y):
        t = y / horizon_y
        r = int(5 + 15 * t)
        g = int(8 + 25 * t)
        b = int(25 + 50 * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Draw checkerboard tiles in perspective
    rows = 18
    row_y = [int(horizon_y + (height - horizon_y) * (i / rows)**2.2) for i in range(rows + 1)]
    cols = 20

    for i in range(rows):
        y1 = row_y[i]
        y2 = row_y[i + 1]
        for c in range(cols):
            # Vanishing lines
            x1_a = int(vp_x + (c - cols/2) * (width / cols) * ((y1 - horizon_y) / (height - horizon_y)) * 2.8)
            x1_b = int(vp_x + (c + 1 - cols/2) * (width / cols) * ((y1 - horizon_y) / (height - horizon_y)) * 2.8)
            x2_a = int(vp_x + (c - cols/2) * (width / cols) * ((y2 - horizon_y) / (height - horizon_y)) * 2.8)
            x2_b = int(vp_x + (c + 1 - cols/2) * (width / cols) * ((y2 - horizon_y) / (height - horizon_y)) * 2.8)

            is_even = (i + c) % 2 == 0
            tile_col = (10, 45, 60) if is_even else (0, 15, 25)
            draw.polygon([(x1_a, y1), (x1_b, y1), (x2_b, y2), (x2_a, y2)], fill=tile_col, outline=(20, 80, 100))

    # 2. Dynamic 3D Primitives (Chrome Sphere, Brass Cylinder, Purple Torus, Green Cone)
    # Chrome sphere with specular reflection
    sx, sy, sr = 240, 250, 65
    for r in range(sr, 0, -2):
        frac = r / sr
        r_col = int(40 + (1.0 - frac) * 200)
        g_col = int(80 + (1.0 - frac) * 170)
        b_col = int(120 + (1.0 - frac) * 135)
        # Offset highlight towards top-left
        ox = sx - int((sr - r) * 0.4)
        oy = sy - int((sr - r) * 0.4)
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(r_col, g_col, b_col))

    # Golden Cylinder
    cx, cy, cw, ch = 410, 230, 45, 80
    draw.ellipse([cx - cw, cy + ch - 15, cx + cw, cy + ch + 15], fill=(160, 120, 20), outline=(220, 180, 40))
    draw.polygon([(cx - cw, cy), (cx + cw, cy), (cx + cw, cy + ch), (cx - cw, cy + ch)], fill=(200, 150, 30))
    draw.ellipse([cx - cw, cy - 15, cx + cw, cy + 15], fill=(240, 190, 50), outline=(255, 230, 100))

    # Neon Violet Torus / Ring floating above
    tx, ty = 320, 150
    draw.ellipse([tx - 70, ty - 22, tx + 70, ty + 22], fill=None, outline=(255, 60, 220), width=12)
    draw.ellipse([tx - 65, ty - 18, tx + 65, ty + 18], fill=None, outline=(255, 200, 255), width=3)

    # Emerald Tetrahedron / Cone
    kx, ky = 120, 270
    draw.polygon([(kx, ky - 60), (kx + 40, ky + 40), (kx - 40, ky + 40)], fill=(0, 180, 100), outline=(50, 255, 160), width=2)
    draw.line([(kx, ky - 60), (kx, ky + 40)], fill=(120, 255, 200), width=2)

    # 3. Rotating Retry Cube indicator in top right
    rc_x, rc_y = width - 70, 60
    draw.rectangle([rc_x - 45, rc_y - 45, rc_x + 45, rc_y + 45], fill=(10, 10, 30), outline=(255, 0, 128), width=2)
    draw.polygon([(rc_x - 20, rc_y - 15), (rc_x + 10, rc_y - 30), (rc_x + 35, rc_y - 15), (rc_x + 5, rc_y)], outline=(255, 100, 200), width=2)
    draw.polygon([(rc_x - 20, rc_y - 15), (rc_x + 5, rc_y), (rc_x + 5, rc_y + 30), (rc_x - 20, rc_y + 15)], outline=(255, 100, 200), width=2)
    draw.polygon([(rc_x + 35, rc_y - 15), (rc_x + 5, rc_y), (rc_x + 5, rc_y + 30), (rc_x + 35, rc_y + 15)], outline=(255, 100, 200), width=2)
    draw.text((rc_x - 38, rc_y + 32), "RETRY CUBE", fill=(255, 150, 220))

    # Top HUD
    draw.rectangle([10, 10, 380, 50], fill=(0, 0, 0, 180), outline=(0, 200, 255), width=2)
    draw.text((20, 16), "PROTOCOL: THE RISE (64-BIT SOFTWARE RAYTRACER)", fill=(0, 255, 255))
    draw.text((20, 32), "ACTIVE PRIMITIVES: 6 | RAYS/SEC: 420,000 | PHONG SPECULAR: ON", fill=(200, 220, 255))

    # 4. Ammo Charge Meter & Launch HUD
    draw.rectangle([20, height - 60, width - 20, height - 14], fill=(0, 10, 20), outline=(255, 200, 0), width=2)
    draw.text((30, height - 52), "AMMO LAUNCHER STATUS: [SPACE / GAMEPAD A] HOLD TO CHARGE IMPULSE BODY", fill=(255, 220, 100))
    # Meter bar
    draw.rectangle([30, height - 34, 300, height - 20], fill=(20, 30, 40), outline=(100, 100, 100))
    draw.rectangle([32, height - 32, 260, height - 22], fill=(255, 180, 0))
    draw.text((310, height - 34), "CHARGE: 88% (SPAWN: SPHERE)", fill=(255, 255, 150))
    draw.text((500, height - 34), "RENDER: QUAD / BILINEAR", fill=(100, 255, 200))

    img.save(out_path)
    print("Saved the rise screen:", out_path)


def create_edge_mode_screen(out_path):
    width, height = 640, 480
    img = Image.new("RGB", (width, height), (15, 8, 28))
    draw = ImageDraw.Draw(img)

    # Background deep space with star dots
    import random
    rng = random.Random(42)
    for _ in range(120):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height)
        draw.point((sx, sy), fill=(rng.randint(150, 255), rng.randint(150, 255), 255))

    # 1. 3D Perspective Pipe Network (Aluminum Tubes on Cube Vertices)
    # Draw major cube wireframe in perspective
    center_x, center_y = 320, 230
    cube_nodes = [
        (-140, -100, -80), (140, -100, -80), (140, 100, -80), (-140, 100, -80),
        (-180, -140, 80), (180, -140, 80), (180, 140, 80), (-180, 140, 80)
    ]
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]

    # Draw aluminum pipes with thickness and highlights
    for (i1, i2) in edges:
        n1 = cube_nodes[i1]
        n2 = cube_nodes[i2]
        x1 = center_x + n1[0]
        y1 = center_y + n1[1]
        x2 = center_x + n2[0]
        y2 = center_y + n2[1]

        # Draw thick pipe
        draw.line([(x1, y1), (x2, y2)], fill=(120, 140, 170), width=10)
        draw.line([(x1, y1), (x2, y2)], fill=(220, 235, 255), width=3) # specular ridge

    # Joint spheres
    for n in cube_nodes:
        nx = center_x + n[0]
        ny = center_y + n[1]
        draw.ellipse([nx - 12, ny - 12, nx + 12, ny + 12], fill=(180, 190, 210), outline=(255, 255, 255), width=2)

    # 2. Player Runner traversing the pipe axis
    px = center_x + 30
    py = center_y + 100
    draw.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(255, 0, 80), outline=(255, 200, 220), width=3)
    # Banking indicator trail
    draw.line([(px - 30, py + 18), (px + 30, py - 18)], fill=(0, 255, 255), width=3)
    draw.text((px - 28, py - 32), "TEST SUBJECT 13", fill=(255, 100, 150))

    # 3. Falling Edge Warning Hazard
    hx, hy = center_x + 140, center_y
    draw.rectangle([hx - 25, hy - 40, hx + 25, hy + 40], outline=(255, 50, 50), width=2)
    draw.line([(hx - 20, hy - 35), (hx + 20, hy + 35)], fill=(255, 0, 0), width=3)
    draw.line([(hx + 20, hy - 35), (hx - 20, hy + 35)], fill=(255, 0, 0), width=3)
    draw.text((hx - 40, hy + 46), "FALLING EDGE!", fill=(255, 80, 80))

    # Top HUD
    draw.rectangle([14, 12, width - 14, 52], fill=(10, 0, 20), outline=(200, 50, 255), width=2)
    draw.text((24, 18), "PROTOCOL: EDGE COMPUTING (6-FACED 3D HYPERCUBE PIPE NETWORK)", fill=(240, 100, 255))
    draw.text((24, 34), "PIPE TRAVERSAL: FACE 3 OF 6 | VELOCITY: 88 KNOTS | COUNTER-STEER: ACTIVE", fill=(180, 200, 255))

    # Bottom Overview Camera Bar
    draw.rectangle([14, height - 56, width - 14, height - 14], fill=(10, 5, 25), outline=(0, 255, 200), width=2)
    draw.text((24, height - 48), "[SPACE / GAMEPAD A] HOLD OVERVIEW CAMERA &bull; [A / D] ROTATE PIPE AXIS", fill=(0, 255, 220))
    draw.text((24, height - 32), "BLOB RESPAWN: STANDBY &bull; ESC: ABORT COGNITIVE RUN", fill=(140, 210, 255))

    img.save(out_path)
    print("Saved edge mode screen:", out_path)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    assets_dir = os.path.join(project_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    create_blueprint_screen(os.path.join(assets_dir, "blueprint_mode_screen.png"))
    create_the_rise_screen(os.path.join(assets_dir, "the_rise_screen.png"))
    create_edge_mode_screen(os.path.join(assets_dir, "edge_mode_screen.png"))
