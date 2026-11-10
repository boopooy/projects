"""Extract five dominant colors from an uploaded image."""

import numpy as np
import streamlit as st
from PIL import Image, ImageOps


st.set_page_config(page_title="Image Color Extractor", page_icon="🖼️", layout="wide")


def extract_dominant_colors(image: Image.Image, count: int = 5) -> list[tuple[int, int, int]]:
    rgb_image = ImageOps.exif_transpose(image).convert("RGB")
    max_size = 120
    width, height = rgb_image.size
    scale = min(max_size / width, max_size / height, 1.0)
    resized = rgb_image.resize((max(1, round(width * scale)), max(1, round(height * scale))))

    pixels = np.asarray(resized).reshape(-1, 3)
    if len(pixels) == 0:
        return [(0, 0, 0)]

    quantized = Image.fromarray(pixels).quantize(colors=max(count, 8), method=Image.MEDIANCUT)
    palette = quantized.getpalette()[: 3 * 16]
    color_counts = quantized.getcolors()
    ranked = sorted(color_counts, key=lambda item: item[0], reverse=True)
    colors = []
    for _, index in ranked:
        color = tuple(palette[index * 3 : index * 3 + 3])
        if color not in colors:
            colors.append(color)
        if len(colors) == count:
            break

    if len(colors) < count:
        unique_pixels = np.unique(pixels, axis=0)
        for color in unique_pixels:
            color_tuple = tuple(int(channel) for channel in color)
            if color_tuple not in colors:
                colors.append(color_tuple)
            if len(colors) == count:
                break

    return colors[:count]


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "%02x%02x%02x" % rgb


st.title("🖼️ Image Color Extractor")
st.write("이미지를 업로드하면 이미지의 주요 색상을 5개 추출해 컬러 테마를 보여드세요.")

uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file is None:
    st.info("이미지를 선택해 주세요.")
else:
    try:
        with Image.open(uploaded_file) as source_image:
            image = ImageOps.exif_transpose(source_image).convert("RGB")
            extracted_colors = extract_dominant_colors(image)
    except (OSError, ValueError) as error:
        st.error(f"이미지를 처리할 수 없습니다: {error}")
    else:
        preview_col, palette_col = st.columns([1.1, 0.9])
        with preview_col:
            st.subheader("업로드 이미지")
            st.image(image, caption="원본 이미지", use_container_width=True)

        with palette_col:
            st.subheader("주요 색상 5개")
            for index, color in enumerate(extracted_colors, start=1):
                hex_code = rgb_to_hex(color)
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 12px; margin: 10px 0;">
                        <div style="width: 44px; height: 44px; background: {hex_code}; border-radius: 10px; border: 1px solid #ddd;"></div>
                        <div>
                            <strong>{index}색</strong>
                            <div style="font-family: monospace; color: #555;">{hex_code.upper()} · RGB {color}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.subheader("색상 테마")
        theme_columns = st.columns(3)
        theme_colors = [extracted_colors[0], extracted_colors[1] if len(extracted_colors) > 1 else extracted_colors[0], extracted_colors[-1]]
        for column, (label, color) in zip(theme_columns, zip(["기본색", "보조색", "배경색"], theme_colors)):
            with column:
                hex_code = rgb_to_hex(color)
                st.markdown(
                    f"""
                    <div style="border: 1px solid #e5e5e5; border-radius: 14px; overflow: hidden;">
                        <div style="height: 88px; background: {hex_code};"></div>
                        <div style="padding: 14px; background: white;">
                            <strong>{label}</strong>
                            <div style="font-family: monospace; margin-top: 5px;">{hex_code.upper()}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

st.divider()
if st.button(
    "색상 선택기 이동",
    key="go_to_color_picker",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/01_color_picker.py")
