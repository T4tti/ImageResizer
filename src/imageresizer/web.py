import io
import streamlit as st
from imageresizer.app import ImageProcessor

PRESETS = {
    "Full HD (1920 x 1080)": (1920, 1080),
    "2K QHD (2560 x 1440)": (2560, 1440),
    "4K UHD (3840 x 2160)": (3840, 2160),
    "Ultrawide WQHD (3440 x 1440)": (3440, 1440),
    "MacBook 16:10 (2560 x 1600)": (2560, 1600),
    "Tùy chỉnh (Custom)": None,
}

MODELS = {
    "Ảnh thực tế / Chung (realesrgan-x4plus)": "realesrgan-x4plus",
    "Anime / Digital Art (realesrgan-x4plus-anime)": "realesrgan-x4plus-anime",
    "Anime nhanh (realesr-animevideov3)": "realesr-animevideov3",
}


@st.cache_resource
def get_processor() -> ImageProcessor:
    return ImageProcessor()


def run_web() -> None:
    st.set_page_config(page_title="Desktop Wallpaper Resizer (Real-ESRGAN)", layout="wide")
    st.title("Desktop Wallpaper Resizer & AI Upscaler")
    st.caption("Tải ảnh từ Internet hoặc máy tính, tự động căn khung và giữ độ sắc nét bằng Real-ESRGAN.")

    with st.sidebar:
        st.header("Cấu hình đầu ra")
        preset_label = st.selectbox("Độ phân giải màn hình", list(PRESETS.keys()), index=0)
        if PRESETS[preset_label] is None:
            col_w, col_h = st.columns(2)
            target_w = int(col_w.number_input("Chiều rộng (px)", min_value=320, max_value=7680, value=1920, step=10))
            target_h = int(col_h.number_input("Chiều cao (px)", min_value=240, max_value=4320, value=1080, step=10))
        else:
            target_w, target_h = PRESETS[preset_label]

        model_label = st.selectbox("Mô hình AI (Real-ESRGAN)", list(MODELS.keys()), index=0)
        model_name = MODELS[model_label]

    tab_url, tab_upload = st.tabs(["Tải từ URL Internet", "Upload từ máy tính"])
    source_input = None

    with tab_url:
        url = st.text_input("Nhập link ảnh trực tiếp (HTTP/HTTPS):", placeholder="https://images.unsplash.com/...")
        if url.strip():
            source_input = url.strip()

    with tab_upload:
        uploaded = st.file_uploader("Chọn file ảnh (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp", "bmp"])
        if uploaded is not None:
            source_input = uploaded.getvalue()

    if st.button("Xử lý ảnh", type="primary", disabled=source_input is None):
        processor = get_processor()
        with st.spinner(f"Đang xử lý ảnh về {target_w}x{target_h} với {model_name}..."):
            try:
                orig_img = processor.load_image(source_input)
                final_img = processor.process_image(
                    orig_img, target_w=target_w, target_h=target_h, model=model_name
                )
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"Ảnh gốc ({orig_img.width}x{orig_img.height})")
                    st.image(orig_img, use_container_width=True)
                with col2:
                    st.subheader(f"Ảnh Desktop ({final_img.width}x{final_img.height})")
                    st.image(final_img, use_container_width=True)

                buf = io.BytesIO()
                final_img.save(buf, format="PNG")
                st.download_button(
                    label=f"Tải xuống hình nền ({target_w}x{target_h} PNG)",
                    data=buf.getvalue(),
                    file_name=f"wallpaper_{target_w}x{target_h}.png",
                    mime="image/png",
                    type="primary",
                )
            except Exception as exc:
                st.error(f"Lỗi khi xử lý ảnh: {exc}")


if __name__ == "__main__":
    run_web()
