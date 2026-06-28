import os
import pandas as pd
import streamlit as st
from datetime import datetime
from config import LOG_FILE

def load_logs():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE).to_dict(orient="records")
    return []
def log_activity(task_name, category, duration, bgm_used, note="",
                 done_text="", progress="", focus="", satisfaction=""):
    entry = {
        "日付": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "カテゴリ": category, "内容": task_name, "BGM": bgm_used,
        "経過時間(分)": duration,
        "やったこと": done_text, "進捗度合い": progress,
        "集中度": focus, "満足度": satisfaction, "メモ": note
    }
    st.session_state.logs.append(entry)
    # スキーマ統一のため毎回全件を書き直す（列追加でも壊れない）
    pd.DataFrame(st.session_state.logs).to_csv(LOG_FILE, index=False, encoding="utf-8-sig")
