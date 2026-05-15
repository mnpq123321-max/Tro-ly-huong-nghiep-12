"""
╔══════════════════════════════════════════════════════════════════╗
║   THẦY T — HƯỚNG NGHIỆP 12 PRO  ·  v7.0                         ║
║   Gemini 2.5 Flash · Streaming · Charts · Templates · Calendar   ║
╚══════════════════════════════════════════════════════════════════╝

NÂNG CẤP v7.0:
  📈 Score trend charts (Plotly) — tự động vẽ biểu đồ điểm chuẩn
  💡 Smart follow-up suggestions — AI đề xuất 3 câu hỏi tiếp theo
  📋 Quick Templates — bộ câu hỏi mẫu theo chủ đề
  📅 Lịch tuyển sinh 2026 — timeline các mốc quan trọng
  🔍 Search xuyên suốt — tìm qua toàn bộ lịch sử chat

requirements.txt:
  google-genai
  streamlit
  plotly
"""

import streamlit as st
import datetime, re, json, time, uuid
from collections import Counter

# ════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Thầy T — Hướng Nghiệp 12",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Plotly (optional — graceful fallback)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ════════════════════════════════════════════════════════
#  CSS
# ════════════════════════════════════════════════════════
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:#0d1117;min-height:100vh;color:#e6edf3}

::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#0d1117}
::-webkit-scrollbar-thumb{background:#30363d;border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#58a6ff}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{background:#010409!important;border-right:1px solid #21262d!important}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small{color:#8b949e!important}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{color:#e6edf3!important;font-family:'Playfair Display',serif!important}
[data-testid="stSidebar"] hr{border-color:#21262d!important;margin:10px 0!important}
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stTextArea"] textarea{
    background:#161b22!important;border:1px solid #30363d!important;
    color:#e6edf3!important;border-radius:8px!important;font-size:.87rem!important}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
[data-testid="stSidebar"] [data-testid="stTextArea"] textarea:focus{
    border-color:#d4a017!important;box-shadow:0 0 0 3px rgba(212,160,23,.12)!important}
[data-testid="stSidebar"] [data-testid="stSelectbox"]>div>div{
    background:#161b22!important;border:1px solid #30363d!important;
    color:#e6edf3!important;border-radius:8px!important}
[data-testid="stSidebar"] .stButton>button{
    width:100%!important;background:#161b22!important;border:1px solid #30363d!important;
    color:#8b949e!important;border-radius:9px!important;font-size:.84rem!important;
    font-weight:600!important;padding:9px 0!important;transition:all .15s!important}
[data-testid="stSidebar"] .stButton>button:hover{
    border-color:#d4a017!important;color:#d4a017!important;background:rgba(212,160,23,.06)!important}

/* ── LAYOUT ── */
.main .block-container{padding:0!important;max-width:100%!important}

/* ── HERO ── */
.hero{background:linear-gradient(135deg,#010409 0%,#0d1117 50%,#121820 100%);
    border-bottom:1px solid #21262d;padding:22px 40px;position:relative;overflow:hidden}
.hero::after{content:'';position:absolute;top:-60px;right:-60px;width:300px;height:300px;
    border-radius:50%;background:radial-gradient(circle,rgba(212,160,23,.07) 0%,transparent 70%);
    pointer-events:none}
.hero-inner{display:flex;align-items:center;justify-content:space-between;gap:20px;position:relative;z-index:1}
.hero-eyebrow{display:inline-flex;align-items:center;gap:6px;background:rgba(212,160,23,.1);
    border:1px solid rgba(212,160,23,.28);color:#d4a017;border-radius:20px;padding:4px 14px;
    font-size:.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
.hero-title{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:900;color:#f0f6fc;line-height:1.15}
.hero-title .gold{color:#d4a017;font-style:italic}
.hero-sub{font-size:.81rem;color:#8b949e;margin-top:5px;line-height:1.6}
.hero-chips{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.hchip{border-radius:20px;padding:4px 12px;font-size:.67rem;font-weight:600;white-space:nowrap;letter-spacing:.3px}
.hc-def{background:#161b22;border:1px solid #30363d;color:#8b949e}
.hc-live{background:rgba(35,197,94,.1);border:1px solid rgba(35,197,94,.3);color:#3fb950}
.hc-gold{background:rgba(212,160,23,.1);border:1px solid rgba(212,160,23,.3);color:#d4a017}
.hc-blue{background:rgba(88,166,255,.08);border:1px solid rgba(88,166,255,.25);color:#79c0ff}
.hc-purple{background:rgba(139,92,246,.1);border:1px solid rgba(139,92,246,.3);color:#c4b5fd}
.hc-green{background:rgba(63,185,80,.1);border:1px solid rgba(63,185,80,.3);color:#3fb950}

/* ── TABS ── */
[data-testid="stTabs"] [data-testid="stTab"]{
    background:transparent!important;color:#8b949e!important;border:none!important;
    border-bottom:2px solid transparent!important;font-weight:600!important;
    font-size:.85rem!important;padding:9px 16px!important;transition:all .15s!important}
[data-testid="stTabs"] [data-testid="stTab"]:hover{color:#e6edf3!important}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"]{color:#d4a017!important;border-bottom:2px solid #d4a017!important}
[data-testid="stTabsContent"]{padding-top:16px!important}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;
    box-shadow:none!important;padding:0!important;margin-bottom:20px!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"]{
    background:#1c2128!important;color:#e6edf3!important;border:1px solid #30363d!important;
    border-radius:18px 18px 4px 18px!important;padding:12px 17px!important;
    font-size:.94rem!important;line-height:1.7!important;max-width:76%!important;margin-left:auto!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"]{
    background:#161b22!important;color:#c9d1d9!important;border:1px solid #21262d!important;
    border-radius:4px 18px 18px 18px!important;padding:20px 24px!important;
    font-size:.95rem!important;line-height:1.85!important;box-shadow:0 4px 28px rgba(0,0,0,.3)!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h1,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h3{
    font-family:'Playfair Display',serif!important;color:#f0f6fc!important;
    margin-top:20px!important;margin-bottom:7px!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) strong{color:#d4a017!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) a{color:#79c0ff!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) li{margin-bottom:4px}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) hr{border-color:#21262d!important;margin:14px 0!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) code{
    background:#0d1117!important;color:#79c0ff!important;border-radius:4px;
    padding:1px 6px;font-size:.86em;border:1px solid #21262d}

/* ── TABLES ── */
.dct-wrap{overflow-x:auto;margin:16px 0 6px;border-radius:12px;border:1px solid #21262d}
.dct{width:100%;border-collapse:collapse;font-size:.86rem}
.dct thead tr{background:#010409}
.dct thead th{padding:11px 14px;text-align:left;font-weight:700;white-space:nowrap;
    color:#d4a017;font-size:.67rem;letter-spacing:1.2px;text-transform:uppercase;border-bottom:1px solid #21262d}
.dct tbody tr{border-bottom:1px solid #161b22;transition:background .12s}
.dct tbody tr:last-child{border-bottom:none}
.dct tbody tr:hover{background:rgba(212,160,23,.03)}
.dct td{padding:10px 14px;color:#8b949e;vertical-align:middle}
.dct td:first-child{color:#e6edf3;font-weight:600;min-width:185px}
.sb-r{display:inline-block;background:#161b22;border:1px solid rgba(212,160,23,.5);
    color:#d4a017;border-radius:6px;padding:2px 9px;font-weight:700;font-size:.84rem}
.sb-n{display:inline-block;background:#161b22;border:1px solid #30363d;
    color:#484f58;border-radius:6px;padding:2px 9px;font-size:.83rem}
.sb-p{display:inline-block;background:linear-gradient(135deg,rgba(139,92,246,.2),rgba(124,58,237,.12));
    border:1px solid rgba(139,92,246,.45);color:#c4b5fd;border-radius:6px;padding:2px 9px;font-weight:700;font-size:.84rem}
.sb-c{display:inline-block;background:#1c2128;border:1px solid #30363d;
    color:#8b949e;border-radius:5px;padding:2px 7px;font-size:.74rem;font-weight:600}
.au{color:#3fb950;font-weight:700} .ad{color:#f85149;font-weight:700} .af{color:#8b949e;font-weight:700}
.note-src{background:rgba(212,160,23,.05);border:1px solid rgba(212,160,23,.18);
    border-radius:9px;padding:9px 14px;margin-top:7px;font-size:.77rem;color:#8b949e;line-height:1.6}

/* ── FOLLOW-UP CHIPS ── */
.fu-wrap{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;padding-top:12px;border-top:1px solid #21262d}
.fu-lbl{font-size:.68rem;color:#484f58;letter-spacing:1.5px;text-transform:uppercase;
    width:100%;margin-bottom:2px}

/* ── TEMPLATE CARD ── */
.tpl-section{margin-bottom:20px}
.tpl-title{font-size:.72rem;color:#8b949e;font-weight:700;letter-spacing:1.5px;
    text-transform:uppercase;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid #21262d}

/* ── CALENDAR ── */
.cal-month{margin-bottom:24px}
.cal-month-title{font-family:'Playfair Display',serif;font-size:1.05rem;
    color:#f0f6fc;font-weight:700;margin-bottom:12px}
.cal-event{display:flex;gap:14px;padding:11px 16px;background:#161b22;
    border:1px solid #21262d;border-radius:10px;margin-bottom:8px;align-items:flex-start}
.cal-event.urgent{border-color:rgba(248,81,73,.35);background:rgba(248,81,73,.04)}
.cal-event.important{border-color:rgba(212,160,23,.3);background:rgba(212,160,23,.04)}
.cal-event.info{border-color:rgba(88,166,255,.25);background:rgba(88,166,255,.04)}
.cal-date{font-weight:800;font-size:.82rem;color:#d4a017;min-width:70px;padding-top:2px}
.cal-content .cal-name{font-weight:600;color:#e6edf3;font-size:.9rem;margin-bottom:3px}
.cal-content .cal-desc{font-size:.8rem;color:#8b949e;line-height:1.55}
.cal-tag{display:inline-block;border-radius:5px;padding:2px 8px;
    font-size:.68rem;font-weight:700;letter-spacing:.5px;margin-top:5px}
.tag-urgent{background:rgba(248,81,73,.15);color:#f85149;border:1px solid rgba(248,81,73,.3)}
.tag-important{background:rgba(212,160,23,.12);color:#d4a017;border:1px solid rgba(212,160,23,.25)}
.tag-info{background:rgba(88,166,255,.08);color:#79c0ff;border:1px solid rgba(88,166,255,.2)}
.tag-done{background:rgba(63,185,80,.1);color:#3fb950;border:1px solid rgba(63,185,80,.25)}

/* ── SEARCH RESULT ── */
.sr-card{background:#161b22;border:1px solid #21262d;border-radius:10px;
    padding:14px 17px;margin-bottom:10px}
.sr-student{font-size:.72rem;color:#d4a017;font-weight:700;letter-spacing:.5px;
    text-transform:uppercase;margin-bottom:5px}
.sr-q{font-weight:600;color:#e6edf3;font-size:.9rem;margin-bottom:6px}
.sr-preview{font-size:.84rem;color:#8b949e;line-height:1.6}
.sr-highlight{background:rgba(212,160,23,.2);color:#d4a017;
    border-radius:3px;padding:0 3px;font-weight:600}

/* ── STUDENT CARD ── */
.stu-card{background:#161b22;border:1px solid #21262d;border-radius:10px;
    padding:11px 14px;margin-bottom:7px;transition:all .15s;position:relative}
.stu-card:hover{border-color:#30363d}
.stu-card.active{border-color:#d4a017;background:rgba(212,160,23,.06)}
.stu-card .sname{font-weight:700;font-size:.88rem;color:#e6edf3}
.stu-card .sinfo{font-size:.74rem;color:#8b949e;margin-top:3px}
.stu-card .sbadge{position:absolute;top:9px;right:11px;background:rgba(212,160,23,.15);
    border:1px solid rgba(212,160,23,.3);color:#d4a017;border-radius:5px;
    padding:1px 7px;font-size:.67rem;font-weight:700}

/* ── DASH STAT ── */
.dash-stat{background:#161b22;border:1px solid #21262d;border-radius:10px;
    padding:15px 17px;text-align:center}
.dash-stat .ds-val{font-size:1.9rem;font-weight:800;color:#d4a017;font-family:'Playfair Display',serif}
.dash-stat .ds-lbl{font-size:.7rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px;margin-top:3px}

/* ── BOOKMARK ── */
.bk-card{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:13px 16px;margin-bottom:8px}
.bk-q{font-size:.81rem;color:#8b949e;margin-bottom:4px}
.bk-preview{font-size:.87rem;color:#c9d1d9;line-height:1.6;
    display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}

/* ── MISC ── */
#MainMenu,footer,header{visibility:hidden}
[data-testid="stDecoration"]{display:none}
hr{border-color:#21262d!important}
.slbl{font-size:.64rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#484f58;margin:8px 0 12px}
.sc{background:#161b22;border:1px solid #21262d;border-radius:9px;padding:10px 14px;margin-bottom:7px}
.sc-l{font-size:.64rem;color:#8b949e;font-weight:700;letter-spacing:1.2px;text-transform:uppercase}
.sc-v{font-size:.96rem;color:#e6edf3;font-weight:700;margin-top:3px}
.sc-v.g{color:#d4a017}
.step-bar{display:flex;align-items:center;gap:8px;padding:11px 16px;background:#161b22;
    border:1px solid #21262d;border-radius:10px;margin-bottom:8px;font-size:.86rem;color:#8b949e}
.step-bar .ico{font-size:1.05rem} .step-bar .txt{flex:1}
.step-bar .spin{width:16px;height:16px;border:2.5px solid #21262d;border-top:2.5px solid #d4a017;
    border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}
@keyframes spin{to{transform:rotate(360deg)}}
[data-testid="stDownloadButton"]>button{background:#161b22!important;border:1px solid #30363d!important;
    color:#8b949e!important;border-radius:9px!important;font-size:.83rem!important;
    width:100%!important;transition:all .2s!important}
[data-testid="stDownloadButton"]>button:hover{border-color:#d4a017!important;color:#d4a017!important}
[data-testid="stChatInput"]>div{background:#161b22!important;border:1.5px solid #30363d!important;
    border-radius:14px!important;transition:border-color .2s!important}
[data-testid="stChatInput"]>div:focus-within{border-color:#d4a017!important}
[data-testid="stChatInput"] textarea{color:#e6edf3!important;font-family:'Inter',sans-serif!important;font-size:.93rem!important;background:transparent!important}
[data-testid="stChatInput"] textarea::placeholder{color:#484f58!important}
div[data-testid="column"] .stButton>button{background:#161b22!important;border:1px solid #21262d!important;
    color:#8b949e!important;border-radius:10px!important;font-size:.79rem!important;font-weight:500!important;
    text-align:left!important;padding:10px 12px!important;width:100%!important;min-height:55px!important;
    line-height:1.4!important;transition:all .16s!important}
div[data-testid="column"] .stButton>button:hover{border-color:#d4a017!important;
    background:rgba(212,160,23,.05)!important;color:#e6edf3!important;transform:translateY(-1px)!important}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  IMPORT google-genai
# ════════════════════════════════════════════════════════
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("❌ Chạy: `pip install google-genai`")
    st.stop()

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
if not GEMINI_API_KEY:
    st.error("❌ Chưa có **GEMINI_API_KEY** trong `.streamlit/secrets.toml`")
    st.stop()

GEMINI_MODELS = [
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)

def get_model(client):
    if "confirmed_model" in st.session_state:
        return st.session_state.confirmed_model
    for m in GEMINI_MODELS:
        try:
            client.models.generate_content(model=m, contents="test",
                config=types.GenerateContentConfig(max_output_tokens=3))
            st.session_state.confirmed_model = m
            return m
        except Exception:
            continue
    st.session_state.confirmed_model = GEMINI_MODELS[-1]
    return GEMINI_MODELS[-1]

def _make_search_tool():
    try:    return types.Tool(google_search=types.GoogleSearch())
    except: pass
    try:    return types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())
    except: pass
    return None

_SEARCH_TOOL = _make_search_tool()

# ════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════
GREETING = (
    "Chào em! Thầy T đây. 👋\n\n"
    "Thầy biết giai đoạn này không dễ — vừa áp lực thi, vừa phải chọn ngành cho cả tương lai. "
    "Đừng lo, thầy ở đây đồng hành cùng em từng bước.\n\n"
    "---\n\n"
    "**Thầy T giúp được em:**\n\n"
    "📊 Điểm chuẩn thực tế 2023–2024–2025 + 📈 biểu đồ xu hướng\n\n"
    "🔮 Dự báo điểm chuẩn 2026 · 🏫 Top trường phân 4 tầng\n\n"
    "🗺️ Thực tế từ Tây Ninh · 💼 Nghề nghiệp & lương thực tế\n\n"
    "---\n\nCứ hỏi thẳng vào vấn đề nhé — thầy không thích vòng vo. 👇"
)

def _new_student(name="Học sinh mới"):
    return {"id": str(uuid.uuid4())[:8], "name": name,
            "profile": {"score":"","combo":"","major":"","strengths":"","budget":"","distance":""},
            "messages": [{"role":"assistant","content":GREETING}],
            "notes": "", "created": datetime.datetime.now().strftime("%d/%m %H:%M")}

def init():
    if "students" not in st.session_state:
        s = _new_student("Học sinh 1")
        st.session_state.students   = {s["id"]: s}
        st.session_state.active_sid = s["id"]
    if "bookmarks"    not in st.session_state: st.session_state.bookmarks    = []
    if "search_query" not in st.session_state: st.session_state.search_query = ""

init()

def S()  -> dict: return st.session_state.students[st.session_state.active_sid]
def P()  -> dict: return S()["profile"]
def M()  -> list: return S()["messages"]

# ════════════════════════════════════════════════════════
#  SYSTEM PROMPT  (v7.0 — thêm FOLLOWUP block)
# ════════════════════════════════════════════════════════
def build_system(profile: dict) -> str:
    base = """Bạn là **Thầy T** — chuyên gia tư vấn hướng nghiệp 15 năm, chuyên học sinh THPT Tây Ninh & miền Nam.

**Tính cách:** Thẳng thắn, ấm áp, trung thực. Không bao giờ bịa điểm chuẩn.

══════════════════════════════════════
🔴 QUY TẮC BẮT BUỘC
══════════════════════════════════════
1. Dùng Google Search cho điểm chuẩn — ưu tiên website trường → VnExpress → Tuổi Trẻ → tuyensinh247
2. Không tìm được → ghi null, thông báo rõ
3. PHẢI xuất JSON_TABLE cho bảng điểm chuẩn và bản đồ trường
4. PHẢI xuất FOLLOWUP ở cuối mỗi câu trả lời dài

**Bảng Điểm Chuẩn:**
~~~JSON_TABLE
{"title":"Điểm Chuẩn [Ngành] (2023-2026)","note":"Nguồn: ...","rows":[
  {"school":"...","combo":"...","y2023":0,"y2024":0,"y2025":0,"y2026_predict":0,"basis":"..."}
]}
~~~END

**Bảng Bản Đồ Trường:**
~~~JSON_TABLE
{"title":"Bản Đồ Trường Gợi Ý","note":"...","rows":[
  {"tier":"🥇 Đỉnh","school":"...","location":"...","strength":"...","distance":"...","note":"..."}
]}
~~~END

**Follow-up (BẮT BUỘC cuối mỗi trả lời):**
~~~FOLLOWUP
{"questions":["Câu hỏi tiếp theo 1?","Câu hỏi tiếp theo 2?","Câu hỏi tiếp theo 3?"]}
~~~END

**Cấu trúc chuẩn:**
## 🔎 [Ngành] — Thực Chất Là Gì?
## 📊 Điểm Chuẩn + Dự Báo 2026 [JSON_TABLE]
## 🏫 Bản Đồ Trường [JSON_TABLE]
## 💼 Đời Sống & Cơ Hội Việc Làm
## 🎯 Chiến Lược Nguyện Vọng
[FOLLOWUP]
"""
    if any(v for v in profile.values() if v and str(v).strip()):
        lines = ["\n══════════════════════════════════════", "👤 HỒ SƠ HỌC SINH:"]
        if profile.get("score"):     lines.append(f"• Điểm thi thử: **{profile['score']}**")
        if profile.get("combo"):     lines.append(f"• Tổ hợp: **{profile['combo']}**")
        if profile.get("major"):     lines.append(f"• Ngành quan tâm: **{profile['major']}**")
        if profile.get("strengths"): lines.append(f"• Sở thích: **{profile['strengths']}**")
        if profile.get("budget"):    lines.append(f"• Ngân sách: **{profile['budget']}**")
        if profile.get("distance"):  lines.append(f"• Khoảng cách: **{profile['distance']}**")
        lines.append("→ Dựa sát hồ sơ này tư vấn.")
        base += "\n".join(lines)
    return base

# ════════════════════════════════════════════════════════
#  RENDER — TABLES + CHARTS + FOLLOW-UP
# ════════════════════════════════════════════════════════
def _trend(a, b):
    if a is None or b is None: return '<span class="af">—</span>'
    try:    d = round(float(b) - float(a), 2)
    except: return '<span class="af">—</span>'
    if d > 0.09:  return f'<span class="au">↑ +{d}</span>'
    if d < -0.09: return f'<span class="ad">↓ {d}</span>'
    return '<span class="af">→ ổn định</span>'

def _badge(v, k="r"):
    if v is None: return '<span class="sb-n">N/A</span>'
    return f'<span class="sb-{k}">{v}</span>'

# ── Plotly chart cho bảng điểm chuẩn ──────────────────
def render_score_chart(rows: list, title: str):
    """Vẽ biểu đồ xu hướng điểm chuẩn bằng Plotly."""
    if not PLOTLY_OK or not rows:
        return
    # Chỉ render nếu có ít nhất 1 dòng có dữ liệu số
    has_data = any(
        any(r.get(y) is not None for y in ["y2023","y2024","y2025","y2026_predict"])
        for r in rows
    )
    if not has_data:
        return

    COLORS = ["#d4a017","#79c0ff","#3fb950","#c4b5fd","#f97316","#ef4444"]
    years  = ["2023","2024","2025","2026\n(dự báo)"]
    fig    = go.Figure()

    for i, r in enumerate(rows):
        vals = [r.get("y2023"), r.get("y2024"), r.get("y2025"), r.get("y2026_predict")]
        if not any(v is not None for v in vals):
            continue
        color = COLORS[i % len(COLORS)]
        # Đường thực (2023-2025)
        real_x = [years[j] for j,v in enumerate(vals[:3]) if v is not None]
        real_y = [v for v in vals[:3] if v is not None]
        if real_x:
            fig.add_trace(go.Scatter(
                x=real_x, y=real_y,
                mode="lines+markers",
                name=r.get("school",""),
                line=dict(color=color, width=2.5),
                marker=dict(size=9, color=color, line=dict(color="#0d1117", width=2)),
            ))
        # Đường dự báo (2025 → 2026, nét đứt)
        if vals[2] is not None and vals[3] is not None:
            fig.add_trace(go.Scatter(
                x=[years[2], years[3]],
                y=[vals[2],  vals[3]],
                mode="lines+markers",
                name=f"{r.get('school','')} (dự báo)",
                line=dict(color=color, width=2, dash="dot"),
                marker=dict(size=9, color=color, symbol="diamond",
                            line=dict(color="#0d1117", width=2)),
                showlegend=False,
            ))

    fig.update_layout(
        title=dict(text=f"📈 {title}", font=dict(color="#d4a017", size=14, family="Playfair Display"), x=0),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(color="#8b949e", family="Inter", size=12),
        legend=dict(bgcolor="#161b22", bordercolor="#21262d", borderwidth=1,
                    font=dict(color="#c9d1d9", size=11)),
        xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e"),
                   title="Điểm chuẩn"),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Parse & render tất cả block đặc biệt ──────────────
def parse_and_render(text: str):
    """
    Xử lý text: render JSON_TABLE (bảng + chart), FOLLOWUP (gợi ý), markdown còn lại.
    Trả về danh sách follow-up questions (nếu có).
    """
    followup_qs = []

    # 1. Tách FOLLOWUP ra khỏi text
    fu_match = re.search(r'~~~FOLLOWUP\s*(.*?)\s*~~~END', text, re.DOTALL)
    if fu_match:
        try:
            fu_data = json.loads(fu_match.group(1).strip())
            followup_qs = fu_data.get("questions", [])
        except Exception:
            pass
        text = text[:fu_match.start()] + text[fu_match.end():]

    # 2. Tìm tất cả JSON_TABLE
    table_blocks = re.findall(r'~~~JSON_TABLE\s*(.*?)\s*~~~END', text, re.DOTALL)
    if not table_blocks:
        st.markdown(text)
        return followup_qs

    clean = text
    htmls = []
    chart_rows_list = []

    for i, raw in enumerate(table_blocks):
        ph = f"__TBL_{i}__"
        for cand in [f"~~~JSON_TABLE{raw}~~~END",
                     f"~~~JSON_TABLE\n{raw}\n~~~END",
                     f"~~~JSON_TABLE\n{raw}~~~END",
                     f"~~~JSON_TABLE{raw}\n~~~END"]:
            if cand in clean: clean = clean.replace(cand, ph, 1); break
        else:
            clean = re.sub(r'~~~JSON_TABLE\s*' + re.escape(raw.strip()) + r'\s*~~~END',
                           ph, clean, count=1, flags=re.DOTALL)

        try: data = json.loads(raw.strip())
        except: htmls.append(None); chart_rows_list.append((None, None)); continue

        title = data.get("title",""); note = data.get("note",""); rows = data.get("rows",[])
        is_school = rows and isinstance(rows[0], dict) and "tier" in rows[0]

        h = (f'<div class="dct-wrap">'
             f'<h3 style="color:#d4a017;margin:12px 0 9px;font-family:\'Playfair Display\',serif;">'
             f'{title}</h3><table class="dct">')
        if is_school:
            h += ("<thead><tr><th>Tầng</th><th>Trường</th><th>Vị trí</th>"
                  "<th>Điểm mạnh</th><th>Khoảng cách</th><th>Ghi chú</th></tr></thead><tbody>")
            for r in rows:
                h += (f"<tr><td><strong>{r.get('tier','')}</strong></td>"
                      f"<td>{r.get('school','')}</td><td>{r.get('location','')}</td>"
                      f"<td>{r.get('strength','')}</td><td>{r.get('distance','')}</td>"
                      f"<td style='font-size:.8rem;color:#8b949e'>{r.get('note','')}</td></tr>")
            chart_rows_list.append((None, None))  # Không chart cho bảng trường
        else:
            h += ("<thead><tr><th>Trường</th><th>Tổ hợp</th>"
                  "<th>2023</th><th>2024</th><th>2025</th>"
                  "<th>Xu hướng</th><th>🔮 Dự báo 2026</th><th>Cơ sở</th></tr></thead><tbody>")
            for r in rows:
                y3,y4,y5,y6 = r.get("y2023"),r.get("y2024"),r.get("y2025"),r.get("y2026_predict")
                h += (f"<tr><td>{r.get('school','')}</td>"
                      f"<td><span class='sb-c'>{r.get('combo','')}</span></td>"
                      f"<td>{_badge(y3)}</td><td>{_badge(y4)}</td><td>{_badge(y5)}</td>"
                      f"<td>{_trend(y4,y5)}</td><td>{_badge(y6,'p')}</td>"
                      f"<td style='font-size:.78rem;color:#8b949e'>{r.get('basis','')}</td></tr>")
            chart_rows_list.append((rows, title))

        h += "</tbody></table>"
        if note: h += f'<div class="note-src">📌 {note}</div>'
        h += "</div>"
        htmls.append(h)

    # 3. Render từng phần
    for i, (tbl, chart_info) in enumerate(zip(htmls, chart_rows_list)):
        ph    = f"__TBL_{i}__"
        parts = clean.split(ph, 1)
        if parts[0].strip(): st.markdown(parts[0])
        if tbl: st.markdown(tbl, unsafe_allow_html=True)
        else:   st.warning("⚠️ Bảng lỗi JSON.")
        # 📈 Tự động vẽ chart nếu là bảng điểm chuẩn
        rows_data, chart_title = chart_info if chart_info else (None, None)
        if rows_data and chart_title:
            render_score_chart(rows_data, chart_title)
        clean = parts[1] if len(parts) > 1 else ""

    if clean.strip(): st.markdown(clean)
    return followup_qs

# ════════════════════════════════════════════════════════
#  AI — STREAMING
# ════════════════════════════════════════════════════════
SCORE_KW = ["điểm chuẩn","tuyển sinh","xét tuyển","nguyện vọng",
            "điểm đầu vào","trúng tuyển","học trường nào"]

def needs_search(t: str) -> bool:
    return any(k in t.lower() for k in SCORE_KW)

def build_hist(msgs: list) -> list:
    history = []
    for m in msgs[1:-1]:
        role = "model" if m["role"] == "assistant" else "user"
        txt  = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END', '[đã hiển thị]',
                      m["content"], flags=re.DOTALL)
        try:    part = types.Part.from_text(txt)
        except: part = types.Part(text=txt)
        history.append(types.Content(role=role, parts=[part]))
    return history

def stream_ai(user_input: str, profile: dict):
    """Generator streaming từng chunk từ Gemini."""
    client  = get_client()
    model   = get_model(client)
    history = build_hist(M())
    use_s   = needs_search(user_input)

    enhanced = user_input
    if use_s:
        enhanced += "\n\n[HỆ THỐNG]: Dùng Google Search tìm điểm chuẩn 2025. Ưu tiên website chính thức."

    tools = [_SEARCH_TOOL] if (use_s and _SEARCH_TOOL) else []
    cfg   = types.GenerateContentConfig(
        system_instruction=build_system(profile),
        tools=tools or None,
        temperature=0.65,
        max_output_tokens=8192,
    )
    try:
        chat = client.chats.create(model=model, config=cfg, history=history)
        for chunk in chat.send_message_stream(enhanced):
            if chunk.text: yield chunk.text
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ["grounding","tool","search","400","invalid"]):
            try:
                cfg2  = types.GenerateContentConfig(
                    system_instruction=build_system(profile),
                    temperature=0.65, max_output_tokens=8192)
                chat2 = client.chats.create(model=model, config=cfg2, history=history)
                for chunk in chat2.send_message_stream(user_input):
                    if chunk.text: yield chunk.text
                yield ("\n\n---\n*(⚠️ Google Search tạm lỗi — Thầy T dùng kiến thức sẵn có. "
                       "Em kiểm tra lại điểm chuẩn trên website trường nhé.)*")
                return
            except Exception as e2:
                yield f"\n\n❌ Lỗi: {str(e2)}"
                return
        yield f"\n\n❌ Lỗi kết nối: {str(e)}"

# ════════════════════════════════════════════════════════
#  QUICK TEMPLATES  (v7.0)
# ════════════════════════════════════════════════════════
TEMPLATES = {
    "🎯 Điểm chuẩn & Dự báo": [
        ("📊", "Điểm chuẩn ngành {ngành} 2023–2025 và dự báo 2026?"),
        ("🏥", "Điểm chuẩn Y Dược TP.HCM 3 năm gần nhất?"),
        ("💻", "CNTT các trường gần Tây Ninh: bảng điểm chuẩn 2023–2025"),
        ("📐", "Sư phạm Toán ĐH Cần Thơ: điểm chuẩn + tổ hợp xét tuyển"),
        ("⚙️", "Kỹ thuật Xây dựng phía Nam: bảng điểm chuẩn đầy đủ"),
        ("🌿", "Nông nghiệp CNC ĐH Nông Lâm: điểm chuẩn + việc làm"),
    ],
    "🏫 Chọn trường phù hợp": [
        ("🗺️", "Với {điểm} điểm tổ hợp {tổ hợp}, em nên đăng ký trường nào?"),
        ("📍", "Trường tốt trong bán kính 100km từ Tây Ninh là trường nào?"),
        ("💰", "Trường có học phí dưới 3 triệu/tháng cho ngành {ngành}?"),
        ("🏠", "Trường nào có ký túc xá tốt, gần Tây Ninh?"),
        ("🎓", "Top 5 trường đại học ở TP.HCM phù hợp học sinh Tây Ninh?"),
        ("🔁", "Nếu rớt NV1, NV2 em nên chọn trường nào dự phòng?"),
    ],
    "💼 Nghề nghiệp & Lương": [
        ("💵", "Ra trường ngành {ngành} làm gì, lương bao nhiêu?"),
        ("📈", "Ngành nào đang thiếu nhân lực, lương cao ở Tây Ninh?"),
        ("🌐", "Ngành CNTT làm remote được không, cần học gì?"),
        ("🏦", "Kế toán vs Tài chính Ngân hàng: việc làm và lương thực tế?"),
        ("🩺", "Điều dưỡng và Y tế cộng đồng: cơ hội việc làm tại địa phương?"),
        ("🔧", "Kỹ sư Cơ khí/Xây dựng: lương năm 1, 5, 10 năm kinh nghiệm?"),
    ],
    "🎯 Chiến lược xét tuyển": [
        ("📝", "Hướng dẫn đăng ký nguyện vọng NV1/NV2/NV3 cho em {điểm} điểm"),
        ("⚠️", "Sai lầm phổ biến khi đăng ký nguyện vọng học sinh cần tránh?"),
        ("🔄", "Xét tuyển sớm (học bạ) và thi THPT khác nhau thế nào?"),
        ("📊", "Với điểm học bạ 8.5, em có thể đăng ký xét tuyển sớm ngành gì?"),
        ("💡", "Khi nào nên đặt trường top làm NV1, khi nào không?"),
        ("🎰", "Chiến lược an toàn khi đặt nguyện vọng: bao nhiêu NV là đủ?"),
    ],
}

def render_templates():
    st.markdown("### 📋 Bộ Câu Hỏi Nhanh")
    st.markdown("*Nhấn để tự động điền vào ô chat — tiết kiệm thời gian tư vấn*")
    st.divider()

    for section, items in TEMPLATES.items():
        st.markdown(f'<div class="tpl-title">{section}</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (ic, txt) in enumerate(items):
            with cols[i % 2]:
                label = f"{ic} {txt}"
                if st.button(label, key=f"tpl_{section}_{i}", use_container_width=True):
                    # Điền vào pending, chuyển sang tab chat
                    filled = (txt
                        .replace("{ngành}", P().get("major","[tên ngành]") or "[tên ngành]")
                        .replace("{điểm}", P().get("score","[điểm của em]") or "[điểm của em]")
                        .replace("{tổ hợp}", P().get("combo","A00").split("—")[0].strip() or "A00"))
                    st.session_state["_pend"] = filled
                    st.toast("✅ Đã điền câu hỏi — chuyển sang tab Chat nhé!", icon="💬")
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  LỊCH TUYỂN SINH 2026  (v7.0)
# ════════════════════════════════════════════════════════
CALENDAR_2026 = [
    {"month": "Tháng 1–2/2026", "events": [
        {"date":"1/1–28/2","name":"Đăng ký dự thi tốt nghiệp THPT 2026",
         "desc":"Học sinh đăng ký môn thi, điểm thi, khu vực ưu tiên. Đây là thời hạn quan trọng nhất — bỏ lỡ sẽ không được thi!",
         "tag":"urgent","tag_label":"⚠️ CỰC KỲ QUAN TRỌNG"},
        {"date":"Tháng 2","name":"Bắt đầu xét tuyển sớm (phương thức học bạ)",
         "desc":"Nhiều trường mở xét tuyển học bạ từ tháng 2. Học sinh đủ điều kiện nên nộp hồ sơ ngay từ đợt đầu.",
         "tag":"important","tag_label":"📋 Nên làm sớm"},
    ]},
    {"month": "Tháng 3–5/2026", "events": [
        {"date":"3–5/2026","name":"Xét tuyển sớm — Học bạ & Năng khiếu",
         "desc":"Phần lớn trường công bố kết quả xét tuyển sớm. Trường top như Y Dược, Sư phạm thường chốt danh sách trước tháng 6.",
         "tag":"important","tag_label":"📋 Theo dõi kết quả"},
        {"date":"Tháng 5","name":"Ôn thi nước rút — Thi thử lần cuối",
         "desc":"Giai đoạn ôn thi tập trung. Tham khảo điểm chuẩn năm trước để điều chỉnh chiến lược nguyện vọng.",
         "tag":"info","tag_label":"📚 Ôn tập"},
    ]},
    {"month": "Tháng 6/2026", "events": [
        {"date":"Khoảng 17–19/6","name":"🎓 KỲ THI THPT QUỐC GIA 2026",
         "desc":"Thi chính thức. Học sinh thi đủ các môn theo đăng ký. Mang đủ CCCD, phiếu dự thi.",
         "tag":"urgent","tag_label":"🎓 NGÀY THI CHÍNH THỨC"},
    ]},
    {"month": "Tháng 7/2026", "events": [
        {"date":"Khoảng 10–15/7","name":"📊 Công bố điểm thi THPT 2026",
         "desc":"Tra điểm tại: thisinh.vnies.edu.vn. Lưu lại điểm để tính tổ hợp. Bắt đầu tính toán nguyện vọng.",
         "tag":"important","tag_label":"📊 Nhận điểm"},
        {"date":"15–30/7","name":"Đăng ký nguyện vọng xét tuyển ĐH-CĐ",
         "desc":"Đăng ký trực tuyến trên hệ thống xét tuyển chung. Được điều chỉnh nguyện vọng đến hết thời hạn. Sắp xếp NV theo thứ tự ưu tiên từ cao xuống thấp.",
         "tag":"urgent","tag_label":"⚠️ ĐĂNG KÝ NGUYỆN VỌNG"},
    ]},
    {"month": "Tháng 8–9/2026", "events": [
        {"date":"Đầu tháng 8","name":"Công bố điểm chuẩn các trường",
         "desc":"Các trường công bố điểm chuẩn theo từng phương thức. So sánh với điểm của em để biết kết quả.",
         "tag":"important","tag_label":"📋 Điểm chuẩn"},
        {"date":"Giữa tháng 8","name":"✅ Xác nhận nhập học",
         "desc":"Sinh viên trúng tuyển xác nhận nhập học trực tuyến. KHÔNG xác nhận sẽ mất suất học. Nộp đúng hạn!",
         "tag":"urgent","tag_label":"✅ XÁC NHẬN NHẬP HỌC"},
        {"date":"Tháng 9","name":"Khai giảng năm học 2026–2027",
         "desc":"Bắt đầu hành trình đại học! Chuẩn bị nhập học: ký túc xá, giấy tờ, học phí học kỳ 1.",
         "tag":"info","tag_label":"🎉 Khai giảng"},
    ]},
]

def render_calendar():
    st.markdown("### 📅 Lịch Tuyển Sinh 2026")
    st.markdown("*Timeline đầy đủ — các mốc quan trọng thầy/cô cần nhắc học sinh*")

    # Legend
    st.markdown("""
<div style="display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 20px;">
  <span class="cal-tag tag-urgent">⚠️ Cực kỳ quan trọng</span>
  <span class="cal-tag tag-important">📋 Quan trọng</span>
  <span class="cal-tag tag-info">ℹ️ Cần biết</span>
</div>
""", unsafe_allow_html=True)
    st.divider()

    now = datetime.datetime.now()
    for block in CALENDAR_2026:
        st.markdown(f'<div class="cal-month-title">📆 {block["month"]}</div>',
                    unsafe_allow_html=True)
        for ev in block["events"]:
            tag_html = f'<span class="cal-tag tag-{ev["tag"]}">{ev["tag_label"]}</span>'
            st.markdown(f"""
<div class="cal-event {ev['tag']}">
  <div class="cal-date">{ev['date']}</div>
  <div class="cal-content">
    <div class="cal-name">{ev['name']}</div>
    <div class="cal-desc">{ev['desc']}</div>
    {tag_html}
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.info("📌 **Lưu ý:** Các mốc trên là dự kiến dựa theo lịch tuyển sinh 2025. "
            "Bộ GD&ĐT có thể điều chỉnh — thầy/cô theo dõi tại moet.gov.vn để cập nhật chính thức.")

# ════════════════════════════════════════════════════════
#  TÌM KIẾM TOÀN BỘ CHAT  (v7.0)
# ════════════════════════════════════════════════════════
def highlight(text: str, query: str) -> str:
    """Highlight từ khoá trong đoạn text."""
    if not query: return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(
        lambda m: f'<span class="sr-highlight">{m.group()}</span>',
        text
    )

def render_search():
    st.markdown("### 🔍 Tìm Kiếm Lịch Sử Chat")
    st.markdown("*Tìm nhanh qua toàn bộ cuộc trò chuyện của tất cả học sinh*")
    st.divider()

    query = st.text_input("🔍 Nhập từ khoá...",
                          placeholder="VD: Y Dược, điểm chuẩn, Sư phạm Toán...",
                          key="search_input")

    if not query or len(query.strip()) < 2:
        st.markdown('<div style="color:#484f58;font-size:.88rem;margin-top:16px;">'
                    'Nhập ít nhất 2 ký tự để tìm kiếm.</div>', unsafe_allow_html=True)
        return

    results = []
    for sid, stu in st.session_state.students.items():
        msgs = stu["messages"]
        for i, msg in enumerate(msgs):
            if msg["role"] != "user": continue
            q_text = msg["content"]
            # Tìm câu trả lời tương ứng
            a_text = msgs[i+1]["content"] if i+1 < len(msgs) else ""
            # Loại bỏ JSON_TABLE để tìm kiếm
            a_clean = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END', '', a_text, flags=re.DOTALL)

            if (query.lower() in q_text.lower() or query.lower() in a_clean.lower()):
                results.append({
                    "student": stu["name"],
                    "sid": sid,
                    "question": q_text,
                    "answer": a_clean.strip()[:300],
                    "msg_idx": i,
                })

    if not results:
        st.warning(f'Không tìm thấy kết quả nào cho **"{query}"**')
        return

    st.markdown(f'<div style="color:#3fb950;font-size:.85rem;margin-bottom:14px;">'
                f'✅ Tìm thấy <strong>{len(results)}</strong> kết quả</div>',
                unsafe_allow_html=True)

    for r in results:
        q_hl = highlight(r["question"][:80] + ("..." if len(r["question"])>80 else ""), query)
        a_hl = highlight(r["answer"][:250] + ("..." if len(r["answer"])>250 else ""), query)
        st.markdown(f"""
<div class="sr-card">
  <div class="sr-student">👤 {r['student']}</div>
  <div class="sr-q">❓ {q_hl}</div>
  <div class="sr-preview">{a_hl}</div>
</div>""", unsafe_allow_html=True)

        if st.button(f"→ Chuyển đến chat của {r['student']}", key=f"sr_go_{r['sid']}_{r['msg_idx']}"):
            st.session_state.active_sid = r["sid"]
            st.toast(f"✅ Đã chuyển sang {r['student']}", icon="👤")
            st.rerun()

# ════════════════════════════════════════════════════════
#  QUIZ
# ════════════════════════════════════════════════════════
QUIZ = [
    {"q":"Em thích làm việc với...","opts":{
        "A":"Con số, dữ liệu, phân tích logic",
        "B":"Con người — dạy học, tư vấn, giao tiếp",
        "C":"Thiên nhiên, sinh vật, thực phẩm, môi trường",
        "D":"Máy móc, công nghệ, lập trình, hệ thống"}},
    {"q":"Điều em tự hào nhất ở bản thân là...","opts":{
        "A":"Tư duy logic, giỏi giải quyết vấn đề",
        "B":"Kỹ năng giao tiếp, thuyết phục",
        "C":"Sự kiên nhẫn, tỉ mỉ, quan sát tốt",
        "D":"Sáng tạo, thích khám phá cái mới"}},
    {"q":"Sau này em muốn làm việc ở...","opts":{
        "A":"Công ty, ngân hàng, cơ quan nhà nước",
        "B":"Trường học, bệnh viện, tổ chức phi lợi nhuận",
        "C":"Nông trại, phòng lab, nhà máy, môi trường",
        "D":"Công ty công nghệ, startup, làm freelance"}},
    {"q":"Môn học em thích nhất ở THPT là...","opts":{
        "A":"Toán, Vật lý, Hóa học","B":"Văn, Lịch sử, GDCD, Ngoại ngữ",
        "C":"Sinh học, Địa lý, Hóa học","D":"Toán, Tin học, Vật lý"}},
    {"q":"Em lo ngại nhất điều gì khi chọn ngành?","opts":{
        "A":"Điểm chuẩn quá cao","B":"Ra trường khó xin việc",
        "C":"Học phí và chi phí tốn kém","D":"Sợ học không phù hợp bản thân"}},
]
QUIZ_RESULT = {
    "A":{"group":"Kinh tế — Tài chính — Kế toán","icon":"💼",
         "desc":"Tư duy phân tích tốt — Kế toán, Tài chính NH, Kinh tế, Quản trị KD.",
         "suggest":"Kế toán, Tài chính Ngân hàng, Kinh tế, Quản trị Kinh doanh",
         "schools":"UEH, ĐH Kinh Tế TPHCM, ĐH Tôn Đức Thắng, ĐH Văn Lang"},
    "B":{"group":"Sư phạm — Y tế — Xã hội","icon":"🏫",
         "desc":"Năng khiếu giao tiếp, muốn cống hiến — Sư phạm, Y tế, Tâm lý học.",
         "suggest":"Sư phạm các môn, Y tế cộng đồng, Tâm lý học, Công tác xã hội",
         "schools":"ĐH Sư Phạm TPHCM, ĐH Y Dược TPHCM, ĐH Cần Thơ"},
    "C":{"group":"Nông — Lâm — Môi trường — Thực phẩm","icon":"🌿",
         "desc":"Gần gũi thiên nhiên — Nông nghiệp, Thú y, Thực phẩm, Môi trường.",
         "suggest":"Nông nghiệp CNC, Thú y, Công nghệ Thực phẩm, Môi trường",
         "schools":"ĐH Nông Lâm TPHCM, ĐH Cần Thơ, ĐH Bình Dương"},
    "D":{"group":"Kỹ thuật — Công nghệ — CNTT","icon":"💻",
         "desc":"Tư duy kỹ thuật, sáng tạo — CNTT, Điện tử, Cơ khí, Xây dựng.",
         "suggest":"Công nghệ Thông tin, Kỹ thuật Điện tử, Cơ khí, Xây dựng",
         "schools":"ĐH Bách Khoa TPHCM, ĐH CNTT ĐHQG, ĐH Sư Phạm Kỹ Thuật"},
}

def run_quiz():
    st.markdown("### 🧭 Quiz Khám Phá Hướng Nghiệp")
    st.markdown("*5 câu · 2 phút · tìm ra nhóm ngành phù hợp nhất*")
    st.divider()
    sid = st.session_state.active_sid
    qa_k, done_k = f"qa_{sid}", f"qd_{sid}"
    if qa_k   not in st.session_state: st.session_state[qa_k]   = {}
    if done_k not in st.session_state: st.session_state[done_k] = False

    if st.session_state[done_k]:
        top = Counter(st.session_state[qa_k].values()).most_common(1)[0][0]
        res = QUIZ_RESULT[top]
        st.success("✅ Hoàn thành!")
        st.markdown(f"""
<div style="background:#161b22;border:1px solid #d4a017;border-radius:13px;padding:20px 24px;">
  <div style="font-size:1.8rem;margin-bottom:7px;">{res['icon']}</div>
  <div style="font-family:'Playfair Display',serif;font-size:1.2rem;color:#f0f6fc;font-weight:700;margin-bottom:7px;">
    Nhóm ngành: <span style="color:#d4a017;">{res['group']}</span></div>
  <div style="color:#8b949e;line-height:1.7;font-size:.9rem;">{res['desc']}</div>
  <div style="margin-top:12px;padding-top:10px;border-top:1px solid #21262d;">
    <span style="font-size:.7rem;color:#8b949e;text-transform:uppercase;">Ngành gợi ý</span>
    <div style="color:#c9d1d9;font-weight:600;margin-top:4px;">{res['suggest']}</div></div>
  <div style="margin-top:9px;">
    <span style="font-size:.7rem;color:#8b949e;text-transform:uppercase;">Trường gần Tây Ninh</span>
    <div style="color:#c9d1d9;font-weight:600;margin-top:4px;">{res['schools']}</div></div>
</div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🔄 Làm lại", use_container_width=True):
                st.session_state[qa_k]={}; st.session_state[done_k]=False; st.rerun()
        with c2:
            if st.button("💬 Hỏi Thầy T ngay", use_container_width=True):
                ng = res["suggest"].split(",")[0].strip()
                st.session_state["_pend"] = (
                    f"Thầy T ơi, em vừa làm quiz, kết quả phù hợp nhóm **{res['group']}**. "
                    f"Ngành **{ng}** điểm chuẩn 2023–2025 bao nhiêu, trường nào tốt gần Tây Ninh?")
                st.toast("✅ Chuyển sang tab Chat nhé!", icon="💬"); st.rerun()
        return

    ans = st.session_state[qa_k]
    st.progress(len(ans)/len(QUIZ))
    st.markdown(f'<div style="font-size:.78rem;color:#8b949e;margin:8px 0 13px;">Tiến độ: {len(ans)}/{len(QUIZ)} câu</div>',
                unsafe_allow_html=True)
    for idx, item in enumerate(QUIZ):
        qno = idx+1
        if qno in ans:
            ch = ans[qno]
            st.markdown(
                f'<div style="background:#161b22;border:1px solid #21262d;border-radius:9px;'
                f'padding:10px 14px;margin-bottom:8px;font-size:.86rem;">'
                f'<span style="color:#8b949e;">Câu {qno}:</span> <span style="color:#c9d1d9;">{item["q"]}</span>'
                f'<br><span style="color:#3fb950;font-weight:600;">✓ {ch}: {item["opts"][ch]}</span></div>',
                unsafe_allow_html=True); continue
        st.markdown(f'<div style="font-weight:700;color:#f0f6fc;font-size:.95rem;margin-bottom:8px;">Câu {qno}/{len(QUIZ)}: {item["q"]}</div>',
                    unsafe_allow_html=True)
        cols = st.columns(2)
        for j,(k,v) in enumerate(item["opts"].items()):
            with cols[j%2]:
                if st.button(f"{k}. {v}", key=f"q{sid}_{idx}_{k}", use_container_width=True):
                    ans[qno]=k
                    if len(ans)==len(QUIZ): st.session_state[done_k]=True
                    st.rerun()
        break

# ════════════════════════════════════════════════════════
#  SO SÁNH NGÀNH
# ════════════════════════════════════════════════════════
def run_compare():
    st.markdown("### ⚖️ So Sánh Ngành Nghề")
    c1,c2 = st.columns(2)
    with c1: ng1 = st.text_input("🅰️ Ngành thứ nhất", placeholder="VD: Kế toán", key="cmp1")
    with c2: ng2 = st.text_input("🅱️ Ngành thứ hai",  placeholder="VD: Tài chính NH", key="cmp2")
    if st.button("🔍 So sánh ngay", use_container_width=True, type="primary"):
        if ng1.strip() and ng2.strip():
            st.session_state["_pend"] = (
                f"Thầy T ơi, em phân vân **{ng1.strip()}** vs **{ng2.strip()}**. "
                f"So sánh: điểm chuẩn 2023–2025, cơ hội việc làm, lương, phù hợp Tây Ninh?")
            st.toast("✅ Chuyển sang tab Chat nhé!", icon="💬"); st.rerun()
        else: st.warning("⚠️ Nhập đủ 2 ngành nhé!")
    st.divider()
    st.markdown("**💡 Cặp ngành hay so sánh:**")
    pairs = [("Kế toán","Tài chính Ngân hàng"),("CNTT","Kỹ thuật Điện tử"),
             ("Y khoa","Dược học"),("Sư phạm Toán","Toán ứng dụng"),
             ("Xây dựng","Kiến trúc"),("Nông nghiệp CNC","Công nghệ Thực phẩm")]
    cols = st.columns(3)
    for i,(a,b) in enumerate(pairs):
        with cols[i%3]:
            if st.button(f"⚖️ {a} vs {b}", key=f"cp_{i}", use_container_width=True):
                st.session_state["_pend"] = (
                    f"Thầy T ơi, em phân vân **{a}** vs **{b}**. "
                    f"So sánh điểm chuẩn, cơ hội việc làm, lương, phù hợp Tây Ninh?")
                st.toast("✅ Chuyển sang tab Chat!", icon="💬"); st.rerun()

# ════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════
def run_dashboard():
    st.markdown("### 📊 Tổng Quan Lớp")
    students = list(st.session_state.students.values())
    c1,c2,c3,c4 = st.columns(4)
    for col,val,lbl in [(c1,len(students),"Học sinh"),
                        (c2,sum(1 for s in students if any(v for v in s["profile"].values() if v)),"Có hồ sơ"),
                        (c3,sum(1 for s in students if len(s["messages"])>1),"Đã tư vấn"),
                        (c4,len(st.session_state.bookmarks),"Bookmark")]:
        with col:
            st.markdown(f'<div class="dash-stat"><div class="ds-val">{val}</div>'
                        f'<div class="ds-lbl">{lbl}</div></div>', unsafe_allow_html=True)
    st.divider()

    # Biểu đồ phân bố ngành quan tâm (nếu có plotly)
    majors = [s["profile"].get("major","") for s in students if s["profile"].get("major","")]
    if majors and PLOTLY_OK:
        st.markdown("#### 🎯 Ngành Học Sinh Quan Tâm")
        mc = Counter(majors)
        fig = go.Figure(go.Bar(
            x=list(mc.values()), y=list(mc.keys()),
            orientation='h',
            marker=dict(color='#d4a017', line=dict(color='#b8860b', width=1)),
            text=list(mc.values()), textposition='outside',
        ))
        fig.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
            font=dict(color="#8b949e", family="Inter", size=12),
            xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
            yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#e6edf3")),
            margin=dict(l=10,r=40,t=10,b=10), height=max(150, len(mc)*45),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        st.divider()

    st.markdown("#### 👥 Danh Sách Học Sinh")
    hdr = st.columns([3,2,2,2,1])
    for c,t in zip(hdr,["Tên","Tổ hợp","Ngành","Điểm thử","# Tin"]):
        c.markdown(f"**{t}**")
    st.markdown('<hr style="margin:5px 0"/>', unsafe_allow_html=True)
    for s in students:
        p  = s["profile"]
        cs = st.columns([3,2,2,2,1])
        is_a = s["id"] == st.session_state.active_sid
        cs[0].markdown(f"{'🟡 ' if is_a else ''}{s['name']}")
        cs[1].markdown(p.get("combo","—").split("—")[0].strip() or "—")
        cs[2].markdown(p.get("major","—") or "—")
        cs[3].markdown(f"**{p.get('score','—')}**" if p.get("score") else "—")
        cs[4].markdown(str(len(s["messages"])-1))

# ════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎓 Thầy T")
    if "confirmed_model" in st.session_state:
        st.markdown(
            f'<div style="font-size:.68rem;color:#484f58;">'
            f'🤖 <span style="color:#3fb950;">{st.session_state.confirmed_model}</span></div>',
            unsafe_allow_html=True)
    st.caption("Teacher Edition v7.0")
    st.divider()

    # ── HỌC SINH ──
    st.markdown("### 👥 Học Sinh")
    for sid, s in list(st.session_state.students.items()):
        is_a  = sid == st.session_state.active_sid
        n_msg = len(s["messages"]) - 1
        combo = s["profile"].get("combo","").split("—")[0].strip()
        info  = " · ".join(filter(None,[combo, s["profile"].get("major",""),
                                        f"{n_msg} tin" if n_msg else ""]))
        st.markdown(
            f'<div class="stu-card {"active" if is_a else ""}">'
            f'<div class="sname">{s["name"]}</div>'
            f'<div class="sinfo">{info or "Chưa có hồ sơ"}</div>'
            f'{"<div class=\'sbadge\'>ACTIVE</div>" if is_a else ""}'
            f'</div>', unsafe_allow_html=True)
        if not is_a:
            if st.button(f"→ Chọn", key=f"sel_{sid}", use_container_width=True):
                st.session_state.active_sid = sid; st.rerun()

    col_inp, col_btn = st.columns([3,1])
    with col_inp:
        new_name = st.text_input("", placeholder="Tên học sinh mới...",
                                 key="new_name", label_visibility="collapsed")
    with col_btn:
        st.markdown("<div style='margin-top:4px'>", unsafe_allow_html=True)
        if st.button("➕", key="add_stu"):
            if new_name.strip():
                ns = _new_student(new_name.strip())
                st.session_state.students[ns["id"]] = ns
                st.session_state.active_sid         = ns["id"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if len(st.session_state.students) > 1:
        if st.button(f"🗑️ Xoá {S()['name']}", use_container_width=True, key="del_stu"):
            del st.session_state.students[st.session_state.active_sid]
            st.session_state.active_sid = list(st.session_state.students.keys())[0]
            st.rerun()
    st.divider()

    # ── HỒ SƠ ──
    st.markdown(f"### 📋 Hồ Sơ: {S()['name']}")
    p = P()
    combo_opts  = ["Chưa chọn","A00 — Toán·Lý·Hóa","A01 — Toán·Lý·Anh","B00 — Toán·Hóa·Sinh",
                   "C00 — Văn·Sử·Địa","D01 — Toán·Văn·Anh","D07 — Toán·Hóa·Anh",
                   "C14 — Văn·Toán·GDCD","Khác"]
    budget_opts = ["Chưa biết","Dưới 3 triệu","3–5 triệu","5–8 triệu","Trên 8 triệu"]
    dist_opts   = ["Không giới hạn","Trong tỉnh Tây Ninh","Bán kính 100 km","Bán kính 200 km"]
    def _i(lst,val,d=0): return lst.index(val) if val in lst else d

    sc_v = st.text_input("📊 Điểm thi thử",       value=p.get("score",""),     placeholder="VD: 23.5",     key="ps")
    cb_v = st.selectbox("📚 Tổ hợp",              combo_opts, index=_i(combo_opts,p.get("combo","Chưa chọn")), key="pc")
    mj_v = st.text_input("🎯 Ngành quan tâm",      value=p.get("major",""),     placeholder="VD: Sư phạm", key="pm")
    st_v = st.text_input("💡 Sở thích",            value=p.get("strengths",""), placeholder="VD: Thích dạy", key="pst")
    bd_v = st.selectbox("💰 Chi phí/tháng",        budget_opts,index=_i(budget_opts,p.get("budget","Chưa biết")), key="pb")
    dt_v = st.selectbox("🗺️ Khoảng cách",          dist_opts,  index=_i(dist_opts,p.get("distance","Không giới hạn")), key="pd")

    if st.button("💾 Lưu hồ sơ", use_container_width=True, key="save_p",
                 type="primary"):
        S()["profile"] = {
            "score":sc_v.strip(),"combo":cb_v if cb_v!="Chưa chọn" else "",
            "major":mj_v.strip(),"strengths":st_v.strip(),
            "budget":bd_v if bd_v!="Chưa biết" else "",
            "distance":dt_v if dt_v!="Không giới hạn" else ""}
        st.success("✅ Đã lưu!")
    st.divider()

    # ── GHI CHÚ ──
    st.markdown(f"### 📝 Ghi Chú")
    notes = st.text_area("", value=S().get("notes",""),
                         placeholder="Ghi chú riêng của thầy/cô...",
                         height=90, key="notes_area", label_visibility="collapsed")
    if st.button("💾 Lưu ghi chú", use_container_width=True, key="save_n"):
        S()["notes"] = notes; st.success("✅ Đã lưu!")
    st.divider()

    # ── EXPORT ──
    if len(M()) > 1:
        ts     = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        export = (f"PHIẾU TƯ VẤN HƯỚNG NGHIỆP — THẦY T v7.0\n"
                  f"Học sinh: {S()['name']}\nNgày: {ts}\n{'='*52}\n\n")
        if S().get("notes"):
            export += f"[GHI CHÚ]\n{S()['notes']}\n\n{'—'*40}\n\n"
        for m in M():
            role = "Học sinh" if m["role"]=="user" else "Thầy T"
            txt  = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END','[Bảng/Gợi ý]',
                          m["content"],flags=re.DOTALL)
            export += f"[{role}]\n{txt}\n\n{'—'*40}\n\n"
        st.download_button(
            label=f"📥 Tải phiếu: {S()['name']}",
            data=export.encode("utf-8"),
            file_name=f"PhieuTuVan_{S()['name'].replace(' ','_')}_{datetime.datetime.now().strftime('%d%m%Y')}.txt",
            mime="text/plain", use_container_width=True)

    if st.button("🗑️ Xoá chat hiện tại", use_container_width=True, key="clr"):
        S()["messages"] = [{"role":"assistant","content":GREETING}]; st.rerun()

# ════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-eyebrow">✦ v7.0 · Gemini 2.5 Flash · Streaming · Charts</div>
      <div class="hero-title">Thầy <span class="gold">T</span> — Hướng Nghiệp 12 PRO</div>
      <div class="hero-sub">Đang tư vấn: <strong style="color:#d4a017;">{S()['name']}</strong> · Điểm chuẩn 2023–2025 + Dự báo 2026 · Biểu đồ xu hướng</div>
    </div>
    <div class="hero-chips">
      <span class="hchip hc-live">⚡ Streaming</span>
      <span class="hchip hc-gold">📈 Charts</span>
      <span class="hchip hc-blue">💡 Follow-up</span>
      <span class="hchip hc-purple">👥 Multi-Student</span>
      <span class="hchip hc-green">📅 Calendar</span>
      <span class="hchip hc-def">🔍 Search</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════
tab_chat, tab_tpl, tab_quiz, tab_compare, tab_cal, tab_dash, tab_bk, tab_search = st.tabs([
    "💬 Chat",
    "📋 Templates",
    "🧭 Quiz",
    "⚖️ So Sánh",
    "📅 Lịch 2026",
    "📊 Dashboard",
    "🔖 Bookmark",
    "🔍 Tìm Kiếm",
])

# ════════════════════════════════════════════════════════
#  TAB 1 — CHAT (STREAMING + CHARTS + FOLLOW-UP)
# ════════════════════════════════════════════════════════
SUGGESTIONS = [
    ("🏥","Điểm chuẩn Y Dược TP.HCM 2023–2025 và dự báo 2026?"),
    ("💻","CNTT: trường nào gần Tây Ninh, bảng điểm chuẩn 3 năm?"),
    ("📐","Sư phạm Toán ĐH Cần Thơ: điểm chuẩn + việc làm"),
    ("⚙️","Kỹ thuật Xây dựng phía Nam: bảng điểm chuẩn 2023–2026"),
    ("🌿","Nông nghiệp CNC: trường tốt, điểm chuẩn, nghề gì?"),
    ("💰","Tài chính Ngân hàng: học ở đâu, ra trường lương bao nhiêu?"),
]

with tab_chat:
    msgs = M()

    for idx, msg in enumerate(msgs):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                # Render với chart + follow-up
                fq = parse_and_render(msg["content"])
                # Bookmark button
                if idx > 0:
                    c_bk, c_exp = st.columns([1, 5])
                    with c_bk:
                        if st.button("🔖", key=f"bk_{st.session_state.active_sid}_{idx}",
                                     help="Bookmark câu trả lời này"):
                            q = msgs[idx-1]["content"] if idx > 0 else ""
                            st.session_state.bookmarks.append({
                                "question": q, "answer": msg["content"],
                                "student":  S()["name"],
                                "ts":       datetime.datetime.now().strftime("%d/%m %H:%M"),
                            })
                            st.toast("✅ Đã bookmark!", icon="🔖")
                # Follow-up suggestions (chỉ hiển thị cho tin nhắn cuối)
                if fq and idx == len(msgs) - 1:
                    st.markdown('<div class="fu-wrap"><div class="fu-lbl">💡 Câu hỏi tiếp theo</div></div>',
                                unsafe_allow_html=True)
                    fu_cols = st.columns(min(3, len(fq)))
                    for fi, fq_text in enumerate(fq[:3]):
                        with fu_cols[fi]:
                            if st.button(f"→ {fq_text}", key=f"fu_{idx}_{fi}",
                                         use_container_width=True):
                                st.session_state["_pend"] = fq_text; st.rerun()
            else:
                st.markdown(msg["content"])

    # Gợi ý nhanh khi chat trống
    if len(msgs) == 1:
        st.markdown('<div class="slbl">✦ Câu hỏi gợi ý</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i,(ic,txt) in enumerate(SUGGESTIONS):
            with cols[i%3]:
                if st.button(f"{ic} {txt}", key=f"sg_{i}_{st.session_state.active_sid}"):
                    st.session_state["_pend"] = txt; st.rerun()

    pend       = st.session_state.pop("_pend", None)
    user_query = pend or st.chat_input(
        f"Hỏi Thầy T cho {S()['name']} — điểm chuẩn, chọn ngành, chọn trường... 💬",
        key=f"cin_{st.session_state.active_sid}",
    )

    if user_query:
        M().append({"role":"user","content":user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            # ⚡ STREAMING: hiện chữ chạy real-time
            full_text = ""
            ph        = st.empty()

            for chunk in stream_ai(user_query, P()):
                full_text += chunk
                # Preview sạch (ẩn JSON/FOLLOWUP block khi đang stream)
                preview = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END',
                                 '\n\n*⏳ Đang tải bảng...*\n\n',
                                 full_text, flags=re.DOTALL)
                ph.markdown(preview + "▌")

            ph.empty()
            # Render final với bảng + chart + follow-up
            fq_final = parse_and_render(full_text)

            # Hiển thị follow-up suggestions ngay sau
            if fq_final:
                st.markdown('<div class="fu-wrap"><div class="fu-lbl">💡 Câu hỏi tiếp theo</div></div>',
                            unsafe_allow_html=True)
                fu_cols = st.columns(min(3, len(fq_final)))
                for fi, fq_text in enumerate(fq_final[:3]):
                    with fu_cols[fi]:
                        if st.button(f"→ {fq_text}", key=f"fu_new_{fi}",
                                     use_container_width=True):
                            st.session_state["_pend"] = fq_text

        M().append({"role":"assistant","content":full_text})
        st.rerun()

# ════════════════════════════════════════════════════════
#  TAB 2 — TEMPLATES
# ════════════════════════════════════════════════════════
with tab_tpl:
    render_templates()

# ════════════════════════════════════════════════════════
#  TAB 3 — QUIZ
# ════════════════════════════════════════════════════════
with tab_quiz:
    run_quiz()

# ════════════════════════════════════════════════════════
#  TAB 4 — SO SÁNH
# ════════════════════════════════════════════════════════
with tab_compare:
    run_compare()

# ════════════════════════════════════════════════════════
#  TAB 5 — LỊCH TUYỂN SINH
# ════════════════════════════════════════════════════════
with tab_cal:
    render_calendar()

# ════════════════════════════════════════════════════════
#  TAB 6 — DASHBOARD
# ════════════════════════════════════════════════════════
with tab_dash:
    run_dashboard()

# ════════════════════════════════════════════════════════
#  TAB 7 — BOOKMARK
# ════════════════════════════════════════════════════════
with tab_bk:
    st.markdown("### 🔖 Câu Trả Lời Đã Lưu")
    bks = st.session_state.bookmarks
    if not bks:
        st.info("Chưa có bookmark. Nhấn **🔖** dưới mỗi câu trả lời hay trong tab Chat!")
    else:
        st.markdown(f"*{len(bks)} bookmark đã lưu*")
        st.divider()
        for i, bk in enumerate(reversed(bks)):
            real_i = len(bks)-1-i
            with st.expander(f"🔖 [{bk['student']}] {bk['question'][:55]}{'...' if len(bk['question'])>55 else ''} · {bk['ts']}"):
                parse_and_render(bk["answer"])
                if st.button("🗑️ Xoá", key=f"del_bk_{real_i}"):
                    st.session_state.bookmarks.pop(real_i); st.rerun()
        st.divider()
        if st.button("🗑️ Xoá tất cả"):
            st.session_state.bookmarks = []; st.rerun()

# ════════════════════════════════════════════════════════
#  TAB 8 — SEARCH
# ════════════════════════════════════════════════════════
with tab_search:
    render_search()

# ════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;color:#484f58;font-size:.7rem;
padding:16px 0 8px;border-top:1px solid #21262d;margin-top:20px;">
✦ <strong style="color:#8b949e;">Thầy T — v7.0 Teacher Edition</strong>
· Gemini 2.5 Flash · Streaming · Plotly Charts · Follow-up AI<br>
Điểm chuẩn từ nguồn chính thức · Dự báo 2026 chỉ mang tính tham khảo<br>
<span style="color:#30363d;">Made with ❤️ for học sinh Tây Ninh</span>
</div>
""", unsafe_allow_html=True)
