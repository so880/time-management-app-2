import os
import json
import streamlit as st
from datetime import date, datetime
from config import SETTINGS_FILE, SESSION_FILE, DEFAULT_SETTINGS
from utils.logger import load_logs

def load_settings():
    s = DEFAULT_SETTINGS.copy()
    saved = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        s.update(saved)
    # 旧形式(toeic/intern固定)から可変goalsへ移行
    if not s.get("goals"):
        s["goals"] = [
            {"name": s.get("toeic_name", "TOEIC"), "date": s.get("toeic_date", "2026-05-24"), "hours": int(s.get("daily_hours_toeic", 3))},
            {"name": s.get("intern_name", "インターン"), "date": s.get("intern_date", "2026-06-01"), "hours": int(s.get("daily_hours_intern", 2))},
        ]
    # 下限は常に30分で固定
    s["study_dur_min"] = 30
    for k in ("study_list_disabled", "focus_study_list_disabled", "refresh_list_disabled", "mustdo_list_disabled"):
        s.setdefault(k, [])
    s.setdefault("mustdo_list", [])
    # 旧 daily_window(単一) -> daily_routine(複数) へ移行（保存ファイルに daily_routine が無い場合のみ）
    if not saved.get("daily_routine") and saved.get("daily_window"):
        dw = saved["daily_window"]
        s["daily_routine"] = [[{"start": d.get("start", "09:00"), "end": d.get("end", "22:00")}] for d in dw]
    return s
def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=4)

PERSIST_KEYS = ['page', 'current_task', 'start_time', 'study_time_total', 'refresh_time_total', 'target_value', 'target_locked', 'target_date', 'last_was_refresh', 'force_study_only', 'mock_exam_done', 'pending_review', 'sos_task', 'rolled_options']

def save_session():
    """永続化対象キーを data/session_state.json に保存"""
    data = {k: st.session_state.get(k) for k in PERSIST_KEYS}
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
    except Exception:
        pass

def commit_rerun():
    """状態を保存してから再実行（st.rerun の置き換え）"""
    save_session()
    st.rerun()

def init_session():
    if "settings" not in st.session_state: st.session_state.settings = load_settings()
    if "logs" not in st.session_state: st.session_state.logs = load_logs()
    today = date.today().isoformat()
    saved = {}
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, encoding="utf-8") as fp: saved = json.load(fp)
        except Exception:
            saved = {}
    restore = bool(saved)
    same_day = saved.get("target_date") == today
    defaults = {
        "page": "dashboard", "current_task": None, "start_time": None,
        "study_time_total": 0, "refresh_time_total": 0, "target_value": 180,
        "target_locked": False, "target_date": today, "last_was_refresh": False,
        "force_study_only": False, "mock_exam_done": False, "pending_review": None,
        "sos_task": None, "rolled_options": None,
    }
    for k, dv in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = saved[k] if (restore and k in saved) else dv
    # 日付またぎ：一部だけリセットし他は復元
    if restore and not same_day:
        st.session_state.target_locked = False
        st.session_state.target_value = 180
        st.session_state.study_time_total = 0
        st.session_state.refresh_time_total = 0
    st.session_state.target_date = today
    if "compact_mode" not in st.session_state: st.session_state.compact_mode = False
    if "bg_custom_data" not in st.session_state: st.session_state.bg_custom_data = None
    # セッションファイルが無い初回は、今日のログから合計を復元
    if not restore:
        today_log = datetime.now().strftime("%Y-%m-%d")
        s_tot = r_tot = 0
        for log in st.session_state.logs:
            if str(log.get("日付", "")).startswith(today_log):
                if "勉強" in log.get("カテゴリ", ""): s_tot += int(log.get("経過時間(分)", 0))
                elif "気分転換" in log.get("カテゴリ", ""): r_tot += int(log.get("経過時間(分)", 0))
        st.session_state.study_time_total = s_tot
        st.session_state.refresh_time_total = r_tot
    save_session()