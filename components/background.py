import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from config import BG_DIR, DEFAULT_SETTINGS
from state import save_settings, commit_rerun
from utils.helpers import file_to_data_uri

def inject_background():
    BG_URL = st.session_state.settings.get("bg_url", DEFAULT_SETTINGS["bg_url"])
    bg_mode_eff = st.session_state.get("bg_mode_radio", st.session_state.settings.get("bg_mode", "カフェ画像"))
    if bg_mode_eff == "黒画面":
        bg_js_image = "none"
        bg_js_color = "#000000"
    elif bg_mode_eff == "アップロード画像":
        # セッションが切れても、保存済みの選択画像をディスクから復元する
        if not st.session_state.bg_custom_data:
            _cur = st.session_state.settings.get("bg_current_file", "")
            if _cur:
                _data = file_to_data_uri(_cur)
                if _data:
                    st.session_state.bg_custom_data = _data
        if st.session_state.bg_custom_data:
            bg_js_image = f"url('{st.session_state.bg_custom_data}')"
            bg_js_color = "transparent"
        else:
            bg_js_image = f"url('{BG_URL}')"
            bg_js_color = "transparent"
    else:
        bg_js_image = f"url('{BG_URL}')"
        bg_js_color = "transparent"
    components.html(f"""
    <script>
        const setBg = () => {{
            const app = window.parent.document.querySelector('.stApp');
            if(app) {{
                app.style.backgroundImage = "{bg_js_image}";
                app.style.backgroundSize = "cover";
                app.style.backgroundPosition = "center";
                app.style.backgroundRepeat = "no-repeat";
                app.style.backgroundAttachment = "fixed";
                app.style.backgroundColor = "{bg_js_color}";
            }}
        }};
        window.parent.addEventListener('load', setBg);
        setInterval(setBg, 1000);
        setBg();
    </script>
    """, height=0)

def render_bg_controls():
    # ★Fix2: 背景の選択（カフェ画像 / 黒画面 / アップロード画像）
    _bg_opts = ["カフェ画像", "黒画面", "アップロード画像"]
    _bg_default = st.session_state.settings.get("bg_mode", "カフェ画像")
    bg_mode = st.radio("背景", _bg_opts, index=_bg_opts.index(_bg_default) if _bg_default in _bg_opts else 0,
                       key="bg_mode_radio", label_visibility="collapsed")
    if bg_mode != st.session_state.settings.get("bg_mode"):
        st.session_state.settings["bg_mode"] = bg_mode
        save_settings(st.session_state.settings)
    if bg_mode == "アップロード画像":
        up = st.file_uploader("新しい画像をアップロード", type=["png", "jpg", "jpeg"], key="bg_up")
        if up is not None:
            raw = up.getvalue()
            sig = f"{up.name}_{len(raw)}"
            if st.session_state.get("bg_up_sig") != sig:
                ext = up.name.rsplit(".", 1)[-1].lower()
                fname = datetime.now().strftime("%Y%m%d_%H%M%S_") + "".join(
                    c for c in up.name if c.isalnum() or c in "._-")
                if not fname.lower().endswith(("." + ext)):
                    fname = fname + "." + ext
                with open(os.path.join(BG_DIR, fname), "wb") as f:
                    f.write(raw)
                hist = st.session_state.settings.get("bg_history", [])
                if fname not in hist:
                    hist.insert(0, fname)
                st.session_state.settings["bg_history"] = hist
                st.session_state.settings["bg_current_file"] = fname
                save_settings(st.session_state.settings)
                st.session_state.bg_custom_data = f"data:image/{'png' if ext=='png' else 'jpeg'};base64,{base64.b64encode(raw).decode()}"
                st.session_state.bg_up_sig = sig
                commit_rerun()
        hist = [h for h in st.session_state.settings.get("bg_history", []) if os.path.exists(os.path.join(BG_DIR, h))]
        if hist:
            cur = st.session_state.settings.get("bg_current_file", "")
            idx = hist.index(cur) if cur in hist else 0
            chosen = st.selectbox("📚 履歴から選ぶ", hist, index=idx, key="bg_hist_select")
            if chosen != st.session_state.settings.get("bg_current_file"):
                st.session_state.settings["bg_current_file"] = chosen
                save_settings(st.session_state.settings)
                st.session_state.bg_custom_data = file_to_data_uri(chosen)
                commit_rerun()
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("🔄 この画像を適用", key="bg_apply"):
                    st.session_state.bg_custom_data = file_to_data_uri(chosen)
                    commit_rerun()
            with cc2:
                if st.button("🗑 履歴から削除", key="bg_hist_del"):
                    hist.remove(chosen)
                    st.session_state.settings["bg_history"] = hist
                    try:
                        os.remove(os.path.join(BG_DIR, chosen))
                    except OSError:
                        pass
                    if st.session_state.settings.get("bg_current_file") == chosen:
                        st.session_state.settings["bg_current_file"] = hist[0] if hist else ""
                        st.session_state.bg_custom_data = file_to_data_uri(hist[0]) if hist else None
                    save_settings(st.session_state.settings)
                    commit_rerun()
            st.caption(f"🖼️ 現在: {st.session_state.settings.get('bg_current_file','(なし)')}")
        else:
            st.caption("まだ画像がありません。上からアップロードしてください。")
    elif bg_mode == "黒画面":
        st.caption("⬛ 画像を消して集中しやすい黒背景にします。")
    else:
        st.caption("☕ カフェ画像（URLは編集モードで変更可）。")
