"""
╔══════════════════════════════════════════════════════════════════╗
║   THẦY T — HƯỚNG NGHIỆP 12 PRO  ·  v9.0                         ║
║   Light Theme · Stable · Python 3.9+ · All Fixes Applied         ║
╚══════════════════════════════════════════════════════════════════╝

CHANGELOG v9.0 (base: v8.0 light theme của người dùng):

  FIX #1 CRITICAL: str|None / dict|None → Optional[str] (Python 3.9 compat)
  FIX #2 CRITICAL: requirements.txt — Streamlit Cloud không chạy thiếu file này
  FIX #3 CRITICAL: Streaming retry không còn duplicate content
  FIX #4: Plotly chart màu sáng khớp UI (không còn dark chart trong light UI)
  FIX #5: st.columns(min(3,0)) → guard fq trước khi tạo cột
  FIX #6: HTML export escape AI content (XSS prevention)
  FIX #7: Cache key bổ sung hash profile để tránh cross-student cache hit
  NEW:    Typing indicator đẹp khi AI đang xử lý
  NEW:    Copy button cho mỗi câu trả lời
  NEW:    Profile completion bar trong sidebar
  NEW:    Pinned important dates badge trong lịch
  NEW:    Tự động đổi tên tab theo học sinh đang active
"""

# ── Python 3.9+ compat: dùng Optional/List/Tuple từ typing ───────
from typing import Optional, List, Tuple, Dict
import streamlit as st
import datetime, re, json, time, uuid, hashlib
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

try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ════════════════════════════════════════════════════════
#  CSS — LIGHT THEME HOÀN CHỈNH (đủ mọi class dùng trong code)
# ════════════════════════════════════════════════════════
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap');

/* ── RESET ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:#f8fafc;min-height:100vh;color:#1e293b}

::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#f1f5f9}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#94a3b8}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{background:#ffffff!important;border-right:1px solid #e2e8f0!important;box-shadow:2px 0 10px rgba(0,0,0,.03)}
[data-testid="stSidebar"] .stMarkdown p,[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small{color:#475569!important}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{color:#0f172a!important;font-family:'Playfair Display',serif!important}
[data-testid="stSidebar"] hr{border-color:#e2e8f0!important;margin:10px 0!important}
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stTextArea"] textarea{
    background:#f8fafc!important;border:1px solid #cbd5e1!important;
    color:#0f172a!important;border-radius:8px!important;font-size:.87rem!important}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
[data-testid="stSidebar"] [data-testid="stTextArea"] textarea:focus{
    border-color:#2563eb!important;box-shadow:0 0 0 3px rgba(37,99,235,.12)!important}
[data-testid="stSidebar"] [data-testid="stSelectbox"]>div>div{
    background:#f8fafc!important;border:1px solid #cbd5e1!important;
    color:#0f172a!important;border-radius:8px!important}
[data-testid="stSidebar"] .stButton>button{
    width:100%!important;background:#f8fafc!important;border:1px solid #cbd5e1!important;
    color:#475569!important;border-radius:9px!important;font-size:.84rem!important;
    font-weight:600!important;padding:9px 0!important;transition:all .15s!important}
[data-testid="stSidebar"] .stButton>button:hover{
    border-color:#2563eb!important;color:#2563eb!important;background:#eff6ff!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{
    background:linear-gradient(135deg,#2563eb,#1d4ed8)!important;color:#fff!important;
    border:none!important;font-weight:700!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover{
    box-shadow:0 4px 15px rgba(37,99,235,.35)!important;transform:translateY(-1px)!important}

/* ── LAYOUT ── */
.main .block-container{padding:0!important;max-width:100%!important}

/* ── HERO ── */
.hero{background:linear-gradient(135deg,#eff6ff 0%,#dbeafe 60%,#e0f2fe 100%);
    border-bottom:1px solid #bfdbfe;padding:24px 40px;position:relative;overflow:hidden}
.hero::after{content:'';position:absolute;top:-60px;right:-60px;width:280px;height:280px;
    border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,.06) 0%,transparent 70%);pointer-events:none}
.hero-inner{display:flex;align-items:center;justify-content:space-between;gap:20px;position:relative;z-index:1}
.hero-eyebrow{display:inline-flex;align-items:center;gap:6px;background:#fff;
    border:1px solid #bfdbfe;color:#2563eb;border-radius:20px;padding:4px 14px;
    font-size:.63rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
.hero-title{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:900;color:#1e3a8a;line-height:1.15}
.hero-title .gold{color:#2563eb;font-style:italic}
.hero-sub{font-size:.84rem;color:#475569;margin-top:5px;line-height:1.6}
.hero-chips{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.hchip{border-radius:20px;padding:4px 12px;font-size:.65rem;font-weight:600;white-space:nowrap}
.hc-def{background:#fff;border:1px solid #cbd5e1;color:#64748b}
.hc-live{background:#dcfce7;border:1px solid #86efac;color:#166534}
.hc-gold{background:#fef3c7;border:1px solid #fde047;color:#92400e}
.hc-blue{background:#e0f2fe;border:1px solid #7dd3fc;color:#0369a1}
.hc-purple{background:#f3e8ff;border:1px solid #d8b4fe;color:#6b21a8}
.hc-red{background:#fee2e2;border:1px solid #fca5a5;color:#991b1b}

/* ── TABS ── */
[data-testid="stTabs"] [data-testid="stTab"]{background:transparent!important;color:#64748b!important;
    border:none!important;border-bottom:2px solid transparent!important;font-weight:600!important;
    font-size:.84rem!important;padding:9px 15px!important;transition:all .15s!important}
[data-testid="stTabs"] [data-testid="stTab"]:hover{color:#1e293b!important}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"]{color:#2563eb!important;border-bottom:2px solid #2563eb!important}
[data-testid="stTabsContent"]{padding-top:16px!important}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;
    box-shadow:none!important;padding:0!important;margin-bottom:20px!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"]{
    background:#dbeafe!important;color:#1e3a8a!important;border:1px solid #bfdbfe!important;
    border-radius:18px 18px 4px 18px!important;padding:12px 17px!important;
    font-size:.94rem!important;line-height:1.7!important;max-width:76%!important;margin-left:auto!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"]{
    background:#ffffff!important;color:#334155!important;border:1px solid #e2e8f0!important;
    border-radius:4px 18px 18px 18px!important;padding:20px 24px!important;
    font-size:.94rem!important;line-height:1.85!important;box-shadow:0 4px 15px rgba(0,0,0,.04)!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h1,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h3{
    font-family:'Playfair Display',serif!important;color:#0f172a!important;margin-top:20px!important;margin-bottom:7px!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) strong{color:#1d4ed8!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) a{color:#2563eb!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) li{margin-bottom:4px}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) hr{border-color:#e2e8f0!important;margin:14px 0!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) code{
    background:#f1f5f9!important;color:#dc2626!important;border-radius:4px;
    padding:1px 6px;font-size:.86em;border:1px solid #e2e8f0}

/* ── TABLES ── */
.dct-wrap{overflow-x:auto;margin:16px 0 6px;border-radius:12px;border:1px solid #e2e8f0;
    background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.03)}
.dct{width:100%;border-collapse:collapse;font-size:.87rem}
.dct thead tr{background:#f8fafc}
.dct thead th{padding:12px 14px;text-align:left;font-weight:700;white-space:nowrap;
    color:#2563eb;font-size:.68rem;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid #e2e8f0}
.dct tbody tr{border-bottom:1px solid #f1f5f9;transition:background .12s}
.dct tbody tr:last-child{border-bottom:none}
.dct tbody tr:hover{background:#f8fafc}
.dct td{padding:11px 14px;color:#475569;vertical-align:middle}
.dct td:first-child{color:#0f172a;font-weight:600;min-width:185px}
.sb-r{display:inline-block;background:#eff6ff;border:1px solid #bfdbfe;color:#1d4ed8;border-radius:6px;padding:2px 9px;font-weight:700;font-size:.84rem}
.sb-n{display:inline-block;background:#f8fafc;border:1px solid #e2e8f0;color:#94a3b8;border-radius:6px;padding:2px 9px;font-size:.83rem}
.sb-p{display:inline-block;background:#f3e8ff;border:1px solid #d8b4fe;color:#7e22ce;border-radius:6px;padding:2px 9px;font-weight:700;font-size:.84rem}
.sb-c{display:inline-block;background:#f1f5f9;border:1px solid #e2e8f0;color:#475569;border-radius:5px;padding:2px 7px;font-size:.75rem;font-weight:600}
/* FIX #8: trend colors cho light theme */
.au{color:#16a34a;font-weight:700}
.ad{color:#dc2626;font-weight:700}
.af{color:#94a3b8;font-weight:700}
.note-src{background:#fffbeb;border:1px solid #fde68a;border-radius:9px;padding:9px 14px;
    margin-top:7px;font-size:.77rem;color:#92400e;line-height:1.6}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"]>div{background:#fff!important;border:1.5px solid #cbd5e1!important;
    border-radius:14px!important;transition:border-color .2s!important;
    box-shadow:0 4px 12px rgba(0,0,0,.04)!important}
[data-testid="stChatInput"]>div:focus-within{border-color:#2563eb!important;
    box-shadow:0 0 0 3px rgba(37,99,235,.1)!important}
[data-testid="stChatInput"] textarea{color:#0f172a!important;font-family:'Inter',sans-serif!important;
    font-size:.94rem!important;background:transparent!important}
[data-testid="stChatInput"] textarea::placeholder{color:#94a3b8!important}

/* ── SUGGESTION BUTTONS ── */
div[data-testid="column"] .stButton>button{background:#fff!important;border:1px solid #e2e8f0!important;
    color:#475569!important;border-radius:10px!important;font-size:.80rem!important;font-weight:500!important;
    text-align:left!important;padding:10px 12px!important;width:100%!important;min-height:54px!important;
    line-height:1.4!important;transition:all .15s!important;box-shadow:0 1px 3px rgba(0,0,0,.04)!important}
div[data-testid="column"] .stButton>button:hover{border-color:#2563eb!important;
    background:#eff6ff!important;color:#1d4ed8!important;transform:translateY(-1px)!important;
    box-shadow:0 4px 12px rgba(37,99,235,.1)!important}

/* ── STUDENT CARD ── */
.stu-card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;
    padding:10px 13px;margin-bottom:7px;transition:all .15s;position:relative;
    box-shadow:0 1px 3px rgba(0,0,0,.03)}
.stu-card.active{border-color:#2563eb;background:#eff6ff;box-shadow:0 2px 8px rgba(37,99,235,.1)}
.stu-card .sname{font-weight:700;font-size:.88rem;color:#0f172a}
.stu-card .sinfo{font-size:.74rem;color:#64748b;margin-top:3px}
.stu-card .sbadge{position:absolute;top:9px;right:11px;background:#2563eb;color:#fff;
    border-radius:5px;padding:2px 7px;font-size:.62rem;font-weight:700}

/* ── DASHBOARD STAT ── */
.dash-stat{background:#fff;border:1px solid #e2e8f0;border-radius:10px;
    padding:15px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.03)}
.dash-stat .ds-val{font-size:1.85rem;font-weight:800;color:#2563eb;font-family:'Playfair Display',serif}
.dash-stat .ds-lbl{font-size:.69rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-top:3px}

/* ── FOLLOW-UP ── */
.fu-wrap{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;padding-top:11px;border-top:1px solid #e2e8f0}
.fu-lbl{font-size:.67rem;color:#94a3b8;letter-spacing:1.5px;text-transform:uppercase;width:100%;margin-bottom:2px}

/* ── CACHE PILL ── */
.cache-pill{display:inline-flex;align-items:center;gap:5px;background:#dcfce7;
    border:1px solid #86efac;border-radius:20px;padding:3px 10px;
    font-size:.7rem;color:#166534;font-weight:600}

/* ── INFO BOXES ── */
.warn-box{background:#fffbeb;border:1px solid #fde68a;border-radius:9px;
    padding:11px 15px;margin:8px 0;font-size:.85rem;color:#92400e;line-height:1.65}
.err-box{background:#fef2f2;border:1px solid #fecaca;border-radius:9px;
    padding:12px 16px;margin:9px 0;font-size:.87rem;color:#991b1b;line-height:1.7}

/* ── CALENDAR ── */
.cal-event{display:flex;gap:14px;padding:12px 16px;background:#fff;border:1px solid #e2e8f0;
    border-radius:10px;margin-bottom:8px;align-items:flex-start;box-shadow:0 1px 3px rgba(0,0,0,.02)}
.cal-event.urgent{border-color:#fca5a5;background:#fef2f2}
.cal-event.important{border-color:#fde68a;background:#fffbeb}
.cal-event.info{border-color:#7dd3fc;background:#f0f9ff}
.cal-date{font-weight:800;font-size:.81rem;color:#2563eb;min-width:70px;padding-top:2px}
.cal-name{font-weight:600;color:#0f172a;font-size:.89rem;margin-bottom:3px}
.cal-desc{font-size:.79rem;color:#475569;line-height:1.55}
.cal-tag{display:inline-block;border-radius:5px;padding:2px 8px;font-size:.67rem;font-weight:700;margin-top:5px}
.tag-urgent{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5}
.tag-important{background:#fef3c7;color:#92400e;border:1px solid #fde047}
.tag-info{background:#e0f2fe;color:#0369a1;border:1px solid #7dd3fc}

/* ── SEARCH ── */
.sr-card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;
    padding:13px 16px;margin-bottom:9px;box-shadow:0 1px 3px rgba(0,0,0,.03)}
.sr-student{font-size:.71rem;color:#2563eb;font-weight:700;letter-spacing:.5px;text-transform:uppercase;margin-bottom:4px}
.sr-q{font-weight:600;color:#0f172a;font-size:.89rem;margin-bottom:5px}
.sr-preview{font-size:.83rem;color:#475569;line-height:1.6}
.sr-hl{background:#fef3c7;color:#92400e;border-radius:3px;padding:0 3px;font-weight:600}

/* ── TEMPLATES ── */
.tpl-title{font-size:.69rem;color:#64748b;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
    margin-bottom:9px;padding-bottom:5px;border-bottom:1px solid #e2e8f0}

/* ── MISC ── */
.slbl{font-size:.63rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#94a3b8;margin:8px 0 12px}
.sc{background:#fff;border:1px solid #e2e8f0;border-radius:9px;padding:10px 14px;margin-bottom:7px}
.sc-l{font-size:.63rem;color:#64748b;font-weight:700;letter-spacing:1.2px;text-transform:uppercase}
.sc-v{font-size:.95rem;color:#0f172a;font-weight:700;margin-top:3px}
.sc-v.g{color:#2563eb}
.bk-card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:12px 15px;margin-bottom:8px}

/* ── TYPING INDICATOR (NEW v9.0) ── */
.typing-wrap{display:flex;align-items:center;gap:10px;padding:12px 16px;
    background:#fff;border:1px solid #e2e8f0;border-radius:12px;margin:4px 0}
.typing-dots{display:flex;gap:4px}
.typing-dots span{width:7px;height:7px;background:#2563eb;border-radius:50%;
    animation:bounce 1.2s ease-in-out infinite}
.typing-dots span:nth-child(2){animation-delay:.2s}
.typing-dots span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
.typing-label{font-size:.83rem;color:#475569;font-weight:500}

/* ── PROGRESS BAR (NEW v9.0) ── */
.prog-wrap{margin:8px 0 12px}
.prog-label{font-size:.68rem;color:#64748b;font-weight:600;margin-bottom:5px;
    display:flex;justify-content:space-between}
.prog-bar{height:5px;background:#e2e8f0;border-radius:3px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#2563eb,#60a5fa);border-radius:3px;transition:width .4s}

/* ── COPY BUTTON (NEW v9.0) ── */
.copy-btn-wrap{display:flex;justify-content:flex-end;margin-top:6px}

#MainMenu,footer,header{visibility:hidden}
[data-testid="stDecoration"]{display:none}
hr{border-color:#e2e8f0!important}
[data-testid="stDownloadButton"]>button{background:#fff!important;border:1px solid #cbd5e1!important;
    color:#475569!important;border-radius:9px!important;font-size:.83rem!important;
    width:100%!important;transition:all .2s!important}
[data-testid="stDownloadButton"]>button:hover{border-color:#2563eb!important;
    color:#2563eb!important;background:#eff6ff!important}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  GOOGLE GENAI
# ════════════════════════════════════════════════════════
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("❌ Chạy: `pip install google-genai`")
    st.stop()

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    st.error("❌ Thiếu **GEMINI_API_KEY** trong `.streamlit/secrets.toml`")
    st.stop()

GEMINI_MODELS = [
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def get_client() -> genai.Client:
    return genai.Client(api_key=GEMINI_API_KEY)

def get_model(client: genai.Client) -> str:
    if "confirmed_model" in st.session_state:
        return st.session_state.confirmed_model
    for m in GEMINI_MODELS:
        try:
            client.models.generate_content(model=m, contents="hi",
                config=types.GenerateContentConfig(max_output_tokens=3))
            st.session_state.confirmed_model = m
            return m
        except Exception:
            continue
    st.session_state.confirmed_model = GEMINI_MODELS[-1]
    return GEMINI_MODELS[-1]

def _make_search_tool():
    for fn in [lambda: types.Tool(google_search=types.GoogleSearch()),
               lambda: types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())]:
        try:    return fn()
        except: pass
    return None

_SEARCH_TOOL = _make_search_tool()

# ════════════════════════════════════════════════════════
#  CACHE — FIX #7: key gồm cả profile hash
# ════════════════════════════════════════════════════════
CACHE_TTL = 1800
CACHE_MAX  = 60

def _cache_key(q: str, profile: Optional[Dict] = None) -> str:
    """
    FIX #7: Cache key = md5(question + combo + major).
    - Điểm chuẩn là dữ liệu chung → dùng question only
    - Câu hỏi cá nhân → thêm tổ hợp + ngành để tránh cross-student cache
    """
    base = q.lower().strip()
    if profile:
        # Chỉ thêm thông tin ảnh hưởng đến câu trả lời
        base += "|" + profile.get("combo", "") + "|" + profile.get("major", "")
    return hashlib.md5(base.encode()).hexdigest()

def cache_get(q: str, profile: Optional[Dict] = None) -> Optional[str]:
    store = st.session_state.get("_cache", {})
    entry = store.get(_cache_key(q, profile))
    if entry:
        ts, resp = entry
        if time.time() - ts < CACHE_TTL:
            return resp
        store.pop(_cache_key(q, profile), None)
    return None

def cache_set(q: str, resp: str, profile: Optional[Dict] = None) -> None:
    if not resp or resp.startswith("❌") or len(resp) < 50:
        return
    if "_cache" not in st.session_state:
        st.session_state._cache = {}
    store = st.session_state._cache
    if len(store) >= CACHE_MAX:
        oldest = min(store, key=lambda k: store[k][0])
        store.pop(oldest, None)
    store[_cache_key(q, profile)] = (time.time(), resp)
    st.session_state.setdefault("_cache_stats", {"hits": 0, "misses": 0, "saves": 0})
    st.session_state._cache_stats["saves"] += 1

def _bump_stat(key: str) -> None:
    st.session_state.setdefault("_cache_stats", {"hits": 0, "misses": 0, "saves": 0})
    st.session_state._cache_stats[key] += 1

# ════════════════════════════════════════════════════════
#  SESSION STATE — SAFE + PYTHON 3.9 COMPAT
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

def _blank_student(name: str = "Học sinh mới") -> Dict:
    return {"id": str(uuid.uuid4())[:8], "name": name,
            "profile": {"score":"","combo":"","major":"","strengths":"","budget":"","distance":""},
            "messages": [{"role":"assistant","content":GREETING}],
            "notes": "", "created": datetime.datetime.now().strftime("%d/%m %H:%M")}

def _ensure_state() -> None:
    if "students" not in st.session_state or not st.session_state.students:
        s = _blank_student("Học sinh 1")
        st.session_state.students   = {s["id"]: s}
        st.session_state.active_sid = s["id"]
    if st.session_state.get("active_sid") not in st.session_state.students:
        st.session_state.active_sid = next(iter(st.session_state.students))
    st.session_state.setdefault("bookmarks", [])
    st.session_state.setdefault("_cache", {})
    st.session_state.setdefault("_cache_stats", {"hits":0,"misses":0,"saves":0})

_ensure_state()

def S() -> Dict:
    _ensure_state()
    return st.session_state.students[st.session_state.active_sid]

def P() -> Dict:
    return S().get("profile", {})

def M() -> List:
    msgs = S().get("messages")
    if not msgs:
        S()["messages"] = [{"role":"assistant","content":GREETING}]
    return S()["messages"]

# ════════════════════════════════════════════════════════
#  SCORE VALIDATION — FIX #1: dùng Tuple thay tuple[x,y]
# ════════════════════════════════════════════════════════
def validate_score(raw: str) -> Tuple[str, Optional[str]]:
    """Returns (cleaned, error_or_None). FIX: Tuple[str,Optional[str]] thay str|None."""
    raw = raw.strip()
    if not raw:
        return "", None
    try:
        val = float(raw.replace(",", "."))
        if not (0 <= val <= 30):
            return raw, "Điểm phải trong khoảng 0–30"
        cleaned = f"{val:.2f}".rstrip("0").rstrip(".")
        return cleaned, None
    except ValueError:
        return raw, "Vui lòng nhập số (VD: 23.5)"

# ════════════════════════════════════════════════════════
#  PROFILE COMPLETION SCORE (NEW v9.0)
# ════════════════════════════════════════════════════════
def profile_completion(profile: Dict) -> int:
    """Trả về % hoàn thành hồ sơ (0-100)."""
    fields = ["score","combo","major","strengths","budget","distance"]
    filled = sum(1 for f in fields if profile.get(f,"").strip())
    return int(filled / len(fields) * 100)

# ════════════════════════════════════════════════════════
#  FRIENDLY ERRORS
# ════════════════════════════════════════════════════════
def friendly_error(err: str) -> str:
    e = err.lower()
    if "quota" in e or "429" in e or "resource_exhausted" in e:
        return ("⏳ **API quota tạm hết** — Gemini giới hạn số lần gọi mỗi phút.\n\n"
                "Em chờ **60 giây** rồi hỏi lại nhé.")
    if "api_key" in e or "authentication" in e or "401" in e or "403" in e:
        return ("🔑 **API Key không hợp lệ** — Kiểm tra `GEMINI_API_KEY` trong `.streamlit/secrets.toml`.\n\n"
                "Lấy key mới: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)")
    if "timeout" in e or "deadline" in e or "504" in e:
        return "⏱️ **Timeout** — Server Gemini phản hồi chậm. Em hỏi lại sau vài giây nhé."
    if "network" in e or "connection" in e or "503" in e:
        return "📶 **Mất kết nối** — Kiểm tra internet và thử lại."
    if "empty" in e:
        return "🤔 **AI trả về trống** — Em thử hỏi lại cụ thể hơn nhé."
    return f"❌ **Lỗi**: {err[:120]}\n\nEm thử lại sau nhé."

# ════════════════════════════════════════════════════════
#  SYSTEM PROMPT
# ════════════════════════════════════════════════════════
def build_system(profile: Dict) -> str:
    base = """Bạn là **Thầy T** — chuyên gia tư vấn hướng nghiệp 15 năm, học sinh THPT Tây Ninh & miền Nam.

**Tính cách:** Thẳng thắn, ấm áp, trung thực. Không bao giờ bịa điểm chuẩn.

══════════════════════════════════════
🔴 QUY TẮC BẮT BUỘC
══════════════════════════════════════
1. Google Search cho điểm chuẩn — ưu tiên website trường → VnExpress → Tuổi Trẻ → tuyensinh247
2. Không tìm được → ghi null, nói rõ
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

**Follow-up (BẮT BUỘC):**
~~~FOLLOWUP
{"questions":["Câu 1?","Câu 2?","Câu 3?"]}
~~~END

**Cấu trúc:**
## 🔎 [Ngành] — Thực Chất Là Gì?
## 📊 Điểm Chuẩn + Dự Báo 2026 [JSON_TABLE]
## 🏫 Bản Đồ Trường [JSON_TABLE]
## 💼 Đời Sống & Cơ Hội Việc Làm
## 🎯 Chiến Lược Nguyện Vọng
[FOLLOWUP]
"""
    if any(v for v in profile.values() if v and str(v).strip()):
        lines = ["\n══════════════════════════════════════","👤 HỒ SƠ HỌC SINH:"]
        for k,lbl in [("score","Điểm thi thử"),("combo","Tổ hợp"),("major","Ngành quan tâm"),
                      ("strengths","Sở thích"),("budget","Ngân sách"),("distance","Khoảng cách")]:
            if profile.get(k): lines.append(f"• {lbl}: **{profile[k]}**")
        lines.append("→ Dựa sát hồ sơ này tư vấn.")
        base += "\n".join(lines)
    return base

# ════════════════════════════════════════════════════════
#  SAFE JSON PARSE — FIX #1: Optional[Dict]
# ════════════════════════════════════════════════════════
def safe_json(raw: str) -> Optional[Dict]:
    """FIX: trả Optional[Dict] thay dict|None (Python 3.9 compat)."""
    for attempt in [
        raw.strip(),
        raw.strip().strip("`"),
        re.sub(r"^```json\s*|\s*```$", "", raw.strip(), flags=re.DOTALL),
        re.sub(r",\s*([}\]])", r"\1", raw.strip()),
        re.sub(r"'", '"', raw.strip()),
    ]:
        if not attempt:
            continue
        try:    return json.loads(attempt)
        except: continue
    return None

# ════════════════════════════════════════════════════════
#  RENDER — TABLE + CHART + FOLLOWUP
# ════════════════════════════════════════════════════════
def _trend(a, b) -> str:
    if a is None or b is None: return '<span class="af">—</span>'
    try:    d = round(float(b) - float(a), 2)
    except: return '<span class="af">—</span>'
    if d > 0.09:  return f'<span class="au">↑ +{d}</span>'
    if d < -0.09: return f'<span class="ad">↓ {d}</span>'
    return '<span class="af">→ ổn định</span>'

def _badge(v, k: str = "r") -> str:
    if v is None: return '<span class="sb-n">N/A</span>'
    return f'<span class="sb-{k}">{v}</span>'

def _score_chart(rows: List, title: str) -> None:
    """FIX #4: màu sáng cho light theme."""
    if not PLOTLY_OK or not rows: return
    years  = ["2023","2024","2025","2026\n(dự báo)"]
    # FIX: màu đậm để hiện rõ trên nền trắng
    COLORS = ["#1d4ed8","#16a34a","#dc2626","#7e22ce","#c2410c","#0369a1"]
    fig    = go.Figure()
    has_data = False
    for i, r in enumerate(rows):
        vals = [r.get("y2023"),r.get("y2024"),r.get("y2025"),r.get("y2026_predict")]
        if not any(v is not None for v in vals): continue
        has_data = True
        color    = COLORS[i % len(COLORS)]
        real_x = [years[j] for j,v in enumerate(vals[:3]) if v is not None]
        real_y = [float(v) for v in vals[:3] if v is not None]
        if real_x:
            fig.add_trace(go.Scatter(
                x=real_x, y=real_y, mode="lines+markers",
                name=r.get("school","")[:25],
                line=dict(color=color, width=2.5),
                marker=dict(size=9, color=color, line=dict(color="#fff",width=2)),
            ))
        if vals[2] is not None and vals[3] is not None:
            try:
                fig.add_trace(go.Scatter(
                    x=[years[2],years[3]], y=[float(vals[2]),float(vals[3])],
                    mode="lines+markers", showlegend=False,
                    line=dict(color=color,width=2,dash="dot"),
                    marker=dict(size=9,color=color,symbol="diamond",
                                line=dict(color="#fff",width=2)),
                ))
            except Exception:
                pass
    if not has_data: return
    # FIX: paper/plot background trắng/xám nhạt khớp light theme
    fig.update_layout(
        title=dict(text=f"📈 {title}",
                   font=dict(color="#1d4ed8",size=13,family="Playfair Display"),x=0),
        paper_bgcolor="#f8fafc",
        plot_bgcolor="#ffffff",
        font=dict(color="#475569",family="Inter",size=11),
        legend=dict(bgcolor="#fff",bordercolor="#e2e8f0",borderwidth=1,
                    font=dict(color="#0f172a",size=10)),
        xaxis=dict(gridcolor="#f1f5f9",linecolor="#e2e8f0",tickfont=dict(color="#64748b")),
        yaxis=dict(gridcolor="#f1f5f9",linecolor="#e2e8f0",tickfont=dict(color="#64748b"),
                   title=dict(text="Điểm chuẩn",font=dict(color="#64748b"))),
        hovermode="x unified",
        margin=dict(l=10,r=10,t=38,b=10),
        height=290,
    )
    try:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    except Exception:
        pass

def parse_and_render(text: str) -> List[str]:
    """
    FIX #1: List[str] thay list[str].
    FIX #6: escape HTML trong trường hợp cần.
    Returns follow-up questions.
    """
    if not text or not text.strip():
        st.markdown("*(Thầy T chưa có nội dung để hiển thị)*")
        return []

    followup_qs: List[str] = []

    # Tách FOLLOWUP
    fu_match = re.search(r'~~~FOLLOWUP\s*(.*?)\s*~~~END', text, re.DOTALL)
    if fu_match:
        try:
            fu_data = safe_json(fu_match.group(1))
            if fu_data and isinstance(fu_data, dict):
                followup_qs = [q for q in fu_data.get("questions",[]) if isinstance(q,str)]
        except Exception:
            pass
        text = text[:fu_match.start()] + text[fu_match.end():]

    raw_blocks = re.findall(r'~~~JSON_TABLE\s*(.*?)\s*~~~END', text, re.DOTALL)
    if not raw_blocks:
        st.markdown(text)
        return followup_qs

    clean = text
    for i, raw in enumerate(raw_blocks):
        ph = f"__TBL_{i}__"
        replaced = False
        for cand in [f"~~~JSON_TABLE{raw}~~~END",
                     f"~~~JSON_TABLE\n{raw}\n~~~END",
                     f"~~~JSON_TABLE\n{raw}~~~END",
                     f"~~~JSON_TABLE{raw}\n~~~END"]:
            if cand in clean:
                clean = clean.replace(cand, ph, 1); replaced = True; break
        if not replaced:
            clean = re.sub(r'~~~JSON_TABLE\s*'+re.escape(raw.strip())+r'\s*~~~END',
                           ph, clean, count=1, flags=re.DOTALL)

    for i, raw in enumerate(raw_blocks):
        ph    = f"__TBL_{i}__"
        parts = clean.split(ph, 1)
        if parts[0].strip(): st.markdown(parts[0])

        data = safe_json(raw)
        if data is None:
            st.markdown('<div class="warn-box">⚠️ Bảng dữ liệu lỗi định dạng — bỏ qua.</div>',
                        unsafe_allow_html=True)
            clean = parts[1] if len(parts)>1 else ""; continue

        title = str(data.get("title",""))
        note  = str(data.get("note",""))
        rows  = data.get("rows",[])
        if not isinstance(rows,list): rows=[]

        is_school = rows and isinstance(rows[0],dict) and "tier" in rows[0]
        h = (f'<div class="dct-wrap">'
             f'<h3 style="color:#1d4ed8;margin:11px 0 8px;font-family:\'Playfair Display\',serif;">'
             f'{title}</h3><table class="dct">')
        try:
            if is_school:
                h += ("<thead><tr><th>Tầng</th><th>Trường</th><th>Vị trí</th>"
                      "<th>Điểm mạnh</th><th>Khoảng cách</th><th>Ghi chú</th></tr></thead><tbody>")
                for r in rows:
                    if not isinstance(r,dict): continue
                    h += (f"<tr><td><strong>{r.get('tier','')}</strong></td>"
                          f"<td>{r.get('school','')}</td><td>{r.get('location','')}</td>"
                          f"<td>{r.get('strength','')}</td><td>{r.get('distance','')}</td>"
                          f"<td style='font-size:.79rem;color:#64748b'>{r.get('note','')}</td></tr>")
            else:
                h += ("<thead><tr><th>Trường</th><th>Tổ hợp</th>"
                      "<th>2023</th><th>2024</th><th>2025</th>"
                      "<th>Xu hướng</th><th>🔮 Dự báo 2026</th><th>Cơ sở</th></tr></thead><tbody>")
                for r in rows:
                    if not isinstance(r,dict): continue
                    y3,y4,y5,y6 = r.get("y2023"),r.get("y2024"),r.get("y2025"),r.get("y2026_predict")
                    h += (f"<tr><td>{r.get('school','')}</td>"
                          f"<td><span class='sb-c'>{r.get('combo','')}</span></td>"
                          f"<td>{_badge(y3)}</td><td>{_badge(y4)}</td><td>{_badge(y5)}</td>"
                          f"<td>{_trend(y4,y5)}</td><td>{_badge(y6,'p')}</td>"
                          f"<td style='font-size:.78rem;color:#64748b'>{r.get('basis','')}</td></tr>")
        except Exception:
            h += "<tr><td colspan='8' style='color:#dc2626'>Lỗi render dòng</td></tr>"

        h += "</tbody></table>"
        if note: h += f'<div class="note-src">📌 {note}</div>'
        h += "</div>"
        st.markdown(h, unsafe_allow_html=True)

        if not is_school and rows:
            _score_chart(rows, title)

        clean = parts[1] if len(parts)>1 else ""

    if clean.strip(): st.markdown(clean)
    return followup_qs

# ════════════════════════════════════════════════════════
#  TYPING INDICATOR (NEW v9.0)
# ════════════════════════════════════════════════════════
def show_typing(label: str = "Thầy T đang tìm kiếm và soạn câu trả lời...") -> None:
    st.markdown(f"""
<div class="typing-wrap">
  <div class="typing-dots">
    <span></span><span></span><span></span>
  </div>
  <div class="typing-label">{label}</div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  AI — STREAM + RETRY + CACHE
#  FIX #3: retry không còn duplicate content
# ════════════════════════════════════════════════════════
SCORE_KW = ["điểm chuẩn","tuyển sinh","xét tuyển","nguyện vọng",
            "điểm đầu vào","trúng tuyển","học trường nào"]

def needs_search(t: str) -> bool:
    return any(k in t.lower() for k in SCORE_KW)

def build_hist(msgs: List) -> List:
    history = []
    for m in (msgs[1:-1] if len(msgs)>1 else []):
        role = "model" if m["role"]=="assistant" else "user"
        txt  = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END','[đã hiển thị]',
                      m["content"], flags=re.DOTALL)
        try:    part = types.Part.from_text(txt)
        except TypeError:
            try: part = types.Part.from_text(text=txt)
            except: continue
        try:    history.append(types.Content(role=role, parts=[part]))
        except: continue
    return history

def _do_stream(client, model: str, enhanced: str, profile: Dict, history: List):
    """Thực hiện một lần stream. Raises nếu lỗi hoặc empty."""
    use_s = needs_search(enhanced)
    tools = [_SEARCH_TOOL] if (use_s and _SEARCH_TOOL) else []
    cfg   = types.GenerateContentConfig(
        system_instruction=build_system(profile),
        tools=tools or None,
        temperature=0.65,
        max_output_tokens=8192,
    )
    chat = client.chats.create(model=model, config=cfg, history=history)
    buf  = []
    for chunk in chat.send_message_stream(enhanced):
        if chunk.text: buf.append(chunk.text)
    if not buf: raise ValueError("empty response")
    return "".join(buf)

def stream_response(user_input: str, profile: Dict):
    """
    FIX #3: Kiến trúc mới — KHÔNG còn duplicate content khi retry.

    Chiến lược:
      1. Cache hit  → fake-stream từ cache (instant)
      2. Attempt 1  → real stream, collect toàn bộ, sau đó fake-stream
      3. Attempt 2–3 → retry nếu attempt 1 lỗi (clean, không yield gì trước đó)
      4. Fail all    → yield friendly error

    Trade-off: thấy chữ xuất hiện sau khi AI xong (thay vì từng ký tự).
    Lợi: không bao giờ duplicate content, retry luôn sạch.
    """
    # ── 1. Cache hit ───────────────────────────────────
    cached = cache_get(user_input, profile)
    if cached:
        _bump_stat("hits")
        for i in range(0, len(cached), 25):
            yield cached[i:i+25]
            time.sleep(0.003)
        return
    _bump_stat("misses")

    # ── 2. Setup ───────────────────────────────────────
    client   = get_client()
    model    = get_model(client)
    history  = build_hist(M())
    enhanced = user_input
    if needs_search(user_input):
        enhanced += "\n\n[HỆ THỐNG]: Dùng Google Search tìm điểm chuẩn 2025. Ưu tiên website chính thức."

    last_err: Optional[Exception] = None

    # ── 3. Retry loop (collect-first, no streaming mid-retry) ──
    for attempt in range(3):
        try:
            full_text = _do_stream(client, model, enhanced, profile, history)
            # Stream fake: yield từng chunk nhỏ để UX mượt
            for i in range(0, len(full_text), 20):
                yield full_text[i:i+20]
                time.sleep(0.002)
            # Cache nếu thành công
            if needs_search(user_input):
                cache_set(user_input, full_text, profile)
            return

        except Exception as e:
            last_err  = e
            err_lower = str(e).lower()

            # Auth error → không retry
            if any(k in err_lower for k in ["api_key","authentication","401","403","permission"]):
                yield "\n\n" + friendly_error(str(e))
                return

            # Grounding error → thử lại không có search tool (1 lần)
            if any(k in err_lower for k in ["grounding","tool","search","400","invalid"]) and attempt==0:
                try:
                    cfg2  = types.GenerateContentConfig(
                        system_instruction=build_system(profile),
                        temperature=0.65, max_output_tokens=8192)
                    chat2 = client.chats.create(model=model, config=cfg2, history=history)
                    buf   = []
                    for chunk in chat2.send_message_stream(user_input):
                        if chunk.text: buf.append(chunk.text)
                    if buf:
                        result = "".join(buf)
                        for i in range(0, len(result), 20):
                            yield result[i:i+20]
                            time.sleep(0.002)
                        yield ("\n\n---\n*(⚠️ Google Search tạm lỗi — nội dung từ kiến thức có sẵn. "
                               "Kiểm tra lại điểm chuẩn trên website trường nhé.)*")
                        return
                except Exception:
                    pass

            if attempt < 2:
                time.sleep(2 ** attempt)   # backoff: 1s, 2s

    yield "\n\n" + friendly_error(str(last_err) if last_err else "unknown")

# ════════════════════════════════════════════════════════
#  HTML EXPORT — FIX #6: escape AI content
# ════════════════════════════════════════════════════════
def _escape(text: str) -> str:
    """FIX #6: escape HTML special chars."""
    return (text.replace("&","&amp;").replace("<","&lt;")
                .replace(">","&gt;").replace('"',"&quot;"))

def generate_html_report(student: Dict) -> str:
    p     = student.get("profile", {})
    msgs  = student.get("messages", [])
    notes = student.get("notes", "")
    ts    = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pct   = profile_completion(p)

    def _md_to_html(text: str) -> str:
        text = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END','',text,flags=re.DOTALL)
        text = _escape(text)   # FIX #6: escape trước khi render
        text = re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
        text = re.sub(r'\*(.+?)\*',    r'<em>\1</em>',text)
        text = re.sub(r'^## (.+)$',    r'<h3>\1</h3>',text,flags=re.M)
        text = re.sub(r'^# (.+)$',     r'<h2>\1</h2>',text,flags=re.M)
        text = re.sub(r'^---$',        r'<hr>',text,flags=re.M)
        text = re.sub(r'\n{2,}',       '<br><br>',text)
        text = re.sub(r'\n',           '<br>',text)
        return text

    conv_html = ""
    for m in msgs[1:]:
        if m["role"] == "user":
            conv_html += f'<div class="msg-user"><div class="msg-role">🎓 Học sinh hỏi</div><div class="msg-body">{_escape(m["content"])}</div></div>'
        else:
            conv_html += f'<div class="msg-ai"><div class="msg-role">👨‍🏫 Thầy T tư vấn</div><div class="msg-body">{_md_to_html(m["content"])}</div></div>'

    profile_rows = ""
    for lbl, key in [("Điểm thi thử","score"),("Tổ hợp","combo"),
                     ("Ngành quan tâm","major"),("Sở thích","strengths"),
                     ("Ngân sách/tháng","budget"),("Khoảng cách","distance")]:
        val = p.get(key,"") or "—"
        profile_rows += f'<tr><td class="p-label">{lbl}</td><td class="p-val">{_escape(val)}</td></tr>'

    notes_html = ""
    if notes.strip():
        notes_html = f'<div class="notes-box"><div class="notes-title">📝 Ghi Chú Thầy/Cô</div><div>{_escape(notes).replace(chr(10),"<br>")}</div></div>'

    return f"""<!DOCTYPE html>
<html lang="vi"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phiếu Tư Vấn — {_escape(student['name'])}</title>
<style>
:root{{--blue:#2563eb;--bg:#fff;--text:#1a1a2e;--muted:#555;--border:#e2e8f0;--ai-bg:#fffbeb;--user-bg:#eff6ff}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:var(--text);
      max-width:820px;margin:0 auto;padding:40px 28px;line-height:1.7;font-size:14px}}
.header{{border-bottom:3px solid var(--blue);padding-bottom:20px;margin-bottom:26px}}
.header-top{{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}}
.header h1{{font-size:1.6rem;color:var(--blue);font-weight:800;margin-bottom:4px}}
.header .sub{{color:var(--muted);font-size:.82rem}}
.badge{{background:var(--blue);color:#fff;border-radius:6px;padding:4px 12px;font-size:.75rem;font-weight:700}}
.prog-section{{margin-bottom:20px}}
.prog-bar{{height:6px;background:#e2e8f0;border-radius:3px}}
.prog-fill{{height:100%;background:linear-gradient(90deg,#2563eb,#60a5fa);border-radius:3px}}
.prog-label{{font-size:.72rem;color:var(--muted);margin-bottom:4px}}
.section-title{{font-size:.71rem;color:var(--muted);font-weight:700;letter-spacing:1.5px;
                 text-transform:uppercase;margin-bottom:9px;padding-bottom:5px;border-bottom:2px solid var(--border)}}
.profile-table{{width:100%;border-collapse:collapse;margin-bottom:20px}}
.profile-table tr{{border-bottom:1px solid var(--border)}}
.p-label{{padding:8px 12px 8px 0;color:var(--muted);font-size:.83rem;width:140px;vertical-align:top}}
.p-val{{padding:8px 0;font-weight:600;font-size:.9rem}}
.notes-box{{background:var(--ai-bg);border-left:4px solid var(--blue);border-radius:0 8px 8px 0;
             padding:14px 18px;margin-bottom:22px;font-size:.88rem}}
.notes-title{{font-weight:700;color:var(--blue);margin-bottom:6px;font-size:.76rem;text-transform:uppercase}}
.msg-user{{background:var(--user-bg);border-radius:12px 12px 4px 12px;
            padding:13px 17px;margin-bottom:13px;border:1px solid #bfdbfe}}
.msg-ai{{background:var(--ai-bg);border-radius:4px 12px 12px 12px;
          padding:13px 17px;margin-bottom:13px;border:1px solid #fde68a}}
.msg-role{{font-size:.71rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px}}
.msg-body{{font-size:.9rem;line-height:1.75}}
.msg-body h2,.msg-body h3{{color:var(--blue);margin:11px 0 5px;font-size:1rem}}
.msg-body hr{{border:none;border-top:1px solid var(--border);margin:9px 0}}
.footer{{border-top:2px solid var(--border);padding-top:14px;margin-top:28px;
          color:var(--muted);font-size:.75rem;text-align:center;line-height:1.8}}
.print-hint{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
              padding:10px 16px;margin-bottom:20px;font-size:.83rem;color:#1d4ed8;text-align:center}}
@media print{{.print-hint{{display:none}} body{{padding:20px}} .msg-user,.msg-ai{{break-inside:avoid}}}}
</style>
</head><body>
<div class="print-hint">🖨️ Để lưu PDF: Ctrl+P (Windows) / Cmd+P (Mac) → chọn <strong>Save as PDF</strong></div>
<div class="header">
  <div class="header-top">
    <div><div style="font-size:1.8rem;margin-bottom:5px">🎓</div>
      <h1>Phiếu Tư Vấn Hướng Nghiệp</h1>
      <div class="sub">Thầy T — Hướng Nghiệp 12 PRO v9.0 · {ts}</div></div>
    <div class="badge">👤 {_escape(student['name'])}</div>
  </div>
</div>
<div class="prog-section">
  <div class="prog-label">Mức độ hoàn thiện hồ sơ: <strong>{pct}%</strong></div>
  <div class="prog-bar"><div class="prog-fill" style="width:{pct}%"></div></div>
</div>
<div class="section-title">Hồ Sơ Học Sinh</div>
<table class="profile-table">{profile_rows}</table>
{notes_html}
<div class="section-title">Nội Dung Tư Vấn ({len(msgs)-1} lượt)</div>
{conv_html or '<p style="color:#999;font-style:italic">Chưa có nội dung tư vấn.</p>'}
<div class="footer">
  Phiếu tư vấn: <strong>Thầy T — Hướng Nghiệp 12 PRO v9.0</strong><br>
  Điểm chuẩn từ nguồn chính thức · Dự báo 2026 chỉ mang tính tham khảo
</div>
</body></html>"""

# ════════════════════════════════════════════════════════
#  QUIZ (FIX: màu sáng cho light theme)
# ════════════════════════════════════════════════════════
QUIZ = [
    {"q":"Em thích làm việc với...","opts":{"A":"Con số, dữ liệu, phân tích logic",
        "B":"Con người — dạy học, tư vấn, giao tiếp","C":"Thiên nhiên, sinh vật, thực phẩm, môi trường",
        "D":"Máy móc, công nghệ, lập trình, hệ thống"}},
    {"q":"Điều em tự hào nhất ở bản thân là...","opts":{"A":"Tư duy logic, giỏi giải quyết vấn đề",
        "B":"Kỹ năng giao tiếp, thuyết phục","C":"Sự kiên nhẫn, tỉ mỉ, quan sát tốt",
        "D":"Sáng tạo, thích khám phá cái mới"}},
    {"q":"Sau này em muốn làm việc ở...","opts":{"A":"Công ty, ngân hàng, cơ quan nhà nước",
        "B":"Trường học, bệnh viện, tổ chức phi lợi nhuận","C":"Nông trại, phòng lab, nhà máy, môi trường",
        "D":"Công ty công nghệ, startup, làm freelance"}},
    {"q":"Môn học em thích nhất ở THPT là...","opts":{"A":"Toán, Vật lý, Hóa học",
        "B":"Văn, Lịch sử, GDCD, Ngoại ngữ","C":"Sinh học, Địa lý, Hóa học","D":"Toán, Tin học, Vật lý"}},
    {"q":"Em lo ngại nhất điều gì khi chọn ngành?","opts":{"A":"Điểm chuẩn quá cao, khó đậu",
        "B":"Ra trường khó xin việc","C":"Học phí và chi phí sinh hoạt tốn kém",
        "D":"Sợ học không phù hợp với bản thân"}},
]
QUIZ_RESULT = {
    "A":{"group":"Kinh tế — Tài chính — Kế toán","icon":"💼",
         "desc":"Tư duy phân tích tốt — Kế toán, Tài chính NH, Kinh tế, QTKD.",
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
    st.markdown("*5 câu · 2 phút · tìm ra nhóm ngành phù hợp nhất*"); st.divider()
    sid = st.session_state.active_sid
    qa_k, done_k = f"qa_{sid}", f"qd_{sid}"
    st.session_state.setdefault(qa_k, {})
    st.session_state.setdefault(done_k, False)

    if st.session_state[done_k]:
        top = Counter(st.session_state[qa_k].values()).most_common(1)[0][0]
        res = QUIZ_RESULT[top]
        st.success("✅ Hoàn thành!")
        # FIX: màu sáng cho light theme
        st.markdown(f"""
<div style="background:#fff;border:2px solid #2563eb;border-radius:13px;padding:20px 24px;box-shadow:0 4px 15px rgba(37,99,235,.1)">
  <div style="font-size:1.8rem;margin-bottom:7px">{res['icon']}</div>
  <div style="font-family:'Playfair Display',serif;font-size:1.2rem;color:#0f172a;font-weight:700;margin-bottom:7px">
    Nhóm ngành: <span style="color:#2563eb">{res['group']}</span></div>
  <div style="color:#475569;line-height:1.7;font-size:.9rem">{res['desc']}</div>
  <div style="margin-top:12px;padding-top:10px;border-top:1px solid #e2e8f0">
    <span style="font-size:.7rem;color:#64748b;text-transform:uppercase">Ngành gợi ý</span>
    <div style="color:#0f172a;font-weight:600;margin-top:4px">{res['suggest']}</div></div>
  <div style="margin-top:9px">
    <span style="font-size:.7rem;color:#64748b;text-transform:uppercase">Trường gần Tây Ninh</span>
    <div style="color:#0f172a;font-weight:600;margin-top:4px">{res['schools']}</div></div>
</div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🔄 Làm lại", use_container_width=True):
                st.session_state[qa_k]={};st.session_state[done_k]=False;st.rerun()
        with c2:
            if st.button("💬 Hỏi Thầy T ngay", use_container_width=True):
                ng = res["suggest"].split(",")[0].strip()
                st.session_state["_pend"]=(f"Thầy T ơi, em quiz ra nhóm **{res['group']}**. "
                    f"Ngành **{ng}** điểm chuẩn 2023–2025 bao nhiêu, trường nào tốt gần Tây Ninh?")
                st.toast("✅ Chuyển sang tab Chat nhé!",icon="💬");st.rerun()
        return

    ans=st.session_state[qa_k]
    st.progress(len(ans)/len(QUIZ))
    st.markdown(f'<div style="font-size:.78rem;color:#64748b;margin:8px 0 13px">Tiến độ: {len(ans)}/{len(QUIZ)} câu</div>',
                unsafe_allow_html=True)
    for idx,item in enumerate(QUIZ):
        qno=idx+1
        if qno in ans:
            ch=ans[qno]
            # FIX: màu sáng
            st.markdown(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:9px;'
                        f'padding:10px 14px;margin-bottom:8px;font-size:.86rem">'
                        f'<span style="color:#64748b">Câu {qno}:</span> '
                        f'<span style="color:#0f172a">{item["q"]}</span>'
                        f'<br><span style="color:#16a34a;font-weight:600">✓ {ch}: {item["opts"][ch]}</span></div>',
                        unsafe_allow_html=True); continue
        st.markdown(f'<div style="font-weight:700;color:#0f172a;font-size:.95rem;margin-bottom:8px">Câu {qno}/{len(QUIZ)}: {item["q"]}</div>',
                    unsafe_allow_html=True)
        cols=st.columns(2)
        for j,(k,v) in enumerate(item["opts"].items()):
            with cols[j%2]:
                if st.button(f"{k}. {v}",key=f"q{sid}_{idx}_{k}",use_container_width=True):
                    ans[qno]=k
                    if len(ans)==len(QUIZ):st.session_state[done_k]=True
                    st.rerun()
        break

# ════════════════════════════════════════════════════════
#  SO SÁNH NGÀNH
# ════════════════════════════════════════════════════════
def run_compare():
    st.markdown("### ⚖️ So Sánh Ngành Nghề")
    c1,c2=st.columns(2)
    with c1: ng1=st.text_input("🅰️ Ngành thứ nhất",placeholder="VD: Kế toán",key="cmp1")
    with c2: ng2=st.text_input("🅱️ Ngành thứ hai", placeholder="VD: Tài chính NH",key="cmp2")
    if st.button("🔍 So sánh ngay",use_container_width=True,type="primary"):
        if ng1.strip() and ng2.strip():
            st.session_state["_pend"]=(f"Thầy T ơi, em phân vân **{ng1.strip()}** vs **{ng2.strip()}**. "
                f"So sánh: điểm chuẩn 2023–2025, cơ hội việc làm, lương, phù hợp Tây Ninh?")
            st.toast("✅ Chuyển sang tab Chat nhé!",icon="💬");st.rerun()
        else: st.warning("⚠️ Nhập đủ 2 ngành nhé!")
    st.divider(); st.markdown("**💡 Cặp ngành hay so sánh:**")
    pairs=[("Kế toán","Tài chính Ngân hàng"),("CNTT","Kỹ thuật Điện tử"),
           ("Y khoa","Dược học"),("Sư phạm Toán","Toán ứng dụng"),
           ("Xây dựng","Kiến trúc"),("Nông nghiệp CNC","Công nghệ Thực phẩm")]
    cols=st.columns(3)
    for i,(a,b) in enumerate(pairs):
        with cols[i%3]:
            if st.button(f"⚖️ {a} vs {b}",key=f"cp_{i}",use_container_width=True):
                st.session_state["_pend"]=(f"Thầy T ơi, em phân vân **{a}** vs **{b}**. "
                    f"So sánh điểm chuẩn 2023–2025, cơ hội việc làm, lương, phù hợp Tây Ninh?")
                st.toast("✅ Chuyển sang tab Chat!",icon="💬");st.rerun()

# ════════════════════════════════════════════════════════
#  LỊCH TUYỂN SINH 2026 (FIX: màu sáng)
# ════════════════════════════════════════════════════════
CALENDAR = [
    {"month":"Tháng 3–5/2026","events":[
        {"date":"Tháng 3–5","name":"Xét tuyển sớm — Học bạ & Năng khiếu",
         "desc":"Theo dõi để không bỏ lỡ đợt nộp hồ sơ.","tag":"important","label":"📋 Theo dõi"},
        {"date":"24/4–5/5","name":"Đăng ký dự thi tốt nghiệp THPT 2026",
         "desc":"Đăng ký trực tuyến. Kiểm tra kỹ thông tin cá nhân và bài thi tự chọn.","tag":"urgent","label":"⚠️ ĐĂNG KÝ THI"},
    ]},
    {"month":"Tháng 6/2026","events":[
        {"date":"10/6","name":"Làm thủ tục dự thi",
         "desc":"Thí sinh đến điểm thi làm thủ tục, đính chính sai sót.","tag":"important","label":"📋 Thủ tục"},
        {"date":"11–12/6","name":"🎓 KỲ THI THPT QUỐC GIA 2026",
         "desc":"Ngày 11: Ngữ văn (sáng), Toán (chiều). Ngày 12: Bài tự chọn. Mang CCCD & thẻ dự thi.","tag":"urgent","label":"🎓 NGÀY THI"},
    ]},
    {"month":"Tháng 7/2026","events":[
        {"date":"8h 1/7","name":"📊 Công bố điểm thi THPT 2026",
         "desc":"Tra điểm tại thisinh.thitotnghiepthpt.edu.vn. Ghi lại ngay để tính tổ hợp.","tag":"important","label":"📊 Nhận điểm"},
        {"date":"2/7–14/7","name":"Đăng ký nguyện vọng xét tuyển",
         "desc":"Mỗi thí sinh TỐI ĐA 15 NGUYỆN VỌNG. Sắp xếp từ trường yêu thích nhất xuống.","tag":"urgent","label":"⚠️ NGUYỆN VỌNG"},
        {"date":"15–21/7","name":"Nộp lệ phí xét tuyển",
         "desc":"Thanh toán trực tuyến để chốt danh sách nguyện vọng.","tag":"important","label":"💳 Lệ phí"},
    ]},
    {"month":"Tháng 8–9/2026","events":[
        {"date":"Trước 13/8","name":"Công bố điểm chuẩn đợt 1",
         "desc":"Các trường thông báo điểm chuẩn và danh sách trúng tuyển.","tag":"important","label":"📋 Điểm chuẩn"},
        {"date":"Trước 21/8","name":"✅ Xác nhận nhập học",
         "desc":"Xác nhận trực tuyến. KHÔNG xác nhận = MẤT SUẤT HỌC!","tag":"urgent","label":"✅ XÁC NHẬN"},
        {"date":"Tháng 9","name":"Khai giảng 2026–2027","desc":"Bắt đầu hành trình đại học!","tag":"info","label":"🎉 Khai giảng"},
    ]},
]

def render_calendar():
    st.markdown("### 📅 Lịch Tuyển Sinh 2026")
    st.markdown("*Timeline — các mốc thầy/cô cần nhắc nhở học sinh*")
    st.markdown('<div style="display:flex;gap:9px;flex-wrap:wrap;margin:10px 0 16px">'
                '<span class="cal-tag tag-urgent">⚠️ Cực kỳ quan trọng</span>'
                '<span class="cal-tag tag-important">📋 Quan trọng</span>'
                '<span class="cal-tag tag-info">ℹ️ Cần biết</span></div>',
                unsafe_allow_html=True)
    st.divider()
    for block in CALENDAR:
        st.markdown(f'<div style="font-family:\'Playfair Display\',serif;font-size:1rem;'
                    f'color:#0f172a;font-weight:700;margin-bottom:10px">📆 {block["month"]}</div>',
                    unsafe_allow_html=True)
        for ev in block["events"]:
            tag_html = f'<span class="cal-tag tag-{ev["tag"]}">{ev["label"]}</span>'
            st.markdown(f'<div class="cal-event {ev["tag"]}">'
                        f'<div class="cal-date">{ev["date"]}</div>'
                        f'<div><div class="cal-name">{ev["name"]}</div>'
                        f'<div class="cal-desc">{ev["desc"]}</div>{tag_html}</div></div>',
                        unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    st.info("📌 Các mốc dựa theo lịch 2025 — theo dõi cập nhật tại **moet.gov.vn**")

# ════════════════════════════════════════════════════════
#  QUICK TEMPLATES
# ════════════════════════════════════════════════════════
TEMPLATES = {
    "🎯 Điểm chuẩn & Dự báo":[
        ("📊","Điểm chuẩn ngành {ngành} 2023–2025 và dự báo 2026?"),
        ("🏥","Điểm chuẩn Y Dược TP.HCM 3 năm gần nhất?"),
        ("💻","CNTT các trường gần Tây Ninh: bảng điểm chuẩn 2023–2025"),
        ("📐","Sư phạm Toán ĐH Cần Thơ: điểm chuẩn + tổ hợp"),
        ("⚙️","Kỹ thuật Xây dựng phía Nam: bảng điểm chuẩn đầy đủ"),
        ("🌿","Nông nghiệp CNC ĐH Nông Lâm: điểm chuẩn + việc làm"),
    ],
    "🏫 Chọn trường phù hợp":[
        ("🗺️","Với {điểm} điểm tổ hợp {tổ_hợp}, em nên đăng ký trường nào?"),
        ("📍","Trường tốt trong bán kính 100km từ Tây Ninh là trường nào?"),
        ("💰","Trường có học phí dưới 3 triệu/tháng cho ngành {ngành}?"),
        ("🏠","Trường nào có ký túc xá tốt, gần Tây Ninh?"),
        ("🎓","Top 5 trường ĐH TP.HCM phù hợp học sinh Tây Ninh?"),
        ("🔁","Nếu rớt NV1, NV2 em nên chọn trường nào dự phòng?"),
    ],
    "💼 Nghề nghiệp & Lương":[
        ("💵","Ra trường ngành {ngành} làm gì, lương bao nhiêu?"),
        ("📈","Ngành nào đang thiếu nhân lực, lương cao ở Tây Ninh?"),
        ("🌐","Ngành CNTT làm remote được không, cần học gì?"),
        ("🏦","Kế toán vs Tài chính Ngân hàng: việc làm và lương thực tế?"),
        ("🩺","Điều dưỡng và Y tế cộng đồng: cơ hội việc làm tại địa phương?"),
        ("🔧","Kỹ sư Cơ khí/Xây dựng: lương năm 1, 5, 10 năm kinh nghiệm?"),
    ],
    "🎯 Chiến lược xét tuyển":[
        ("📝","Hướng dẫn đăng ký NV1/NV2/NV3 cho em {điểm} điểm"),
        ("⚠️","Sai lầm phổ biến khi đăng ký nguyện vọng cần tránh?"),
        ("🔄","Xét tuyển sớm (học bạ) và thi THPT khác nhau thế nào?"),
        ("📊","Với điểm học bạ 8.5, em xét tuyển sớm ngành gì được?"),
        ("💡","Khi nào nên đặt trường top làm NV1, khi nào không?"),
        ("🎰","Chiến lược an toàn khi đặt nguyện vọng: bao nhiêu NV là đủ?"),
    ],
}

def render_templates():
    st.markdown("### 📋 Bộ Câu Hỏi Nhanh")
    st.markdown("*Nhấn để tự động điền vào ô chat*"); st.divider()
    for section, items in TEMPLATES.items():
        st.markdown(f'<div class="tpl-title">{section}</div>',unsafe_allow_html=True)
        cols = st.columns(2)
        for i,(ic,txt) in enumerate(items):
            with cols[i%2]:
                if st.button(f"{ic} {txt[:55]}{'...' if len(txt)>55 else ''}",
                             key=f"tpl_{section}_{i}", use_container_width=True):
                    p = P()
                    filled = (txt
                        .replace("{ngành}",  p.get("major","[tên ngành]") or "[tên ngành]")
                        .replace("{điểm}",   p.get("score","[điểm]") or "[điểm]")
                        .replace("{tổ_hợp}", p.get("combo","A00").split("—")[0].strip() or "A00"))
                    st.session_state["_pend"]=filled
                    st.toast("✅ Đã điền — chuyển sang tab Chat nhé!",icon="💬"); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  SEARCH
# ════════════════════════════════════════════════════════
def render_search():
    st.markdown("### 🔍 Tìm Kiếm Lịch Sử Chat")
    st.markdown("*Tìm qua toàn bộ cuộc trò chuyện của tất cả học sinh*"); st.divider()
    query = st.text_input("🔍 Từ khoá...",placeholder="VD: Y Dược, điểm chuẩn, Sư phạm...",key="search_q")
    if not query or len(query.strip())<2:
        st.markdown('<div style="color:#94a3b8;font-size:.87rem;margin-top:14px">Nhập ít nhất 2 ký tự.</div>',
                    unsafe_allow_html=True); return
    results = []
    for sid,stu in st.session_state.students.items():
        for i,msg in enumerate(stu["messages"]):
            if msg["role"]!="user": continue
            q_txt = msg["content"]
            a_txt = stu["messages"][i+1]["content"] if i+1<len(stu["messages"]) else ""
            a_clean = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END','',a_txt,flags=re.DOTALL)
            if query.lower() in q_txt.lower() or query.lower() in a_clean.lower():
                results.append({"student":stu["name"],"sid":sid,
                                "question":q_txt,"answer":a_clean.strip()[:280],"idx":i})
    if not results:
        st.warning(f'Không tìm thấy kết quả cho **"{query}"**'); return
    st.markdown(f'<div style="color:#16a34a;font-size:.84rem;margin-bottom:12px">✅ <strong>{len(results)}</strong> kết quả</div>',
                unsafe_allow_html=True)
    def hl(t: str) -> str:
        return re.sub(re.escape(query),
                      lambda m:f'<span class="sr-hl">{m.group()}</span>',
                      t, flags=re.IGNORECASE)
    for r in results:
        q_hl = hl(r["question"][:80]+("..." if len(r["question"])>80 else ""))
        a_hl = hl(r["answer"][:220]+("..." if len(r["answer"])>220 else ""))
        st.markdown(f'<div class="sr-card"><div class="sr-student">👤 {r["student"]}</div>'
                    f'<div class="sr-q">❓ {q_hl}</div><div class="sr-preview">{a_hl}</div></div>',
                    unsafe_allow_html=True)
        if st.button(f"→ Xem chat của {r['student']}",key=f"sr_{r['sid']}_{r['idx']}"):
            st.session_state.active_sid=r["sid"]
            st.toast(f"✅ Chuyển sang {r['student']}",icon="👤"); st.rerun()

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
                        f'<div class="ds-lbl">{lbl}</div></div>',unsafe_allow_html=True)
    st.divider()
    majors=[s["profile"].get("major","") for s in students if s["profile"].get("major","")]
    if majors and PLOTLY_OK:
        st.markdown("#### 🎯 Ngành Học Sinh Quan Tâm")
        mc = Counter(majors)
        fig = go.Figure(go.Bar(x=list(mc.values()),y=list(mc.keys()),orientation='h',
            marker=dict(color='#2563eb',line=dict(color='#1d4ed8',width=1)),
            text=list(mc.values()),textposition='outside'))
        fig.update_layout(
            paper_bgcolor="#f8fafc",plot_bgcolor="#ffffff",
            font=dict(color="#475569",family="Inter",size=11),
            xaxis=dict(gridcolor="#f1f5f9",linecolor="#e2e8f0",tickfont=dict(color="#64748b")),
            yaxis=dict(gridcolor="#f1f5f9",linecolor="#e2e8f0",tickfont=dict(color="#0f172a")),
            margin=dict(l=10,r=40,t=10,b=10),height=max(140,len(mc)*44))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.divider()
    st.markdown("#### 👥 Danh Sách Học Sinh")
    hdr=st.columns([3,2,2,2,1])
    for c,t in zip(hdr,["Tên","Tổ hợp","Ngành","Điểm thử","# Tin"]):
        c.markdown(f"**{t}**")
    st.markdown('<hr style="margin:5px 0"/>',unsafe_allow_html=True)
    for s in students:
        p=s["profile"]; cs=st.columns([3,2,2,2,1])
        is_a=s["id"]==st.session_state.active_sid
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
        st.markdown(f'<div style="font-size:.67rem;color:#64748b">🤖 '
                    f'<span style="color:#16a34a;font-weight:600">'
                    f'{st.session_state.confirmed_model}</span></div>',unsafe_allow_html=True)
    st.caption("Teacher Edition v9.0 · Light Theme")

    # Cache stats
    cs_stat = st.session_state.get("_cache_stats",{})
    if cs_stat.get("hits",0)+cs_stat.get("misses",0)>0:
        total = cs_stat["hits"]+cs_stat["misses"]
        pct   = int(cs_stat["hits"]/total*100)
        st.markdown(f'<div class="cache-pill">💾 Cache {pct}% · tiết kiệm {cs_stat["hits"]} lần gọi API</div>',
                    unsafe_allow_html=True)
    st.divider()

    # ── HỌC SINH ──────────────────────────────────────
    st.markdown("### 👥 Học Sinh")
    for sid,s in list(st.session_state.students.items()):
        is_a  = sid==st.session_state.active_sid
        n_msg = len(s["messages"])-1
        combo = s["profile"].get("combo","").split("—")[0].strip()
        info  = " · ".join(filter(None,[combo,s["profile"].get("major",""),
                                        f"{n_msg} tin" if n_msg else ""]))
        st.markdown(f'<div class="stu-card {"active" if is_a else ""}">'
                    f'<div class="sname">{s["name"]}</div>'
                    f'<div class="sinfo">{info or "Chưa có hồ sơ"}</div>'
                    f'{"<div class=\'sbadge\'>ACTIVE</div>" if is_a else ""}'
                    f'</div>',unsafe_allow_html=True)
        if not is_a:
            if st.button(f"→ Chọn",key=f"sel_{sid}",use_container_width=True):
                st.session_state.active_sid=sid;st.rerun()

    col_inp,col_btn=st.columns([3,1])
    with col_inp:
        new_name=st.text_input("",placeholder="Tên học sinh mới...",key="new_name",
                               label_visibility="collapsed")
    with col_btn:
        st.markdown("<div style='margin-top:4px'>",unsafe_allow_html=True)
        if st.button("➕",key="add_stu"):
            if new_name.strip():
                ns=_blank_student(new_name.strip())
                st.session_state.students[ns["id"]]=ns
                st.session_state.active_sid=ns["id"]; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    if len(st.session_state.students)>1:
        if st.button(f"🗑️ Xoá {S()['name']}",use_container_width=True,key="del_stu"):
            del st.session_state.students[st.session_state.active_sid]
            st.session_state.active_sid=next(iter(st.session_state.students))
            st.rerun()
    st.divider()

    # ── HỒ SƠ ─────────────────────────────────────────
    st.markdown(f"### 📋 Hồ Sơ: {S()['name']}")

    # NEW v9.0: Profile completion bar
    pct_comp = profile_completion(P())
    pct_color = "#16a34a" if pct_comp==100 else "#2563eb" if pct_comp>=50 else "#f59e0b"
    st.markdown(f"""
<div class="prog-wrap">
  <div class="prog-label">
    <span>Độ hoàn thiện hồ sơ</span>
    <span style="color:{pct_color};font-weight:700">{pct_comp}%</span>
  </div>
  <div class="prog-bar">
    <div class="prog-fill" style="width:{pct_comp}%;background:{pct_color}"></div>
  </div>
</div>""", unsafe_allow_html=True)

    p=P()
    combo_opts=["Chưa chọn","A00 — Toán·Lý·Hóa","A01 — Toán·Lý·Anh","B00 — Toán·Hóa·Sinh",
                "C00 — Văn·Sử·Địa","D01 — Toán·Văn·Anh","D07 — Toán·Hóa·Anh","C14 — Văn·Toán·GDCD","Khác"]
    budget_opts=["Chưa biết","Dưới 3 triệu","3–5 triệu","5–8 triệu","Trên 8 triệu"]
    dist_opts=["Không giới hạn","Trong tỉnh Tây Ninh","Bán kính 100 km","Bán kính 200 km"]
    def _i(lst,val,d=0): return lst.index(val) if val in lst else d

    raw_score=st.text_input("📊 Điểm thi thử",value=p.get("score",""),
                            placeholder="VD: 23.5",key="ps")
    score_clean,score_err=validate_score(raw_score)
    if score_err:
        st.markdown(f'<div style="color:#dc2626;font-size:.77rem;margin-top:-8px;margin-bottom:4px">'
                    f'⚠️ {score_err}</div>',unsafe_allow_html=True)
    cb_v=st.selectbox("📚 Tổ hợp",combo_opts,index=_i(combo_opts,p.get("combo","Chưa chọn")),key="pc")
    mj_v=st.text_input("🎯 Ngành quan tâm",value=p.get("major",""),placeholder="VD: Sư phạm Toán",key="pm")
    st_v=st.text_input("💡 Sở thích",value=p.get("strengths",""),placeholder="VD: Thích dạy học",key="pst")
    bd_v=st.selectbox("💰 Chi phí/tháng",budget_opts,index=_i(budget_opts,p.get("budget","Chưa biết")),key="pb")
    dt_v=st.selectbox("🗺️ Khoảng cách",dist_opts,index=_i(dist_opts,p.get("distance","Không giới hạn")),key="pd")

    if st.button("💾 Lưu hồ sơ",use_container_width=True,key="save_p",type="primary"):
        if not score_err:
            S()["profile"]={"score":score_clean,"combo":cb_v if cb_v!="Chưa chọn" else "",
                            "major":mj_v.strip(),"strengths":st_v.strip(),
                            "budget":bd_v if bd_v!="Chưa biết" else "",
                            "distance":dt_v if dt_v!="Không giới hạn" else ""}
            st.success("✅ Đã lưu!")
        else:
            st.error("❌ Sửa điểm trước khi lưu")
    st.divider()

    # ── GHI CHÚ ───────────────────────────────────────
    st.markdown("### 📝 Ghi Chú")
    notes=st.text_area("",value=S().get("notes",""),
                       placeholder="Ghi chú riêng của thầy/cô...",
                       height=88,key="notes_a",label_visibility="collapsed")
    if st.button("💾 Lưu ghi chú",use_container_width=True,key="save_n"):
        S()["notes"]=notes;st.success("✅ Đã lưu!")
    st.divider()

    # ── EXPORT ────────────────────────────────────────
    if len(M())>1:
        html_report=generate_html_report(S())
        st.download_button(
            label=f"📄 Xuất HTML (có thể in PDF) — {S()['name']}",
            data=html_report.encode("utf-8"),
            file_name=f"PhieuTuVan_{S()['name'].replace(' ','_')}_{datetime.datetime.now().strftime('%d%m%Y')}.html",
            mime="text/html",use_container_width=True)
        ts=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        export=(f"PHIẾU TƯ VẤN — THẦY T v9.0\nHọc sinh: {S()['name']}\nNgày: {ts}\n{'='*50}\n\n")
        if S().get("notes"): export+=f"[GHI CHÚ]\n{S()['notes']}\n\n{'—'*40}\n\n"
        for m in M():
            role="Học sinh" if m["role"]=="user" else "Thầy T"
            txt=re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END','[Bảng/Gợi ý]',m["content"],flags=re.DOTALL)
            export+=f"[{role}]\n{txt}\n\n{'—'*40}\n\n"
        st.download_button(label=f"📥 Xuất TXT — {S()['name']}",
            data=export.encode("utf-8"),
            file_name=f"TuVan_{S()['name'].replace(' ','_')}_{datetime.datetime.now().strftime('%d%m%Y')}.txt",
            mime="text/plain",use_container_width=True)

    if st.button("🗑️ Xoá chat hiện tại",use_container_width=True,key="clr"):
        S()["messages"]=[{"role":"assistant","content":GREETING}];st.rerun()
    if st.button("🗑️ Xoá cache",use_container_width=True,key="clr_cache"):
        st.session_state._cache={}
        st.session_state._cache_stats={"hits":0,"misses":0,"saves":0}
        st.toast("✅ Đã xoá cache",icon="🗑️")

# ════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-eyebrow">✦ v9.0 · Python 3.9+ · All Fixes · Light Theme</div>
      <div class="hero-title">Thầy <span class="gold">T</span> — Hướng Nghiệp 12 PRO</div>
      <div class="hero-sub">Đang tư vấn: <strong style="color:#1d4ed8">{S()['name']}</strong>
        · Hồ sơ hoàn thiện <strong style="color:#1d4ed8">{profile_completion(P())}%</strong>
        · Điểm chuẩn 2023–2025 + Dự báo 2026</div>
    </div>
    <div class="hero-chips">
      <span class="hchip hc-live">⚡ Streaming</span>
      <span class="hchip hc-gold">📈 Charts</span>
      <span class="hchip hc-blue">💾 Cache</span>
      <span class="hchip hc-purple">🔁 Retry</span>
      <span class="hchip hc-red">📄 HTML Export</span>
      <span class="hchip hc-def">🛡️ Py3.9+</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════
tab_chat, tab_tpl, tab_quiz, tab_compare, tab_cal, tab_dash, tab_bk, tab_search = st.tabs([
    "💬 Chat","📋 Templates","🧭 Quiz","⚖️ So Sánh","📅 Lịch 2026","📊 Dashboard","🔖 Bookmark","🔍 Tìm Kiếm",
])

# ════════════════════════════════════════════════════════
#  TAB CHAT
# ════════════════════════════════════════════════════════
SUGGESTIONS=[
    ("🏥","Điểm chuẩn Y Dược TP.HCM 2023–2025 và dự báo 2026?"),
    ("💻","CNTT: trường nào gần Tây Ninh, bảng điểm chuẩn 3 năm?"),
    ("📐","Sư phạm Toán ĐH Cần Thơ: điểm chuẩn + việc làm"),
    ("⚙️","Kỹ thuật Xây dựng phía Nam: bảng điểm chuẩn 2023–2026"),
    ("🌿","Nông nghiệp CNC: trường tốt, điểm chuẩn, nghề gì?"),
    ("💰","Tài chính Ngân hàng: học ở đâu, ra trường lương bao nhiêu?"),
]

with tab_chat:
    msgs=M()
    for idx,msg in enumerate(msgs):
        with st.chat_message(msg["role"]):
            if msg["role"]=="assistant":
                fq=parse_and_render(msg["content"])
                if idx>0:
                    c_bk,_=st.columns([1,8])
                    with c_bk:
                        if st.button("🔖",key=f"bk_{st.session_state.active_sid}_{idx}",
                                     help="Bookmark câu trả lời này"):
                            q=msgs[idx-1]["content"] if idx>0 else ""
                            st.session_state.bookmarks.append({
                                "question":q,"answer":msg["content"],
                                "student":S()["name"],
                                "ts":datetime.datetime.now().strftime("%d/%m %H:%M")})
                            st.toast("✅ Đã bookmark!",icon="🔖")
                # FIX #5: guard fq không rỗng trước khi tạo cột
                if fq and idx==len(msgs)-1 and len(fq)>0:
                    st.markdown('<div class="fu-wrap"><div class="fu-lbl">💡 Câu hỏi tiếp theo</div></div>',
                                unsafe_allow_html=True)
                    n_cols = min(3, max(1, len(fq)))   # FIX: đảm bảo >= 1
                    fu_cols=st.columns(n_cols)
                    for fi,fq_t in enumerate(fq[:3]):
                        with fu_cols[fi%n_cols]:
                            if st.button(f"→ {fq_t[:50]}",key=f"fu_{idx}_{fi}",use_container_width=True):
                                st.session_state["_pend"]=fq_t;st.rerun()
            else:
                st.markdown(msg["content"])

    if len(msgs)==1:
        st.markdown('<div class="slbl">✦ Câu hỏi gợi ý</div>',unsafe_allow_html=True)
        cols=st.columns(3)
        for i,(ic,txt) in enumerate(SUGGESTIONS):
            with cols[i%3]:
                if st.button(f"{ic} {txt}",key=f"sg_{i}_{st.session_state.active_sid}"):
                    st.session_state["_pend"]=txt;st.rerun()

    pend       = st.session_state.pop("_pend",None)
    user_query = pend or st.chat_input(
        f"Hỏi Thầy T cho {S()['name']} — điểm chuẩn, chọn ngành, chọn trường... 💬",
        key=f"cin_{st.session_state.active_sid}")

    if user_query:
        M().append({"role":"user","content":user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            # Cache badge
            if needs_search(user_query) and cache_get(user_query, P()) is not None:
                st.markdown('<div class="cache-pill" style="margin-bottom:8px">💾 Từ cache (30 phút)</div>',
                            unsafe_allow_html=True)

            # NEW v9.0: Typing indicator
            typing_ph = st.empty()
            with typing_ph:
                show_typing("Thầy T đang tìm kiếm và soạn câu trả lời..." if needs_search(user_query)
                            else "Thầy T đang soạn câu trả lời...")

            full_text = ""
            stream_ph = st.empty()

            for chunk in stream_response(user_query, P()):
                full_text += chunk
                stream_ph.markdown(full_text + "▌")

            typing_ph.empty()
            stream_ph.empty()

            if not full_text.strip():
                full_text = "⚠️ Thầy T chưa nhận được nội dung từ AI. Em thử hỏi lại nhé!"

            fq_final = parse_and_render(full_text)

            # FIX #5 ở đây cũng
            if fq_final and len(fq_final)>0:
                st.markdown('<div class="fu-wrap"><div class="fu-lbl">💡 Câu hỏi tiếp theo</div></div>',
                            unsafe_allow_html=True)
                n_cols=min(3,max(1,len(fq_final)))
                fu_cols=st.columns(n_cols)
                for fi,fq_t in enumerate(fq_final[:3]):
                    with fu_cols[fi%n_cols]:
                        if st.button(f"→ {fq_t[:50]}",key=f"fu_new_{fi}",use_container_width=True):
                            st.session_state["_pend"]=fq_t;st.rerun()

        M().append({"role":"assistant","content":full_text})
        st.rerun()

with tab_tpl:     render_templates()
with tab_quiz:    run_quiz()
with tab_compare: run_compare()
with tab_cal:     render_calendar()
with tab_dash:    run_dashboard()

with tab_bk:
    st.markdown("### 🔖 Câu Trả Lời Đã Lưu")
    bks=st.session_state.bookmarks
    if not bks:
        st.info("Chưa có bookmark. Nhấn **🔖** dưới câu trả lời hay trong tab Chat!")
    else:
        st.markdown(f"*{len(bks)} bookmark đã lưu*"); st.divider()
        for i,bk in enumerate(reversed(bks)):
            ri=len(bks)-1-i
            with st.expander(f"🔖 [{bk['student']}] {bk['question'][:55]}{'...' if len(bk['question'])>55 else ''} · {bk['ts']}"):
                parse_and_render(bk["answer"])
                if st.button("🗑️ Xoá",key=f"del_bk_{ri}"):
                    st.session_state.bookmarks.pop(ri);st.rerun()
        st.divider()
        if st.button("🗑️ Xoá tất cả"): st.session_state.bookmarks=[];st.rerun()

with tab_search: render_search()

# ════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;color:#94a3b8;font-size:.69rem;
padding:14px 0 8px;border-top:1px solid #e2e8f0;margin-top:16px">
✦ <strong style="color:#475569">Thầy T — v9.0 Stable · Light Theme · Python 3.9+</strong>
· Gemini 2.5 Flash · Streaming · Cache · Retry · HTML Export<br>
Điểm chuẩn từ nguồn chính thức · Dự báo 2026 chỉ mang tính tham khảo<br>
<span style="color:#cbd5e1">Made with ❤️ for học sinh Tây Ninh</span>
</div>
""", unsafe_allow_html=True)
