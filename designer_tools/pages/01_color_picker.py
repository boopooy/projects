"""RGB color picker with a generated designer color theme."""

import colorsys

import streamlit as st


st.set_page_config(page_title="RGB Color Picker", page_icon="🎨", layout="wide")


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "%02x%02x%02x" % rgb


def classify_color_family(rgb: tuple[int, int, int]) -> str:
    hue, saturation, _ = colorsys.rgb_to_hsv(*(channel / 255 for channel in rgb))

    if saturation < 0.12:
        return "무채색 계열"
    if hue < 15 / 360 or hue >= 345 / 360:
        return "빨강 계열"
    if hue < 45 / 360:
        return "노랑 계열"
    if hue < 75 / 360:
        return "파랑 계열"
    if hue < 165 / 360:
        return "초록 계열"
    return "보라 계열"


def mix_color(rgb: tuple[int, int, int], target: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(start + (end - start) * amount) for start, end in zip(rgb, target))


def create_theme(rgb: tuple[int, int, int]) -> dict[str, tuple[int, int, int]]:
    hue, saturation, value = colorsys.rgb_to_hsv(*(channel / 255 for channel in rgb))
    complementary_hue = (hue + 0.5) % 1.0
    secondary_rgb = tuple(
        round(channel * 255)
        for channel in colorsys.hsv_to_rgb(complementary_hue, saturation, value)
    )
    background_rgb = mix_color(rgb, (255, 255, 255), 0.72)
    return {
        "primary": rgb,
        "secondary": secondary_rgb,
        "background": background_rgb,
    }


st.title("🎨 RGB Color Picker")
st.write("슬라이더를 이동해 색상을 선택하고 생성된 테마를 확인해보세요.")

col1, col2 = st.columns([1, 1.5])
with col1:
    red = st.slider("Red", 0, 255, value=108)
    green = st.slider("Green", 0, 255, value=92)
    blue = st.slider("Blue", 0, 255, value=231)
    selected_rgb = (red, green, blue)

with col2:
    selected_hex = rgb_to_hex(selected_rgb)
    color_family = classify_color_family(selected_rgb)
    st.markdown(
        f"""
        <div style="
            background: {selected_hex};
            color: {'#ffffff' if sum(selected_rgb) / 3 < 140 else '#111111'};
            padding: 48px 24px;
            border-radius: 18px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
        ">
            <div style="font-size: 14px; letter-spacing: 1px; opacity: 0.8;">SELECTED COLOR</div>
            <div style="font-size: 32px; font-weight: 700; margin-top: 8px;">{selected_hex.upper()}</div>
            <div style="font-size: 18px; margin-top: 8px;">RGB {selected_rgb}</div>
            <div style="font-size: 16px; font-weight: 700; margin-top: 12px;">{color_family}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("생성된 컬러 테마")
theme = create_theme(selected_rgb)
columns = st.columns(3)
for column, (name, color) in zip(columns, theme.items()):
    with column:
        color_hex = rgb_to_hex(color)
        st.markdown(
            f"""
            <div style="border: 1px solid #e5e5e5; border-radius: 14px; overflow: hidden;">
                <div style="height: 92px; background: {color_hex};"></div>
                <div style="padding: 16px; background: white;">
                    <strong>{name.title()}</strong>
                    <div style="font-family: monospace; margin-top: 5px;">{color_hex.upper()}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
if st.button("다시 시작", type="secondary", key="reset_color_picker"):
    st.rerun()

if st.button(
    "이미지 색상 추출기 이동",
    key="go_to_image_color",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/02_image_color.py")
