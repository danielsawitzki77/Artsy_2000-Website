#!/usr/bin/env python3
"""
Generates a 1920x1080 retro Windows 95 desktop mock-up screenshot depicting
Artsy_2000's end-to-end POV-Ray 3.7 export & turntable rendering pipeline:

  1. Artsy_2000 running in windowed mode (Chase Mode 3D scene exported via X)
  2. Exported POV-Ray 3.7 script (scene.pov) open in Win95 Notepad
  3. Export folder in Windows Explorer with double-click cursor on render.bat
  4. Interactive MS-DOS prompt (render.bat) selecting MP4/GIF & 10 lighting themes
  5. Headless POV-Ray 3.7 renderer actively tracing progressive scanlines
  6. Output Animated GIF viewer displaying turntable.gif (360-degree loop)

Renders via headless Microsoft Edge at exact 1920x1080 (device scale factor 1)
and outputs:
  tools/generated/artsy_2000_povray_pipeline_win95_1920x1080.png
"""

import base64
import io
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image


WEB_ROOT = Path(__file__).resolve().parent.parent
GAME_ROOT = WEB_ROOT.parent / "Artsy_2000"
SCREENSHOT_SOURCE_ROOT = Path(r"G:\My Drive\Artsy_2000\Screenshots")
OUTPUT_DIR = WEB_ROOT / "tools" / "generated"
OUTPUT_PNG = OUTPUT_DIR / "artsy_2000_povray_pipeline_win95_1920x1080.png"

EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def img_to_data_uri(im: Image.Image, fmt: str = "PNG", quality: int = 92) -> str:
    buf = io.BytesIO()
    if fmt.upper() == "JPEG":
        im.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
        mime = "image/jpeg"
    else:
        im.save(buf, format="PNG", optimize=True)
        mime = "image/png"
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def load_assets() -> dict:
    # 1. Crop inner 3D viewport from Chase3D_2.png cleanly (no gray CRT monitor bezel)
    chase_src = SCREENSHOT_SOURCE_ROOT / "Chase3D_2.png"
    if not chase_src.exists():
        raise FileNotFoundError(f"Missing screenshot: {chase_src}")
    with Image.open(chase_src) as im:
        # Cleanly inset inside the curved CRT bezel corners
        inner = im.crop((312, 102, 1608, 1094)).convert("RGB")
        inner = inner.resize((660, 420), Image.Resampling.LANCZOS)
        chase_window_uri = img_to_data_uri(inner, "PNG")

    # 2. High-res POV-Ray still of the same Chase scene for hero viewer & progressive render
    pov_still_path = WEB_ROOT / "assets" / "povray_chase.jpg"
    if not pov_still_path.exists():
        raise FileNotFoundError(f"Missing POV-Ray still: {pov_still_path}")
    with Image.open(pov_still_path) as im:
        still_rgb = im.convert("RGB")
        pov_hero_uri = img_to_data_uri(still_rgb, "JPEG", quality=94)

        # Create a coarse mosaic preview for the unrendered lower scanlines in POV-Ray window
        w, h = still_rgb.size
        mosaic = still_rgb.resize((w // 22, h // 22), Image.Resampling.BILINEAR)
        mosaic = mosaic.resize((w, h), Image.Resampling.NEAREST)
        pov_mosaic_uri = img_to_data_uri(mosaic, "JPEG", quality=85)

    # 3. Extract 5 distinct 360-degree rotation frames from povray_chase_spin.gif
    gif_path = WEB_ROOT / "assets" / "povray_chase_spin.gif"
    if not gif_path.exists():
        raise FileNotFoundError(f"Missing POV-Ray GIF: {gif_path}")
    spin_frames = []
    with Image.open(gif_path) as gif:
        n_frames = getattr(gif, "n_frames", 1)
        angles = [0, 72, 144, 216, 288]
        for deg in angles:
            idx = int(round((deg / 360.0) * n_frames)) % n_frames
            gif.seek(idx)
            fr = gif.convert("RGB").resize((124, 70), Image.Resampling.LANCZOS)
            spin_frames.append((deg, idx + 1, img_to_data_uri(fr, "PNG")))

        # Also grab an angled mid-orbit frame (~216 deg) for the active POV-Ray render viewport
        mid_idx = int(round(0.62 * n_frames)) % n_frames
        gif.seek(mid_idx)
        mid_frame = gif.convert("RGB").resize((640, 360), Image.Resampling.LANCZOS)
        pov_mid_uri = img_to_data_uri(mid_frame, "PNG")
        mid_mosaic = mid_frame.resize((32, 18), Image.Resampling.BILINEAR).resize(
            (640, 360), Image.Resampling.NEAREST
        )
        pov_mid_mosaic_uri = img_to_data_uri(mid_mosaic, "PNG")

    # 4. Buck-Fifty Cube App Icon
    icon_candidates = [
        GAME_ROOT / "assets" / "images" / "ui" / "app_icon.png",
        WEB_ROOT / "press" / "media" / "branding" / "buck_fifty_cube_icon.png",
    ]
    icon_path = next((p for p in icon_candidates if p.exists()), None)
    if icon_path is None:
        raise FileNotFoundError("Missing Buck-Fifty app_icon.png")
    with Image.open(icon_path) as im:
        icon_48 = im.convert("RGBA").resize((42, 42), Image.Resampling.LANCZOS)
        icon_16 = im.convert("RGBA").resize((16, 16), Image.Resampling.LANCZOS)
        cube_icon_48_uri = img_to_data_uri(icon_48, "PNG")
        cube_icon_16_uri = img_to_data_uri(icon_16, "PNG")

    return {
        "chase_window_uri": chase_window_uri,
        "pov_hero_uri": pov_hero_uri,
        "pov_mosaic_uri": pov_mosaic_uri,
        "pov_mid_uri": pov_mid_uri,
        "pov_mid_mosaic_uri": pov_mid_mosaic_uri,
        "spin_frames": spin_frames,
        "cube_icon_48_uri": cube_icon_48_uri,
        "cube_icon_16_uri": cube_icon_16_uri,
    }


def build_html(assets: dict) -> str:
    filmstrip_html = []
    for i, (deg, fnum, uri) in enumerate(assets["spin_frames"]):
        active_cls = " active" if i == 2 else ""
        filmstrip_html.append(
            f"""
            <div class="film-frame{active_cls}">
              <img src="{uri}" alt="Frame {deg} deg">
              <div class="film-label">{deg}&deg; &middot; F{fnum:02d}</div>
            </div>
            """
        )
    filmstrip_markup = "\n".join(filmstrip_html)

    return rf"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Artsy_2000 POV-Ray Pipeline Desktop Mockup</title>
<style>
  * {{
    box-sizing: border-box;
    user-select: none;
  }}

  html, body {{
    margin: 0;
    padding: 0;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    background: #008080;
    font-family: "MS Sans Serif", "Tahoma", "Segoe UI", Arial, sans-serif;
    font-size: 12px;
    color: #000000;
    -webkit-font-smoothing: none;
  }}

  /* Classic Win95 Teal Desktop with subtle CRT scanline texture */
  .desktop {{
    position: relative;
    width: 1920px;
    height: 1080px;
    background:
      radial-gradient(circle at 75% 24%, rgba(0, 152, 152, 0.35), transparent 55%),
      linear-gradient(180deg, #008282 0%, #007777 100%);
    overflow: hidden;
  }}

  /* Far-left Desktop Icons */
  .desktop-icons {{
    position: absolute;
    left: 14px;
    top: 18px;
    width: 82px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    z-index: 2;
  }}

  .d-icon {{
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 5px;
  }}

  .d-icon-glyph {{
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .d-icon-label {{
    color: #ffffff;
    font-size: 11.5px;
    line-height: 1.22;
    text-shadow: 1px 1px 0 #000000;
    padding: 1px 3px;
  }}

  .d-icon.selected .d-icon-label {{
    background: #000080;
    outline: 1px dotted #ffff00;
  }}

  /* ===================================================================== */
  /* AUTHENTIC WINDOWS 95 WINDOW CHROME                                    */
  /* ===================================================================== */
  .w95-win {{
    position: absolute;
    background: #c0c0c0;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #404040;
    border-bottom: 2px solid #404040;
    box-shadow:
      inset 1px 1px 0 #dfdfdf,
      inset -1px -1px 0 #808080,
      6px 8px 0 rgba(0, 0, 0, 0.34);
    padding: 3px;
    display: flex;
    flex-direction: column;
  }}

  .w95-titlebar {{
    height: 24px;
    background: linear-gradient(90deg, #000080 0%, #1084d0 100%);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 3px 0 5px;
    font-weight: 700;
    font-size: 12.5px;
    letter-spacing: 0.01em;
    flex-shrink: 0;
  }}

  .w95-titlebar.inactive {{
    background: linear-gradient(90deg, #7f7f7f 0%, #b0b0b0 100%);
    color: #dfdfdf;
  }}

  .w95-title-left {{
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .w95-title-icon {{
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }}

  .w95-win-controls {{
    display: flex;
    gap: 2px;
    flex-shrink: 0;
  }}

  .w95-ctrl {{
    width: 18px;
    height: 16px;
    background: #c0c0c0;
    color: #000000;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #404040;
    border-bottom: 1px solid #404040;
    box-shadow: inset -1px -1px 0 #808080;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 900;
    line-height: 1;
  }}

  .w95-menubar {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 3px 8px;
    background: #c0c0c0;
    border-bottom: 1px solid #808080;
    font-size: 12px;
    color: #000000;
    flex-shrink: 0;
  }}

  .w95-menubar span u {{
    text-decoration: underline;
  }}

  .w95-sunken {{
    border-top: 2px solid #808080;
    border-left: 2px solid #808080;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
    box-shadow: inset 1px 1px 0 #404040, inset -1px -1px 0 #dfdfdf;
  }}

  .w95-raised {{
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #404040;
    border-bottom: 1px solid #404040;
    box-shadow: inset -1px -1px 0 #808080;
    background: #c0c0c0;
  }}

  .w95-statusbar {{
    display: flex;
    gap: 4px;
    padding-top: 3px;
    flex-shrink: 0;
  }}

  .w95-status-pane {{
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    padding: 2px 7px;
    font-size: 11px;
    color: #111111;
    background: #c0c0c0;
    white-space: nowrap;
  }}

  /* Classic Win95 Pale-Yellow Step Tooltip Callout */
  .step-tip {{
    position: absolute;
    background: #ffffe1;
    color: #000000;
    border: 1px solid #000000;
    box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.45);
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 700;
    z-index: 60;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
  }}

  .step-num {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    background: #000080;
    color: #ffffff;
    font-size: 11px;
    font-weight: 900;
  }}

  /* ===================================================================== */
  /* WINDOW 1: ARTSY_2000 GAME IN WINDOWED MODE (TOP-LEFT)                 */
  /* ===================================================================== */
  .win-game {{
    left: 110px;
    top: 32px;
    width: 676px;
    height: 454px;
    z-index: 14;
  }}

  .game-viewport {{
    position: relative;
    flex: 1;
    background: #04020a;
    margin-top: 2px;
    overflow: hidden;
  }}

  .game-viewport img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}

  /* Subtle CRT scanline sheen on the game canvas */
  .game-viewport::after {{
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.14) 0px,
      rgba(0, 0, 0, 0.14) 1px,
      transparent 2px,
      transparent 3px
    );
    pointer-events: none;
  }}

  .game-export-banner {{
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: 10px;
    z-index: 3;
    background: rgba(4, 14, 10, 0.92);
    border: 2px solid #39ff88;
    box-shadow: 0 0 14px rgba(57, 255, 136, 0.35);
    padding: 6px 10px;
    font-family: "Consolas", "Courier New", monospace;
    color: #39ff88;
    font-size: 11.8px;
    line-height: 1.35;
  }}

  .game-export-banner .sub {{
    color: #a8ffd0;
    font-size: 10.8px;
  }}

  /* ===================================================================== */
  /* WINDOW 2: NOTEPAD — EXPORTED scene.pov SCRIPT (TOP-CENTER)            */
  /* ===================================================================== */
  .win-notepad {{
    left: 762px;
    top: 40px;
    width: 422px;
    height: 424px;
    z-index: 16;
  }}

  .notepad-body {{
    flex: 1;
    display: flex;
    background: #ffffff;
    margin-top: 2px;
    overflow: hidden;
  }}

  .notepad-code {{
    flex: 1;
    margin: 0;
    padding: 7px 9px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10.7px;
    line-height: 1.35;
    color: #111111;
    white-space: pre;
    overflow: hidden;
  }}

  .c-com {{ color: #007700; }}
  .c-dir {{ color: #0000bb; font-weight: 700; }}
  .c-kw  {{ color: #8b008b; font-weight: 700; }}
  .c-num {{ color: #b54500; }}

  .w95-vscroll {{
    width: 17px;
    background: #dfdfdf;
    border-left: 1px solid #808080;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .w95-scroll-btn {{
    height: 17px;
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #404040;
    border-bottom: 1px solid #404040;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 8px;
  }}

  .w95-scroll-thumb {{
    height: 78px;
    margin-bottom: auto;
    margin-top: 16px;
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #404040;
    border-bottom: 1px solid #404040;
  }}

  /* ===================================================================== */
  /* WINDOW 3: WINDOWS EXPLORER — DOUBLE-CLICK render.bat (BOTTOM-LEFT)    */
  /* ===================================================================== */
  .win-explorer {{
    left: 98px;
    top: 492px;
    width: 530px;
    height: 528px;
    z-index: 20;
  }}

  .exp-addressbar {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 6px;
    background: #c0c0c0;
    border-bottom: 1px solid #808080;
    font-size: 11.5px;
  }}

  .exp-address-input {{
    flex: 1;
    background: #ffffff;
    padding: 3px 6px;
    font-family: "Tahoma", Arial, sans-serif;
    font-size: 11.5px;
    color: #000000;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .exp-list {{
    position: relative;
    flex: 1;
    background: #ffffff;
    margin-top: 2px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  .exp-colhead {{
    display: grid;
    grid-template-columns: 185px 78px 1fr;
    background: #c0c0c0;
    border-bottom: 1px solid #808080;
    font-size: 11.5px;
    font-weight: 700;
  }}

  .exp-colhead div {{
    padding: 3px 8px;
    border-right: 1px solid #808080;
    border-left: 1px solid #ffffff;
    border-top: 1px solid #ffffff;
  }}

  .exp-rows {{
    padding: 4px 2px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .exp-row {{
    display: grid;
    grid-template-columns: 185px 78px 1fr;
    align-items: center;
    padding: 6px 8px;
    font-size: 12.5px;
    color: #000000;
  }}

  .exp-row .fname {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
  }}

  .exp-row .fsize {{
    text-align: right;
    padding-right: 14px;
    font-family: "Tahoma", Arial, sans-serif;
    color: #333333;
  }}

  .exp-row .ftype {{
    color: #333333;
  }}

  .exp-row.selected {{
    background: #000080;
    color: #ffffff;
    outline: 1px dotted #ffff00;
    outline-offset: -1px;
  }}

  .exp-row.selected .fsize,
  .exp-row.selected .ftype {{
    color: #e8f0ff;
  }}

  .exp-note-box {{
    margin: auto 12px 14px 12px;
    background: #f4f4dc;
    border: 1px solid #808080;
    padding: 9px 11px;
    font-size: 11.5px;
    line-height: 1.45;
    color: #111111;
  }}

  .exp-note-box strong {{
    color: #000080;
  }}

  /* Classic double-click cursor positioned cleanly on render.bat */
  .dblclick-cursor {{
    position: absolute;
    left: 122px;
    top: 72px;
    z-index: 15;
    pointer-events: none;
  }}

  .click-ring {{
    position: absolute;
    left: -13px;
    top: -13px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid #ff2a55;
    box-shadow: 0 0 0 4px rgba(255, 224, 60, 0.72);
  }}

  .dblclick-hint {{
    margin: 10px 12px 0 12px;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    align-self: flex-start;
    background: #ffffe1;
    border: 1px solid #000000;
    box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.25);
    padding: 4px 10px;
    font-size: 11.5px;
    font-weight: 700;
    color: #000000;
  }}

  /* ===================================================================== */
  /* WINDOW 4: MS-DOS PROMPT — render.bat INTERACTIVE CLI (BOTTOM-CENTER)  */
  /* ===================================================================== */
  .win-dos {{
    left: 606px;
    top: 492px;
    width: 624px;
    height: 534px;
    z-index: 24;
  }}

  .dos-toolbar {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 3px 5px;
    background: #c0c0c0;
    border-bottom: 1px solid #808080;
    font-size: 11px;
  }}

  .dos-tb-pill {{
    padding: 1px 7px;
    background: #ffffff;
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    font-size: 11px;
  }}

  .dos-tb-btn {{
    padding: 1px 6px;
    font-size: 10.5px;
    font-weight: 700;
  }}

  .dos-screen {{
    flex: 1;
    background: #000000;
    margin-top: 2px;
    padding: 9px 11px;
    font-family: "Consolas", "Lucida Console", "Courier New", monospace;
    font-size: 11.15px;
    line-height: 1.32;
    color: #cccccc;
    white-space: pre;
    overflow: hidden;
  }}

  .d-cyan   {{ color: #55ffff; font-weight: 700; }}
  .d-green  {{ color: #55ff55; font-weight: 700; }}
  .d-yellow {{ color: #ffff55; font-weight: 700; }}
  .d-white  {{ color: #ffffff; font-weight: 700; }}
  .d-dim    {{ color: #8c96a8; }}
  .d-mag    {{ color: #ff66cc; font-weight: 700; }}

  /* ===================================================================== */
  /* WINDOW 5: POV-RAY 3.7 HEADLESS RENDERER (BOTTOM-RIGHT)                */
  /* ===================================================================== */
  .win-povray {{
    left: 1210px;
    top: 544px;
    width: 688px;
    height: 484px;
    z-index: 26;
  }}

  .pov-toolbar {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 4px 6px;
    background: #c0c0c0;
    border-bottom: 1px solid #808080;
  }}

  .pov-btn {{
    padding: 2px 9px;
    font-size: 11px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}

  .pov-btn.pressed {{
    border-top: 1px solid #404040;
    border-left: 1px solid #404040;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    background: #dfdfdf;
    color: #006600;
  }}

  .pov-stage-wrap {{
    flex: 1;
    background: #20242c;
    margin-top: 2px;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow: hidden;
  }}

  .pov-render-canvas {{
    position: relative;
    flex: 1;
    background: #141414;
    border: 1px solid #000000;
    overflow: hidden;
  }}

  /* Bottom mosaic layer (untraced scanlines) */
  .pov-layer-mosaic {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0.42) contrast(1.05);
  }}

  /* Top raytraced layer clipped at 72% height */
  .pov-layer-traced {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    clip-path: inset(0 0 28% 0);
  }}

  /* Classic POV-Ray active scanline beam + block highlight */
  .pov-scanbeam {{
    position: absolute;
    left: 0;
    right: 0;
    top: 72%;
    height: 2px;
    background: #39ff88;
    box-shadow: 0 0 10px #39ff88, 0 0 4px #ffffff;
    z-index: 4;
  }}

  .pov-trace-block {{
    position: absolute;
    left: 64%;
    top: calc(72% - 14px);
    width: 34px;
    height: 28px;
    border: 2px solid #ffff00;
    box-shadow: 0 0 8px rgba(255, 255, 0, 0.8);
    z-index: 5;
  }}

  .pov-hud-tag {{
    position: absolute;
    left: 10px;
    top: 10px;
    z-index: 6;
    background: rgba(0, 0, 0, 0.82);
    border: 1px solid #38e8ff;
    color: #38e8ff;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    padding: 4px 8px;
  }}

  .pov-progress-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: #c0c0c0;
    padding: 5px 8px;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #808080;
    border-bottom: 1px solid #808080;
  }}

  .pov-prog-label {{
    font-size: 11px;
    font-weight: 700;
    color: #000000;
    white-space: nowrap;
  }}

  .w95-progress-well {{
    flex: 1;
    height: 17px;
    background: #ffffff;
    padding: 2px;
    display: flex;
    gap: 2px;
    overflow: hidden;
  }}

  .w95-prog-block {{
    width: 11px;
    height: 100%;
    background: #000080;
    flex-shrink: 0;
  }}

  /* ===================================================================== */
  /* WINDOW 6: ANIMATED GIF VIEWER — turntable.gif (TOP-RIGHT HERO)        */
  /* ===================================================================== */
  .win-gif {{
    left: 1172px;
    top: 32px;
    width: 724px;
    height: 484px;
    z-index: 30;
  }}

  .gif-stage {{
    position: relative;
    height: 296px;
    background: #080510;
    margin-top: 2px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .gif-stage img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}

  .gif-playing-pill {{
    position: absolute;
    left: 10px;
    top: 10px;
    background: rgba(0, 0, 128, 0.9);
    border: 1px solid #38e8ff;
    color: #ffffff;
    padding: 3px 9px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11.5px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}

  .rec-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #39ff88;
    display: inline-block;
  }}

  .gif-theme-pill {{
    position: absolute;
    right: 10px;
    top: 10px;
    background: rgba(12, 8, 22, 0.88);
    border: 1px solid #ff66cc;
    color: #ffd6f2;
    padding: 3px 9px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    font-weight: 700;
  }}

  /* 5-Frame 360° Rotation Filmstrip inside the GIF Player */
  .filmstrip-bar {{
    background: #141720;
    padding: 6px 8px;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 7px;
    border-top: 1px solid #404040;
  }}

  .film-frame {{
    background: #000000;
    border: 1px solid #555c70;
    padding: 2px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .film-frame.active {{
    border: 2px solid #38e8ff;
    box-shadow: 0 0 8px rgba(56, 232, 255, 0.55);
  }}

  .film-frame img {{
    width: 100%;
    height: 60px;
    object-fit: cover;
    display: block;
  }}

  .film-label {{
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9.5px;
    text-align: center;
    color: #b8c4dc;
  }}

  .film-frame.active .film-label {{
    color: #38e8ff;
    font-weight: 700;
  }}

  .gif-controls {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 6px;
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
  }}

  .media-btn {{
    width: 26px;
    height: 21px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 900;
  }}

  .media-btn.playing {{
    background: #dfdfdf;
    border-top: 1px solid #404040;
    border-left: 1px solid #404040;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    color: #000080;
  }}

  .scrubber {{
    flex: 1;
    height: 12px;
    background: #808080;
    border-top: 1px solid #404040;
    border-left: 1px solid #404040;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    position: relative;
  }}

  .scrubber-fill {{
    width: 47%;
    height: 100%;
    background: #000080;
  }}

  .scrubber-thumb {{
    position: absolute;
    left: 46%;
    top: -4px;
    width: 11px;
    height: 18px;
    background: #c0c0c0;
    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #404040;
    border-bottom: 1px solid #404040;
  }}

  .theme-dots {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    margin-left: 4px;
  }}

  .t-dot {{
    width: 10px;
    height: 10px;
    border: 1px solid #000000;
  }}

  /* ===================================================================== */
  /* WINDOWS 95 TASKBAR                                                    */
  /* ===================================================================== */
  .taskbar {{
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 38px;
    background: #c0c0c0;
    border-top: 2px solid #ffffff;
    display: flex;
    align-items: center;
    padding: 3px 5px;
    gap: 5px;
    z-index: 80;
  }}

  .start-btn {{
    height: 29px;
    padding: 0 11px 0 8px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-weight: 700;
    font-size: 13px;
    color: #000000;
    background: #c0c0c0;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #404040;
    border-bottom: 2px solid #404040;
    box-shadow: inset -1px -1px 0 #808080;
  }}

  .tb-divider {{
    width: 2px;
    height: 24px;
    border-left: 1px solid #808080;
    border-right: 1px solid #ffffff;
    margin: 0 2px;
  }}

  .tb-tasks {{
    flex: 1;
    display: flex;
    gap: 4px;
    overflow: hidden;
  }}

  .tb-item {{
    height: 28px;
    min-width: 165px;
    max-width: 225px;
    padding: 0 9px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #000000;
    background: #c0c0c0;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #404040;
    border-bottom: 2px solid #404040;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .tb-item.active {{
    background: #dfdfdf;
    font-weight: 700;
    border-top: 2px solid #404040;
    border-left: 2px solid #404040;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
  }}

  .tb-tray {{
    height: 28px;
    padding: 0 10px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    font-size: 12px;
    color: #000000;
  }}
</style>
</head>
<body>
<div class="desktop">

  <!-- =================================================================== -->
  <!-- CLASSIC WIN95 DESKTOP ICONS                                         -->
  <!-- =================================================================== -->
  <div class="desktop-icons">
    <div class="d-icon">
      <div class="d-icon-glyph">
        <svg width="36" height="36" viewBox="0 0 36 36">
          <rect x="4" y="4" width="28" height="20" fill="#c0c0c0" stroke="#000" stroke-width="1.5"/>
          <rect x="7" y="7" width="22" height="14" fill="#008080" stroke="#404040" stroke-width="1"/>
          <rect x="13" y="24" width="10" height="4" fill="#808080" stroke="#000" stroke-width="1"/>
          <rect x="6" y="28" width="24" height="5" fill="#c0c0c0" stroke="#000" stroke-width="1.5"/>
          <rect x="22" y="30" width="5" height="1.5" fill="#00aa00"/>
        </svg>
      </div>
      <div class="d-icon-label">My Computer</div>
    </div>

    <div class="d-icon">
      <div class="d-icon-glyph">
        <svg width="36" height="36" viewBox="0 0 36 36">
          <circle cx="18" cy="14" r="10" fill="#2090d0" stroke="#000" stroke-width="1.5"/>
          <ellipse cx="18" cy="14" rx="5" ry="10" fill="none" stroke="#80ff80" stroke-width="1.5"/>
          <line x1="8" y1="14" x2="28" y2="14" stroke="#80ff80" stroke-width="1.5"/>
          <rect x="10" y="25" width="16" height="7" fill="#c0c0c0" stroke="#000" stroke-width="1.5"/>
        </svg>
      </div>
      <div class="d-icon-label">Network<br>Neighborhood</div>
    </div>

    <div class="d-icon">
      <div class="d-icon-glyph">
        <svg width="36" height="36" viewBox="0 0 36 36">
          <polygon points="8,10 28,10 25,32 11,32" fill="#d8e0e8" stroke="#000" stroke-width="1.5"/>
          <rect x="6" y="6" width="24" height="4" fill="#c0c0c0" stroke="#000" stroke-width="1.5"/>
          <line x1="13" y1="13" x2="14" y2="29" stroke="#808080" stroke-width="1.5"/>
          <line x1="18" y1="13" x2="18" y2="29" stroke="#808080" stroke-width="1.5"/>
          <line x1="23" y1="13" x2="22" y2="29" stroke="#808080" stroke-width="1.5"/>
        </svg>
      </div>
      <div class="d-icon-label">Recycle Bin</div>
    </div>

    <div class="d-icon selected">
      <div class="d-icon-glyph">
        <img src="{assets['cube_icon_48_uri']}" width="38" height="38" style="border:1px solid #000;" alt="Artsy_2000">
      </div>
      <div class="d-icon-label">Artsy_2000</div>
    </div>

    <div class="d-icon">
      <div class="d-icon-glyph">
        <svg width="36" height="36" viewBox="0 0 36 36">
          <path d="M3,10 L14,10 L17,13 L33,13 L33,30 L3,30 Z" fill="#f8d850" stroke="#000" stroke-width="1.5"/>
          <path d="M3,14 L33,14 L31,30 L5,30 Z" fill="#ffe878" stroke="#806000" stroke-width="1"/>
        </svg>
      </div>
      <div class="d-icon-label">Povray<br>Exports</div>
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- WINDOW 1: ARTSY_2000 IN WINDOWED MODE (EXPORTING 3D SCENE)          -->
  <!-- =================================================================== -->
  <div class="w95-win win-game">
    <div class="w95-titlebar">
      <div class="w95-title-left">
        <span class="w95-title-icon"><img src="{assets['cube_icon_16_uri']}" width="16" height="16" alt=""></span>
        <span>Artsy_2000 &mdash; Chase Mode [Windowed &middot; Pure CPU Renderer]</span>
      </div>
      <div class="w95-win-controls">
        <div class="w95-ctrl">_</div>
        <div class="w95-ctrl">&#9633;</div>
        <div class="w95-ctrl">&times;</div>
      </div>
    </div>
    <div class="game-viewport w95-sunken">
      <img src="{assets['chase_window_uri']}" alt="Artsy_2000 Windowed Chase Mode">
      <div class="game-export-banner">
        <div>&#9658; [KEY X] POV-RAY 3.7 EXPORT COMPLETE &mdash; 64 3D PRIMITIVES WRITTEN</div>
        <div class="sub">Saved: C:\Users\Subject13\AppData\Local\Artsy_2000\Povray\Chase_01\ (scene.pov + render.bat)</div>
      </div>
    </div>
    <div class="w95-statusbar">
      <div class="w95-status-pane" style="flex:1;">Mode: Chase 3D (User Sculptures &amp; Gameplay Scenes Exportable)</div>
      <div class="w95-status-pane">0% GPU</div>
      <div class="w95-status-pane">X: POV-Ray</div>
    </div>
  </div>

  <!-- Step 1 Callout -->
  <div class="step-tip" style="left: 110px; top: 5px;">
    <span class="step-num">1</span> Export 3D Scene From Game (Press X)
  </div>

  <!-- =================================================================== -->
  <!-- WINDOW 2: NOTEPAD — GENERATED scene.pov SCRIPT                      -->
  <!-- =================================================================== -->
  <div class="w95-win win-notepad">
    <div class="w95-titlebar inactive">
      <div class="w95-title-left">
        <span class="w95-title-icon">
          <svg width="14" height="14" viewBox="0 0 16 16">
            <rect x="2" y="1" width="12" height="14" fill="#fff" stroke="#000" stroke-width="1"/>
            <rect x="2" y="1" width="12" height="3" fill="#008080"/>
            <line x1="4" y1="7" x2="12" y2="7" stroke="#000" stroke-width="1"/>
            <line x1="4" y1="10" x2="12" y2="10" stroke="#000" stroke-width="1"/>
            <line x1="4" y1="13" x2="9" y2="13" stroke="#000" stroke-width="1"/>
          </svg>
        </span>
        <span>scene.pov - Notepad</span>
      </div>
      <div class="w95-win-controls">
        <div class="w95-ctrl">_</div>
        <div class="w95-ctrl">&#9633;</div>
        <div class="w95-ctrl">&times;</div>
      </div>
    </div>
    <div class="w95-menubar">
      <span><u>F</u>ile</span><span><u>E</u>dit</span><span><u>S</u>earch</span><span><u>H</u>elp</span>
    </div>
    <div class="notepad-body w95-sunken">
      <pre class="notepad-code"><span class="c-com">// Artsy_2000 - 360 Turntable Export</span>
<span class="c-com">// POV-Ray 3.7 Scene Description</span>
<span class="c-dir">#version</span> <span class="c-num">3.7</span>;
<span class="c-dir">#ifndef</span> (ThemeId)
  <span class="c-dir">#declare</span> ThemeId = <span class="c-num">1</span>; <span class="c-com">// 1..10 Themes</span>
<span class="c-dir">#end</span>

<span class="c-com">// 360-Degree Orbit Camera</span>
<span class="c-dir">#declare</span> OrbitAngle = clock * <span class="c-num">2</span> * pi;
<span class="c-kw">camera</span> {{
  location &lt;CamX, CamElev, CamZ&gt;
  look_at TargetCenter
  angle <span class="c-num">48</span>
}}

<span class="c-com">// 3-Point Parameterized Studio Lights</span>
<span class="c-kw">light_source</span> {{ &lt;<span class="c-num">35</span>,<span class="c-num">45</span>,<span class="c-num">-30</span>&gt; rgb ThemeKey }}
<span class="c-kw">light_source</span> {{ &lt;<span class="c-num">-35</span>,<span class="c-num">28</span>,<span class="c-num">30</span>&gt; rgb ThemeFill }}

<span class="c-com">// Scene Objects (Total: 64)</span>
<span class="c-kw">sphere</span> {{ &lt;<span class="c-num">0</span>, <span class="c-num">2.4</span>, <span class="c-num">0</span>&gt;, <span class="c-num">1.85</span>
  pigment {{ rgb ThemeGrade(&lt;<span class="c-num">0.9</span>,<span class="c-num">0.2</span>,<span class="c-num">0.8</span>&gt;) }}
  finish  {{ specular <span class="c-num">0.85</span> reflection <span class="c-num">0.48</span> }}
}}</pre>
      <div class="w95-vscroll">
        <div class="w95-scroll-btn">&#9650;</div>
        <div class="w95-scroll-thumb"></div>
        <div class="w95-scroll-btn">&#9660;</div>
      </div>
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- WINDOW 3: WINDOWS EXPLORER — DOUBLE-CLICKING render.bat             -->
  <!-- =================================================================== -->
  <div class="w95-win win-explorer">
    <div class="w95-titlebar inactive">
      <div class="w95-title-left">
        <span class="w95-title-icon">
          <svg width="15" height="15" viewBox="0 0 16 16">
            <path d="M1,4 L6,4 L8,6 L15,6 L15,14 L1,14 Z" fill="#f8d850" stroke="#000" stroke-width="1"/>
          </svg>
        </span>
        <span>Chase_01 &mdash; Exported POV-Ray Folder</span>
      </div>
      <div class="w95-win-controls">
        <div class="w95-ctrl">_</div>
        <div class="w95-ctrl">&#9633;</div>
        <div class="w95-ctrl">&times;</div>
      </div>
    </div>
    <div class="w95-menubar">
      <span><u>F</u>ile</span><span><u>E</u>dit</span><span><u>V</u>iew</span><span><u>T</u>ools</span><span><u>H</u>elp</span>
    </div>
    <div class="exp-addressbar">
      <span style="font-weight:700;">Path:</span>
      <div class="exp-address-input w95-sunken">C:\Users\Subject13\AppData\Local\Artsy_2000\Povray\Chase_01</div>
    </div>
    <div class="exp-list w95-sunken">
      <div class="exp-colhead">
        <div>Name</div>
        <div>Size</div>
        <div>Type</div>
      </div>
      <div class="exp-rows">
        <div class="exp-row">
          <div class="fname">
            <svg width="16" height="16" viewBox="0 0 16 16">
              <rect x="2" y="1" width="11" height="14" fill="#fff" stroke="#000" stroke-width="1"/>
              <circle cx="8" cy="8" r="3.5" fill="#9933ff" stroke="#000" stroke-width="0.8"/>
            </svg>
            scene.pov
          </div>
          <div class="fsize">24 KB</div>
          <div class="ftype">POV-Ray 3.7 Scene Script</div>
        </div>

        <div class="exp-row selected">
          <div class="fname">
            <svg width="16" height="16" viewBox="0 0 16 16">
              <rect x="1" y="2" width="14" height="12" fill="#e0e0e0" stroke="#000" stroke-width="1"/>
              <rect x="2" y="3" width="12" height="3" fill="#000080"/>
              <circle cx="8" cy="9.5" r="2.6" fill="#008080" stroke="#000" stroke-width="0.8"/>
            </svg>
            render.bat
          </div>
          <div class="fsize">6 KB</div>
          <div class="ftype">MS-DOS Batch File</div>
        </div>

        <div class="exp-row">
          <div class="fname">
            <svg width="16" height="16" viewBox="0 0 16 16">
              <rect x="1" y="2" width="14" height="12" fill="#202030" stroke="#000" stroke-width="1"/>
              <polygon points="6,5 12,8 6,11" fill="#38e8ff"/>
            </svg>
            turntable.mp4
          </div>
          <div class="fsize">3,184 KB</div>
          <div class="ftype">MPEG-4 Video (1280&times;720)</div>
        </div>

        <div class="exp-row">
          <div class="fname">
            <svg width="16" height="16" viewBox="0 0 16 16">
              <rect x="1" y="2" width="14" height="12" fill="#301040" stroke="#000" stroke-width="1"/>
              <circle cx="8" cy="8" r="3.8" fill="#ff3d9a"/>
              <circle cx="8" cy="8" r="1.5" fill="#ffffff"/>
            </svg>
            turntable.gif
          </div>
          <div class="fsize">1,501 KB</div>
          <div class="ftype">Animated GIF (360&deg; Loop)</div>
        </div>
      </div>

      <!-- Classic White Pixel Arrow Cursor Double-Clicking render.bat -->
      <div class="dblclick-cursor">
        <div class="click-ring"></div>
        <svg width="24" height="30" viewBox="0 0 24 30" style="position:relative; z-index:2; filter: drop-shadow(2px 2px 0 rgba(0,0,0,0.45));">
          <polygon points="1,1 1,23 6,18 10,27 14,25 10,16 17,16" fill="#ffffff" stroke="#000000" stroke-width="1.8" stroke-linejoin="miter"/>
        </svg>
      </div>

      <div class="dblclick-hint">&#9654; Double-click <code>render.bat</code> &mdash; launches interactive renderer automatically</div>

      <div class="exp-note-box">
        <strong>Zero-Setup Pipeline:</strong> Pressing <code>X</code> in <em>Ascend</em>, <em>Chase</em>, <em>Rise</em>, <em>Edge</em>, or <em>Blueprint</em> writes a ready-to-render <code>scene.pov</code> plus a self-configuring <code>render.bat</code>. Just double-click <code>render.bat</code> &mdash; no manual POV-Ray flags or FFmpeg commands required.
      </div>
    </div>
    <div class="w95-statusbar" style="padding-right: 26px;">
      <div class="w95-status-pane" style="flex:1;">4 object(s) (1 selected)</div>
      <div class="w95-status-pane">4.61 MB</div>
    </div>
  </div>

  <!-- Step 2 Callout -->
  <div class="step-tip" style="left: 98px; top: 467px;">
    <span class="step-num">2</span> Double-Click render.bat
  </div>

  <!-- =================================================================== -->
  <!-- WINDOW 4: MS-DOS PROMPT — INTERACTIVE render.bat                    -->
  <!-- =================================================================== -->
  <div class="w95-win win-dos">
    <div class="w95-titlebar">
      <div class="w95-title-left">
        <span class="w95-title-icon">
          <svg width="15" height="15" viewBox="0 0 16 16">
            <rect x="1" y="2" width="14" height="12" fill="#000" stroke="#fff" stroke-width="1"/>
            <text x="2.5" y="11" fill="#fff" font-family="monospace" font-size="7" font-weight="bold">C:\</text>
          </svg>
        </span>
        <span>C:\WINDOWS\COMMAND.COM &mdash; render.bat</span>
      </div>
      <div class="w95-win-controls">
        <div class="w95-ctrl">_</div>
        <div class="w95-ctrl">&#9633;</div>
        <div class="w95-ctrl">&times;</div>
      </div>
    </div>
    <div class="dos-toolbar">
      <span class="dos-tb-pill">Auto</span>
      <span class="w95-raised dos-tb-btn">Mark</span>
      <span class="w95-raised dos-tb-btn">Copy</span>
      <span class="w95-raised dos-tb-btn">Paste</span>
      <span class="w95-raised dos-tb-btn">Full</span>
      <span style="margin-left:8px; color:#404040;">Artsy_2000 Turntable Batch</span>
    </div>
    <div class="dos-screen w95-sunken"><span class="d-cyan">==============================================================
   ARTSY_2000 -- POV-RAY 360 TURNTABLE RENDERER
==============================================================</span>
<span class="d-dim">Using POV-Ray: C:\Steam\...\Artsy_2000\bin\pvengine64.exe
Using FFmpeg:  C:\Steam\...\Artsy_2000\bin\ffmpeg.exe</span>

<span class="d-white">Select output format to generate:</span>
  [1] Both MP4 video and Animated GIF
  [2] Animated GIF only (turntable.gif)
  [3] MP4 video only (turntable.mp4)
Enter choice (1-3) [default=1]: <span class="d-green">1</span>

<span class="d-white">Select Lighting &amp; Color Scheme (1-10):</span>
  <span class="d-yellow">[1] Original Studio</span>        [6] Blueberry Cyanotype
  [2] Creme Brulee           [7] Blood Orange Valenciana
  [3] Lavender Haze          [8] Espresso Sepia
  [4] Matcha Pistachio       <span class="d-mag">[9] Peppermint Neon</span>
  [5] Cherry Blossom        [10] Midnight Licorice
Enter theme number (1-10) [default=1]: <span class="d-green">1</span>

<span class="d-cyan">Selected Output:</span> Both MP4 video and Animated GIF
<span class="d-cyan">Selected Theme:</span>  #1 - Original Studio
<span class="d-yellow">[1/3] Rendering 90 turntable frames via POV-Ray (headless)...</span>
      pvengine64.exe /EXIT /NR /RENDER scene.pov +KFF90
<span class="d-green">[2/3] Encoding turntable.mp4 (1280x720, 30 FPS)... DONE</span>
<span class="d-green">[3/3] Encoding turntable.gif (palettegen + loop)... DONE</span>
<span class="d-white">SUCCESS! Outputs saved in Chase_01\</span>  <span class="d-green">&#9608;</span></div>
    <div class="w95-statusbar" style="padding-right: 26px;">
      <div class="w95-status-pane" style="flex:1;">Running: pvengine64.exe + ffmpeg.exe (Unattended)</div>
      <div class="w95-status-pane">10 Themes</div>
    </div>
  </div>

  <!-- Step 3 Callout -->
  <div class="step-tip" style="left: 606px; top: 467px;">
    <span class="step-num">3</span> Pick MP4 / GIF &amp; 10 Lighting Schemes
  </div>

  <!-- =================================================================== -->
  <!-- WINDOW 5: POV-RAY 3.7 HEADLESS RENDERER (BOTTOM-RIGHT)              -->
  <!-- =================================================================== -->
  <div class="w95-win win-povray">
    <div class="w95-titlebar">
      <div class="w95-title-left">
        <span class="w95-title-icon">
          <svg width="15" height="15" viewBox="0 0 16 16">
            <circle cx="8" cy="8" r="6.5" fill="url(#povg)" stroke="#000" stroke-width="1"/>
            <defs>
              <radialGradient id="povg" cx="35%" cy="30%" r="70%">
                <stop offset="0%" stop-color="#ffffff"/>
                <stop offset="50%" stop-color="#38a0ff"/>
                <stop offset="100%" stop-color="#101050"/>
              </radialGradient>
            </defs>
          </svg>
        </span>
        <span>POV-Ray v3.7 (Headless) &mdash; Rendering scene.pov [Frame 65/90]</span>
      </div>
      <div class="w95-win-controls">
        <div class="w95-ctrl">_</div>
        <div class="w95-ctrl">&#9633;</div>
        <div class="w95-ctrl">&times;</div>
      </div>
    </div>
    <div class="pov-toolbar">
      <span class="w95-raised pov-btn pressed">&#9654; Tracing</span>
      <span class="w95-raised pov-btn">Pause</span>
      <span class="w95-raised pov-btn">Stop</span>
      <span class="w95-raised pov-btn">Threads: 8</span>
      <span style="margin-left:auto; font-family:Consolas,monospace; font-size:11px; color:#222;">+W1280 +H720 +A0.3 +KFF90</span>
    </div>

    <div class="pov-stage-wrap w95-sunken">
      <div class="pov-render-canvas">
        <img class="pov-layer-mosaic" src="{assets['pov_mid_mosaic_uri']}" alt="Untraced preview mosaic">
        <img class="pov-layer-traced" src="{assets['pov_mid_uri']}" alt="Raytraced scanlines">
        <div class="pov-scanbeam"></div>
        <div class="pov-trace-block"></div>
        <div class="pov-hud-tag">HEADLESS RAYTRACER &middot; SCANLINE 518 / 720 &middot; CLOCK 0.719 &middot; 64 OBJECTS</div>
      </div>

      <div class="pov-progress-row">
        <span class="pov-prog-label">Frame 65 / 90 (72%)</span>
        <div class="w95-progress-well w95-sunken">
          {''.join('<div class="w95-prog-block"></div>' for _ in range(28))}
        </div>
        <span class="pov-prog-label" style="color:#000080;">14.8M rays/s</span>
      </div>
    </div>

    <div class="w95-statusbar">
      <div class="w95-status-pane" style="flex:1;">Theme: #1 Original Studio &middot; Anti-Aliasing 0.3 &middot; Auto-Exit on Complete</div>
      <div class="w95-status-pane">CPU 100%</div>
    </div>
  </div>

  <!-- Step 4 Callout -->
  <div class="step-tip" style="left: 1210px; top: 519px;">
    <span class="step-num">4</span> Headless POV-Ray Tracing
  </div>

  <!-- =================================================================== -->
  <!-- WINDOW 6: ANIMATED GIF VIEWER — turntable.gif (TOP-RIGHT HERO)      -->
  <!-- =================================================================== -->
  <div class="w95-win win-gif">
    <div class="w95-titlebar">
      <div class="w95-title-left">
        <span class="w95-title-icon">
          <svg width="15" height="15" viewBox="0 0 16 16">
            <rect x="1" y="2" width="14" height="12" fill="#200038" stroke="#fff" stroke-width="1"/>
            <polygon points="6,4.5 12,8 6,11.5" fill="#39ff88"/>
          </svg>
        </span>
        <span>turntable.gif &mdash; Animated GIF Viewer [360&deg; Loop Playing]</span>
      </div>
      <div class="w95-win-controls">
        <div class="w95-ctrl">_</div>
        <div class="w95-ctrl">&#9633;</div>
        <div class="w95-ctrl">&times;</div>
      </div>
    </div>
    <div class="w95-menubar">
      <span><u>F</u>ile</span><span><u>P</u>layback</span><span><u>L</u>oop: Infinite</span><span><u>Z</u>oom: 100%</span><span><u>H</u>elp</span>
    </div>

    <div class="gif-stage w95-sunken">
      <img src="{assets['pov_hero_uri']}" alt="Rendered turntable.gif animated preview">
      <div class="gif-playing-pill">
        <span class="rec-dot"></span> PLAYING ANIMATED GIF &middot; 360&deg; TURNTABLE &middot; 30 FPS
      </div>
      <div class="gif-theme-pill">EXAMPLE: povray_chase_spin.gif</div>
    </div>

    <!-- Real 360-degree filmstrip extracted directly from povray_chase_spin.gif -->
    <div class="filmstrip-bar">
      {filmstrip_markup}
    </div>

    <div class="gif-controls">
      <span class="w95-raised media-btn">|&lt;</span>
      <span class="w95-raised media-btn">&lt;&lt;</span>
      <span class="w95-raised media-btn playing">&#9654;</span>
      <span class="w95-raised media-btn">&#9632;</span>
      <span class="w95-raised media-btn">&gt;|</span>
      <div class="scrubber">
        <div class="scrubber-fill"></div>
        <div class="scrubber-thumb"></div>
      </div>
      <span style="font-family:Consolas,monospace; font-size:11px; font-weight:700;">LOOP</span>
      <div class="theme-dots" title="10 Built-in Lighting Schemes">
        <span class="t-dot" style="background:#9d4dff;"></span>
        <span class="t-dot" style="background:#f5b762;"></span>
        <span class="t-dot" style="background:#b994ff;"></span>
        <span class="t-dot" style="background:#6cd484;"></span>
        <span class="t-dot" style="background:#ff7ab8;"></span>
        <span class="t-dot" style="background:#38c4ff;"></span>
        <span class="t-dot" style="background:#ff5a2a;"></span>
        <span class="t-dot" style="background:#a67b5b;"></span>
        <span class="t-dot" style="background:#39ffaa;"></span>
        <span class="t-dot" style="background:#c4ccd8;"></span>
      </div>
    </div>

    <div class="w95-statusbar">
      <div class="w95-status-pane" style="flex:1;">turntable.gif &middot; 360&deg; Orbit &middot; Also exported: turntable.mp4 (H.264 720p)</div>
      <div class="w95-status-pane">10 Color Presets</div>
    </div>
  </div>

  <!-- Step 5 Callout -->
  <div class="step-tip" style="left: 1172px; top: 5px;">
    <span class="step-num">5</span> Shareable Animated GIF / MP4
  </div>

  <!-- =================================================================== -->
  <!-- CLASSIC WINDOWS 95 TASKBAR                                          -->
  <!-- =================================================================== -->
  <div class="taskbar">
    <div class="start-btn">
      <svg width="18" height="16" viewBox="0 0 18 16">
        <rect x="1" y="1" width="7" height="6" fill="#ff2a2a"/>
        <rect x="10" y="1" width="7" height="6" fill="#32cd32"/>
        <rect x="1" y="9" width="7" height="6" fill="#1e90ff"/>
        <rect x="10" y="9" width="7" height="6" fill="#ffd700"/>
      </svg>
      <span>Start</span>
    </div>
    <div class="tb-divider"></div>
    <div class="tb-tasks">
      <div class="tb-item">
        <img src="{assets['cube_icon_16_uri']}" width="15" height="15" alt="">
        <span>Artsy_2000</span>
      </div>
      <div class="tb-item">
        <svg width="15" height="15" viewBox="0 0 16 16"><path d="M1,4 L6,4 L8,6 L15,6 L15,14 L1,14 Z" fill="#f8d850" stroke="#000" stroke-width="1"/></svg>
        <span>Chase_01</span>
      </div>
      <div class="tb-item">
        <svg width="14" height="14" viewBox="0 0 16 16"><rect x="2" y="1" width="12" height="14" fill="#fff" stroke="#000" stroke-width="1"/><rect x="2" y="1" width="12" height="3" fill="#008080"/></svg>
        <span>scene.pov - Notepad</span>
      </div>
      <div class="tb-item">
        <svg width="15" height="15" viewBox="0 0 16 16"><rect x="1" y="2" width="14" height="12" fill="#000" stroke="#404040" stroke-width="1"/><text x="2.5" y="11" fill="#fff" font-family="monospace" font-size="7" font-weight="bold">C:\</text></svg>
        <span>render.bat</span>
      </div>
      <div class="tb-item">
        <svg width="14" height="14" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="#2080e0" stroke="#000" stroke-width="1"/><circle cx="6" cy="6" r="2" fill="#fff"/></svg>
        <span>POV-Ray v3.7 (72%)</span>
      </div>
      <div class="tb-item active">
        <svg width="15" height="15" viewBox="0 0 16 16"><rect x="1" y="2" width="14" height="12" fill="#200038" stroke="#000" stroke-width="1"/><polygon points="6,4.5 12,8 6,11.5" fill="#39ff88"/></svg>
        <span>turntable.gif</span>
      </div>
    </div>
    <div class="tb-tray">
      <svg width="15" height="15" viewBox="0 0 16 16">
        <polygon points="2,6 6,6 10,2 10,14 6,10 2,10" fill="#404040"/>
        <path d="M12,5 Q14,8 12,11" fill="none" stroke="#000080" stroke-width="1.5"/>
      </svg>
      <span>11:42 PM</span>
    </div>
  </div>

</div>
</body>
</html>
"""


def find_edge() -> Path:
    for p in EDGE_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError("Microsoft Edge not found in standard Windows locations.")


def generate() -> Path:
    assets = load_assets()
    html = build_html(assets)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    edge = find_edge()

    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "win95_pipeline.html"
        html_path.write_text(html, encoding="utf-8")

        raw_png = Path(tmpdir) / "raw_capture.png"
        url = html_path.as_uri()
        cmd = [
            str(edge),
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--window-size=1920,1080",
            f"--screenshot={raw_png}",
            url,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if not raw_png.exists():
            raise RuntimeError(
                f"Edge failed to render mockup PNG (rc={res.returncode}): {res.stderr}"
            )

        with Image.open(raw_png) as im:
            w, h = im.size
            if (w, h) != (1920, 1080):
                im = im.crop((0, 0, min(w, 1920), min(h, 1080)))
                if im.size != (1920, 1080):
                    im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
            im.convert("RGB").save(OUTPUT_PNG, format="PNG", optimize=True)

    with Image.open(OUTPUT_PNG) as check:
        print(f"Generated: {OUTPUT_PNG}")
        print(f"Dimensions: {check.size}, Bytes: {OUTPUT_PNG.stat().st_size:,}")
    return OUTPUT_PNG


if __name__ == "__main__":
    generate()
