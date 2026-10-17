# ImageResizer — Sharp Desktop Wallpaper Resizer & AI Upscaler

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://imageresizer-uxz8jkawxmrzwh3agjkedc.streamlit.app/)

**Live Web Demo:** [https://imageresizer-uxz8jkawxmrzwh3agjkedc.streamlit.app/](https://imageresizer-uxz8jkawxmrzwh3agjkedc.streamlit.app/)

**ImageResizer** is a lightweight tool (CLI & Web UI) that converts images from the internet or your local machine into crisp, distortion-free desktop wallpapers. It preserves image sharpness whether you are upscaling a small image or downscaling a high-resolution photo.

## ✨ Key Features

- **Flexible Input:** Load images directly from an HTTP/HTTPS URL or upload from your local disk.
- **Smart Aspect-Ratio Cropping:** Center-crops images to match your target desktop resolution (Full HD, 2K QHD, 4K UHD, Ultrawide, 16:10, or custom dimensions) before scaling—no stretching or wasted GPU cycles.
- **AI Super-Resolution Upscaling:** Automatically downloads and runs [`Real-ESRGAN-ncnn-vulkan`](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan) (`realesrgan-x4plus`, `realesrgan-x4plus-anime`, `realesr-animevideov3`) when the source image is smaller than the target resolution.
- **High-Precision Downscaling:** Uses `LANCZOS` resampling paired with `UnsharpMask` micro-contrast restoration to keep fine details razor-sharp when shrinking large images.
- **Cross-Platform:** Automatically fetches the appropriate `realesrgan-ncnn-vulkan` binary for Windows, Linux, or macOS on first run.

---

## 🚀 Quick Start

### 1. Try Online (No Installation Required)
Open the deployed Streamlit Web App:
👉 **[https://imageresizer-uxz8jkawxmrzwh3agjkedc.streamlit.app/](https://imageresizer-uxz8jkawxmrzwh3agjkedc.streamlit.app/)**

### 2. Run Locally (Web UI or CLI)

Clone the repository and install dependencies with [`uv`](https://docs.astral.sh/uv/):

```bash
git clone <your-repo-url>
cd ImageResizer
uv sync
```

#### Launch the Web UI
```bash
uv run streamlit run streamlit_app.py
```

#### Use the Command Line Interface (CLI)
```bash
# Resize an image from a URL (automatically detects your screen resolution on Windows)
uv run imageresizer "https://images.unsplash.com/photo-..." -o wallpaper.png

# Resize a local image to 2K (2560x1440) using the anime model
uv run imageresizer "./my_image.jpg" -o wallpaper.png -W 2560 -H 1440 -m realesrgan-x4plus-anime
```

---

## 🙏 Acknowledgements & Recommended Upstream Repository

The AI super-resolution capability in this project is powered by **[xinntao/Real-ESRGAN-ncnn-vulkan](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan)** — the official NCNN/Vulkan C++ implementation of [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN).

If you need standalone, fast, cross-platform AI image/video upscaling on Intel, AMD, or Nvidia GPUs without heavy Python/PyTorch dependencies, we highly recommend checking out and starring **[xinntao/Real-ESRGAN-ncnn-vulkan](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan)**!
