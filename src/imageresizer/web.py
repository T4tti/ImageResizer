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

SPEED_MODES = {
    "⚡ Siêu tốc — Lanczos + Smart Sharpen (< 0.5s, khuyên dùng trên Web)": (False, "realesr-animevideov3"),
    "🚀 AI Nhanh — Real-ESRGAN Compact (realesr-animevideov3)": (True, "realesr-animevideov3"),
    "💎 AI Tối đa — Ảnh thực tế (realesrgan-x4plus)": (True, "realesrgan-x4plus"),
    "🎨 AI Tối đa — Anime / Art (realesrgan-x4plus-anime)": (True, "realesrgan-x4plus-anime"),
}


@st.cache_resource
def get_processor() -> ImageProcessor:
    return ImageProcessor()


@st.cache_data(show_spinner=False, max_entries=12)
def process_cached(
    source_data: str | bytes,
    target_w: int,
    target_h: int,
    model_name: str,
    use_ai: bool,
) -> tuple[bytes, tuple[int, int], bytes, tuple[int, int]]:
    processor = get_processor()
    orig_img = processor.load_image(source_data)
    final_img = processor.process_image(
        orig_img,
        target_w=target_w,
        target_h=target_h,
        model=model_name,
        use_ai=use_ai,
    )
    orig_buf = io.BytesIO()
    orig_img.save(orig_buf, format="JPEG", quality=85)
    final_buf = io.BytesIO()
    final_img.save(final_buf, format="PNG", compress_level=2)
    return orig_buf.getvalue(), orig_img.size, final_buf.getvalue(), final_img.size


def run_web() -> None:
    st.set_page_config(page_title="Desktop Wallpaper Resizer (Real-ESRGAN)", layout="wide")
    st.title("Desktop Wallpaper Resizer & AI Upscaler")
    st.caption("Tải ảnh từ Internet hoặc máy tính, tự động căn khung và giữ độ sắc nét.")

    with st.sidebar:
        st.header("Cấu hình đầu ra")
        preset_label = st.selectbox("Độ phân giải màn hình", list(PRESETS.keys()), index=0)
        if PRESETS[preset_label] is None:
            col_w, col_h = st.columns(2)
            target_w = int(col_w.number_input("Chiều rộng (px)", min_value=320, max_value=7680, value=1920, step=10))
            target_h = int(col_h.number_input("Chiều cao (px)", min_value=240, max_value=4320, value=1080, step=10))
        else:
            target_w, target_h = PRESETS[preset_label]

        mode_label = st.selectbox("Chế độ xử lý & Tốc độ", list(SPEED_MODES.keys()), index=0)
        use_ai, model_name = SPEED_MODES[mode_label]
        if use_ai:
            st.info("💡 Lưu ý: Trên Streamlit Cloud (không có GPU rời), chế độ AI chạy bằng CPU nên sẽ mất vài giây đến ~30s.")

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
        with st.spinner(f"Đang xử lý ảnh về {target_w}x{target_h}..."):
            try:
                st.session_state["last_result"] = process_cached(
                    source_input, target_w, target_h, model_name, use_ai
                )
            except Exception as exc:
                st.error(f"Lỗi khi xử lý ảnh: {exc}")

    if "last_result" in st.session_state:
        orig_bytes, (orig_w, orig_h), final_bytes, (final_w, final_h) = st.session_state["last_result"]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Ảnh gốc ({orig_w}x{orig_h})")
            st.image(orig_bytes, use_container_width=True)
        with col2:
            st.subheader(f"Ảnh Desktop ({final_w}x{final_h})")
            st.image(final_bytes, use_container_width=True)

        st.download_button(
            label=f"Tải xuống hình nền ({final_w}x{final_h} PNG)",
            data=final_bytes,
            file_name=f"wallpaper_{final_w}x{final_h}.png",
            mime="image/png",
            type="primary",
        )


if __name__ == "__main__":
    run_web()
