import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def make_b_polygons():
    """
    Returns (outer_poly, [hole_top, hole_bot]) for the Buck-Fifty 'B' in face-local (u, v) in [-1, 1]^2,
    matching the iconic beveled brutalist/synthwave 'B' from ref_bf_original.png.
    """
    outer = [
        (-0.80,  0.76),  # top-left serif tip
        ( 0.42,  0.76),  # top bar right
        ( 0.70,  0.48),  # upper loop top-right bevel
        ( 0.70,  0.14),  # upper loop bottom-right
        ( 0.40,  0.00),  # middle waist V-notch
        ( 0.74, -0.16),  # lower loop top-right
        ( 0.74, -0.48),  # lower loop bottom-right bevel
        ( 0.44, -0.76),  # bottom bar right
        (-0.80, -0.76),  # bottom-left serif tip
        (-0.62, -0.52),  # bottom-left serif inner corner
        (-0.62,  0.52),  # top-left serif inner corner
    ]
    hole_top = [
        (-0.24,  0.46),
        ( 0.24,  0.46),
        ( 0.34,  0.35),
        ( 0.34,  0.22),
        ( 0.24,  0.13),
        (-0.24,  0.13),
    ]
    hole_bot = [
        (-0.24, -0.13),
        ( 0.26, -0.13),
        ( 0.36, -0.23),
        ( 0.36, -0.36),
        ( 0.26, -0.46),
        (-0.24, -0.46),
    ]
    return outer, [hole_top, hole_bot]


def make_f_polygons():
    """
    Returns (outer_poly, []) for the Buck-Fifty 'F' in face-local (u, v) in [-1, 1]^2,
    matching the iconic beveled 'F' from ref_bf_original.png.
    """
    outer = [
        (-0.74,  0.76),  # top-left corner
        ( 0.80,  0.76),  # top-right sharp spur
        ( 0.56,  0.34),  # top bar bottom-right bevel
        (-0.22,  0.34),  # stem inner top
        (-0.22,  0.10),  # mid bar top-left
        ( 0.52,  0.10),  # mid bar top-right
        ( 0.32, -0.26),  # mid bar bottom-right bevel
        (-0.22, -0.26),  # stem inner mid
        (-0.22, -0.54),  # stem bottom-right before point
        (-0.56, -0.82),  # dramatic pointed bottom tip of F
        (-0.68, -0.60),  # bottom-left bevel of stem
        (-0.68,  0.54),  # left spine
    ]
    return outer, []


def rotate_point(pt, yaw, tilt):
    x, y, z = pt
    cy, sy = math.cos(yaw), math.sin(yaw)
    rx = x * cy + z * sy
    rz = -x * sy + z * cy
    ry = y
    ct, st = math.cos(tilt), math.sin(tilt)
    ry2 = ry * ct - rz * st
    rz2 = ry * st + rz * ct
    return np.array([rx, ry2, rz2], dtype=np.float64)


def project_point(pt_cam, cx, cy, scale, cam_dist=5.0):
    x, y, z = pt_cam
    depth = cam_dist - z
    persp = cam_dist / max(0.5, depth)
    sx = cx + x * scale * persp
    sy = cy - y * scale * persp
    return (float(sx), float(sy), float(z))


def build_box_faces_and_edges(x0, x1, y0, y1, z0, z1):
    v = [
        np.array([x0, y0, z0], dtype=float),
        np.array([x1, y0, z0], dtype=float),
        np.array([x1, y1, z0], dtype=float),
        np.array([x0, y1, z0], dtype=float),
        np.array([x0, y0, z1], dtype=float),
        np.array([x1, y0, z1], dtype=float),
        np.array([x1, y1, z1], dtype=float),
        np.array([x0, y1, z1], dtype=float),
    ]
    faces = [
        ([v[4], v[5], v[6], v[7]], np.array([ 0.0,  0.0,  1.0])),  # +Z
        ([v[1], v[0], v[3], v[2]], np.array([ 0.0,  0.0, -1.0])),  # -Z
        ([v[5], v[1], v[2], v[6]], np.array([ 1.0,  0.0,  0.0])),  # +X
        ([v[0], v[4], v[7], v[3]], np.array([-1.0,  0.0,  0.0])),  # -X
        ([v[7], v[6], v[2], v[3]], np.array([ 0.0,  1.0,  0.0])),  # +Y
        ([v[0], v[1], v[5], v[4]], np.array([ 0.0, -1.0,  0.0])),  # -Y
    ]
    edges = [
        (v[0], v[1]), (v[1], v[2]), (v[2], v[3]), (v[3], v[0]),
        (v[4], v[5]), (v[5], v[6]), (v[6], v[7]), (v[7], v[4]),
        (v[0], v[4]), (v[1], v[5]), (v[2], v[6]), (v[3], v[7]),
    ]
    return faces, edges


def rasterize_convex_quad_zbuf(color_buf, z_buf, pts_proj, color_top, color_bot=None):
    """
    Rasterizes a 3D projected convex polygon into (color_buf, z_buf) using plane/barycentric interpolation.
    pts_proj: list of (sx, sy, z) with len >= 3.
    """
    h, w, _ = color_buf.shape
    if color_bot is None:
        color_bot = color_top

    # Split into triangles (0, i, i+1)
    for i in range(1, len(pts_proj) - 1):
        x0, y0, z0 = pts_proj[0]
        x1, y1, z1 = pts_proj[i]
        x2, y2, z2 = pts_proj[i + 1]

        xmin = max(0, int(math.floor(min(x0, x1, x2))))
        xmax = min(w - 1, int(math.ceil(max(x0, x1, x2))))
        ymin = max(0, int(math.floor(min(y0, y1, y2))))
        ymax = min(h - 1, int(math.ceil(max(y0, y1, y2))))
        if xmin > xmax or ymin > ymax:
            continue

        denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(denom) < 1e-6:
            continue

        yy, xx = np.mgrid[ymin:ymax + 1, xmin:xmax + 1]
        px = xx + 0.5
        py = yy + 0.5

        w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / denom
        w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / denom
        w2 = 1.0 - w0 - w1

        inside = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
        if not np.any(inside):
            continue

        z_interp = w0 * z0 + w1 * z1 + w2 * z2
        sub_z = z_buf[ymin:ymax + 1, xmin:xmax + 1]
        vis = inside & (z_interp >= sub_z)
        if not np.any(vis):
            continue

        sub_z[vis] = z_interp[vis]
        sub_col = color_buf[ymin:ymax + 1, xmin:xmax + 1]
        for c in range(3):
            sub_col[:, :, c][vis] = color_top[c]


def draw_3d_line_zbuf(color_buf, z_buf, p0_proj, p1_proj, color, radius=1, z_bias=0.045):
    """
    Draws a 3D depth-tested line segment into color_buf where z + z_bias >= z_buf.
    """
    h, w, _ = color_buf.shape
    x0, y0, z0 = p0_proj
    x1, y1, z1 = p1_proj
    dist = max(1, int(math.hypot(x1 - x0, y1 - y0) * 1.5))
    ts = np.linspace(0.0, 1.0, dist + 1)
    xs = np.round(x0 + (x1 - x0) * ts).astype(np.int32)
    ys = np.round(y0 + (y1 - y0) * ts).astype(np.int32)
    zs = z0 + (z1 - z0) * ts + z_bias

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy > radius * radius + 1:
                continue
            px = xs + dx
            py = ys + dy
            valid = (px >= 0) & (px < w) & (py >= 0) & (py < h)
            px = px[valid]
            py = py[valid]
            pz = zs[valid]
            vis = pz >= z_buf[py, px]
            px_v = px[vis]
            py_v = py[vis]
            if len(px_v) > 0:
                color_buf[py_v, px_v, 0] = np.maximum(color_buf[py_v, px_v, 0], color[0])
                color_buf[py_v, px_v, 1] = np.maximum(color_buf[py_v, px_v, 1], color[1])
                color_buf[py_v, px_v, 2] = np.maximum(color_buf[py_v, px_v, 2], color[2])


def render_frame(yaw, width=640, height=480):
    tilt = math.radians(24.0)
    cx = width * 0.5
    cy = height * 0.372
    scale = height * 0.222
    cam_dist = 5.0

    # Initialize color and Z buffers
    color_buf = np.zeros((height, width, 3), dtype=np.uint8)
    color_buf[:, :, 0] = 1
    color_buf[:, :, 1] = 7
    color_buf[:, :, 2] = 3
    z_buf = np.full((height, width), -1e9, dtype=np.float64)

    # Subtle radial CRT phosphor glow in background
    yy, xx = np.mgrid[0:height, 0:width]
    r2 = ((xx - cx) / (width * 0.42)) ** 2 + ((yy - cy) / (height * 0.40)) ** 2
    bg_glow = np.exp(-r2 * 1.6)
    color_buf[:, :, 1] = np.clip(color_buf[:, :, 1] + bg_glow * 18.0, 0, 255).astype(np.uint8)
    color_buf[:, :, 2] = np.clip(color_buf[:, :, 2] + bg_glow * 5.0, 0, 255).astype(np.uint8)

    # 1. Build the 12 solid 3D beams of the hollow cube [-1, 1]^3
    S = 1.0
    b = 0.14
    I = S - b
    beam_faces = []
    # 4 vertical corner posts
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, x1 = (-S, -I) if sx < 0 else (I, S)
            z0, z1 = (-S, -I) if sz < 0 else (I, S)
            f, _ = build_box_faces_and_edges(x0, x1, -S, S, z0, z1)
            beam_faces.extend(f)
    # 4 horizontal X-beams
    for sy in (-1, 1):
        for sz in (-1, 1):
            y0, y1 = (-S, -I) if sy < 0 else (I, S)
            z0, z1 = (-S, -I) if sz < 0 else (I, S)
            f, _ = build_box_faces_and_edges(-I, I, y0, y1, z0, z1)
            beam_faces.extend(f)
    # 4 horizontal Z-beams
    for sy in (-1, 1):
        for sx in (-1, 1):
            y0, y1 = (-S, -I) if sy < 0 else (I, S)
            x0, x1 = (-S, -I) if sx < 0 else (I, S)
            f, _ = build_box_faces_and_edges(x0, x1, y0, y1, -I, I)
            beam_faces.extend(f)

    light_dir = np.array([-0.42, 0.68, 0.60])
    light_dir /= np.linalg.norm(light_dir)

    # Rasterize all beam faces into the Z-buffer
    for verts3d, norm3d in beam_faces:
        r_norm = rotate_point(norm3d, yaw, tilt)
        pts_cam = [rotate_point(v, yaw, tilt) for v in verts3d]
        center_cam = np.mean(pts_cam, axis=0)
        view_vec = np.array([0.0, 0.0, cam_dist]) - center_cam
        if np.dot(r_norm, view_vec) <= 0.0:
            continue

        pts_proj = [project_point(p, cx, cy, scale, cam_dist) for p in pts_cam]
        avg_z = float(np.mean([p[2] for p in pts_proj]))
        ndotl = max(0.0, float(np.dot(r_norm, light_dir)))
        depth_factor = float(np.clip((avg_z + 1.35) / 2.7, 0.22, 1.0))

        if abs(norm3d[1]) > 0.5:
            base_g = 52 + int(85 * ndotl)
        else:
            base_g = 34 + int(72 * ndotl)
        g_val = int(np.clip(base_g * (0.38 + 0.62 * depth_factor), 16, 175))
        r_val = int(g_val * 0.14)
        b_val = int(g_val * 0.30)
        rasterize_convex_quad_zbuf(color_buf, z_buf, pts_proj, (r_val, g_val, b_val))

    # 2. Rasterize the 3D extruded B and F letters into the Z-buffer
    b_outer, b_holes = make_b_polygons()
    f_outer, f_holes = make_f_polygons()

    letter_faces = [
        (np.array([ 0.0, 0.0,  1.0]), np.array([ 1.0, 0.0,  0.0]), np.array([0.0, 1.0, 0.0]), b_outer, b_holes),
        (np.array([ 0.0, 0.0, -1.0]), np.array([-1.0, 0.0,  0.0]), np.array([0.0, 1.0, 0.0]), b_outer, b_holes),
        (np.array([ 1.0, 0.0,  0.0]), np.array([ 0.0, 0.0, -1.0]), np.array([0.0, 1.0, 0.0]), f_outer, f_holes),
        (np.array([-1.0, 0.0,  0.0]), np.array([ 0.0, 0.0,  1.0]), np.array([0.0, 1.0, 0.0]), f_outer, f_holes),
    ]

    letter_outline_segments = []

    for n_vec, r_vec, u_vec, outer_poly, holes in letter_faces:
        r_norm = rotate_point(n_vec, yaw, tilt)
        face_center_cam = rotate_point(n_vec * 0.88, yaw, tilt)
        view_vec = np.array([0.0, 0.0, cam_dist]) - face_center_cam
        facing = float(np.dot(r_norm, view_vec / np.linalg.norm(view_vec)))
        if facing <= 0.04:
            continue

        d_back = 0.75
        d_front = 0.94
        window_scale = 0.84

        def to_world(u_coord, v_coord, d_val):
            return n_vec * d_val + r_vec * (u_coord * window_scale) + u_vec * (v_coord * window_scale)

        # Extruded side walls of the letter
        for loop in [outer_poly] + holes:
            is_hole = (loop is not outer_poly)
            n_pts = len(loop)
            for i in range(n_pts):
                u0, v0 = loop[i]
                u1, v1 = loop[(i + 1) % n_pts]
                p0_f = rotate_point(to_world(u0, v0, d_front), yaw, tilt)
                p1_f = rotate_point(to_world(u1, v1, d_front), yaw, tilt)
                p1_b = rotate_point(to_world(u1, v1, d_back), yaw, tilt)
                p0_b = rotate_point(to_world(u0, v0, d_back), yaw, tilt)
                pj = [project_point(p, cx, cy, scale, cam_dist) for p in (p0_f, p1_f, p1_b, p0_b)]
                wall_col = (14, 102, 38) if not is_hole else (10, 76, 28)
                rasterize_convex_quad_zbuf(color_buf, z_buf, pj, wall_col)
                letter_outline_segments.append((pj[0], pj[1], (190, 255, 210), 2))

        # Front face of the letter (using 2D polygon mask + exact plane Z interpolation)
        pts_front_cam = [rotate_point(to_world(u, v, d_front), yaw, tilt) for (u, v) in outer_poly]
        pts_front_proj = [project_point(p, cx, cy, scale, cam_dist) for p in pts_front_cam]
        outer_2d = [(p[0], p[1]) for p in pts_front_proj]

        holes_2d = []
        for h_loop in holes:
            h_cam = [rotate_point(to_world(u, v, d_front), yaw, tilt) for (u, v) in h_loop]
            holes_2d.append([(project_point(p, cx, cy, scale, cam_dist)[0], project_point(p, cx, cy, scale, cam_dist)[1]) for p in h_cam])

        mask = Image.new("L", (width, height), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.polygon(outer_2d, fill=255)
        for h2d in holes_2d:
            mdraw.polygon(h2d, fill=0)

        bevel_mask = mask.filter(ImageFilter.MinFilter(7))

        # Plane equation for z across the letter's front face from 3 reference points on the face
        ref_pts_cam = [
            rotate_point(to_world(-0.5, -0.5, d_front), yaw, tilt),
            rotate_point(to_world( 0.5, -0.5, d_front), yaw, tilt),
            rotate_point(to_world(-0.5,  0.5, d_front), yaw, tilt),
        ]
        ref_proj = [project_point(p, cx, cy, scale, cam_dist) for p in ref_pts_cam]
        (rx0, ry0, rz0), (rx1, ry1, rz1), (rx2, ry2, rz2) = ref_proj
        denom = (ry1 - ry2) * (rx0 - rx2) + (rx2 - rx1) * (ry0 - ry2)

        ys_p = [p[1] for p in outer_2d]
        xs_p = [p[0] for p in outer_2d]
        y_min, y_max = max(0, int(min(ys_p)) - 2), min(height - 1, int(max(ys_p)) + 2)
        x_min, x_max = max(0, int(min(xs_p)) - 2), min(width - 1, int(max(xs_p)) + 2)

        if y_max > y_min and x_max > x_min and abs(denom) > 1e-6:
            mask_np = np.array(mask)[y_min:y_max + 1, x_min:x_max + 1] > 127
            bevel_np = np.array(bevel_mask)[y_min:y_max + 1, x_min:x_max + 1] > 127

            py_grid, px_grid = np.mgrid[y_min:y_max + 1, x_min:x_max + 1]
            px_f = px_grid + 0.5
            py_f = py_grid + 0.5
            w0 = ((ry1 - ry2) * (px_f - rx2) + (rx2 - rx1) * (py_f - ry2)) / denom
            w1 = ((ry2 - ry0) * (px_f - rx2) + (rx0 - rx2) * (py_f - ry2)) / denom
            w2 = 1.0 - w0 - w1
            z_face = w0 * rz0 + w1 * rz1 + w2 * rz2

            sub_z = z_buf[y_min:y_max + 1, x_min:x_max + 1]
            vis_mask = mask_np & (z_face >= sub_z)
            sub_z[vis_mask] = z_face[vis_mask]

            vis_bevel = vis_mask & bevel_np
            vis_rim = vis_mask & (~bevel_np)

            t_y = np.linspace(0.0, 1.0, y_max - y_min + 1)[:, None]
            horizon = np.exp(-((t_y - 0.36) / 0.11) ** 2)
            bot_glow = np.clip((t_y - 0.55) / 0.45, 0.0, 1.0) * 0.55
            lum = np.clip(0.16 + 0.76 * horizon + bot_glow, 0.14, 1.0) * (0.65 + 0.35 * min(1.0, facing * 1.4))

            face_r = np.broadcast_to((lum * 50).astype(np.uint8), mask_np.shape)
            face_g = np.broadcast_to((lum * 210).astype(np.uint8), mask_np.shape)
            face_b = np.broadcast_to((lum * 80).astype(np.uint8), mask_np.shape)

            sub_col = color_buf[y_min:y_max + 1, x_min:x_max + 1]
            sub_col[:, :, 0][vis_bevel] = face_r[vis_bevel]
            sub_col[:, :, 1][vis_bevel] = face_g[vis_bevel]
            sub_col[:, :, 2][vis_bevel] = face_b[vis_bevel]

            # Glowing bevel rim
            sub_col[:, :, 0][vis_rim] = 145
            sub_col[:, :, 1][vis_rim] = 255
            sub_col[:, :, 2][vis_rim] = 175

    # 3. Draw depth-tested glowing 3D edge lines for the cube frame and letter bevels
    # Outer 12 cube edges + inner window loops on each of the 6 cube faces
    cube_face_defs = [
        (np.array([ 0.0,  0.0,  1.0]), np.array([ 1.0, 0.0,  0.0]), np.array([0.0, 1.0,  0.0])),
        (np.array([ 0.0,  0.0, -1.0]), np.array([-1.0, 0.0,  0.0]), np.array([0.0, 1.0,  0.0])),
        (np.array([ 1.0,  0.0,  0.0]), np.array([ 0.0, 0.0, -1.0]), np.array([0.0, 1.0,  0.0])),
        (np.array([-1.0,  0.0,  0.0]), np.array([ 0.0, 0.0,  1.0]), np.array([0.0, 1.0,  0.0])),
        (np.array([ 0.0,  1.0,  0.0]), np.array([ 1.0, 0.0,  0.0]), np.array([0.0, 0.0, -1.0])),
        (np.array([ 0.0, -1.0,  0.0]), np.array([ 1.0, 0.0,  0.0]), np.array([0.0, 0.0,  1.0])),
    ]

    for n_vec, r_vec, u_vec in cube_face_defs:
        r_norm = rotate_point(n_vec, yaw, tilt)
        face_center_cam = rotate_point(n_vec * S, yaw, tilt)
        view_vec = np.array([0.0, 0.0, cam_dist]) - face_center_cam
        is_front = (np.dot(r_norm, view_vec) > 0.0)

        for d_surf, rad in [(S, S), (S, I), (I, I)]:
            corners = [
                n_vec * d_surf + r_vec * (-rad) + u_vec * (-rad),
                n_vec * d_surf + r_vec * ( rad) + u_vec * (-rad),
                n_vec * d_surf + r_vec * ( rad) + u_vec * ( rad),
                n_vec * d_surf + r_vec * (-rad) + u_vec * ( rad),
            ]
            for i in range(4):
                p0_cam = rotate_point(corners[i], yaw, tilt)
                p1_cam = rotate_point(corners[(i + 1) % 4], yaw, tilt)
                pj0 = project_point(p0_cam, cx, cy, scale, cam_dist)
                pj1 = project_point(p1_cam, cx, cy, scale, cam_dist)
                az = 0.5 * (pj0[2] + pj1[2])
                df = float(np.clip((az + 1.35) / 2.7, 0.25, 1.0))
                if is_front and d_surf == S:
                    col = (int(130 * df), int(255 * df), int(160 * df))
                    rad_px = 2 if rad == S else 1
                else:
                    col = (int(35 * df), int(165 * df), int(65 * df))
                    rad_px = 1
                draw_3d_line_zbuf(color_buf, z_buf, pj0, pj1, col, radius=rad_px, z_bias=0.05)

    # Also draw the 4 inner corner post edges so the back vertical post has crisp edges
    for sx in (-1, 1):
        for sz in (-1, 1):
            p0_cam = rotate_point(np.array([sx * I, -I, sz * I]), yaw, tilt)
            p1_cam = rotate_point(np.array([sx * I,  I, sz * I]), yaw, tilt)
            pj0 = project_point(p0_cam, cx, cy, scale, cam_dist)
            pj1 = project_point(p1_cam, cx, cy, scale, cam_dist)
            az = 0.5 * (pj0[2] + pj1[2])
            df = float(np.clip((az + 1.35) / 2.7, 0.25, 1.0))
            col = (int(45 * df), int(185 * df), int(75 * df))
            draw_3d_line_zbuf(color_buf, z_buf, pj0, pj1, col, radius=1, z_bias=0.05)

    # Draw depth-tested bright outlines around the visible B and F front faces
    for pj0, pj1, col, rad_px in letter_outline_segments:
        draw_3d_line_zbuf(color_buf, z_buf, pj0, pj1, col, radius=1, z_bias=0.05)

    img = Image.fromarray(color_buf)

    # Add phosphor bloom (soft additive glow from bright edges)
    base_np = np.array(img, dtype=np.float32)
    bright_only = np.clip(base_np - 95.0, 0.0, 255.0).astype(np.uint8)
    bloom_img = Image.fromarray(bright_only).filter(ImageFilter.GaussianBlur(radius=5.5))
    bloom_np = np.array(bloom_img, dtype=np.float32)
    combined = np.clip(base_np + bloom_np * 0.62, 0, 255).astype(np.uint8)
    img = Image.fromarray(combined)
    draw = ImageDraw.Draw(img)

    # Draw CRT UI text overlays (matching ref_bf_original.png & BfCubeRenderer)
    try:
        font_top = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 16)
        font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 19)
        font_city = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 14)
    except Exception:
        font_top = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_city = ImageFont.load_default()

    draw.text((18, 12), "SYS_LOAD: B50_LABS_LOGO.EXE", fill=(110, 255, 140), font=font_top)

    t1 = "BUCK-FIFTY"
    bb1 = draw.textbbox((0, 0), t1, font=font_title)
    w1 = bb1[2] - bb1[0]
    y1 = int(height * 0.795)
    draw.text(((width - w1) // 2 + 2, y1 + 2), t1, fill=(10, 95, 35), font=font_title)
    draw.text(((width - w1) // 2, y1), t1, fill=(145, 255, 175), font=font_title)

    t2 = "INNOVATION LABS"
    bb2 = draw.textbbox((0, 0), t2, font=font_sub)
    w2 = bb2[2] - bb2[0]
    y2 = y1 + 37
    draw.text(((width - w2) // 2, y2), t2, fill=(90, 240, 125), font=font_sub)

    t3 = "SALT LAKE CITY, UT"
    bb3 = draw.textbbox((0, 0), t3, font=font_city)
    w3 = bb3[2] - bb3[0]
    y3 = y2 + 21
    draw.text(((width - w3) // 2, y3), t3, fill=(60, 195, 90), font=font_city)

    # Downsample 2x to 320x240 with Lanczos for razor-sharp anti-aliasing
    out_img = img.resize((width // 2, height // 2), Image.Resampling.LANCZOS)

    # Subtle CRT scanlines on the final 320x240 frame
    out_np = np.array(out_img, dtype=np.float32)
    out_np[1::2, :, :] *= 0.82
    return Image.fromarray(np.clip(out_np, 0, 255).astype(np.uint8))


def generate_bf_cube_gif(out_gif_path=None):
    if out_gif_path is None:
        web_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_gif_path = os.path.join(web_dir, "assets", "bf_cube_rotating.gif")

    n_frames = 24
    frames = []
    start_yaw = math.radians(-42.0)
    for i in range(n_frames):
        yaw = start_yaw + (2.0 * math.pi * i) / n_frames
        frames.append(render_frame(yaw, 640, 480))

    frames[0].save(
        out_gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=75,
        loop=0,
        optimize=True,
    )
    print(f"Saved {out_gif_path} ({os.path.getsize(out_gif_path)} bytes, {n_frames} frames)")
    return frames


if __name__ == "__main__":
    frames = generate_bf_cube_gif()
    scratch_dir = r"C:\Users\Daniel Sawitzki\.gemini\antigravity\brain\809c1c6c-946b-4cd5-a552-fb101168d1af\scratch"
    if os.path.exists(scratch_dir):
        sheet = Image.new("RGB", (320 * 4, 240 * 3))
        for idx in range(12):
            sheet.paste(frames[idx * 2], ((idx % 4) * 320, (idx // 4) * 240))
        sheet.save(os.path.join(scratch_dir, "new_cube_sheet_v2.png"))
        frames[0].resize((80, 60), Image.Resampling.LANCZOS).save(os.path.join(scratch_dir, "new_cube_80x60_v2.png"))
