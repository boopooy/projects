"""Apply common image filters and download the processed image."""

from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


st.set_page_config(page_title="Image Filter Studio", page_icon="🧙", layout="wide")


def apply_filter(image: Image.Image, filter_name: str) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")

    if filter_name == "grayscale":
        return image.convert("L").convert("RGB")
    if filter_name == "sepia":
        sepia_pixels = image.load()
        result = Image.new("RGB", image.size)
        for y in range(image.height):
            for x in range(image.width):
                red, green, blue = sepia_pixels[x, y]
                result.putpixel((x, y), (
                    min(255, round(red * 0.393 + green * 0.769 + blue * 0.189)),
                    min(255, round(red * 0.349 + green * 0.686 + blue * 0.168)),
                    min(255, round(red * 0.272 + green * 0.534 + blue * 0.131)),
                ))
        return result
    if filter_name == "blur":
        return image.filter(ImageFilter.GaussianBlur(radius=3))
    if filter_name == "contrast":
        return ImageEnhance.Contrast(image).enhance(2.0)
    if filter_name == "invert":
        return ImageOps.invert(image)
    return image


def download_image(image: Image.Image, filter_name: str) -> bytes:
    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    output.seek(0)
    return output.getvalue()


st.title("🧙 Image Filter Studio")
st.write("이미지를 업로드해 필터를 선택하고, 결과 이미지를 바로 다운로드해보세요.")

uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg", "webp"])
filter_name = st.selectbox(
    "필터 선택",
    ["grayscale", "sepia", "blur", "contrast", "invert"],
    format_func=lambda value: {
        "grayscale": "흑백",
        "sepia": "세피아",
        "blur": "블러",
        "contrast": "대비 강화",
        "invert": "색상 반전",
    }[value],
)

if uploaded_file is None:
    st.info("이미지를 선택해 주세요.")
else:
    try:
        with Image.open(uploaded_file) as source_image:
            original = ImageOps.exif_transpose(source_image).convert("RGB")
            filtered = apply_filter(original, filter_name)
    except (OSError, ValueError) as error:
        st.error(f"이미지를 처리할 수 없습니다: {error}")
    else:
        original_col, filtered_col = st.columns(2)
        with original_col:
            st.subheader("원본 이미지")
            st.image(original, use_container_width=True)

        with filtered_col:
            st.subheader("필터 적용 결과")
            st.image(filtered, use_container_width=True)

        image_bytes = download_image(filtered, filter_name)
        file_name = f"{Path(uploaded_file.name).stem}_{filter_name}.png"
        st.download_button(
            "필터 적용 이미지 다운로드",
            data=image_bytes,
            file_name=file_name,
            mime="image/png",
            type="primary",
            use_container_width=True,
        )

st.divider()
if st.button(
    "이미지 색상 추출기 이동",
    key="go_to_image_color_from_filter",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/02_image_color.py")
