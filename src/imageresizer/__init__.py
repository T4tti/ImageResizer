import argparse
from imageresizer.app import ImageProcessor, get_screen_resolution


def main() -> None:
    default_w, default_h = get_screen_resolution()
    parser = argparse.ArgumentParser(
        description="Resize internet or local images into sharp desktop wallpapers using Real-ESRGAN."
    )
    parser.add_argument("source", help="Image URL (http/https) or local file path")
    parser.add_argument("-o", "--output", default="wallpaper.png", help="Output file path (default: wallpaper.png)")
    parser.add_argument("-W", "--width", type=int, default=default_w, help=f"Target width (default: {default_w})")
    parser.add_argument("-H", "--height", type=int, default=default_h, help=f"Target height (default: {default_h})")
    parser.add_argument(
        "-m",
        "--model",
        default="realesrgan-x4plus",
        choices=[
            "realesrgan-x4plus",
            "realesrgan-x4plus-anime",
            "realesr-animevideov3",
        ],
        help="Real-ESRGAN model name (default: realesrgan-x4plus)",
    )
    args = parser.parse_args()
    processor = ImageProcessor()
    out = processor.process(
        source=args.source,
        output_path=args.output,
        target_w=args.width,
        target_h=args.height,
        model=args.model,
    )
    print(f"Saved sharp wallpaper ({args.width}x{args.height}) to: {out.resolve()}")
