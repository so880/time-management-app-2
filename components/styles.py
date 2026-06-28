import streamlit as st

GLOBAL_CSS = '''<style>
    [data-testid="stHeader"] { background-color: transparent !important; }

    .block-container {
        background: rgba(14, 17, 23, 0.75) !important;
        border-radius: 15px; padding: 2rem !important; margin-top: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] {
        background: rgba(14, 17, 23, 0.65) !important;
        backdrop-filter: blur(15px); border-right: 1px solid rgba(255,255,255,0.1);
    }
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    div[data-testid="metric-container"] {
        background-color: rgba(30, 30, 30, 0.7); border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;
    }

    .stButton>button {
        border-radius: 8px; border: 2px solid #4CAF50; background-color: rgba(0,0,0,0.5);
        color: #4CAF50; font-weight: bold; font-size: 1.3rem; backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #4CAF50; color: #000; box-shadow: 0 0 15px rgba(76,175,80,0.8); }

    /* ★Fix1: ルーレット/スタートボタンを特に大きく */
    .st-key-roulette_btn button, div[data-testid="stForm"] button {
        font-size: 1.8rem !important;
        padding: 22px 24px !important;
        border-width: 3px !important;
    }

    button[kind="primary"] { border: 2px solid #ff4b4b !important; color: #ff4b4b !important; }
    button[kind="primary"]:hover { background-color: #ff4b4b !important; color: #fff !important; box-shadow: 0 0 15px rgba(255,75,75,0.8) !important; }
    @keyframes pulse { 0% {transform: scale(1); text-shadow: 0 0 10px rgba(255,235,59,0.5);} 50% {transform: scale(1.03); text-shadow: 0 0 25px rgba(255,235,59,1);} 100% {transform: scale(1); text-shadow: 0 0 10px rgba(255,235,59,0.5);} }

    .milestone-card {
        background: linear-gradient(135deg, rgba(30,30,30,0.8) 0%, rgba(42,42,42,0.8) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-left: 6px solid #ffeb3b;
        padding: 20px; border-radius: 12px; text-align: center; margin-top: 10px;
    }
    .glowing-hours { animation: pulse 2s infinite; color: #ffeb3b; font-size: 3rem; font-weight: bold; margin-top: 5px; }

    /* ★Fix3/4: 確定済みの目標時間を大きく表示 */
    .goal-time-card {
        background: linear-gradient(135deg, rgba(20,33,15,0.85) 0%, rgba(30,30,30,0.85) 100%);
        border: 2px solid #4CAF50; border-radius: 14px; padding: 16px 24px;
        text-align: center; margin: 6px 0 4px 0;
    }
    .goal-time-label { font-size: 1.15rem; color: #ccc; }
    .goal-time-value { font-size: 4rem; font-weight: 900; color: #4CAF50; line-height: 1.1; }
    .goal-time-unit { font-size: 1.5rem; color: #fff; }
</style>'''

COMPACT_CSS = '''    <style>
        .block-container {
            background: transparent !important;
            box-shadow: none !important;
            border: none !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            padding-top: 0rem !important;
            padding-left: 1rem !important;
        }
        .stButton>button {
            padding: 4px 10px !important;
            font-size: 1rem !important;
            width: auto !important;
            background-color: rgba(0,0,0,0.6) !important;
            color: #fff !important;
            border-color: rgba(255,255,255,0.2) !important;
        }
    </style>'''

def inject_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def inject_compact_styles():
    st.markdown(COMPACT_CSS, unsafe_allow_html=True)
