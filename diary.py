import calendar
import json
from datetime import date
import os
import tempfile
import uuid

import pandas as pd
import streamlit as st


DIARY_FILE = "diary.csv"
SETTINGS_FILE = "settings.json"
WEATHER_OPTIONS = ["맑음", "흐림", "비", "눈", "바람"]
MOOD_OPTIONS = ["매우 좋음", "좋음", "보통", "슬픔", "화남", "피곤함"]
COLUMNS = ["날짜", "제목", "내용", "날씨", "작성자", "기분", "먹은 음식", "일기 ID"]
THEME_OPTIONS = ["파랑", "초록", "보라", "주황", "빨강"]
THEME_COLORS = {
    "파랑": "#2563eb",
    "초록": "#16a34a",
    "보라": "#7c3aed",
    "주황": "#ea580c",
    "빨강": "#dc2626",
}
DEFAULT_SETTINGS = {
    "author_name": "",
    "theme": THEME_OPTIONS[0],
    "last_viewed_date": None,
}
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    with open(SETTINGS_FILE, encoding="utf-8") as settings_file:
        settings = json.load(settings_file)
    if not isinstance(settings, dict):
        raise ValueError(f"{SETTINGS_FILE} must contain a JSON object")

    loaded_settings = DEFAULT_SETTINGS.copy()
    loaded_settings.update(settings)
    if loaded_settings["theme"] not in THEME_OPTIONS:
        loaded_settings["theme"] = THEME_OPTIONS[0]
    return loaded_settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, ensure_ascii=False, indent=2)


def save_diary(diary):
    for column in COLUMNS:
        if column not in diary.columns:
            diary[column] = ""
    ordered_columns = COLUMNS + [column for column in diary.columns if column not in COLUMNS]
    diary = diary[ordered_columns]

    temporary_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8-sig",
        newline="",
        dir=os.path.dirname(os.path.abspath(DIARY_FILE)),
        suffix=".tmp",
        delete=False,
    )
    try:
        with temporary_file:
            diary.to_csv(temporary_file, index=False)
        os.replace(temporary_file.name, DIARY_FILE)
    except Exception:
        if os.path.exists(temporary_file.name):
            os.remove(temporary_file.name)
        raise


def load_diary():
    if not os.path.exists(DIARY_FILE):
        return pd.DataFrame(columns=COLUMNS)

    try:
        diary = pd.read_csv(DIARY_FILE, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)

    original_columns = list(diary.columns)
    needs_migration = any(column not in diary.columns for column in COLUMNS)
    for column in COLUMNS:
        if column not in diary.columns:
            diary[column] = ""

    used_ids = set()
    for index, value in diary["일기 ID"].items():
        diary_id = "" if pd.isna(value) else str(value).strip()
        if not diary_id or diary_id in used_ids:
            diary_id = uuid.uuid4().hex
            diary.at[index, "일기 ID"] = diary_id
            needs_migration = True
        used_ids.add(diary_id)

    if len(diary) and (needs_migration or original_columns != list(diary.columns)):
        save_diary(diary)

    return diary.fillna("")


def diary_value(entry, column):
    value = entry.get(column, "")
    return "" if pd.isna(value) else str(value)


def normalized_date(value):
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


settings = load_settings()
last_viewed_date = settings["last_viewed_date"]
settings["last_viewed_date"] = date.today().strftime("%Y-%m-%d")
save_settings(settings)

with st.sidebar:
    st.header("설정")
    author_name = st.text_input("작성자 이름", value=settings["author_name"])
    theme = st.selectbox(
        "테마 색상",
        THEME_OPTIONS,
        index=THEME_OPTIONS.index(settings["theme"]),
    )
    if theme != settings["theme"]:
        settings["theme"] = theme
        save_settings(settings)
    if st.button("저장", key="save_settings"):
        settings["author_name"] = author_name
        settings["theme"] = theme
        save_settings(settings)
        st.success("설정이 저장되었어요!")
    selected_page = st.radio("메뉴", ["일기장", "달력"], key="selected_page")

st.markdown(
    f"""
    <div style="background-color: {THEME_COLORS[theme]}; color: white;
                padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        오늘의 테마: {theme}
    </div>
    """,
    unsafe_allow_html=True,
)
if st.session_state.get("flash_message"):
    st.success(st.session_state.pop("flash_message"))

diary = load_diary()
if selected_page == "일기장":
    st.title("📔 나의 일기장")
    with st.form("new_diary_form"):
        title = st.text_input("제목")
        content = st.text_area("내용", height=150)
        weather = st.selectbox("오늘의 날씨", WEATHER_OPTIONS)
        mood = st.selectbox("오늘의 기분", MOOD_OPTIONS, index=2)
        food = st.text_input("오늘 먹은 음식", placeholder="예: 김치찌개, 계란말이, 아이스크림")
        save_entry = st.form_submit_button("일기 저장")

    if save_entry:
        entry = {
            "날짜": date.today().strftime("%Y-%m-%d"),
            "제목": title,
            "내용": content,
            "날씨": weather,
            "작성자": author_name,
            "기분": mood,
            "먹은 음식": food,
            "일기 ID": uuid.uuid4().hex,
        }
        diary = pd.concat([diary, pd.DataFrame([entry])], ignore_index=True)
        save_diary(diary)
        st.session_state["flash_message"] = "일기가 저장되었어요!"
        st.rerun()

    if not diary.empty:
        st.subheader("저장된 일기")
        for _, entry in diary.iterrows():
            entry_id = diary_value(entry, "일기 ID")
            entry_date = diary_value(entry, "날짜") or "날짜 없음"
            entry_title = diary_value(entry, "제목") or "(제목 없음)"
            with st.expander(f"{entry_date} - {entry_title}"):
                st.write(f"날씨: {diary_value(entry, '날씨') or '기록 없음'}")
                st.write(f"기분: {diary_value(entry, '기분') or '기록 없음'}")
                st.write("내용:")
                st.text(diary_value(entry, "내용") or "기록 없음")
                st.write(f"먹은 음식: {diary_value(entry, '먹은 음식') or '기록 없음'}")
                st.write(f"작성자: {diary_value(entry, '작성자') or '기록 없음'}")
                if st.button("삭제", key=f"delete_diary_{entry_id}"):
                    st.session_state["pending_delete_id"] = entry_id

        st.subheader("일기 수정")
        edit_number = st.selectbox(
            "수정할 일기",
            range(1, len(diary) + 1),
            format_func=lambda number: (
                f"{number}. {diary.iloc[number - 1]['날짜']} - "
                f"{diary_value(diary.iloc[number - 1], '제목')}"
            ),
        )
        edit_entry = diary.iloc[edit_number - 1]
        edit_id = diary_value(edit_entry, "일기 ID")
        with st.form(f"edit_diary_form_{edit_id}"):
            edited_title = st.text_input(
                "제목 수정",
                value=diary_value(edit_entry, "제목"),
                key=f"edit_title_{edit_id}",
            )
            edited_content = st.text_area(
                "내용 수정",
                value=diary_value(edit_entry, "내용"),
                key=f"edit_content_{edit_id}",
            )
            current_weather = diary_value(edit_entry, "날씨")
            edited_weather = st.selectbox(
                "날씨 수정",
                WEATHER_OPTIONS,
                index=WEATHER_OPTIONS.index(current_weather)
                if current_weather in WEATHER_OPTIONS
                else 0,
                key=f"edit_weather_{edit_id}",
            )
            current_mood = diary_value(edit_entry, "기분")
            edited_mood = st.selectbox(
                "기분 수정",
                MOOD_OPTIONS,
                index=MOOD_OPTIONS.index(current_mood) if current_mood in MOOD_OPTIONS else 2,
                key=f"edit_mood_{edit_id}",
            )
            edited_food = st.text_input(
                "먹은 음식 수정",
                value=diary_value(edit_entry, "먹은 음식"),
                key=f"edit_food_{edit_id}",
            )
            update_entry = st.form_submit_button("수정 저장")
        if update_entry:
            latest_diary = load_diary()
            matching_rows = latest_diary.index[latest_diary["일기 ID"] == edit_id]
            if len(matching_rows):
                row_index = matching_rows[0]
                latest_diary.loc[row_index, "제목"] = edited_title
                latest_diary.loc[row_index, "내용"] = edited_content
                latest_diary.loc[row_index, "날씨"] = edited_weather
                latest_diary.loc[row_index, "기분"] = edited_mood
                latest_diary.loc[row_index, "먹은 음식"] = edited_food
                save_diary(latest_diary)
                st.session_state["flash_message"] = "일기가 수정되었어요!"
                st.rerun()
            st.error("수정할 일기를 찾을 수 없어요. 목록을 새로 확인해 주세요.")
    else:
        st.write("아직 작성된 일기가 없어요.")

    if last_viewed_date is None:
        st.write("처음 방문이에요! 일기를 써봐요 🌱")
    else:
        st.write(f"마지막으로 일기를 확인한 날: {last_viewed_date}")

else:
    st.title("📅 일기 달력")
    if "calendar_month" not in st.session_state:
        st.session_state["calendar_month"] = date.today().replace(day=1)
    if "selected_calendar_date" not in st.session_state:
        st.session_state["selected_calendar_date"] = None

    month_start = st.session_state["calendar_month"]
    previous_month, month_label, next_month = st.columns([1, 3, 1])
    if previous_month.button("이전 달", key="previous_month"):
        if month_start.month == 1:
            st.session_state["calendar_month"] = date(month_start.year - 1, 12, 1)
        else:
            st.session_state["calendar_month"] = date(month_start.year, month_start.month - 1, 1)
        st.rerun()
    month_label.markdown(f"### {month_start.year}년 {month_start.month}월")
    if next_month.button("다음 달", key="next_month"):
        if month_start.month == 12:
            st.session_state["calendar_month"] = date(month_start.year + 1, 1, 1)
        else:
            st.session_state["calendar_month"] = date(month_start.year, month_start.month + 1, 1)
        st.rerun()

    daily_counts = {}
    for diary_date in diary["날짜"]:
        parsed_date = normalized_date(diary_date)
        if parsed_date is not None:
            daily_counts[parsed_date] = daily_counts.get(parsed_date, 0) + 1

    for weekday, column in zip(WEEKDAYS, st.columns(7)):
        column.markdown(f"**{weekday}**")
    for week in calendar.monthcalendar(month_start.year, month_start.month):
        for day_number, column in zip(week, st.columns(7)):
            if day_number == 0:
                column.write("")
                continue
            calendar_date = date(month_start.year, month_start.month, day_number)
            count = daily_counts.get(calendar_date, 0)
            label = f"{day_number}\n{count}건" if count else str(day_number)
            if column.button(label, key=f"calendar_day_{calendar_date.isoformat()}"):
                st.session_state["selected_calendar_date"] = calendar_date.isoformat()

    selected_date_value = st.session_state["selected_calendar_date"]
    selected_date = normalized_date(selected_date_value) if selected_date_value else None
    if selected_date is None:
        st.info("달력에서 날짜를 선택하면 해당 일기를 확인할 수 있어요.")
    else:
        st.subheader(f"{selected_date.isoformat()} 일기")
        selected_entries = diary[
            diary["날짜"].map(normalized_date) == selected_date
        ]
        if selected_entries.empty:
            st.info("선택한 날짜에는 작성된 일기가 없어요.")
        else:
            for _, entry in selected_entries.iterrows():
                entry_id = diary_value(entry, "일기 ID")
                with st.expander(diary_value(entry, "제목") or "(제목 없음)"):
                    st.write(f"내용: {diary_value(entry, '내용')}")
                    st.write(f"기분: {diary_value(entry, '기분') or '기록 없음'}")
                    st.write(f"먹은 음식: {diary_value(entry, '먹은 음식') or '기록 없음'}")
                    st.write(f"날씨: {diary_value(entry, '날씨')}")
                    st.write(f"작성자: {diary_value(entry, '작성자')}")
                    if st.button("이 일기 삭제", key=f"request_calendar_delete_{entry_id}"):
                        st.session_state["pending_delete_id"] = entry_id

pending_delete_id = st.session_state.get("pending_delete_id")
if pending_delete_id:
    pending_rows = diary[diary["일기 ID"] == pending_delete_id]
    if pending_rows.empty:
        st.warning("삭제 대상 일기가 이미 목록에 없어요.")
        st.session_state.pop("pending_delete_id", None)
    else:
        pending_entry = pending_rows.iloc[0]
        st.warning(
            f"{diary_value(pending_entry, '날짜')} - "
            f"{diary_value(pending_entry, '제목') or '(제목 없음)'} 을(를) 삭제할까요?"
        )
        confirm_column, cancel_column = st.columns(2)
        if confirm_column.button("삭제 확정", key="confirm_diary_delete"):
            try:
                latest_diary = load_diary()
                if not (latest_diary["일기 ID"] == pending_delete_id).any():
                    st.session_state.pop("pending_delete_id", None)
                    st.warning("삭제 대상 일기가 이미 없어요. 목록을 새로 확인해 주세요.")
                else:
                    latest_diary = latest_diary[
                        latest_diary["일기 ID"] != pending_delete_id
                    ].reset_index(drop=True)
                    save_diary(latest_diary)
                    st.session_state.pop("pending_delete_id", None)
                    st.session_state["flash_message"] = "일기가 삭제되었어요!"
                    st.rerun()
            except (OSError, UnicodeError, pd.errors.ParserError) as error:
                st.error(f"일기 파일을 읽거나 저장하지 못했어요: {error}")
        if cancel_column.button("취소", key="cancel_diary_delete"):
            st.session_state.pop("pending_delete_id", None)
            st.rerun()
