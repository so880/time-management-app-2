import os

# === パス：config.py の場所を基準にする ===
# どのフォルダから `streamlit run app.py` しても、必ず同じ data/ を使うので
# 設定や進捗の保存が「消える」ことがなくなる。
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_BASE_DIR, "data")
BG_DIR = os.path.join(_BASE_DIR, "bg_images")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BG_DIR, exist_ok=True)
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
LOG_FILE = os.path.join(DATA_DIR, "activity_log.csv")
SESSION_FILE = os.path.join(DATA_DIR, "session_state.json")

# === 定数 ===
SHORT_TASK_THRESHOLD = 40  # これ以下(分)の勉強課題は「短い課題」
GOAL_CAP = 6               # 目標は最大6個まで
GAME_LIST = ["イナイレ", "スト６", "バウンティ", "ドラゴンボールスクアドラ"]
SOS_LIST = ["瞑想", "深呼吸", "腹筋30回", "昼寝", "読書", "Geminiと話す"]

# === 初期設定 ===
DEFAULT_SETTINGS = {
    "toeic_date": "2026-05-24",
    "intern_date": "2026-06-01",
    "daily_hours_toeic": 3,
    "daily_hours_intern": 2,
    "study_dur_min": 30,   # 勉強タスクのランダム所要時間（最短・分）※30分固定
    "study_dur_max": 60,   # 勉強タスクのランダム所要時間（最長・分）
    "daily_routine": [     # 曜日別の「勉強できる時間帯」(複数OK・月=0 ... 日=6)
        [{"start": "09:00", "end": "22:00"}],
        [{"start": "09:00", "end": "22:00"}],
        [{"start": "09:00", "end": "22:00"}],
        [{"start": "09:00", "end": "22:00"}],
        [{"start": "09:00", "end": "22:00"}],
        [{"start": "10:00", "end": "23:00"}],
        [{"start": "10:00", "end": "23:00"}],
    ],
    "daily_window": [      # 曜日別の「勉強に使える時間帯」(月=0 ... 日=6)
        {"start": "09:00", "end": "22:00"},
        {"start": "09:00", "end": "22:00"},
        {"start": "09:00", "end": "22:00"},
        {"start": "09:00", "end": "22:00"},
        {"start": "09:00", "end": "22:00"},
        {"start": "10:00", "end": "23:00"},
        {"start": "10:00", "end": "23:00"},
    ],
    "goals": [             # 目標（可変個）
        {"name": "TOEIC", "date": "2026-05-24", "hours": 3},
        {"name": "インターン", "date": "2026-06-01", "hours": 2},
    ],
    "study_list_disabled": [],   # 無効化した通常勉強項目
    "focus_study_list_disabled": [],
    "refresh_list_disabled": [],
    "mustdo_list_disabled": [],
    "toeic_name": "TOEIC",
    "intern_name": "インターン",
    "bg_url": "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?q=80&w=2000&auto=format&fit=crop",
    "bg_mode": "カフェ画像",
    "bg_history": [],       # 過去にアップロードした画像ファイル名の履歴
    "bg_current_file": "",  # 現在選択中のアップロード画像ファイル名
    "snd_cafe_url": "e_04ZrNroTo",   # 環境音「カフェ」のYouTube URL/ID（変更可）
    "snd_chat_url": "bZ2XhA_kXYQ",   # 環境音「雑踏」のYouTube URL/ID（変更可）
    "snd_relax_url": "vPhg6sc1Mk4",  # 環境音「波と鯨」のYouTube URL/ID（変更可）
    "mustdo_list": [],   # 今日絶対やる（あれば勉強の抽選はここからのみ。空になると通常へ）
    "study_list": [
        "Santa Part7長文の写経", "英語の記事の写経", "Gemini提案英文の写経",
        "プログラミング(paiza)", "洋楽の本気カラオケ(英語発音)",
        "Santa Part3・4のオーバーラッピング", "海外車レビュー記事の音読・写経",
        "Santa 単語", "Geminiと面接練習"
    ],
    "focus_study_list": ["大学の履修について考える"],
    "refresh_list": [
        "料理探し", "読書", "仮眠", "腕立て30回", "腹筋30回",
        "ダンベル30回", "洋楽カラオケ", "机の掃除", "床の片づけ",
        "掃除機掛け", "スト6 コンボ練習"
    ]
}