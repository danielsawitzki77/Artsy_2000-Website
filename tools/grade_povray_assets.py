#!/usr/bin/env python3
"""
Post-processes the 6 overly bright / washed-out POV-Ray renders (720p stills
and 360-degree spin GIFs) in Artsy_2000-Website/assets/ to restore rich shadow
depth, punchy contrast, and natural retro-synth saturation without re-raytracing.

Note:
- `povray_turntable.jpg` is intentionally untouched (it already has deep blacks
  and strong contrast).
- By default, source bytes are read from git revision `7a3b090` (the original
  ungraded POV-Ray import commit) so re-running this script is 100% idempotent
  and can never accidentally double-darken already-graded files. Pass
  `--from-disk` to grade the current on-disk files instead.
"""

import argparse
import io
import os
import subprocess
from PIL import Image, ImageEnhance, ImageSequence

WEB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(WEB_DIR, "assets")
RAW_SOURCE_REV = "7a3b090"

RECIPES = {
    "chase": dict(
        jpg="povray_chase.jpg",
        gif="povray_chase_spin.gif",
        black_in=0.15,
        white_in=0.98,
        gamma=2.15,
        s_curve=0.16,
        sat=1.05,
        out_max=0.94,
    ),
    "diner": dict(
        jpg="povray_diner.jpg",
        gif="povray_diner_spin.gif",
        black_in=0.12,
        white_in=0.96,
        gamma=1.78,
        s_curve=0.18,
        sat=0.98,
        out_max=0.93,
    ),
    "facility": dict(
        jpg="povray_facility.jpg",
        gif="povray_facility_spin.gif",
        black_in=0.18,
        white_in=0.91,
        gamma=1.92,
        s_curve=0.24,
        sat=0.93,
        out_max=0.93,
    ),
    "logo": dict(
        jpg="povray_logo.jpg",
        gif="povray_logo_spin.gif",
        black_in=0.06,
        white_in=1.00,
        gamma=1.95,
        s_curve=0.10,
        sat=1.08,
        out_max=0.96,
    ),
    "pizza": dict(
        jpg="povray_pizza_slice.jpg",
        gif="povray_pizza_spin.gif",
        black_in=0.06,
        white_in=0.97,
        gamma=1.85,
        s_curve=0.18,
        sat=0.96,
        out_max=0.93,
    ),
    "terminal": dict(
        jpg="povray_terminal.jpg",
        gif="povray_terminal_spin.gif",
        black_in=0.07,
        white_in=0.96,
        gamma=1.90,
        s_curve=0.14,
        sat=1.04,
        out_max=0.92,
    ),
}


def make_lut(black_in=0.0, white_in=1.0, gamma=2.0, s_curve=0.0, out_max=1.0):
    lut = []
    span = max(1e-6, white_in - black_in)
    for i in range(256):
        x = (i / 255.0 - black_in) / span
        x = 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)
        y = x ** gamma
        if s_curve > 0.0:
            sc = y * y * (3.0 - 2.0 * y)
            y = y * (1.0 - s_curve) + sc * s_curve
        y = max(0.0, min(1.0, y * out_max))
        lut.append(int(round(y * 255.0)))
    return lut


def grade_rgb(im, lut, sat=1.0):
    rgb = im.convert("RGB")
    out = rgb.point(lut * 3)
    if abs(sat - 1.0) > 1e-3:
        out = ImageEnhance.Color(out).enhance(sat)
    return out


def load_source_bytes(filename, source_rev):
    if source_rev is None:
        with open(os.path.join(ASSETS_DIR, filename), "rb") as f:
            return f.read()
    spec = f"{source_rev}:assets/{filename}"
    return subprocess.check_output(["git", "-C", WEB_DIR, "show", spec])


def luma_stats(rgb_im):
    hist = rgb_im.convert("L").histogram()
    tot = sum(hist)
    mean = sum(i * c for i, c in enumerate(hist)) / max(1, tot)

    def pct(q):
        acc = 0
        for i, c in enumerate(hist):
            acc += c
            if acc >= tot * q:
                return i
        return 255

    return pct(0.01), pct(0.50), pct(0.99), mean


def pack_exact_paletted_frames(graded_frames):
    """
    When all frames share <= 255 unique RGB triples (true for all 6 POV-Ray
    turntable GIFs, which each use <= 127 global colors), map every frame into
    one shared exact global palette with zero double-dithering and zero
    quantization loss. Falls back to FASTOCTREE if > 255 unique colors exist.
    """
    unique_colors = set()
    exceeded = False
    for fr in graded_frames:
        cols = fr.getcolors(maxcolors=255)
        if cols is None:
            exceeded = True
            break
        for _, col in cols:
            unique_colors.add(col)
        if len(unique_colors) > 255:
            exceeded = True
            break

    if exceeded:
        return [
            fr.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
            for fr in graded_frames
        ]

    palette_colors = sorted(unique_colors)
    color_to_idx = {c: idx for idx, c in enumerate(palette_colors)}
    flat_palette = []
    for r, g, b in palette_colors:
        flat_palette.extend((r, g, b))
    flat_palette.extend([0] * (768 - len(flat_palette)))

    p_frames = []
    for fr in graded_frames:
        pixels = fr.get_flattened_data() if hasattr(fr, "get_flattened_data") else fr.getdata()
        idx_bytes = bytes(color_to_idx[px] for px in pixels)
        pf = Image.frombytes("P", fr.size, idx_bytes)
        pf.putpalette(flat_palette)
        p_frames.append(pf)
    return p_frames


def process_pair(name, cfg, source_rev):
    lut = make_lut(
        black_in=cfg["black_in"],
        white_in=cfg["white_in"],
        gamma=cfg["gamma"],
        s_curve=cfg["s_curve"],
        out_max=cfg["out_max"],
    )
    sat = cfg["sat"]

    # 1. Grade 720p JPG still
    jpg_name = cfg["jpg"]
    jpg_bytes = load_source_bytes(jpg_name, source_rev)
    with Image.open(io.BytesIO(jpg_bytes)) as src_jpg:
        before_stats = luma_stats(src_jpg.convert("RGB"))
        graded_jpg = grade_rgb(src_jpg, lut, sat=sat)
        after_stats = luma_stats(graded_jpg)
        out_jpg = os.path.join(ASSETS_DIR, jpg_name)
        graded_jpg.save(out_jpg, format="JPEG", quality=93, optimize=True)
    print(
        f"[{name:8s}] {jpg_name:24s} "
        f"mean {before_stats[3]:5.1f} -> {after_stats[3]:5.1f} "
        f"(p01 {before_stats[0]:3d}->{after_stats[0]:3d}, p99 {before_stats[2]:3d}->{after_stats[2]:3d}) "
        f"{os.path.getsize(out_jpg)/1024:.1f} KB"
    )

    # 2. Grade animated 360-degree spin GIF (preserving exact frame timings & loop)
    gif_name = cfg["gif"]
    gif_bytes = load_source_bytes(gif_name, source_rev)
    with Image.open(io.BytesIO(gif_bytes)) as src_gif:
        loop = src_gif.info.get("loop", 0)
        durations = []
        graded_frames = []
        for fr in ImageSequence.Iterator(src_gif):
            durations.append(fr.info.get("duration", 70))
            graded_frames.append(grade_rgb(fr, lut, sat=sat))

    p_frames = pack_exact_paletted_frames(graded_frames)
    out_gif = os.path.join(ASSETS_DIR, gif_name)
    p_frames[0].save(
        out_gif,
        format="GIF",
        save_all=True,
        append_images=p_frames[1:],
        duration=durations,
        loop=loop,
        optimize=True,
    )
    print(
        f"[{name:8s}] {gif_name:24s} "
        f"{len(p_frames):2d} frames, "
        f"{len(gif_bytes)/1024:.1f} KB -> {os.path.getsize(out_gif)/1024:.1f} KB"
    )


def main():
    parser = argparse.ArgumentParser(description="Post-process washed-out POV-Ray website assets.")
    parser.add_argument(
        "--from-disk",
        action="store_true",
        help="Read current files from assets/ instead of ungraded git baseline.",
    )
    parser.add_argument(
        "--source-rev",
        default=RAW_SOURCE_REV,
        help=f"Git revision containing ungraded POV-Ray assets (default: {RAW_SOURCE_REV}).",
    )
    args = parser.parse_args()
    source_rev = None if args.from_disk else args.source_rev

    for name, cfg in RECIPES.items():
        process_pair(name, cfg, source_rev)

    print("Done grading all 6 POV-Ray still + spin GIF pairs.")


if __name__ == "__main__":
    main()
