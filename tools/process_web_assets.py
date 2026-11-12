import os
import shutil
from PIL import Image

def process_assets():
    web_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.abspath(os.path.join(web_dir, "..", "Artsy_2000"))
    base_dir = os.path.join(project_root, "tools")
    assets_dir = os.path.join(web_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    print(f"Target assets directory: {assets_dir}")

    # 1. Assemble rotating BF cube GIF (using 3D Z-buffered green CRT renderer)
    from generate_bf_cube_gif import generate_bf_cube_gif
    gif_path = os.path.join(assets_dir, "bf_cube_rotating.gif")
    generate_bf_cube_gif(gif_path)

    # 2. Convert rendered BMPs to PNG
    bmp_names = [
        "guts_decompression.bmp",
        "crt_terminal_boot.bmp",
        "pizza_race_screen.bmp",
        "labyrinth_screen.bmp",
        "parking_lot_screen.bmp",
        "parking_lot_hallucination.bmp",
        "interlude_green_crt.bmp"
    ]
    for b in bmp_names:
        src = os.path.join(base_dir, b)
        if os.path.exists(src):
            img = Image.open(src)
            out_png = os.path.join(assets_dir, os.path.splitext(b)[0] + ".png")
            img.save(out_png, "PNG")
            print(f"Converted {b} -> {out_png}")

    # 3. Copy source images from promo_video/source_images and assets/images
    promo_src_dir = os.path.join(project_root, "promo_video", "source_images")
    if os.path.exists(promo_src_dir):
        for f in os.listdir(promo_src_dir):
            if f.endswith((".jpg", ".png")):
                src_path = os.path.join(promo_src_dir, f)
                dst_path = os.path.join(assets_dir, f)
                shutil.copy2(src_path, dst_path)
                print(f"Copied promo asset: {f}")

    founder_src = os.path.join(project_root, "assets", "images", "ui", "founder.png")
    if os.path.exists(founder_src):
        shutil.copy2(founder_src, os.path.join(assets_dir, "founder.png"))
        print("Copied founder.png")

    # 4. Copy Parking Lot & Pizza Race assets
    diner_src = os.path.join(project_root, "assets", "images", "pizza_race", "gas_station_diner.png")
    if os.path.exists(diner_src):
        shutil.copy2(diner_src, os.path.join(assets_dir, "gas_station_diner.png"))
        print("Copied gas_station_diner.png")

    parking_sprites = ["scientist.png", "player_13.png", "pizza_car.png", "bubble_brain.png", "bubble_dollar.png", "bubble_pizza.png"]
    parking_src_dir = os.path.join(project_root, "assets", "images", "parking_lot")
    for s in parking_sprites:
        s_src = os.path.join(parking_src_dir, s)
        if os.path.exists(s_src):
            shutil.copy2(s_src, os.path.join(assets_dir, f"parking_{s}"))
            print(f"Copied parking sprite: {s} -> parking_{s}")

    print("All web assets processed successfully!")

if __name__ == "__main__":
    process_assets()

