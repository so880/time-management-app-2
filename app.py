import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from config import LOG_FILE, SESSION_FILE
from state import init_session, save_session, save_settings, commit_rerun
from components.styles import inject_styles, inject_compact_styles
from components.background import inject_background, render_bg_controls
from components.bgm_player import BGM_PLAYER_HTML, get_bgm_html
from views import dashboard, active, review, sos

# === ページ設定（最初のStreamlitコマンド：画面幅いっぱいに使う） ===
st.set_page_config(page_title="Focus & Cafe Roulette", layout="wide")

# === 初期化・グローバル装飾 ===
init_session()
inject_background()
inject_styles()
# Streamlit の自動ページナビ（app/dashboard等）を隠す
st.markdown("<style>[data-testid=\"stSidebarNav\"]{display:none;}</style>", unsafe_allow_html=True)
if st.session_state.page == 'active' and st.session_state.compact_mode:
    inject_compact_styles()

# === サイドバー ===
with st.sidebar:
    # サイドバー開閉の操作性アップ：黒い空白クリックで閉じる／左端の縦帯で開く（ホバーで光る）
    components.html("""
    <script>
    (function(){
      const doc = window.parent.document;
      function findCollapseBtn(){
        return doc.querySelector('[data-testid="stSidebarCollapseButton"] button')
            || doc.querySelector('[data-testid="stSidebarCollapseButton"]')
            || doc.querySelector('[data-testid="baseButton-headerNoPadding"]')
            || doc.querySelector('section[data-testid="stSidebar"] button[kind="header"]');
      }
      function findExpandBtn(){
        return doc.querySelector('[data-testid="stSidebarCollapsedControl"] button')
            || doc.querySelector('[data-testid="stSidebarCollapsedControl"]')
            || doc.querySelector('[data-testid="stExpandSidebarButton"]')
            || findCollapseBtn();
      }
      function setup(){
        const sb = doc.querySelector('section[data-testid="stSidebar"]');
        if(!sb) return;

        // (1) 黒い空白クリックで閉じる
        if(!sb.dataset.blankClose){
          sb.dataset.blankClose = '1';
          sb.addEventListener('click', function(e){
            const interactive = e.target.closest(
              'button, a, input, textarea, select, label, summary, iframe, ' +
              '[role="radio"], [role="checkbox"], [role="slider"], [role="tab"], ' +
              '[data-baseweb], [data-testid="stExpander"], [data-testid="stFileUploader"], [data-testid="stSlider"]'
            );
            if(!interactive){ const b = findCollapseBtn(); if(b) b.click(); }
          });
        }

        // (2) 左端の縦帯（折りたたみ時のみ表示・ホバーで光る）で開く
        let opener = doc.getElementById('sidebar-reopen-strip');
        if(!opener){
          opener = doc.createElement('div');
          opener.id = 'sidebar-reopen-strip';
          opener.title = 'クリックでサイドバーを開く';
          opener.style.cssText = 'position:fixed; left:0; top:0; width:18px; height:100%; cursor:pointer; z-index:99980; background:rgba(76,175,80,0.12); transition:all .15s; display:none;';
          opener.addEventListener('mouseenter', function(){ opener.style.background='rgba(76,175,80,0.55)'; opener.style.boxShadow='0 0 18px rgba(76,175,80,0.9)'; });
          opener.addEventListener('mouseleave', function(){ opener.style.background='rgba(76,175,80,0.12)'; opener.style.boxShadow='none'; });
          opener.addEventListener('click', function(){ const b = findExpandBtn(); if(b) b.click(); });
          doc.body.appendChild(opener);
        }
        // 折りたたみ状態を判定して左端帯の表示を切り替え
        const rect = sb.getBoundingClientRect();
        const collapsed = (rect.width < 50) || (rect.right < 10);
        opener.style.display = collapsed ? 'block' : 'none';
      }
      setInterval(setup, 600);
      setup();
    })();
    </script>
    """, height=0)
    # 背景・モード切替をブロック風UIにして選択中を明るく表示するCSS
    st.markdown("""
    <style>
    div[class*="st-key-bg_mode_radio"] [role="radiogroup"],
    div[class*="st-key-app_mode_radio"] [role="radiogroup"] { gap: 8px; }
    div[class*="st-key-bg_mode_radio"] [role="radiogroup"] > label,
    div[class*="st-key-app_mode_radio"] [role="radiogroup"] > label {
        background: rgba(255,255,255,0.06);
        border: 1px solid #555;
        border-radius: 6px;
        padding: 10px 12px;
        margin: 0;
        width: 100%;
        transition: all .15s;
    }
    div[class*="st-key-bg_mode_radio"] [role="radiogroup"] > label:hover,
    div[class*="st-key-app_mode_radio"] [role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.13);
    }
    div[class*="st-key-bg_mode_radio"] [role="radiogroup"] > label:has(input:checked),
    div[class*="st-key-app_mode_radio"] [role="radiogroup"] > label:has(input:checked) {
        background: rgba(76,175,80,0.35);
        border-color: #4CAF50;
        box-shadow: 0 0 12px rgba(76,175,80,0.75);
        font-weight: bold;
    }
    /* トグル(expander)の見出しを大きく統一（環境音コントロールと同じ大きさ） */
    [data-testid="stSidebar"] summary p { font-size: 1.12rem !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

    # 🎧 環境音コントロール（トグルで開閉）
    with st.expander("🎧 環境音コントロール", expanded=True):
        _cafe = st.session_state.settings.get("snd_cafe_url", "e_04ZrNroTo")
        _chat = st.session_state.settings.get("snd_chat_url", "bZ2XhA_kXYQ")
        _relax = st.session_state.settings.get("snd_relax_url", "vPhg6sc1Mk4")
        _player_html = (BGM_PLAYER_HTML
                        .replace("__CAFE_ID__", _cafe.replace("'", ""))
                        .replace("__CHAT_ID__", _chat.replace("'", ""))
                        .replace("__RELAX_ID__", _relax.replace("'", "")))
        components.html(_player_html, height=480)
        if st.checkbox("⚙️ ボタン(カフェ/雑踏/波)のURLを変更", key="snd_edit_chk"):
            nc = st.text_input("☕ カフェ のURL/ID", value=_cafe, key="snd_cafe_in")
            nh = st.text_input("🗣️ 雑踏 のURL/ID", value=_chat, key="snd_chat_in")
            nr = st.text_input("🐋 波と鯨 のURL/ID", value=_relax, key="snd_relax_in")
            if st.button("💾 環境音のURLを保存", key="snd_save"):
                st.session_state.settings["snd_cafe_url"] = nc.strip() or _cafe
                st.session_state.settings["snd_chat_url"] = nh.strip() or _chat
                st.session_state.settings["snd_relax_url"] = nr.strip() or _relax
                save_settings(st.session_state.settings)
                st.toast("環境音のURLを保存しました ✅")
                commit_rerun()

    # 🖼️ 背景（トグルで開閉）
    with st.expander("🖼️ 背景", expanded=False):
        render_bg_controls()

    # 🔄 モード切替（トグルで開閉）
    with st.expander("🔄 モード切替", expanded=True):
        app_mode = st.radio("モード切替", ["🚀 集中モード (Use)", "🛠️ 編集モード (Edit)"],
                            key="app_mode_radio", label_visibility="collapsed")
    st.divider()
    st.write(f"📁 記録数: {len(st.session_state.logs)}件")
    if st.session_state.logs:
        csv = pd.DataFrame(st.session_state.logs).to_csv(index=False).encode('utf-8-sig')
        st.download_button("履歴ダウンロード", csv, "activity_log.csv", "text/csv")
    if app_mode == "🛠️ 編集モード (Edit)" and st.button("全データリセット"):
        st.session_state.logs = []
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        for _k, _v in {"study_time_total": 0, "refresh_time_total": 0, "page": "dashboard",
                       "current_task": None, "start_time": None, "rolled_options": None,
                       "pending_review": None, "target_locked": False}.items():
            st.session_state[_k] = _v
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
        commit_rerun()

# === ページルーティング ===
_page = st.session_state.page
if _page == 'active':
    active.render()
elif _page == 'review':
    review.render()
elif _page == 'sos':
    sos.render()
else:
    dashboard.render()

save_session()