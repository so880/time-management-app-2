import streamlit as st
import streamlit.components.v1 as components
from state import commit_rerun


def render():
    st.warning("集中力が切れましたね。自分を責めず、一旦リセットしましょう！（5分間だけ）")
    st.markdown(f"<h2 style='text-align:center;'>緊急指令：【{st.session_state.sos_task}】</h2>", unsafe_allow_html=True)
    sos_ms = 5 * 60 * 1000
    sos_js = f"""
    <div style="text-align:center; margin-top:10px;">
        <div id="sos-timer" style="font-size:5rem; font-weight:bold; color:#ff9800; font-family:monospace;"></div>
        <div id="sos-alarm" style="display:none; font-size:2.4rem; font-weight:bold; color:#fff; background:red; padding:16px; border-radius:10px;">⏰ 5分経過！そろそろ机に戻りましょう</div>
    </div>
    <script>
        if(!sessionStorage.getItem('sosStart')) sessionStorage.setItem('sosStart', Date.now());
        const sEnd = parseInt(sessionStorage.getItem('sosStart')) + {sos_ms};
        const tEl = document.getElementById('sos-timer');
        const aEl = document.getElementById('sos-alarm');
        const iv = setInterval(() => {{
            const now = Date.now();
            const rem = Math.max(0, sEnd - now);
            tEl.innerText = Math.floor(rem/60000).toString().padStart(2,'0') + ":" + Math.floor((rem%60000)/1000).toString().padStart(2,'0');
            if (now >= sEnd && !sessionStorage.getItem('sosPlayed')) {{
                sessionStorage.setItem('sosPlayed', 'true');
                clearInterval(iv);
                tEl.style.display = 'none';
                aEl.style.display = 'inline-block';
                try {{
                    const a = new (window.AudioContext || window.webkitAudioContext)();
                    const o = a.createOscillator();
                    o.type = 'square'; o.frequency.setValueAtTime(440, a.currentTime);
                    o.connect(a.destination); o.start(); setTimeout(()=>o.stop(), 1500);
                }} catch(e) {{}}
                setInterval(() => {{ document.body.style.backgroundColor = document.body.style.backgroundColor === 'red' ? 'transparent' : 'red'; }}, 500);
            }}
        }}, 250);
    </script>
    """
    components.html(sos_js, height=170)
    if st.button("ダッシュボードへ戻る", use_container_width=True):
        components.html("<script>sessionStorage.removeItem('sosStart'); sessionStorage.removeItem('sosPlayed');</script>", height=0)
        st.session_state.page = 'dashboard'
        commit_rerun()
