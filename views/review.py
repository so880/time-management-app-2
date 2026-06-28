import streamlit as st
from utils.logger import log_activity
from state import commit_rerun, save_settings


def render():
    pr = st.session_state.get("pending_review", {}) or {}
    st.markdown("<h2 style='text-align:center;'>📝 ふりかえり（すべて任意）</h2>", unsafe_allow_html=True)
    st.caption(f"【{pr.get('cat','')}】{pr.get('task','')} ／ 経過 {pr.get('em',0)} 分")
    done = st.text_area("やったこと（自由記述）", key="rv_done", placeholder="例）長文を3本写経した など")
    _opts = ["未記入", "1", "2", "3", "4", "5"]
    progress = st.select_slider("進捗度合い（1=少し / 5=大きく進んだ）", options=_opts, value="未記入", key="rv_prog")
    focus = st.select_slider("集中度（1=散漫 / 5=没頭）", options=_opts, value="未記入", key="rv_focus")
    sat = st.select_slider("満足度（1=不満 / 5=満足）", options=_opts, value="未記入", key="rv_sat")

    # 🔴 『今日絶対やる』タスクなら、終わったか質問（消すと回答→自動でリストから削除）
    _remove_mustdo = False
    if pr.get("mustdo"):
        st.markdown("---")
        st.markdown("#### 🔴 『今日絶対やる』タスクの確認")
        _ans = st.radio(
            f"「{pr.get('task','')}」は終わりましたか？",
            ["まだ（リストに残す）", "✅ 終わったのでリストから消す"],
            key="rv_mustdo_done",
        )
        _remove_mustdo = _ans.startswith("✅")

    rc1, rc2 = st.columns(2)

    def _finish_review(save_details):
        log_activity(
            pr.get("task", ""), pr.get("cat", ""), pr.get("em", 0), "設定BGM",
            done_text=(done if save_details else ""),
            progress=("" if (not save_details or progress == "未記入") else progress),
            focus=("" if (not save_details or focus == "未記入") else focus),
            satisfaction=("" if (not save_details or sat == "未記入") else sat),
        )
        # 「終わった」と答えていたら『今日絶対やる』から自動削除
        if _remove_mustdo:
            _s = st.session_state.settings
            _ml = _s.get("mustdo_list", [])
            if pr.get("task") in _ml:
                _ml.remove(pr.get("task"))
                _s["mustdo_list"] = _ml
            _md = _s.get("mustdo_list_disabled", [])
            if pr.get("task") in _md:
                _md.remove(pr.get("task"))
                _s["mustdo_list_disabled"] = _md
            save_settings(_s)
        for _k in ["rv_done", "rv_prog", "rv_focus", "rv_sat", "rv_mustdo_done"]:
            if _k in st.session_state:
                del st.session_state[_k]
        st.session_state.pending_review = None
        st.session_state.page = 'dashboard'
        commit_rerun()

    with rc1:
        if st.button("💾 保存してダッシュボードへ", use_container_width=True, type="primary"):
            _finish_review(True)
    with rc2:
        if st.button("スキップ（記録のみ）", use_container_width=True):
            _finish_review(False)
