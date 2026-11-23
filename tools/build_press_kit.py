#!/usr/bin/env python3
"""
Builds curated press kit media assets, plain-text/Markdown fact sheets,
and downloadable ZIP packs under Artsy_2000-Website/press/.

Run from anywhere:
    python tools/build_press_kit.py
"""

import json
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
MEDIA_THUMBS_DIR = PRESS_ROOT / "media" / "thumbs"
DOWNLOADS_DIR = PRESS_ROOT / "downloads"


# Interleaved ordering mixing 3D gameplay/editor, CRT/arcade, and archival FMV/cutscene stills.
# Strictly uses the primary 1920x1200 screenshots and ignores *_1920x1080 duplicates.
SCREENSHOT_SPECS = [
    (
        SCREENSHOT_SOURCE_ROOT / "Chase3D_2.png",
        "artsy_2000_01_chase_daemon_host.png",
        "Chase Mode — Daemon Host Boss (MK_NEXUS)",
        "3d",
        "Crimson Fibonacci Spike Sphere boss ('Attack Pattern Beta') rendered natively on CPU threads over a neon wireframe horizon — and exportable directly to POV-Ray 3.7.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Lobby.png",
        "artsy_2000_02_fmv_vance_lobby.png",
        "Archival FMV — Dr. Brad Vance & Lobby Brain Mural",
        "fmv",
        "1993 VHS reception-cam footage of Clinical Director Dr. Brad Vance strolling past Buck-Fifty Innovation Labs' pastel rainbow brain mural.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Editor_1.png",
        "artsy_2000_03_editor_sphereflake_ascend.png",
        "Ascend Mode 3D Editor — Sphereflake & POV-Ray Export",
        "3d",
        "Free-flight pure-CPU 3D raytracer sculptor rendering Eric Haines' reflective Sphereflake fractal over neon wireframe peaks with one-key X export to POV-Ray 3.7.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Gps_1.png",
        "artsy_2000_04_gps_utah_triangulation.png",
        "GPS Mode — Utah Orbital Satellite Triangulation",
        "crt",
        "'Grid-Locked & Pepperoni-Shocked': zooming across public-domain USGS/USDA Utah aerial imagery to triangulate Site Alpha-4 before the pass expires.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Ascend_1.png",
        "artsy_2000_05_fmv_ascend_runway.png",
        "Archival Cutscene — Ascend Mode Checkerboard Runway",
        "fmv",
        "Subject 13 striding down a glossy raytraced checkerboard runway flanked by floating 3D geometric primitives, green wireframe ridges, and a synthwave sun.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Rise_2.png",
        "artsy_2000_06_the_rise_cpu_raytracer.png",
        "The Rise — Real-Time CPU Raytracer & Reflections",
        "3d",
        "Multi-threaded CPU raytracing with reflective crystal monoliths, mirrored checkerboard ocean, floating horizon sphere, and live ECG vitals.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Conversation.png",
        "artsy_2000_07_conversation_prep_ward.png",
        "Terminal Interrogation — Surgical Prep Ward (Stall 03)",
        "crt",
        "High-pressure CRT dialogue bluffing the Prep Orderly while pre-sedative interference scrambles reply options under a ticking suspicion meter.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "B-50.png",
        "artsy_2000_08_fmv_b50_pickup_compound.png",
        "Archival TV Break — Model B-50 Outside Site Alpha-4",
        "fmv",
        "16mm commercial footage of a Model B-50 pickup ripping donuts outside Buck-Fifty Innovation Labs' brutalist rooftop concrete hypercube.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Isolate_2.png",
        "artsy_2000_09_isolate_containment_grid.png",
        "Iso-Lation Ward — 14x14 Stepped Isometric Grid",
        "3d",
        "Tactical 3D raytraced containment board with five elevation tiers, glowing patrol trails, and R/G/B sentinel drones hunting Subject 13.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Surgery_1.png",
        "artsy_2000_10_surgery_just_let_go.png",
        "Brain Surgery ('Just Let Go') — Operating Theater",
        "crt",
        "1990s point-and-click operating theater with surgical tool inventory, verb actions, and flashing crimson alert cues.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Surgeon.png",
        "artsy_2000_11_fmv_dr_sterling_surgeon.png",
        "Archival FMV — Dr. Sterling (Cranial Bay 04)",
        "fmv",
        "Live-action TV Break transmission introducing Chief Neurocompliance Officer Dr. Sterling outside Theatre 04's operating bay.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Chase3D_7.png",
        "artsy_2000_12_chase_crt_shatter.png",
        "Chase Mode — CRT Distortion & Spike Sphere Shatter",
        "3d",
        "Full Buck-Fifty CRT bezel presentation of Chase Mode mid-chaos: chromatic scanline distortion rippling across a detonating pink Fibonacci Spike Sphere and debris storm over a reflective checkerboard floor.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Loading.png",
        "artsy_2000_13_loading_raytracing_irl.png",
        "CRT Intermission — 'Raytracing IRL' Animated Bumper",
        "crt",
        "Green phosphor retro rubber-hose cartoon playing on the Buck-Fifty CRT monitor between cognitive evaluation protocols.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Skullthor.png",
        "artsy_2000_14_fmv_skullthor_cartoon.png",
        "Archival TV Break — Skullthor Animated Broadcast",
        "fmv",
        "1990s Saturday-morning animated TV Break hijack showing armored nemesis Skullthor breaching the Sub-Level 4 green-CRT server room.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Edge_1.png",
        "artsy_2000_15_edge_pipe_hypercube.png",
        "Edge Computing — 3D Aluminum Pipe Hypercube",
        "3d",
        "High-speed banking traversal along metallic conduit pipes wrapping a massive 3D hypercube, complete with manifold key radar HUD.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Labyrinth_1.png",
        "artsy_2000_16_labyrinth_emerald_crt.png",
        "The Labyrinth — Emerald Phosphor Maze & ECG HUD",
        "crt",
        "Dual-panel phosphor CRT maze and first-person wireframe corridor with live electrocardiogram readout and scanline sprite-catching.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Vouchers.png",
        "artsy_2000_17_fmv_vance_vouchers.png",
        "Archival FMV — 1990s Value Pack & Pizza Vouchers",
        "fmv",
        "Dr. Brad Vance pitching the 1990s Value Pack of complimentary personal pan pizza vouchers during a mandatory Sub-Level 4 TV Break.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Editor_2.png",
        "artsy_2000_18_editor_sculpt_chain.png",
        "Ascend Mode 3D Editor — Sculpted Reflective Sphere Chain",
        "3d",
        "User-sculpted curving chain of checkered emerald, cyan, and violet reflective spheres built in Ascend Mode and ready for instant POV-Ray 3.7 turntable export.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "PizzaRace_1.png",
        "artsy_2000_19_pizza_delivery_race.png",
        "Pizza Delivery Race — 16-Bit Desert Highway Run",
        "crt",
        "OutRun-inspired 5-lane desert highway escape featuring roadside brick barriers, oncoming traffic, and a cosmic rotating pizza skybox.",
    ),
    (
        SCREENSHOT_SOURCE_ROOT / "Chase3D_4.png",
        "artsy_2000_20_chase_checkerboard_horizon.png",
        "Chase Mode — Reflective Checkerboard Pursuit",
        "3d",
        "High-velocity software-rendered 3D pursuit across a rippling blue checkerboard plane with reflective geometric projectiles and skyline peaks.",
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
        WEB_ROOT / "tools" / "generated" / "artsy_2000_povray_pipeline_win95_1920x1080.png",
        "artsy_2000_povray_pipeline_win95_1920x1080.png",
        "POV-Ray 3.7 Export & Turntable Pipeline (Retro Win95 Desktop Mockup, 1920x1080)",
        "povray",
        False,
    ),
    (
        WEB_ROOT / "assets" / "povray_chase_spin.gif",
        "artsy_2000_povray_chase_spin.gif",
        "POV-Ray 3.7 Animated GIF Example — Chase Mode 360-Degree Turntable",
        "povray",
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
DEVELOPER:         Daniel M Sawitzki
PUBLISHER / LABEL: Buck-Fifty Innovation Labs
LOCATION:          Santa Rosa, CA, USA
RELEASE DATE:      February 2027
PRICE:             $1.50 USD
PLATFORM:          Windows 10 / 11 (64-bit) — Steam
STEAM STORE:       https://store.steampowered.com/app/5641470/
GENRE:             Multi-Genre Retro Arcade / 1990s Sci-Fi Satire /
                   Software-Raytraced Anthology & Mystery
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
A $1.50 multi-genre 1990s retro-futuristic arcade escape — and a deep rabbit
hole of cross-media Buck-Fifty Labs secrets — built entirely in pure C++17 CPU
software rendering (zero GPU), spanning 11 playable genres, 74 FMV broadcasts,
and one-click POV-Ray 3.7 export of both user-built and live 3D scenes into
multi-themed MP4 and animated GIF turntables.

--------------------------------------------------------------------------------
SHORT DESCRIPTION
--------------------------------------------------------------------------------
Artsy_2000 casts you as Subject 13 inside Buck-Fifty Innovation Labs' Sub-Level 4
— a satirical 1996 Salt Lake City cognitive research bunker promising a $1.50 per
diem and one personal pan pizza voucher. Built from scratch in pure C++17 and
Win32/GDI with zero GPU dependencies, the game shifts seamlessly across 11
narratively connected retro genres, 5 high-pressure CRT interrogations, and 74
archival FMV clips. Beneath its atmospheric arcade gauntlet lies an unusually
deep well of discoverable secrets reaching far into the Buck-Fifty Labs universe
— from unlockable archival TV spots to clues concealed across the companion
1996 website, Volunteer Manual, and graphic novels, including mysteries that can
only be cracked by pairing the game and website together. Players can also
export both their own 3D sculptures and live 3D gameplay scenes directly into
POV-Ray 3.7 scripts and double-click a bundled script to render 360-degree MP4
videos or animated GIFs across 10 color and lighting schemes.

--------------------------------------------------------------------------------
KEY FEATURES
--------------------------------------------------------------------------------
* 11 Narratively Connected Genres + 5 CRT Interrogations:
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

* A Deep Well of Secrets & Cross-Media Buck-Fifty Lore:
  Some discoveries sit just off the main corridor; others require genuine
  persistence. Players who dig past the primary escape uncover unlockable
  archival TV spots, anomalous broadcast fragments, and mysteries woven across
  the game's accompanying artifacts — the 1996 corporate website
  (buckfiftylabs.com), the 46-page Volunteer Manual, and the graphic novels —
  including hidden content that can only be accessed by using the game and the
  website in tandem. How deep Buck-Fifty Labs really goes depends on how far
  you are willing to look.

* Export User-Created & Live 3D Gameplay Scenes to POV-Ray 3.7 (MP4 & GIF):
  Pressing X exports both player-sculpted 3D creations in Ascend Mode (complete
  with Eric Haines' Standard Procedural Database generator) and live 3D gameplay
  scenes (Chase, The Rise, Edge Computing, Blueprint) straight into genuine
  POV-Ray 3.7 scripts (scene.pov) paired with a zero-setup render.bat launcher.
  Double-clicking render.bat opens an interactive picker for output format
  (MP4, animated GIF, or both) and 10 embedded color/lighting schemes (Original
  Studio, Creme Brulee, Lavender Haze, Matcha Pistachio, Cherry Blossom,
  Blueberry Cyanotype, Blood Orange Valenciana, Espresso Sepia, Peppermint Neon,
  and Midnight Licorice), then runs POV-Ray headless and outputs shareable 360-
  degree raytraced animations.

* 100% Pure CPU Software Rendering (Zero GPU Required):
  Every 3D raytraced reflection, Mode-7 ground plane, CRT curvature shader, and
  scanline filter runs natively on multi-threaded CPU silicon via Win32/GDI —
  no DirectX, OpenGL, or Vulkan required.

* 74 Archival FMV Clips & 50 In-World TV Breaks:
  Full-motion video broadcasts starring Clinical Director Dr. Brad Vance,
  satirical 1990s commercials (Slab-O-Bull, Fissi-Efficient, Omni-Smile, Model
  B-50), unlockable TV spots, and hidden VHS anomalies.

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
Daniel M Sawitzki / Buck-Fifty Innovation Labs explicitly grants press, reviewers,
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

Copyright (c) 2026-2027 Daniel M Sawitzki / Buck-Fifty Innovation Labs.
"""


FACT_SHEET_MD = """# Artsy_2000 — Official Press Fact Sheet

| Field | Details |
| :--- | :--- |
| **Title** | Artsy_2000 |
| **Developer** | Daniel M Sawitzki |
| **Publisher / Label** | Buck-Fifty Innovation Labs |
| **Location** | Santa Rosa, CA, USA |
| **Release Date** | February 2027 |
| **Price** | $1.50 USD |
| **Platform** | Windows 10 / 11 (64-bit) via Steam |
| **Steam Store** | https://store.steampowered.com/app/5641470/ |
| **Genre** | Multi-Genre Retro Arcade / 1990s Sci-Fi Satire / Software-Raytraced Anthology & Mystery |
| **Players** | Single-Player + Local 2-Player PvP (*Them Apples*) |
| **Input** | Full Keyboard, Mouse & Gamepad Support |
| **Steam Features** | 153 Steam Achievements, Steam Cloud |
| **Tech Stack** | Custom C++17 & Win32/GDI Multi-Threaded CPU Software Renderer (0% GPU) |
| **Original Soundtrack** | 6 Synthwave Tracks by [Holon](https://holon-subatomic-audio.bandcamp.com/) |
| **Official Website** | https://buckfiftylabs.com/ |
| **Press Kit** | https://buckfiftylabs.com/press/ |
| **Press Contact / Keys** | info@buckfiftylabs.com |

## One-Line Pitch
A $1.50 multi-genre 1990s retro-futuristic arcade escape — and a deep well of cross-media Buck-Fifty Labs secrets — built entirely in pure C++17 CPU software rendering (zero GPU), spanning 11 playable genres, 74 FMV broadcasts, and one-click POV-Ray 3.7 export of both user-created and live 3D gameplay scenes into multi-themed MP4/GIF turntables.

## Short Description
*Artsy_2000* casts you as Subject 13 inside Buck-Fifty Innovation Labs' Sub-Level 4 — a satirical 1996 Salt Lake City cognitive research bunker promising a $1.50 per diem and one personal pan pizza voucher. Built from scratch in pure C++17 and Win32/GDI with zero GPU dependencies, the game shifts seamlessly across 11 narratively connected retro genres, 5 timed CRT interrogations, and 74 archival FMV clips. Beneath its atmospheric arcade anthology lies an unexpectedly deep well of secrets reaching into the hidden corners of the Buck-Fifty Labs universe — from unlockable archival TV spots to clues embedded across the companion 1996 website, Volunteer Manual, and graphic novels, including mysteries that only unlock when game and website are investigated together. Players can also export both their own 3D sculptures and live 3D gameplay scenes into genuine POV-Ray 3.7 scripts and double-click a bundled script to render 360° MP4 videos or animated GIFs across 10 color and lighting schemes.

## Key Features
- **11 Narratively Connected Campaign Modes + 5 Staff Interrogations:** Chase Mode, Them Apples (CRT Snake + Local 2P PvP), Iso-Lation Ward (14×14 isometric raytraced arena), Brain Surgery (*Just Let Go* 90s point-and-click), The Rise (CPU raytracer + physics), The Labyrinth (wireframe maze + ECG vitals), Edge Computing (3D aluminum pipe hypercube), Grid-Locked & Pepperoni-Shocked (Utah USGS satellite triangulation), Blueprint Mode (CAD schematic + 3D lobby tour), Parking Lot Stealth (with Dark Ages oxygen hallucination), and Pizza Delivery Race (OutRun-style desert highway).
- **Deep Well of Secrets & Cross-Media Buck-Fifty Lore:** From readily spotted curiosities to buried facility lore, *Artsy_2000* rewards curious investigators with unlockable archival TV spots, secrets tucked into the companion 1996 website (`buckfiftylabs.com`), the 46-page Volunteer Manual, and the graphic novels — plus hidden revelations that can only be discovered by combining the game and website together.
- **POV-Ray 3.7 Export & One-Click Multi-Lighting MP4/GIF Pipeline:** Export both player-built 3D sculptures (*Ascend Mode* + Eric Haines' SPD generator) and live 3D gameplay scenes (*Chase*, *The Rise*, *Edge Computing*, *Blueprint*) into authentic `scene.pov` raytracing scripts. Double-clicking the generated `render.bat` lets players pick MP4, animated GIF, or both — plus **10 lighting & color schemes** (*Original Studio*, *Crème Brûlée*, *Lavender Haze*, *Matcha Pistachio*, *Cherry Blossom*, *Blueberry Cyanotype*, *Blood Orange Valenciana*, *Espresso Sepia*, *Peppermint Neon*, and *Midnight Licorice*) — and runs POV-Ray headless to output smooth 360° animations.
- **Zero GPU Dependencies:** Multi-threaded CPU software rasterization, Phong raytracing, and CRT post-processing written in pure C++17 & Win32/GDI.
- **74 Archival FMV Clips (50 TV Breaks):** Hosted by Clinical Director Dr. Brad Vance with satirical 1996 commercials, unlockable TV spots, and hidden VHS anomalies.
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

All screenshots, logos, key art, POV-Ray renders, pipeline mockups, and text
contained in this archive are cleared for editorial, review, news, streaming,
YouTube thumbnail, and event/festival coverage of Artsy_2000 (Daniel M Sawitzki / Buck-Fifty
Innovation Labs).

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


def validate_screenshot_sources():
    """Verify every curated screenshot exists, is native 1920x1200 (never _1920x1080), and has unique names."""
    seen_src = set()
    seen_dst = set()
    for src, dst_name, *_ in SCREENSHOT_SPECS:
        if "_1920x1080" in src.name.lower():
            raise ValueError(f"Disallowed _1920x1080 variant in SCREENSHOT_SPECS: {src.name}")
        if not src.exists():
            raise FileNotFoundError(f"Missing curated screenshot source: {src}")
        with Image.open(src) as im:
            if im.size != (1920, 1200):
                raise ValueError(
                    f"Unexpected resolution for {src.name}: {im.size} (expected 1920x1200)"
                )
        if src.name in seen_src:
            raise ValueError(f"Duplicate source screenshot in SCREENSHOT_SPECS: {src.name}")
        if dst_name in seen_dst:
            raise ValueError(f"Duplicate destination filename in SCREENSHOT_SPECS: {dst_name}")
        seen_src.add(src.name)
        seen_dst.add(dst_name)


def build():
    validate_screenshot_sources()

    MEDIA_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_BRANDING_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Clear old generated files in target folders so re-runs stay clean
    for d in (MEDIA_SCREENSHOTS_DIR, MEDIA_BRANDING_DIR, MEDIA_THUMBS_DIR, DOWNLOADS_DIR):
        for child in d.iterdir():
            if child.is_file():
                child.unlink()

    manifest = {"screenshots": [], "branding": [], "downloads": {}}

    # 1. Copy curated screenshots + generate lightweight web thumbnails (640x400 JPG)
    #    ZIPs and direct downloads always serve the untouched lossless 1920x1200 PNGs.
    for src, dst_name, title, category, caption in SCREENSHOT_SPECS:
        if not src.exists():
            raise FileNotFoundError(f"Missing screenshot source: {src}")
        dst = MEDIA_SCREENSHOTS_DIR / dst_name
        shutil.copy2(src, dst)
        thumb_name = Path(dst_name).stem + ".jpg"
        thumb_dst = MEDIA_THUMBS_DIR / thumb_name
        with Image.open(dst) as im:
            w, h = im.size
            thumb = im.convert("RGB").resize((640, 400), Image.Resampling.LANCZOS)
            thumb.save(thumb_dst, format="JPEG", quality=84, optimize=True, progressive=True)
        size = dst.stat().st_size
        manifest["screenshots"].append({
            "file": f"media/screenshots/{dst_name}",
            "thumb": f"media/thumbs/{thumb_name}",
            "filename": dst_name,
            "source": src.name,
            "title": title,
            "category": category,
            "caption": caption,
            "width": w,
            "height": h,
            "bytes": size,
            "sizeLabel": fmt_size(size),
        })

    # 2. Copy curated branding / logos / key art / renders (+ preview thumb for heavy PNGs)
    for src, dst_name, title, kind, transparent in BRANDING_SPECS:
        if not src.exists():
            raise FileNotFoundError(f"Missing branding source: {src}")
        dst = MEDIA_BRANDING_DIR / dst_name
        shutil.copy2(src, dst)
        with Image.open(dst) as im:
            w, h = im.size
            # Generate crisp web preview JPEG for the 1920x1080 Win95 pipeline mockup & large non-alpha PNG banners
            if dst_name in (
                "artsy_2000_povray_pipeline_win95_1920x1080.png",
                "artsy_2000_keyart_banner_1920x622.png",
            ):
                tw = 1200
                th = max(1, round(h * (tw / w)))
                prev = im.convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
                prev.save(
                    MEDIA_THUMBS_DIR / (Path(dst_name).stem + ".jpg"),
                    format="JPEG",
                    quality=88,
                    optimize=True,
                    progressive=True,
                )
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
    for item in manifest["branding"]:
        if item["kind"] == "povray":
            print(f"  POVRAY: {item['filename']} -> {item['width']}x{item['height']} ({item['sizeLabel']})")


if __name__ == "__main__":
    build()
