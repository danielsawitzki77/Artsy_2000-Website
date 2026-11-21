#!/usr/bin/env python3
"""
Builds curated press kit media assets, plain-text/Markdown fact sheets,
and downloadable ZIP packs under Artsy_2000-Website/press/.

Run from anywhere:
    python tools/build_press_kit.py
"""

import json
import os
import shutil
import zipfile
from pathlib import Path
from PIL import Image


WEB_ROOT = Path(__file__).resolve().parent.parent
GAME_ROOT = WEB_ROOT.parent / "Artsy_2000"
SCREENSHOT_SOURCE_ROOT = Path(r"G:\My Drive\Artsy_2000\Screenshots")
PRESS_ROOT = WEB_ROOT / "press"
MEDIA_SCREENSHOTS_DIR = PRESS_ROOT / "media" / "screenshots"
MEDIA_BRANDING_DIR = PRESS_ROOT / "media" / "branding"
DOWNLOADS_DIR = PRESS_ROOT / "downloads"


SCREENSHOT_SPECS = [
    (
        SCREENSHOT_SOURCE_ROOT / "Chase3D_2.png",
        "artsy_2000_01_chase_daemon_host.png",
        "Chase Mode — Daemon Host Boss (MK_NEXUS)",
        "3d",
        "Crimson Fibonacci Spike Sphere boss ('Attack Pattern Beta') rendered natively on CPU threads over a neon wireframe horizon inside the Buck-Fifty CRT frame.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Chase3D_4.png",
        "artsy_2000_02_chase_checkerboard_horizon.png",
        "Chase Mode — Reflective Checkerboard Pursuit",
        "3d",
        "High-velocity software-rendered 3D pursuit across a rippling blue checkerboard plane with reflective geometric projectiles and skyline peaks.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Rise_2.png",
        "artsy_2000_03_the_rise_cpu_raytracer.png",
        "The Rise — Real-Time CPU Raytracer & Reflections",
        "3d",
        "Multi-threaded CPU raytracing with reflective crystal monoliths, mirrored checkerboard ocean, floating horizon sphere, and live ECG vitals.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Isolate_2.png",
        "artsy_2000_04_isolate_containment_grid.png",
        "Iso-Lation Ward — 14x14 Stepped Isometric Grid",
        "3d",
        "Tactical 3D raytraced containment board with five elevation tiers, glowing patrol trails, and R/G/B sentinel drones hunting Subject 13.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Edge_1.png",
        "artsy_2000_05_edge_pipe_hypercube.png",
        "Edge Computing — 3D Aluminum Pipe Hypercube",
        "3d",
        "High-speed banking traversal along metallic conduit pipes wrapping a massive 3D hypercube, complete with manifold key radar HUD.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Gps_1.png",
        "artsy_2000_06_gps_utah_triangulation.png",
        "GPS Mode — Utah Orbital Satellite Triangulation",
        "crt",
        "'Grid-Locked & Pepperoni-Shocked': zooming across public-domain USGS/USDA Utah aerial imagery to triangulate Site Alpha-4 before the pass expires.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Surgery_1.png",
        "artsy_2000_07_surgery_just_let_go.png",
        "Brain Surgery ('Just Let Go') — Operating Theater",
        "crt",
        "1990s point-and-click operating theater with surgical tool inventory, verb actions, and flashing crimson alert cues.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Labyrinth_1.png",
        "artsy_2000_08_labyrinth_emerald_crt.png",
        "The Labyrinth — Emerald Phosphor Maze & ECG HUD",
        "crt",
        "Dual-panel phosphor CRT maze and first-person wireframe corridor with live electrocardiogram readout and scanline sprite-catching.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "PizzaRace_1.png",
        "artsy_2000_09_pizza_delivery_race.png",
        "Pizza Delivery Race — 16-Bit Desert Highway Run",
        "crt",
        "OutRun-inspired 5-lane desert highway escape featuring roadside brick barriers, oncoming traffic, and a cosmic rotating pizza skybox.",
    ),
]


BRANDING_SPECS = [
    (
        WEB_ROOT / "assets" / "artsy_2000_logo.png",
        "artsy_2000_logo_transparent.png",
        "Artsy_2000 Official Wordmark (Transparent PNG)",
        "logo",
        True,
    ),
    (
        GAME_ROOT / "assets" / "images" / "ui" / "app_icon.png",
        "buck_fifty_cube_icon.png",
        "Buck-Fifty Neon Hypercube Icon (Square PNG)",
        "logo",
        False,
    ),
    (
        GAME_ROOT / "assets" / "images" / "ui" / "buck_fifty_splash.png",
        "buck_fifty_labs_crt_splash.png",
        "Buck-Fifty Innovation Labs CRT Workstation Splash",
        "keyart",
        False,
    ),
    (
        WEB_ROOT / "assets" / "buck_fifty_supersized_logo.jpg",
        "buck_fifty_labs_manual_emblem.jpg",
        "Buck-Fifty Innovation Labs Print Manual Emblem",
        "logo",
        False,
    ),
    (
        GAME_ROOT / "steam" / "community_pages" / "b50_event_header_1920x622.png",
        "artsy_2000_keyart_banner_1920x622.png",
        "Artsy_2000 Widescreen Key Art Header (1920x622)",
        "keyart",
        False,
    ),
    (
        GAME_ROOT / "steam" / "community_pages" / "b50_event_cover_800x450.png",
        "artsy_2000_keyart_cover_800x450.png",
        "Artsy_2000 16:9 Key Art Cover (800x450)",
        "keyart",
        False,
    ),
    (
        GAME_ROOT / "steam" / "community_pages" / "b50_creator_header_1500x220.png",
        "buck_fifty_studio_banner_1500x220.png",
        "Buck-Fifty Innovation Labs Studio Header (1500x220)",
        "keyart",
        False,
    ),
    (
        GAME_ROOT / "steam" / "store_page" / "b50_showcase_protocols.png",
        "artsy_2000_showcase_protocols.png",
        "Feature Collage — Pure CPU Protocols Showcase",
        "showcase",
        False,
    ),
    (
        GAME_ROOT / "steam" / "store_page" / "b50_showcase_facility.png",
        "artsy_2000_showcase_facility.png",
        "Feature Collage — Suite G & Dr. Brad Vance",
        "showcase",
        False,
    ),
    (
        GAME_ROOT / "steam" / "store_page" / "b50_showcase_cpu_farm.gif",
        "artsy_2000_showcase_cpu_farm.gif",
        "Animated Showcase GIF — Sub-Level 4 Pure CPU Raytracing",
        "showcase",
        False,
    ),
    (
        WEB_ROOT / "assets" / "povray_turntable.jpg",
        "artsy_2000_povray_turntable_studio.jpg",
        "POV-Ray 3.7 Turntable Render — Ascend Mode Studio",
        "povray",
        False,
    ),
    (
        WEB_ROOT / "assets" / "povray_facility.jpg",
        "artsy_2000_povray_facility_compound.jpg",
        "POV-Ray 3.7 Render — Buck-Fifty Brutalist Compound",
        "povray",
        False,
    ),
    (
        WEB_ROOT / "assets" / "povray_chase.jpg",
        "artsy_2000_povray_chase_diorama.jpg",
        "POV-Ray 3.7 Render — Chase Mode Retrosynth Diorama",
        "povray",
        False,
    ),
]


FACT_SHEET_TXT = """================================================================================
ARTSY_2000 — OFFICIAL PRESS FACT SHEET
================================================================================

GAME TITLE:        Artsy_2000
DEVELOPER:         Buck-Fifty Innovation Labs / Daniel Sawitzki
PUBLISHER:         Buck-Fifty Innovation Labs (Buck-Fifty Studios)
LOCATION:          Salt Lake City, Utah, USA
RELEASE DATE:      January 2027
PRICE:             $1.50 USD
PLATFORM:          Windows 10 / 11 (64-bit) — Steam
STEAM STORE:       https://store.steampowered.com/app/5641470/
GENRE:             Multi-Genre Retro Arcade / 1990s Sci-Fi Satire /
                   Software-Raytraced Anthology
PLAYERS:           Single-Player + Local 2-Player PvP ("Them Apples")
INPUT SUPPORT:     Full Keyboard, Mouse & Gamepad Support
ACHIEVEMENTS:      153 Steam Achievements + Steam Cloud Saves
ENGINE / RENDER:   Custom C++17 & Win32/GDI Multi-Threaded CPU Software Renderer
                   & Raytracer (Zero GPU / Zero DirectX, OpenGL, or Vulkan)
SOUNDTRACK:        6 Original Synthwave Tracks by Holon
                   (https://holon-subatomic-audio.bandcamp.com/)
WEBSITE:           https://buckfiftylabs.com/
PRESS KIT:         https://buckfiftylabs.com/press/
PRESS CONTACT:     info@buckfiftylabs.com
OFFICIAL TRAILER:  https://youtu.be/hl4ftXtNqVU

--------------------------------------------------------------------------------
ONE-LINE PITCH
--------------------------------------------------------------------------------
A $1.50 multi-genre 1990s retro-futuristic arcade escape built entirely in pure
C++17 CPU software rendering (zero GPU required), spanning 11 playable genres,
5 CRT staff interrogations, 74 live-action/archival FMV clips, and an actual
built-in POV-Ray 3.7 3D turntable studio.

--------------------------------------------------------------------------------
SHORT DESCRIPTION
--------------------------------------------------------------------------------
Artsy_2000 casts you as Subject 13 inside Buck-Fifty Innovation Labs' Sub-Level 4
— a satirical 1996 Salt Lake City cognitive research bunker promising a $1.50 per
diem and one personal pan pizza voucher. Built from scratch in pure C++17 and
Win32/GDI with zero GPU dependencies, the game shifts seamlessly across 11
interconnected retro genres: CPU-raytraced 3D pursuits, Mode-7 highways, emerald
phosphor mazes, 90s point-and-click brain surgery, 3D pipe hypercubes, satellite
triangulation over real Utah USGS imagery, top-down stealth, and high-pressure
CRT interrogations — culminating in a secret 3D raytracer sculptor that exports
real POV-Ray 3.7 360-degree turntable animations.

--------------------------------------------------------------------------------
KEY FEATURES
--------------------------------------------------------------------------------
* 11 Interconnected Campaign Genres + 5 CRT Interrogations:
  1. Chase Mode ("Spike the Ball") — CPU-raytraced 3D pursuit & boss fight
  2. Them Apples (Revenge + Local 2P PvP) — Dual-snake CRT duel vs Daemon 0x0666
  3. Iso-Lation Ward — 14x14 stepped raytraced isometric sentinel containment
  4. Brain Surgery ("Just Let Go") — 90s 8-verb point-and-click theater escape
  5. The Rise ("Fancy a Lift?") — Real-time CPU raytracer & rigid-body physics
  6. The Labyrinth ("Straight Forward") — Emerald wireframe maze & live ECG HUD
  7. Edge Computing — High-speed 3D aluminum pipe hypercube key hunt
  8. Grid-Locked & Pepperoni-Shocked (GPS) — Real Utah USGS aerial triangulation
  9. Blueprint Mode — Split-screen CAD schematic maze & 3D lobby tour
  10. Parking Lot Stealth ("Parxing Jordan") — 23s stealth + Dark Ages shift
  11. Pizza Delivery Race ("Healthful Delivery") — 16-bit 5-lane desert racer
  + 5 timed CRT dialogue interrogations with facility staff.

* 100% Pure CPU Software Rendering (Zero GPU Required):
  Every 3D raytraced reflection, Mode-7 ground plane, CRT curvature shader, and
  scanline filter runs natively on multi-threaded CPU silicon via Win32/GDI —
  no DirectX, OpenGL, or Vulkan required.

* Secret "Ascend" Mode & Real POV-Ray 3.7 Turntable Export:
  Survivors unlock a free-flight 3D raytracer sculptor featuring Eric Haines'
  Standard Procedural Database (SPD) generator and one-click export to genuine
  POV-Ray 3.7 SDL scripts + automated 90-frame 360-degree MP4/GIF rendering.

* 74 Archival FMV Clips & 50 In-World TV Breaks:
  Full-motion video broadcasts starring Clinical Director Dr. Brad Vance,
  satirical 1990s commercials (Slab-O-Bull, Fissi-Efficient, Omni-Smile, Model
  B-50), and hidden VHS glitch folders.

* Deep Replayability & 153 Steam Achievements:
  Includes Relive Trauma mode select, Local 2-Player PvP, Perma-Death, 15-minute
  Speed Run, and 4 full-campaign visual distortion difficulties (Dog Video Wave,
  Green CRT, Rotating Cube, Hexagonal Tiles).

* Priced Literally at a Buck-Fifty ($1.50):
  Matching the in-game per diem promised to test volunteers.

* Original Soundtrack by Holon:
  6 original synthwave compositions ("Everything Has Its Cost", "From These
  Ruins", "Point Of Origin", "Coherence Drift", "Initial State", and "Afterlight")
  streaming seamlessly via XAudio2 with automatic FMV audio ducking.

--------------------------------------------------------------------------------
SYSTEM REQUIREMENTS (WINDOWS)
--------------------------------------------------------------------------------
* OS:         Windows 10 or Windows 11 (64-bit)
* Processor:  64-bit multi-core CPU with AVX2 support
              (Intel 4th Gen Core / AMD Ryzen or newer)
* Graphics:   No dedicated 3D GPU required (pure multi-threaded CPU software
              renderer; standard desktop display output only)
* Input:      Keyboard & Mouse, or XInput / standard gamepad
* Notice:     Contains bright flashing patterns, scanlines, CRT flicker, and
              rapid screen distortions (photosensitivity advisory).

--------------------------------------------------------------------------------
STREAMING & MONETIZATION POLICY
--------------------------------------------------------------------------------
Buck-Fifty Innovation Labs / Daniel Sawitzki explicitly grants press, reviewers,
YouTubers, Twitch streamers, and content creators permission to record, stream,
publish, and monetize (via ad revenue, sponsorships, tips, and memberships)
gameplay footage, reviews, critiques, and videos featuring Artsy_2000 and the
assets provided in this press kit.

Note on Music: The original soundtrack by Holon is licensed for in-game
distribution; creators are welcome to include game audio in gameplay coverage
and streams with credit to Holon (https://holon-subatomic-audio.bandcamp.com/).

--------------------------------------------------------------------------------
COMPANION MEDIA & LINKS
--------------------------------------------------------------------------------
* Steam Store Page:        https://store.steampowered.com/app/5641470/
* Official 1996 Portal:    https://buckfiftylabs.com/
* Press Kit:               https://buckfiftylabs.com/press/
* Official Trailer:        https://youtu.be/hl4ftXtNqVU
* Book Series (Amazon):    https://www.amazon.com/dp/B0HSFRJ2HQ?binding=paperback&ref=dbs_dp_rwt_sb_pc_tpbk
* Official Merch Shop:     https://buckfiftyverse.myspreadshop.com/
* Soundtrack (Holon):      https://holon-subatomic-audio.bandcamp.com/
* Press & Review Keys:     info@buckfiftylabs.com

Copyright (c) 2026-2027 Daniel Sawitzki / Buck-Fifty Innovation Labs.
"""


FACT_SHEET_MD = """# Artsy_2000 — Official Press Fact Sheet

| Field | Details |
| :--- | :--- |
| **Title** | Artsy_2000 |
| **Developer / Publisher** | Buck-Fifty Innovation Labs (Daniel Sawitzki) |
| **Location** | Salt Lake City, Utah, USA |
| **Release Date** | January 2027 |
| **Price** | $1.50 USD |
| **Platform** | Windows 10 / 11 (64-bit) via Steam |
| **Steam Store** | https://store.steampowered.com/app/5641470/ |
| **Genre** | Multi-Genre Retro Arcade / 1990s Sci-Fi Satire / Software-Raytraced Anthology |
| **Players** | Single-Player + Local 2-Player PvP (*Them Apples*) |
| **Input** | Full Keyboard, Mouse & Gamepad Support |
| **Steam Features** | 153 Steam Achievements, Steam Cloud |
| **Tech Stack** | Custom C++17 & Win32/GDI Multi-Threaded CPU Software Renderer (0% GPU) |
| **Original Soundtrack** | 6 Synthwave Tracks by [Holon](https://holon-subatomic-audio.bandcamp.com/) |
| **Official Website** | https://buckfiftylabs.com/ |
| **Press Kit** | https://buckfiftylabs.com/press/ |
| **Press Contact / Keys** | info@buckfiftylabs.com |

## One-Line Pitch
A $1.50 multi-genre 1990s retro-futuristic arcade escape built entirely in pure C++17 CPU software rendering (zero GPU required), spanning 11 playable genres, 5 CRT staff interrogations, 74 FMV clips, and a built-in POV-Ray 3.7 3D turntable studio.

## Short Description
*Artsy_2000* casts you as Subject 13 inside Buck-Fifty Innovation Labs' Sub-Level 4 — a satirical 1996 Salt Lake City cognitive research bunker promising a $1.50 per diem and one personal pan pizza voucher. Built from scratch in pure C++17 and Win32/GDI with zero GPU dependencies, the game shifts seamlessly across 11 interconnected retro genres: CPU-raytraced 3D pursuits, Mode-7 highways, emerald phosphor mazes, 90s point-and-click brain surgery, 3D pipe hypercubes, satellite triangulation over real Utah USGS imagery, top-down stealth, and high-pressure CRT interrogations — culminating in a secret 3D raytracer sculptor that exports real POV-Ray 3.7 360° turntable animations.

## Key Features
- **11 Interconnected Campaign Modes + 5 Staff Interrogations:** Chase Mode, Them Apples (CRT Snake + Local 2P PvP), Iso-Lation Ward (14×14 isometric raytraced arena), Brain Surgery (*Just Let Go* 90s point-and-click), The Rise (CPU raytracer + physics), The Labyrinth (wireframe maze + ECG vitals), Edge Computing (3D aluminum pipe hypercube), Grid-Locked & Pepperoni-Shocked (Utah USGS satellite triangulation), Blueprint Mode (CAD schematic + 3D lobby tour), Parking Lot Stealth (with Dark Ages oxygen hallucination), and Pizza Delivery Race (OutRun-style desert highway).
- **Zero GPU Dependencies:** Multi-threaded CPU software rasterization, Phong raytracing, and CRT post-processing written in pure C++17 & Win32/GDI.
- **Built-In POV-Ray 3.7 Turntable Studio:** Secret *Ascend* mode lets players sculpt 3D scenes, invoke Eric Haines' Standard Procedural Database (SPD), and export real POV-Ray SDL + 90-frame 360° MP4/GIF turntables.
- **74 Archival FMV Clips (50 TV Breaks):** Hosted by Clinical Director Dr. Brad Vance with satirical 1996 commercials and hidden VHS glitch folders.
- **153 Steam Achievements & 7 Campaign Modes:** Normal (*Joe Six-Pack*), *Perma-Death*, *Speed Run*, and 4 visual distortion campaigns (*Dog Video Wave*, *Green CRT*, *Rotating Cube*, *Hexagonal Tiles*).
- **Original Soundtrack by Holon:** *Everything Has Its Cost*, *From These Ruins*, *Point Of Origin*, *Coherence Drift*, *Initial State*, and *Afterlight*.
- **Literally $1.50:** Priced to match Buck-Fifty's legendary per diem.

## Videos & Links
- **Official Broadcast Trailer:** https://youtu.be/hl4ftXtNqVU
- **Raytracing & POV-Ray Archive Reel:** https://www.youtube.com/watch?v=lHGAPG5uiAc
- **From Utah to Pixar (3D Graphics Heritage):** https://youtu.be/dSGkUbqt4p0
- **Steam Store:** https://store.steampowered.com/app/5641470/
- **1996 Corporate Site & Companion PDFs:** https://buckfiftylabs.com/
- **Official Print Book Series (Amazon):** https://www.amazon.com/dp/B0HSFRJ2HQ?binding=paperback&ref=dbs_dp_rwt_sb_pc_tpbk
- **Merchandise Shop:** https://buckfiftyverse.myspreadshop.com/
- **Press & Review Keys:** info@buckfiftylabs.com

## Streaming & Monetization Policy
Press, reviewers, YouTubers, and streamers are explicitly permitted to capture, broadcast, publish, and monetize gameplay, reviews, and coverage of *Artsy_2000* using any assets included in this press kit.
"""


README_PRESS_TXT = """ARTSY_2000 — PRESS KIT ASSET USAGE GUIDE
========================================

All screenshots, logos, key art, renders, and text contained in this archive
are cleared for editorial, review, news, streaming, YouTube thumbnail, and
event/festival coverage of Artsy_2000 (Buck-Fifty Innovation Labs).

- Steam Store:    https://store.steampowered.com/app/5641470/
- Official Site:  https://buckfiftylabs.com/
- Press Kit:      https://buckfiftylabs.com/press/
- Press Contact:  info@buckfiftylabs.com

Thank you for covering Artsy_2000!
"""


def fmt_size(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    return f"{max(1, round(num_bytes / 1024))} KB"


def build():
    MEDIA_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_BRANDING_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Clear old generated files in target folders so re-runs stay clean
    for d in (MEDIA_SCREENSHOTS_DIR, MEDIA_BRANDING_DIR, DOWNLOADS_DIR):
        for child in d.iterdir():
            if child.is_file():
                child.unlink()

    manifest = {"screenshots": [], "branding": [], "downloads": {}}

    # 1. Copy curated screenshots
    for src, dst_name, title, category, caption in SCREENSHOT_SPECS:
        if not src.exists():
            raise FileNotFoundError(f"Missing screenshot source: {src}")
        dst = MEDIA_SCREENSHOTS_DIR / dst_name
        shutil.copy2(src, dst)
        with Image.open(dst) as im:
            w, h = im.size
        size = dst.stat().st_size
        manifest["screenshots"].append({
            "file": f"media/screenshots/{dst_name}",
            "filename": dst_name,
            "title": title,
            "category": category,
            "caption": caption,
            "width": w,
            "height": h,
            "bytes": size,
            "sizeLabel": fmt_size(size),
        })

    # 2. Copy curated branding / logos / key art / renders
    for src, dst_name, title, kind, transparent in BRANDING_SPECS:
        if not src.exists():
            raise FileNotFoundError(f"Missing branding source: {src}")
        dst = MEDIA_BRANDING_DIR / dst_name
        shutil.copy2(src, dst)
        with Image.open(dst) as im:
            w, h = im.size
        size = dst.stat().st_size
        manifest["branding"].append({
            "file": f"media/branding/{dst_name}",
            "filename": dst_name,
            "title": title,
            "kind": kind,
            "transparent": transparent,
            "width": w,
            "height": h,
            "bytes": size,
            "sizeLabel": fmt_size(size),
        })

    # 3. Write standalone Fact Sheet files
    fs_txt_path = DOWNLOADS_DIR / "Artsy_2000_Fact_Sheet.txt"
    fs_md_path = DOWNLOADS_DIR / "Artsy_2000_Fact_Sheet.md"
    fs_txt_path.write_text(FACT_SHEET_TXT.strip() + "\n", encoding="utf-8")
    fs_md_path.write_text(FACT_SHEET_MD.strip() + "\n", encoding="utf-8")

    # 4. Build ZIP archives (deflate compression level 9)
    zip_screenshots = DOWNLOADS_DIR / "Artsy_2000_Screenshots.zip"
    with zipfile.ZipFile(zip_screenshots, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("README_PRESS.txt", README_PRESS_TXT)
        for item in manifest["screenshots"]:
            src_file = PRESS_ROOT / item["file"]
            zf.write(src_file, arcname=f"Artsy_2000_Screenshots/{item['filename']}")

    zip_branding = DOWNLOADS_DIR / "Artsy_2000_Logos_KeyArt.zip"
    with zipfile.ZipFile(zip_branding, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("README_PRESS.txt", README_PRESS_TXT)
        for item in manifest["branding"]:
            src_file = PRESS_ROOT / item["file"]
            zf.write(src_file, arcname=f"Artsy_2000_Logos_KeyArt/{item['filename']}")

    zip_full = DOWNLOADS_DIR / "Artsy_2000_Press_Kit.zip"
    with zipfile.ZipFile(zip_full, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("Artsy_2000_Press_Kit/README_PRESS.txt", README_PRESS_TXT)
        zf.write(fs_txt_path, arcname="Artsy_2000_Press_Kit/FACT_SHEET.txt")
        zf.write(fs_md_path, arcname="Artsy_2000_Press_Kit/FACT_SHEET.md")
        for item in manifest["screenshots"]:
            src_file = PRESS_ROOT / item["file"]
            zf.write(src_file, arcname=f"Artsy_2000_Press_Kit/screenshots/{item['filename']}")
        for item in manifest["branding"]:
            src_file = PRESS_ROOT / item["file"]
            zf.write(src_file, arcname=f"Artsy_2000_Press_Kit/branding/{item['filename']}")

    for key, p in [
        ("full", zip_full),
        ("screenshots", zip_screenshots),
        ("branding", zip_branding),
        ("factsheet_txt", fs_txt_path),
        ("factsheet_md", fs_md_path),
    ]:
        sz = p.stat().st_size
        manifest["downloads"][key] = {
            "file": f"downloads/{p.name}",
            "filename": p.name,
            "bytes": sz,
            "sizeLabel": fmt_size(sz),
        }

    print(json.dumps(manifest["downloads"], indent=2))
    print(f"Screenshots: {len(manifest['screenshots'])}, Branding: {len(manifest['branding'])}")


if __name__ == "__main__":
    build()
