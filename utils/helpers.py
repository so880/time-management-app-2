import os
import base64
import random
import streamlit as st
from config import BG_DIR, GAME_LIST

def active_items(key_name):
    """無効化されていない項目のみ返す"""
    s = st.session_state.settings
    disabled = set(s.get(f"{key_name}_disabled", []))
    return [t for t in s.get(key_name, []) if t not in disabled]
def file_to_data_uri(fname):
    """保存済みの背景画像ファイルを data URI に変換"""
    path = os.path.join(BG_DIR, fname)
    if not os.path.exists(path):
        return None
    ext = fname.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
def get_pool():
    # 「今日絶対やる」に項目があれば、勉強の抽選はそこからのみ。空になったら通常へ。
    must = list(active_items("mustdo_list"))
    if must:
        return must
    pool = list(active_items("study_list"))
    for t in active_items("focus_study_list"): pool.extend([t]*3)
    if not st.session_state.mock_exam_done: pool.append("TOEIC模擬試験(2時間)")
    return pool or ["（勉強項目がありません・編集モードで追加/有効化してください）"]
def roll_once(can_game):
    study_only = st.session_state.last_was_refresh or st.session_state.force_study_only
    refresh_pool = active_items("refresh_list") + (GAME_LIST if can_game else [])
    refresh_pool = refresh_pool or ["（気分転換項目がありません）"]
    st.session_state.rolled_options = {
        "勉強": random.choice(get_pool()),
        "気分転換": "なし(連続お休み)" if study_only else random.choice(refresh_pool)
    }
