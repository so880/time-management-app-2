import random
import time
import json
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
from config import GOAL_CAP, GAME_LIST, SHORT_TASK_THRESHOLD
from state import save_settings, commit_rerun
from utils.helpers import roll_once, get_pool, active_items

def edit_list_ui(label, key_name, add_prefix):
    s = st.session_state.settings
    lst = s.get(key_name, [])
    dkey = f"{key_name}_disabled"
    disabled = s.get(dkey, [])
    # 【世代キー方式】削除のたび gen を +1 して、全行のウィジェットキーを作り直す。
    # キーを使い回さないので古い入力状態が一切残らず、押した行が確実に消える。
    gkey = f"{key_name}_gen"
    gen = st.session_state.get(gkey, 0)
    st.caption("チェックを外すと『無効』になり、消さずに抽選から除外できます。🗑で削除。")
    for i, item in enumerate(list(lst)):
        col1, col2, col3 = st.columns([5, 1.4, 1])
        with col1:
            nv = st.text_input(f"{label}_{i}", value=item, key=f"{key_name}_e_{gen}_{i}", label_visibility="collapsed")
            if nv != item:
                if item in disabled:
                    disabled[disabled.index(item)] = nv
                    s[dkey] = disabled
                lst[i] = nv
                s[key_name] = lst
                save_settings(s)
                item = nv
        with col2:
            is_active = item not in disabled
            new_active = st.checkbox("有効", value=is_active, key=f"{key_name}_a_{gen}_{i}")
            if new_active != is_active:
                if new_active and item in disabled:
                    disabled.remove(item)
                elif (not new_active) and item not in disabled:
                    disabled.append(item)
                s[dkey] = disabled
                save_settings(s)
                commit_rerun()
        with col3:
            if st.button("🗑", key=f"{key_name}_d_{gen}_{i}"):
                if item in disabled:
                    disabled.remove(item)
                    s[dkey] = disabled
                lst.pop(i)
                s[key_name] = lst
                save_settings(s)
                st.session_state[gkey] = gen + 1  # 世代を更新 → 全行のキーが新しくなり確実に再描画
                commit_rerun()
    # 追加はフォーム化：Enter（または➕）で確定し、入力欄は自動でクリアされる
    with st.form(f"{add_prefix}_form", clear_on_submit=True):
        fc1, fc2 = st.columns([6, 1])
        with fc1:
            av = st.text_input(f"add_{key_name}", key=f"{add_prefix}_input",
                               label_visibility="collapsed",
                               placeholder=f"新しい{label}を入力してEnter…")
        with fc2:
            submitted = st.form_submit_button("➕ 追加")
        if submitted:
            if av.strip():
                lst.append(av.strip())
                s[key_name] = lst
                save_settings(s)
                st.toast(f"「{av.strip()}」を追加しました ✅")
                st.session_state[f"{add_prefix}_focus"] = True
                commit_rerun()
            else:
                st.toast("⚠️ 空欄は追加できません")
    # 追加直後は入力欄に自動フォーカス（続けて入力できる）
    if st.session_state.pop(f"{add_prefix}_focus", False):
        components.html(f"""<script>
          const sel = 'input[aria-label="add_{key_name}"]';
          const f = () => {{ const el = window.parent.document.querySelector(sel); if (el) el.focus(); }};
          setTimeout(f, 50); setTimeout(f, 250); setTimeout(f, 600);
        </script>""", height=0)
def render_roulette_and_goals():
    s = st.session_state.settings
    current_study = st.session_state.study_time_total
    target_time = int(st.session_state.target_value)
    can_game = (datetime.now().hour >= 20 or datetime.now().hour <= 3) and (current_study >= target_time)
    if can_game: st.success("🎉 ゲーム解放条件クリア！")
    else: st.info(f"🔒 ゲーム解放まで: 勉強 {current_study}/{target_time}分 & 20時以降")
    is_rolled = st.session_state.rolled_options is not None
    if st.button("🎲 カフェルーレットを回す！", key="roulette_btn", use_container_width=True, disabled=is_rolled):
        st.session_state.force_study_only = False
        roll_once(can_game)
        commit_rerun()
    if st.session_state.rolled_options:
        st.markdown("<div id='roulette-result'></div>", unsafe_allow_html=True)
        components.html("""
        <script>
            let attempts = 0;
            const scrollInt = setInterval(() => {
                const el = window.parent.document.getElementById('roulette-result');
                if(el) { el.scrollIntoView({behavior: 'smooth', block: 'center'}); clearInterval(scrollInt); }
                attempts++;
                if(attempts > 20) clearInterval(scrollInt);
            }, 100);
        </script>
        """, height=0)
        ro = st.session_state.rolled_options
        st.markdown("""
        <style>
        div[class*="st-key-exec_task_radio"] [role="radiogroup"] { gap: 10px; }
        div[class*="st-key-exec_task_radio"] [role="radiogroup"] > label {
            background: rgba(255,255,255,0.06); border: 2px solid #555; border-radius: 10px;
            padding: 16px 18px; margin: 0; width: 100%; font-size: 1.15rem; transition: all .15s;
        }
        div[class*="st-key-exec_task_radio"] [role="radiogroup"] > label:hover { background: rgba(255,255,255,0.13); }
        div[class*="st-key-exec_task_radio"] [role="radiogroup"] > label:has(input:checked) {
            background: rgba(76,175,80,0.4); border-color: #4CAF50; box-shadow: 0 0 16px rgba(76,175,80,0.85); font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
        _study_only = st.session_state.last_was_refresh or st.session_state.force_study_only
        if st.session_state.force_study_only and not st.session_state.last_was_refresh:
            st.info("📚 短い課題を時間内に終えたので、今回は『勉強』のみの抽選です。")
        with st.form("sel"):
            ch = [f"【勉強】 {ro['勉強']}"]
            if not _study_only: ch.append(f"【気分転換】 {ro['気分転換']}")
            sm = st.radio("実行タスク:", ch, key="exec_task_radio")
            if st.form_submit_button("集中モードへ！"):
                cat = "勉強" if "【勉強】" in sm else "気分転換"
                tn = sm.replace(f"【{cat}】 ", "")
                if "模試" in tn or "模擬" in tn:
                    dur = 120
                    st.session_state.mock_exam_done = True
                elif cat == "勉強":
                    _dmin = int(s.get("study_dur_min", 30))
                    _dmax = int(s.get("study_dur_max", 60))
                    if _dmin > _dmax: _dmin, _dmax = _dmax, _dmin
                    dur = random.randint(_dmin, _dmax)
                else:
                    dur = random.randint(15, 30)
                _is_mustdo = (cat == "勉強" and tn in s.get("mustdo_list", []))
                st.session_state.current_task = {"カテゴリ": cat, "タスク": tn, "duration": dur, "mustdo": _is_mustdo}
                st.session_state.start_time = time.time()
                st.session_state.force_study_only = False
                st.session_state.last_was_refresh = (cat == "気分転換")
                st.session_state.rolled_options = None
                st.session_state.page = 'active'
                st.session_state.compact_mode = False
                commit_rerun()
    st.divider()
    st.markdown("##### 🏁 残り作業可能時間（目標まで）")
    td = datetime.now().date()
    goals = s.get("goals", [])
    for row_start in range(0, len(goals), 2):
        row = goals[row_start:row_start + 2]
        _cards = ""
        for g in row:
            try:
                _gd = datetime.strptime(g.get("date", td.isoformat()), "%Y-%m-%d").date()
            except Exception:
                _gd = td
            days = max((_gd - td).days, 0)
            hours = int(g.get("hours", 2))
            _cards += (
                "<div class='milestone-card' style='flex:1; margin-top:0; box-sizing:border-box; "
                "display:flex; flex-direction:column; text-align:center;'>"
                # 目標名+残り日数は行数がバラつくので min-height で固定 → 下の要素が横で揃う
                f"<div style='color:#ccc; min-height:3.4em; display:flex; align-items:center; justify-content:center;'>"
                f"{g.get('name','目標')} ({g.get('date','')}) まであと {days} 日</div>"
                "<div style='color:#ccc; margin-top:2px;'>🔥 残り作業可能</div>"
                f"<div class='glowing-hours'>{days * hours} <span style='font-size:1.5rem;color:white;'>時間</span></div></div>"
            )
        # align-items:stretch で、隣のブロックと高さを一番高いものに揃える
        st.markdown(
            f"<div style='display:flex; align-items:stretch; gap:12px; margin-top:10px;'>{_cards}</div>",
            unsafe_allow_html=True)
def today_remaining_hours():
    """今日まだ勉強に使える残り時間（h）と、その曜日の時間帯を返す"""
    s = st.session_state.settings
    win = s.get("daily_window", [])
    wd = datetime.now().weekday()
    w = win[wd] if wd < len(win) else {"start": "09:00", "end": "22:00"}
    try:
        sh, sm = [int(x) for x in str(w.get("start", "09:00")).split(":")[:2]]
        eh, emn = [int(x) for x in str(w.get("end", "22:00")).split(":")[:2]]
    except Exception:
        sh, sm, eh, emn = 9, 0, 22, 0
    now = datetime.now()
    start_dt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end_dt = now.replace(hour=eh, minute=emn, second=0, microsecond=0)
    eff = max(now, start_dt)
    remaining = max(0.0, (end_dt - eff).total_seconds() / 3600.0)
    return remaining, w
def today_intervals_ms():
    """今日の『勉強できる時間帯』を [開始ms, 終了ms] のリストで返す"""
    s = st.session_state.settings
    routine = s.get("daily_routine", [])
    wd = datetime.now().weekday()
    blocks = routine[wd] if wd < len(routine) else []
    now = datetime.now()
    out = []
    for b in blocks:
        try:
            sh, sm = [int(x) for x in str(b.get("start", "09:00")).split(":")[:2]]
            eh, emn = [int(x) for x in str(b.get("end", "22:00")).split(":")[:2]]
        except Exception:
            continue
        sdt = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        edt = now.replace(hour=eh, minute=emn, second=0, microsecond=0)
        if edt > sdt:
            out.append([int(sdt.timestamp() * 1000), int(edt.timestamp() * 1000)])
    return out
def render_progress():
    s = st.session_state.settings
    current_study = st.session_state.study_time_total
    st.subheader("📊 今日の進捗")
    _ivs = today_intervals_ms()
    _ivs_json = json.dumps(_ivs)
    components.html(f"""
    <div style="background: linear-gradient(135deg, rgba(20,33,15,0.9) 0%, rgba(30,30,30,0.9) 100%);
                border:2px solid #4CAF50; border-radius:14px; padding:14px; text-align:center;
                font-family:'Segoe UI',sans-serif; box-sizing:border-box;">
      <div style="font-size:1.05rem;color:#ccc;">🕐 今日まだ勉強できる時間</div>
      <div id="rcd" style="font-size:2.4rem;font-weight:900;color:#4CAF50;line-height:1.25;">--</div>
      <div style="font-size:0.8rem;color:#999;">勉強できる時間帯のみで計算（大学・食事などは除外）</div>
    </div>
    <script>
      const IV = {_ivs_json};
      const el = document.getElementById('rcd');
      function tick() {{
        const now = Date.now();
        let total = 0;
        for (const p of IV) {{ if (now < p[1]) total += (p[1] - Math.max(now, p[0])); }}
        let r = Math.floor(total / 1000);
        if (r <= 0) {{ el.innerText = "本日は終了です"; el.style.color = "#ff5252"; return; }}
        el.style.color = "#4CAF50";
        const h = Math.floor(r / 3600), m = Math.floor((r % 3600) / 60), sc = r % 60;
        el.innerText = (h > 0 ? h + "時間 " : "") + m + "分 " + sc + "秒";
      }}
      tick(); setInterval(tick, 1000);
    </script>
    """, height=175)
    if not st.session_state.target_locked:
        cur = st.number_input("今日の目標勉強時間(分)", min_value=30, value=int(st.session_state.target_value), step=30, key="target_input_widget")
        st.caption("⚠️ 一度確定すると、今日はもう変更できません。")
        if st.button("✅ この目標で今日を確定する", key="lock_target"):
            st.session_state.target_value = int(cur)
            st.session_state.target_locked = True
            commit_rerun()
        target_time = int(cur)
    else:
        target_time = int(st.session_state.target_value)
        h, m = target_time // 60, target_time % 60
        st.markdown(f"""
        <div class='goal-time-card'>
            <div class='goal-time-label'>本日の目標（確定済み・変更不可）</div>
            <div class='goal-time-value' style='font-size:2.4rem;'>{h}時間 {m}分 0秒</div>
            <div class='goal-time-label'>（合計 {target_time}分）</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("🔒 本日は確定済みです（日付が変わるとリセット）。")
    progress_percent = min(current_study / target_time, 1.0) if target_time > 0 else 1.0
    remaining_time = max(0, target_time - current_study)
    deg = int(progress_percent * 360)
    circle_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 10px;">
        <div style="width: 180px; height: 180px; border-radius: 50%;
            background: conic-gradient(#4CAF50 {deg}deg, rgba(255,255,255,0.1) {deg}deg);
            display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(0,0,0,0.5);">
            <div style="width: 140px; height: 140px; border-radius: 50%; background-color: rgba(20, 24, 30, 0.95);
                display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <span style="font-size: 2.5rem; font-weight: bold; color: #4CAF50;">{int(progress_percent*100)}%</span>
            </div>
        </div>
    </div>
    """
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.markdown(circle_html, unsafe_allow_html=True)
    with c2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.metric("今日の勉強時間", f"{current_study} 分")
        st.caption(f"目標まであと: {remaining_time} 分")
    with c3:
        st.write("<br><br>", unsafe_allow_html=True)
        st.metric("今日の気分転換", f"{st.session_state.refresh_time_total} 分")
# ----------------------------------------------------
# ダッシュボード画面
# ----------------------------------------------------
def render():
    app_mode = st.session_state.get("app_mode_radio", "🚀 集中モード (Use)")
    st.title("☕ Focus & Cafe Roulette")
    s = st.session_state.settings

    if app_mode == "🛠️ 編集モード (Edit)":
        # 列間ショートカット（編集モードのスクロール削減）
        st.markdown('''
        <div style="display:flex; gap:8px; flex-wrap:wrap; margin:4px 0 12px 0;">
          <a href="#anchor-settings" style="text-decoration:none; background:rgba(76,175,80,0.25); border:1px solid #4CAF50; color:#fff; padding:8px 14px; border-radius:20px; font-weight:bold;">⚙️ 設定パネルへ</a>
          <a href="#anchor-roulette" style="text-decoration:none; background:rgba(33,150,243,0.25); border:1px solid #2196F3; color:#fff; padding:8px 14px; border-radius:20px; font-weight:bold;">📝 ルーレット項目へ</a>
          <a href="#anchor-tabs" style="text-decoration:none; background:rgba(255,193,7,0.25); border:1px solid #ffc107; color:#fff; padding:8px 14px; border-radius:20px; font-weight:bold;">📊 ルーレット/進捗へ</a>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div id="anchor-settings"></div>', unsafe_allow_html=True)
        st.markdown("#### ⚙️ 設定パネル")
        st.caption("🔧 build 2026-06-26e（全削除=世代キー統一）— この表示が出ていれば最新コードが動いています")
        goals = s.get("goals", [])
        # 【世代キー方式】目標を削除したら gen を +1（全行のキーを作り直す＝確実に押した行が消える）
        _ggen = st.session_state.get("goals_gen", 0)

        # 🏷️ 目標物の名前（追加・削除もここ）
        with st.expander("🏷️ 目標物の名前", expanded=False):
            for i, g in enumerate(goals):
                nc1, nc2 = st.columns([6, 1])
                with nc1:
                    nv = st.text_input(f"目標{i+1}の名前", value=g.get("name", ""), key=f"gname_{_ggen}_{i}", label_visibility="collapsed")
                    if nv != g.get("name", ""):
                        g["name"] = nv
                        save_settings(s)
                with nc2:
                    if st.button("🗑", key=f"gdel_{_ggen}_{i}"):
                        if len(goals) > 1:
                            goals.pop(i)
                            save_settings(s)
                            st.session_state["goals_gen"] = _ggen + 1
                            commit_rerun()
                        else:
                            st.toast("⚠️ 目標は最低1つ必要です")
            if len(goals) < GOAL_CAP:
                if st.button("➕ 目標を追加", key="add_goal"):
                    goals.append({"name": "新しい目標", "date": date.today().isoformat(), "hours": 2})
                    save_settings(s)
                    commit_rerun()
            else:
                st.caption(f"見やすさのため目標は最大{GOAL_CAP}個までです。")

        # 🖼️ 背景画像のURL
        with st.expander("🖼️ 背景画像のURL（カフェ画像用）", expanded=False):
            new_bg = st.text_input("背景画像のURL (画像アドレスを貼り付け)", value=s.get("bg_url", ""), label_visibility="collapsed")
            if st.button("💾 背景URLを保存", key="save_bgurl"):
                s["bg_url"] = new_bg
                save_settings(s)
                st.toast("保存しました ✅")
                commit_rerun()

        # 📅 目標の日付・1日の作業時間
        with st.expander("📅 目標の日付・1日の作業時間", expanded=False):
            _today = date.today()
            for i, g in enumerate(goals):
                st.markdown(f"**{g.get('name', '目標'+str(i+1))}**")
                try:
                    _saved = datetime.strptime(g.get("date", _today.isoformat()), "%Y-%m-%d").date()
                except Exception:
                    _saved = _today
                _default = _saved if _saved >= _today else _today
                dc1, dc2 = st.columns([2, 1])
                with dc1:
                    nd = st.date_input("日付", _default, key=f"gdate_{_ggen}_{i}")
                with dc2:
                    nh = st.number_input("1日の時間", 1, 24, int(g.get("hours", 2)), key=f"ghours_{_ggen}_{i}")
                if _saved < _today:
                    st.caption("⚠️ 保存日が過去のため初期値を今日にしています。")
                _newdate = nd.strftime("%Y-%m-%d")
                if _newdate != g.get("date") or int(nh) != int(g.get("hours", 2)):
                    g["date"] = _newdate
                    g["hours"] = int(nh)
                    save_settings(s)
                st.markdown("---")

        # ⏱️ 勉強タスクの所要時間（独立ブロック）
        with st.expander("⏱️ 勉強タスクの所要時間", expanded=False):
            st.caption("下限は30分で固定。上限はスライダーで一気に、±ボタンや直接入力（10刻み・キーボード可）でも変更できます。")
            if "study_max_val" not in st.session_state:
                st.session_state.study_max_val = int(s.get("study_dur_max", 60))
            _cur = int(st.session_state.study_max_val)
            def _apply_max(v):
                st.session_state.study_max_val = max(30, min(600, int(v)))
                s["study_dur_min"] = 30
                s["study_dur_max"] = st.session_state.study_max_val
                save_settings(s)
            # スライダー：ドラッグした分だけ一気に変えられる（長押し加速の代わり）
            sv = st.slider("上限(分)・スライダーで素早く調整", min_value=30, max_value=600,
                           value=_cur, step=10, key=f"smax_slider_{_cur}")
            if int(sv) != _cur:
                _apply_max(sv); commit_rerun()
            # ±ボタン（10刻み・大きく動かす用に30も）
            qc = st.columns(4)
            if qc[0].button("−30", key="smx_m30"):
                _apply_max(_cur - 30); commit_rerun()
            if qc[1].button("−10", key="smx_m10"):
                _apply_max(_cur - 10); commit_rerun()
            if qc[2].button("＋10", key="smx_p10"):
                _apply_max(_cur + 10); commit_rerun()
            if qc[3].button("＋30", key="smx_p30"):
                _apply_max(_cur + 30); commit_rerun()
            # 直接入力（キーボード／ネイティブ±は10刻み・下限30固定）
            nv = st.number_input("上限(分)・直接入力 ※下限は30分固定", min_value=30, step=10,
                                 value=_cur, key=f"smax_num_{_cur}")
            if int(nv) != _cur:
                _apply_max(nv); commit_rerun()
            st.info(f"勉強タスクは 30分 〜 {st.session_state.study_max_val}分 の範囲でランダムになります。")

        # 🕐 勉強できる時間帯（曜日別・複数OK）
        with st.expander("🕐 勉強できる時間帯（曜日別・複数OK）", expanded=False):
            st.caption("曜日ごとに『勉強できる時間帯』を複数登録できます（大学・食事の時間は除いて登録）。ダッシュボードの『今日まだ勉強できる時間』に反映されます。")
            import datetime as _dt
            _days = ["月", "火", "水", "木", "金", "土", "日"]
            _routine = s.get("daily_routine", [])
            while len(_routine) < 7:
                _routine.append([{"start": "09:00", "end": "22:00"}])
            for _di, _dn in enumerate(_days):
                _rgen = st.session_state.get(f"rt_gen_{_di}", 0)
                st.markdown(f"**{_dn}曜日**")
                if not _routine[_di]:
                    st.caption("（時間帯なし）")
                for _ri, _iv in enumerate(_routine[_di]):
                    rc1, rc2, rc3 = st.columns([2, 2, 1])
                    try:
                        _sh, _sm = [int(x) for x in str(_iv.get("start", "09:00")).split(":")[:2]]
                        _eh, _emn = [int(x) for x in str(_iv.get("end", "22:00")).split(":")[:2]]
                    except Exception:
                        _sh, _sm, _eh, _emn = 9, 0, 22, 0
                    with rc1:
                        _stt = st.time_input("開始", value=_dt.time(_sh, _sm), key=f"rt_s_{_di}_{_rgen}_{_ri}", label_visibility="collapsed")
                    with rc2:
                        _ent = st.time_input("終了", value=_dt.time(_eh, _emn), key=f"rt_e_{_di}_{_rgen}_{_ri}", label_visibility="collapsed")
                    with rc3:
                        if st.button("🗑", key=f"rt_del_{_di}_{_rgen}_{_ri}"):
                            _routine[_di].pop(_ri)
                            s["daily_routine"] = _routine
                            save_settings(s)
                            st.session_state[f"rt_gen_{_di}"] = _rgen + 1
                            commit_rerun()
                    _ns = _stt.strftime("%H:%M"); _ne = _ent.strftime("%H:%M")
                    if _ns != _iv.get("start") or _ne != _iv.get("end"):
                        _iv["start"] = _ns; _iv["end"] = _ne
                        s["daily_routine"] = _routine
                        save_settings(s)
                if st.button(f"➕ {_dn}に時間帯を追加", key=f"rt_add_{_di}"):
                    _routine[_di].append({"start": "09:00", "end": "12:00"})
                    s["daily_routine"] = _routine
                    save_settings(s)
                    commit_rerun()
                st.markdown("---")

        st.markdown('<div id="anchor-roulette"></div>', unsafe_allow_html=True)
        st.markdown("#### 📝 ルーレット項目（トグルで開閉・1個ずつ編集）")
        st.caption("文字を変えるとその場で自動保存。追加は Enter か『➕ 追加』で確定します。")
        _mustdo_n = len([t for t in s.get("mustdo_list", []) if t not in s.get("mustdo_list_disabled", [])])
        with st.expander(f"🔴 今日絶対やる（{_mustdo_n}件）— あれば勉強はここからのみ抽選", expanded=(_mustdo_n > 0)):
            st.caption("ここに項目があると、勉強の抽選はこのリストだけから出ます。空になると通常勉強に戻ります。タスク終了後に『消す』と答えると自動で消えます。")
            edit_list_ui("今日絶対やる", "mustdo_list", "add_mustdo")
        with st.expander("📘 通常勉強", expanded=False):
            edit_list_ui("通常勉強", "study_list", "add_study")
        with st.expander("🔥 重点(3倍)", expanded=False):
            edit_list_ui("🔥 重点(3倍)", "focus_study_list", "add_focus")
        with st.expander("☕ 気分転換", expanded=False):
            edit_list_ui("気分転換", "refresh_list", "add_refresh")

    # ▼ ルーレット＆残り作業可能時間 と 今日の進捗 を 1ページに左右2分割で表示 ▼
    st.markdown('<div id="anchor-tabs"></div>', unsafe_allow_html=True)
    _left, _right = st.columns([1.05, 1], gap="large")
    with _left:
        st.markdown("#### 🎲 ルーレット ＆ 残り作業可能時間")
        render_roulette_and_goals()
    with _right:
        render_progress()
# ----------------------------------------------------
# 画面2: アクティブ（集中モード）
# ----------------------------------------------------