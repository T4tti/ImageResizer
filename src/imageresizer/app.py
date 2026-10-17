import ctypes
import io
import os
import platform
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, ImageFilter, ImageOps

REALESRGAN_RELEASES = {
    "Windows": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/"
        "v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip",
        "realesrgan-ncnn-vulkan.exe",
    ),
    "Linux": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/"
        "v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip",
        "realesrgan-ncnn-vulkan",
    ),
    "Darwin": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/"
        "v0.2.5.0/realesrgan-ncnn-vulkan-20220424-macos.zip",
        "realesrgan-ncnn-vulkan",
    ),
}
DEFAULT_BIN_DIR = Path(__file__).resolve().parents[2] / "bin"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ImageResizer/0.1"


def get_screen_resolution() -> tuple[int, int]:
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        w, h = int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))
        if w > 0 and h > 0:
            return w, h
    except Exception:
        pass
    return 1920, 1080


class ImageProcessor:
    def __init__(self, bin_dir: str | Path | None = None) -> None:
        self.bin_dir = Path(bin_dir) if bin_dir else DEFAULT_BIN_DIR
        sys_name = platform.system()
        self.zip_url, self.bin_name = REALESRGAN_RELEASES.get(
            sys_name, REALESRGAN_RELEASES["Linux"]
        )
        self.exe_path = self.bin_dir / self.bin_name

    def ensure_binary(self) -> Path:
        if self.exe_path.exists():
            return self.exe_path
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        resp = requests.get(self.zip_url, headers={"User-Agent": USER_AGENT}, timeout=120)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(self.bin_dir)
        if not self.exe_path.exists():
            matches = list(self.bin_dir.rglob(self.bin_name))
            if not matches:
                raise FileNotFoundError(f"{self.bin_name} not found in release archive")
            self.exe_path = matches[0]
        if platform.system() != "Windows":
            os.chmod(self.exe_path, 0o755)
        return self.exe_path

    def download_image(self, url: str) -> Image.Image:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        with Image.open(io.BytesIO(resp.content)) as img:
            return ImageOps.exif_transpose(img).convert("RGB")

    def load_image(self, source: str | Path | bytes | io.BytesIO) -> Image.Image:
        if isinstance(source, (bytes, bytearray)):
            with Image.open(io.BytesIO(source)) as img:
                return ImageOps.exif_transpose(img).convert("RGB")
        if hasattr(source, "read"):
            with Image.open(source) as img:
                return ImageOps.exif_transpose(img).convert("RGB")
        s = str(source)
        parsed = urlparse(s)
        if parsed.scheme in ("http", "https"):
            return self.download_image(s)
        path = Path(source).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Local image file not found: {path}")
        with Image.open(path) as img:
            return ImageOps.exif_transpose(img).convert("RGB")

    def crop_to_aspect(self, img: Image.Image, target_w: int, target_h: int) -> Image.Image:
        src_w, src_h = img.size
        target_ratio = target_w / target_h
        src_ratio = src_w / src_h
        if abs(src_ratio - target_ratio) < 1e-4:
            return img
        if src_ratio > target_ratio:
            new_w = max(1, round(src_h * target_ratio))
            left = (src_w - new_w) // 2
            return img.crop((left, 0, left + new_w, src_h))
        new_h = max(1, round(src_w / target_ratio))
        top = (src_h - new_h) // 2
        return img.crop((0, top, src_w, top + new_h))

    def upscale(
        self, img: Image.Image, model: str = "realesrgan-x4plus", scale: int = 4
    ) -> Image.Image:
        try:
            exe = self.ensure_binary()
            with tempfile.TemporaryDirectory() as tmpdir:
                in_path = Path(tmpdir) / "input.png"
                out_path = Path(tmpdir) / "output.png"
                img.save(in_path, format="PNG")
                cmd = [
                    str(exe),
                    "-i",
                    str(in_path),
                    "-o",
                    str(out_path),
                    "-n",
                    model,
                    "-s",
                    str(scale),
                ]
                subprocess.run(cmd, cwd=str(exe.parent), check=True, capture_output=True, text=True)
                with Image.open(out_path) as out_img:
                    return out_img.convert("RGB")
        except (subprocess.CalledProcessError, OSError):
            # ponytail: fallback to Lanczos + UnsharpMask if cloud container lacks Vulkan driver
            res = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)
            return res.filter(ImageFilter.UnsharpMask(radius=1.5, percent=140, threshold=2))

    def resize_and_sharpen(self, img: Image.Image, target_w: int, target_h: int) -> Image.Image:
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        return img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=110, threshold=3))

    def process_image(
        self,
        source: str | Path | bytes | io.BytesIO | Image.Image,
        target_w: int = 1920,
        target_h: int = 1080,
        model: str = "realesrgan-x4plus",
    ) -> Image.Image:
        img = source.convert("RGB") if isinstance(source, Image.Image) else self.load_image(source)
        img = self.crop_to_aspect(img, target_w, target_h)
        while img.width < target_w or img.height < target_h:
            img = self.upscale(img, model=model, scale=4)
        return self.resize_and_sharpen(img, target_w, target_h)

    def process(
        self,
        source: str | Path,
        output_path: str | Path = "wallpaper.png",
        target_w: int = 1920,
        target_h: int = 1080,
        model: str = "realesrgan-x4plus",
    ) -> Path:
        img = self.process_image(source, target_w=target_w, target_h=target_h, model=model)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, quality=95)
        return out