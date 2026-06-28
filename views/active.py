import time
import random
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from config import SHORT_TASK_THRESHOLD, SOS_LIST
from utils.logger import log_activity
from utils.helpers import roll_once
from components.sf6_trainer import SF6_HTML_CODE
from state import commit_rerun


def render():
    t = st.session_state.current_task
    dms = t['duration'] * 60000
    show_timer_js = "true" if t['カテゴリ'] == "気分転換" else "false"
    is_short = (t['カテゴリ'] == "勉強" and t['duration'] <= SHORT_TASK_THRESHOLD)
    # start_time(Unix秒)から開始時刻ms を渡す。sessionStorage は使わない（再起動でも継続）
    start_ms = int((st.session_state.start_time or time.time()) * 1000)
    # ===============================================
    # パターンA： 没入(コンパクト)モード ON
    # ===============================================
    if st.session_state.compact_mode:
        if st.button("🗖 拡大表示に戻す", help="終了する場合はここを押して元の画面に戻ってください"):
            st.session_state.compact_mode = False
            commit_rerun()
        # 左上に「文字＋半透明の無地背景（座布団）」のパネルだけを描画し、SOS等のボタンは一切出さない！
        js_compact = f"""
        <style>
            body {{ margin: 0; padding: 0; font-family: sans-serif; }}
            .panel {{
                background: rgba(0, 0, 0, 0.75);
                padding: 15px 25px;
                border-radius: 12px;
                display: inline-block;
                backdrop-filter: blur(5px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .task-name {{ font-size: 1.2rem; color: #fff; font-weight: bold; margin-bottom: 5px; }}
            .timer {{ font-size: 2.5rem; color: #4CAF50; font-family: monospace; font-weight: bold; text-shadow: 0 0 10px #4CAF50; }}
            .alarm {{ display: none; font-size: 1.2rem; font-weight: bold; color: #ffeb3b; margin-top: 5px; }}
            .stoic-msg {{ font-size: 1rem; color: rgba(255,255,255,0.7); }}
        </style>
        <div class="panel">
            <div class="task-name">{t['タスク']}</div>
            <div class="timer" id="t"></div>
            <div class="alarm" id="alarm-msg">⏰ 終了！拡大して記録してください</div>
        </div>

        <script>
            const e = {start_ms} + {dms};
            const show = {show_timer_js};

            const tick = setInterval(() => {{
                const now = Date.now();
                const remain = Math.max(0, e - now);
                const tEl = document.getElementById('t');

                if (show) {{
                    tEl.innerText = Math.floor(remain/60000).toString().padStart(2,'0') + ":" + Math.floor((remain%60000)/1000).toString().padStart(2,'0');
                    if (now >= e && !sessionStorage.getItem('played')) {{
                        sessionStorage.setItem('played', 'true');
                        tEl.style.display = 'none';
                        document.getElementById('alarm-msg').style.display = 'block';
                        try {{
                            const actx = new (window.AudioContext || window.webkitAudioContext)();
                            const osc = actx.createOscillator();
                            osc.type = 'square'; osc.frequency.setValueAtTime(440, actx.currentTime);
                            osc.connect(actx.destination); osc.start(); setTimeout(()=>osc.stop(),1500);
                        }} catch(err) {{}}
                    }}
                }} else {{
                    if (now < e) {{
                        tEl.innerText = "集中モード実行中...";
                        tEl.className = "stoic-msg";
                    }} else {{
                        tEl.innerText = "✅ 達成！拡大して記録";
                        tEl.style.fontSize = "1.1rem";
                        tEl.style.color = "#ffeb3b";
                        clearInterval(tick);
                    }}
                }}
            }}, 200);
        </script>
        """
        components.html(js_compact, height=150)
    # ===============================================
    # パターンB： 通常表示（フルサイズ）モード
    # ===============================================
    else:
        btn_col, _ = st.columns([1, 15])
        with btn_col:
            if st.button("🗕", help="没入表示（背景メイン）にする"):
                st.session_state.compact_mode = True
                commit_rerun()
        st.markdown(f"<h1 style='text-align:center;font-size:3rem;text-shadow:2px 2px 4px #000;'>{t['タスク']}</h1>", unsafe_allow_html=True)
        if "スト6" in t['タスク']: components.html(SF6_HTML_CODE, height=650, scrolling=True)

        js_full = f"""
        <div id="t" style="text-align:center;font-size:7rem;color:#4CAF50;font-family:monospace;font-weight:bold;text-shadow:0 0 20px #4CAF50;"></div>
        <div id="alarm-msg" style="display:none; text-align:center; font-size:4rem; font-weight:bold; color:white; background:rgba(255,0,0,0.8); padding:20px; border-radius:10px; backdrop-filter:blur(10px);">⏰ 終了時間です！</div>

        <script>
            const e = {start_ms} + {dms};
            const show = {show_timer_js};

            const tick = setInterval(() => {{
                const now = Date.now();
                const remain = Math.max(0, e - now);
                const tEl = document.getElementById('t');

                const btns = Array.from(window.parent.document.querySelectorAll('button'));
                const endBtn = btns.find(b => b.innerText.includes('終了して記録') || b.textContent.includes('終了して記録'));
                if (show) {{
                    tEl.innerText = Math.floor(remain/60000).toString().padStart(2,'0') + ":" + Math.floor((remain%60000)/1000).toString().padStart(2,'0');
                    if (now >= e && !sessionStorage.getItem('played')) {{
                        sessionStorage.setItem('played', 'true');
                        tEl.style.display = 'none';
                        document.getElementById('alarm-msg').style.display = 'block';
                        try {{
                            const actx = new (window.AudioContext || window.webkitAudioContext)();
                            const osc = actx.createOscillator();
                            osc.type = 'square'; osc.frequency.setValueAtTime(440, actx.currentTime);
                            osc.connect(actx.destination); osc.start(); setTimeout(()=>osc.stop(),1500);
                        }} catch(err) {{}}
                    }}
                }} else {{
                    if (now < e) {{
                        tEl.innerText = "予定時間: ？？？ 分\\n（見事達成するまで終了ボタンは出現しません）";
                        tEl.style.fontSize = "1.5rem";
                        tEl.style.color = "rgba(255,255,255,0.7)";
                        tEl.style.textShadow = "none";
                        if (endBtn) endBtn.style.display = 'none';
                    }} else {{
                        tEl.innerText = "✅ 規定時間が終了しました！\\n記録して終了できます。";
                        tEl.style.fontSize = "2rem";
                        tEl.style.color = "#ffeb3b";
                        if (endBtn) endBtn.style.display = 'inline-flex';
                        clearInterval(tick);
                    }}
                }}
            }}, 200);
        </script>
        """
        components.html(js_full, height=200)
        st.divider()

        # ★Fix5: 短い課題のときだけ、途中でも「修了してもう1回抽選」を押せる
        if is_short:
            st.info("🟡 これは短い課題です。途中でも『🔁 修了してもう1回抽選』を押せます（規定の時間ぶん、もう一度だけ抽選します）。")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("■ 終了して記録する", use_container_width=True, type="primary"):
                em = max(0, min(int((time.time() - st.session_state.start_time) / 60), t['duration']))
                if t['カテゴリ'] == "勉強": st.session_state.study_time_total += em
                else: st.session_state.refresh_time_total += em
                # 記録は次の「ふりかえり」画面で確定する
                st.session_state.pending_review = {"task": t['タスク'], "cat": t['カテゴリ'], "em": em, "mustdo": t.get("mustdo", False)}
                time.sleep(0.3)
                st.session_state.page = 'review'
                commit_rerun()
        with c2:
            if is_short:
                if st.button("🔁 修了してもう1回抽選する", use_container_width=True):
                    em = max(0, min(int((time.time() - st.session_state.start_time) / 60), t['duration']))
                    st.session_state.study_time_total += em
                    log_activity(t['タスク'], "勉強(短縮修了)", em, "設定BGM", "短い課題のため早期修了→再抽選")
                    time.sleep(0.3)
                    st.session_state.last_was_refresh = False
                    st.session_state.force_study_only = True  # 再抽選は勉強のみ表示
                    _cg = (datetime.now().hour >= 20 or datetime.now().hour <= 3) and (st.session_state.study_time_total >= int(st.session_state.target_value))
                    roll_once(_cg)
                    st.session_state.page = 'dashboard'
                    commit_rerun()
            elif t['カテゴリ'] == "勉強":
                if st.button("🚨 集中切れ！(SOS)", use_container_width=True):
                    em = max(0, min(int((time.time() - st.session_state.start_time) / 60), t['duration']))
                    st.session_state.study_time_total += em
                    log_activity(t['タスク'], "中断", em, "設定BGM", "集中切れ")
                    time.sleep(0.5)
                    st.session_state.sos_task = random.choice(SOS_LIST)
                    st.session_state.page = 'sos'
                    commit_rerun()

        # 短い課題でもSOSは使えるように別行で用意
        if is_short:
            if st.button("🚨 集中切れ！(SOS)", use_container_width=True, key="sos_short"):
                em = max(0, min(int((time.time() - st.session_state.start_time) / 60), t['duration']))
                st.session_state.study_time_total += em
                log_activity(t['タスク'], "中断", em, "設定BGM", "集中切れ")
                time.sleep(0.5)
                st.session_state.sos_task = random.choice(SOS_LIST)
                st.session_state.page = 'sos'
                commit_rerun()
