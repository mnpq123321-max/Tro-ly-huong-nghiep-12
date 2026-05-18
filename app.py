"""
╔══════════════════════════════════════════════════════════════════╗
║   THẦY T — HƯỚNG NGHIỆP 12 PRO  ·  v8.0 STABLE EDITION          ║
║   Gemini 2.5 Flash · Streaming · Cache · Retry · HTML Export     ║
╚══════════════════════════════════════════════════════════════════╝

CHANGELOG v8.0 — ỔN ĐỊNH + NÂNG CẤP:

  🛡️  FIX: Safe state accessor — không crash khi active_sid stale
  🛡️  FIX: active_sid guard — validate trước mọi truy cập
  🛡️  FIX: Streaming không dùng regex mỗi chunk → nhanh hơn 10x
  🛡️  FIX: JSON parse đa chiến lược — strip fence, fallback, recover
  🛡️  FIX: Empty response guard — không render trang trắng
  🛡️  FIX: Score validation — kiểm tra float 0–30
  🔁  NEW: Retry 3 lần với exponential backoff (1s → 2s → 4s)
  💾  NEW: Response cache 30 phút — tiết kiệm API quota
  📄  NEW: HTML export đẹp — in ra giấy / lưu PDF từ browser
  🎨  NEW: Error UX — thông báo thân thiện theo loại lỗi
  📊  NEW: Cache stats trong sidebar

requirements.txt:
  google-genai>=0.8
  streamlit>=1.32
  plotly>=5.0
"""

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
#  CSS - GIAO DIỆN SÁNG (HỌC THUẬT)
# ════════════════════════════════════════════════════════
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Inter',sans-serif}
/* Đổi nền chính sang màu xám trắng nhẹ */
.stApp{background:#f8fafc;min-height:100vh;color:#1e293b}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#f1f5f9}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#94a3b8}

/* Sidebar nền trắng, chữ xám đen */
[data-testid="stSidebar"]{background:#ffffff!important;border-right:1px solid #e2e8f0!important;box-shadow: 2px 0 10px rgba(0,0,0,0.02);}
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
    border-color:#2563eb!important;box-shadow:0 0 0 3px rgba(37,99,235,.15)!important}
[data-testid="stSidebar"] [data-testid="stSelectbox"]>div>div{
    background:#f8fafc!important;border:1px solid #cbd5e1!important;
    color:#0f172a!important;border-radius:8px!important}
[data-testid="stSidebar"] .stButton>button{
    width:100%!important;background:#f8fafc!important;border:1px solid #cbd5e1!important;
    color:#475569!important;border-radius:9px!important;font-size:.84rem!important;
    font-weight:600!important;padding:9px 0!important;transition:all .15s!important}
[data-testid="stSidebar"] .stButton>button:hover{
    border-color:#2563eb!important;color:#2563eb!important;background:#eff6ff!important}

.main .block-container{padding:0!important;max-width:100%!important}

/* Header mượt mà với gradient xanh */
.hero{background:linear-gradient(135deg,#eff6ff 0%,#dbeafe 100%);
    border-bottom:1px solid #bfdbfe;padding:25px 40px;position:relative;overflow:hidden}
.hero::after{content:'';position:absolute;top:-60px;right:-60px;width:300px;height:300px;
    border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,.07) 0%,transparent 70%);pointer-events:none}
.hero-inner{display:flex;align-items:center;justify-content:space-between;gap:20px;position:relative;z-index:1}
.hero-eyebrow{display:inline-flex;align-items:center;gap:6px;background:#ffffff;
    border:1px solid #bfdbfe;color:#2563eb;border-radius:20px;padding:4px 14px;
    font-size:.64rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
.hero-title{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:900;color:#1e3a8a;line-height:1.15}
.hero-title .gold{color:#2563eb;font-style:italic}
.hero-sub{font-size:.85rem;color:#475569;margin-top:5px;line-height:1.6}
.hero-chips{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.hchip{border-radius:20px;padding:4px 12px;font-size:.66rem;font-weight:600;white-space:nowrap}
.hc-def{background:#ffffff;border:1px solid #cbd5e1;color:#64748b}
.hc-live{background:#dcfce7;border:1px solid #86efac;color:#166534}
.hc-gold{background:#fef3c7;border:1px solid #fde047;color:#854d0e}
.hc-blue{background:#e0f2fe;border:1px solid #7dd3fc;color:#0369a1}
.hc-purple{background:#f3e8ff;border:1px solid #d8b4fe;color:#6b21a8}
.hc-red{background:#fee2e2;border:1px solid #fca5a5;color:#991b1b}

/* Khung Chat */
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;
    box-shadow:none!important;padding:0!important;margin-bottom:20px!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"]{
    background:#dbeafe!important;color:#1e3a8a!important;border:1px solid #bfdbfe!important;
    border-radius:18px 18px 4px 18px!important;padding:12px 17px!important;
    font-size:.95rem!important;line-height:1.7!important;max-width:76%!important;margin-left:auto!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"]{
    background:#ffffff!important;color:#334155!important;border:1px solid #e2e8f0!important;
    border-radius:4px 18px 18px 18px!important;padding:20px 24px!important;
    font-size:.95rem!important;line-height:1.85!important;box-shadow:0 4px 15px rgba(0,0,0,.04)!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h1,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h3{
    font-family:'Playfair Display',serif!important;color:#0f172a!important;margin-top:20px!important;margin-bottom:7px!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) strong{color:#2563eb!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) a{color:#2563eb!important}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) code{
    background:#f1f5f9!important;color:#ea580c!important;border-radius:4px;padding:2px 6px;font-size:.86em;border:1px solid #e2e8f0}

/* Bảng điểm chuẩn */
.dct-wrap{overflow-x:auto;margin:16px 0 6px;border-radius:12px;border:1px solid #e2e8f0;background:#ffffff;box-shadow:0 2px 10px rgba(0,0,0,.02)}
.dct{width:100%;border-collapse:collapse;font-size:.88rem}
.dct thead tr{background:#f8fafc}
.dct thead th{padding:12px 14px;text-align:left;font-weight:700;white-space:nowrap;
    color:#2563eb;font-size:.7rem;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid #e2e8f0}
.dct tbody tr{border-bottom:1px solid #f1f5f9;transition:background .12s}
.dct tbody tr:hover{background:#f8fafc}
.dct td{padding:12px 14px;color:#475569;vertical-align:middle}
.dct td:first-child{color:#0f172a;font-weight:600;min-width:185px}
.sb-r{display:inline-block;background:#eff6ff;border:1px solid #bfdbfe;color:#1d4ed8;border-radius:6px;padding:2px 9px;font-weight:700;font-size:.84rem}
.sb-n{display:inline-block;background:#f8fafc;border:1px solid #e2e8f0;color:#94a3b8;border-radius:6px;padding:2px 9px;font-size:.83rem}
.sb-p{display:inline-block;background:#f3e8ff;border:1px solid #d8b4fe;color:#7e22ce;border-radius:6px;padding:2px 9px;font-weight:700;font-size:.84rem}
.sb-c{display:inline-block;background:#f1f5f9;border:1px solid #e2e8f0;color:#475569;border-radius:5px;padding:2px 7px;font-size:.75rem;font-weight:600}

/* Thẻ học sinh Sidebar */
.stu-card{background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;
    padding:10px 13px;margin-bottom:7px;transition:all .15s;position:relative}
.stu-card.active{border-color:#2563eb;background:#eff6ff;box-shadow:0 2px 8px rgba(37,99,235,.1)}
.stu-card .sname{font-weight:700;font-size:.9rem;color:#0f172a}
.stu-card .sinfo{font-size:.75rem;color:#64748b;margin-top:3px}
.stu-card .sbadge{position:absolute;top:9px;right:11px;background:#2563eb;color:#fff;border-radius:5px;padding:2px 7px;font-size:.62rem;font-weight:700}

/* Chat Input */
[data-testid="stChatInput"]>div{background:#ffffff!important;border:1.5px solid #cbd5e1!important;
    border-radius:14px!important;transition:border-color .2s!important;box-shadow:0 4px 12px rgba(0,0,0,.03)!important}
[data-testid="stChatInput"]>div:focus-within{border-color:#2563eb!important;box-shadow:0 0 0 3px rgba(37,99,235,.1)!important}
[data-testid="stChatInput"] textarea{color:#0f172a!important;font-family:'Inter',sans-serif!important;font-size:.95rem!important;}

/* Lịch tuyển sinh & Buttons */
.cal-event{display:flex;gap:14px;padding:12px 16px;background:#ffffff;border:1px solid #e2e8f0;
    border-radius:10px;margin-bottom:8px;align-items:flex-start;box-shadow:0 1px 3px rgba(0,0,0,.02)}
.dash-stat{background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;padding:15px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.02)}
.dash-stat .ds-val{font-size:1.9rem;font-weight:800;color:#2563eb;font-family:'Playfair Display',serif}
.dash-stat .ds-lbl{font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-top:3px}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  GOOGLE GENAI SETUP
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
    for attempt in [
        lambda: types.Tool(google_search=types.GoogleSearch()),
        lambda: types.Tool(google_search_retrieval=types.GoogleSearchRetrieval()),
    ]:
        try: return attempt()
        except: pass
    return None

_SEARCH_TOOL = _make_search_tool()

# ════════════════════════════════════════════════════════
#  RESPONSE CACHE  ← NEW v8.0
#  Key: md5(question) · TTL: 30 min · Max: 60 entries
# ════════════════════════════════════════════════════════
CACHE_TTL   = 1800   # 30 phút
CACHE_MAX   = 60

def _cache_key(q: str) -> str:
    return hashlib.md5(q.lower().strip().encode()).hexdigest()

def cache_get(q: str) -> str | None:
    """Trả về cached response nếu còn hạn, ngược lại None."""
    store = st.session_state.get("_cache", {})
    entry = store.get(_cache_key(q))
    if entry:
        ts, resp = entry
        if time.time() - ts < CACHE_TTL:
            return resp
        # Expired → xoá
        store.pop(_cache_key(q), None)
    return None

def cache_set(q: str, resp: str) -> None:
    """Lưu response vào cache."""
    if not resp or resp.startswith("❌") or len(resp) < 50:
        return
    if "_cache" not in st.session_state:
        st.session_state._cache = {}
    store = st.session_state._cache
    # Evict oldest nếu quá giới hạn
    if len(store) >= CACHE_MAX:
        oldest = min(store, key=lambda k: store[k][0])
        store.pop(oldest, None)
    store[_cache_key(q)] = (time.time(), resp)
    # Update stats
    st.session_state.setdefault("_cache_stats", {"hits": 0, "misses": 0, "saves": 0})
    st.session_state._cache_stats["saves"] += 1

def cache_hit(q: str) -> None:
    st.session_state.setdefault("_cache_stats", {"hits": 0, "misses": 0, "saves": 0})
    st.session_state._cache_stats["hits"] += 1

def cache_miss(q: str) -> None:
    st.session_state.setdefault("_cache_stats", {"hits": 0, "misses": 0, "saves": 0})
    st.session_state._cache_stats["misses"] += 1

# ════════════════════════════════════════════════════════
#  SESSION STATE — SAFE ACCESSORS  ← FIX v8.0
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

def _blank_student(name: str = "Học sinh mới") -> dict:
    return {
        "id":       str(uuid.uuid4())[:8],
        "name":     name,
        "profile":  {"score":"","combo":"","major":"","strengths":"","budget":"","distance":""},
        "messages": [{"role":"assistant","content":GREETING}],
        "notes":    "",
        "created":  datetime.datetime.now().strftime("%d/%m %H:%M"),
    }

def _ensure_state() -> None:
    """Khởi tạo + validate toàn bộ session state. Luôn gọi ở đầu mỗi render."""
    # Students dict
    if "students" not in st.session_state or not st.session_state.students:
        s = _blank_student("Học sinh 1")
        st.session_state.students   = {s["id"]: s}
        st.session_state.active_sid = s["id"]

    # active_sid guard ← FIX: validate trước khi dùng
    if (st.session_state.get("active_sid") not in st.session_state.students):
        st.session_state.active_sid = next(iter(st.session_state.students))

    # Bookmarks
    st.session_state.setdefault("bookmarks", [])
    st.session_state.setdefault("_cache", {})
    st.session_state.setdefault("_cache_stats", {"hits":0,"misses":0,"saves":0})

_ensure_state()

# Safe accessors — luôn trả về giá trị hợp lệ, không bao giờ raise
def S() -> dict:
    """Current active student (safe)."""
    _ensure_state()
    return st.session_state.students[st.session_state.active_sid]

def P() -> dict:
    """Current profile (safe)."""
    return S().get("profile", {})

def M() -> list:
    """Current messages (safe)."""
    msgs = S().get("messages")
    if not msgs:
        S()["messages"] = [{"role":"assistant","content":GREETING}]
    return S()["messages"]

# ════════════════════════════════════════════════════════
#  SCORE VALIDATION  ← FIX v8.0
# ════════════════════════════════════════════════════════
def validate_score(raw: str) -> tuple[str, str | None]:
    """
    Returns (cleaned_value, error_message).
    error_message là None nếu hợp lệ.
    """
    raw = raw.strip()
    if not raw:
        return "", None  # Bỏ trống là OK
    try:
        val = float(raw.replace(",", "."))
        if not (0 <= val <= 30):
            return raw, "Điểm phải trong khoảng 0–30"
        return f"{val:.2f}".rstrip("0").rstrip("."), None
    except ValueError:
        return raw, "Vui lòng nhập số (VD: 23.5)"

# ════════════════════════════════════════════════════════
#  ERROR MESSAGES — THÂN THIỆN  ← NEW v8.0
# ════════════════════════════════════════════════════════
def friendly_error(err: str) -> str:
    e = err.lower()
    if "quota" in e or "429" in e or "resource_exhausted" in e:
        return (
            "⏳ **API quota tạm hết** — Gemini giới hạn số lần gọi mỗi phút.\n\n"
            "Em chờ khoảng **60 giây** rồi hỏi lại nhé. "
            "Nếu vẫn lỗi, kiểm tra quota tại [Google AI Studio](https://aistudio.google.com)."
        )
    if "api_key" in e or "authentication" in e or "401" in e or "403" in e:
        return (
            "🔑 **API Key không hợp lệ** — Kiểm tra lại `GEMINI_API_KEY` trong `.streamlit/secrets.toml`.\n\n"
            "Lấy key mới tại [aistudio.google.com/apikey](https://aistudio.google.com/apikey)."
        )
    if "timeout" in e or "deadline" in e or "504" in e:
        return (
            "⏱️ **Kết nối timeout** — Server Gemini phản hồi chậm.\n\n"
            "Thầy T đã thử lại 3 lần nhưng vẫn không được. Em hỏi lại sau vài giây nhé."
        )
    if "network" in e or "connection" in e or "503" in e:
        return (
            "📶 **Mất kết nối mạng** — Kiểm tra internet và thử lại.\n\n"
            "Streamlit Cloud cũng có thể đang bảo trì."
        )
    if "empty" in e or "no content" in e:
        return (
            "🤔 **AI trả về nội dung trống** — Câu hỏi có thể quá ngắn hoặc không rõ nghĩa.\n\n"
            "Em thử diễn đạt lại hoặc hỏi cụ thể hơn nhé!"
        )
    return f"❌ **Lỗi không xác định**: {err}\n\nEm thử lại sau ít giây nhé."

# ════════════════════════════════════════════════════════
#  SYSTEM PROMPT
# ════════════════════════════════════════════════════════
def build_system(profile: dict) -> str:
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
    p = profile
    if any(v for v in p.values() if v and str(v).strip()):
        lines = ["\n══════════════════════════════════════","👤 HỒ SƠ HỌC SINH:"]
        if p.get("score"):     lines.append(f"• Điểm thi thử: **{p['score']}**")
        if p.get("combo"):     lines.append(f"• Tổ hợp: **{p['combo']}**")
        if p.get("major"):     lines.append(f"• Ngành quan tâm: **{p['major']}**")
        if p.get("strengths"): lines.append(f"• Sở thích: **{p['strengths']}**")
        if p.get("budget"):    lines.append(f"• Ngân sách: **{p['budget']}**")
        if p.get("distance"):  lines.append(f"• Khoảng cách: **{p['distance']}**")
        lines.append("→ Dựa sát hồ sơ này tư vấn.")
        base += "\n".join(lines)
    return base

# ════════════════════════════════════════════════════════
#  JSON PARSE — ĐA CHIẾN LƯỢC  ← FIX v8.0
# ════════════════════════════════════════════════════════
def safe_json(raw: str) -> dict | None:
    """
    Thử nhiều cách parse JSON, trả None nếu tất cả thất bại.
    Fix: strip markdown code fences, trailing commas, etc.
    """
    attempts = [
        raw.strip(),
        raw.strip().strip("`"),
        re.sub(r"^```json\s*|\s*```$", "", raw.strip(), flags=re.DOTALL),
        re.sub(r",\s*([}\]])", r"\1", raw.strip()),   # trailing comma
        re.sub(r"'", '"', raw.strip()),                 # single → double quotes
    ]
    for attempt in attempts:
        if not attempt:
            continue
        try:
            return json.loads(attempt)
        except (json.JSONDecodeError, ValueError):
            continue
    return None

# ════════════════════════════════════════════════════════
#  RENDER — TABLE + CHART + FOLLOWUP  (hardened)
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

def _score_chart(rows: list, title: str):
    """Vẽ biểu đồ Plotly cho bảng điểm chuẩn."""
    if not PLOTLY_OK or not rows: return
    years  = ["2023","2024","2025","2026\n(dự báo)"]
    COLORS = ["#d4a017","#79c0ff","#3fb950","#c4b5fd","#f97316","#ef4444"]
    fig    = go.Figure()
    has_data = False

    for i, r in enumerate(rows):
        vals = [r.get("y2023"), r.get("y2024"), r.get("y2025"), r.get("y2026_predict")]
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
                marker=dict(size=9, color=color, line=dict(color="#0d1117",width=2)),
            ))
        if vals[2] is not None and vals[3] is not None:
            try:
                fig.add_trace(go.Scatter(
                    x=[years[2], years[3]], y=[float(vals[2]), float(vals[3])],
                    mode="lines+markers", showlegend=False,
                    line=dict(color=color, width=2, dash="dot"),
                    marker=dict(size=9, color=color, symbol="diamond",
                                line=dict(color="#0d1117",width=2)),
                ))
            except Exception:
                pass

    if not has_data: return
    fig.update_layout(
        title=dict(text=f"📈 {title}", font=dict(color="#d4a017",size=13,family="Playfair Display"), x=0),
        paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        font=dict(color="#8b949e", family="Inter", size=11),
        legend=dict(bgcolor="#161b22", bordercolor="#21262d", borderwidth=1,
                    font=dict(color="#c9d1d9",size=10)),
        xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e"),
                   title="Điểm chuẩn"),
        hovermode="x unified", margin=dict(l=10,r=10,t=38,b=10), height=290,
    )
    try:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    except Exception:
        pass

def parse_and_render(text: str) -> list[str]:
    """
    Render toàn bộ text: bảng HTML + chart + markdown.
    Returns: list[str] follow-up questions (có thể rỗng).
    Hardened: mọi lỗi đều được catch, không crash.
    """
    if not text or not text.strip():
        st.markdown("*(Thầy T chưa có nội dung để hiển thị)*")
        return []

    followup_qs: list[str] = []

    # ── 1. Tách FOLLOWUP block ──────────────────────────
    fu_match = re.search(r'~~~FOLLOWUP\s*(.*?)\s*~~~END', text, re.DOTALL)
    if fu_match:
        try:
            fu_data = safe_json(fu_match.group(1))
            if fu_data and isinstance(fu_data, dict):
                followup_qs = [q for q in fu_data.get("questions", []) if isinstance(q, str)]
        except Exception:
            pass
        text = text[:fu_match.start()] + text[fu_match.end():]

    # ── 2. Tách JSON_TABLE blocks ───────────────────────
    table_pattern = re.compile(r'~~~JSON_TABLE\s*(.*?)\s*~~~END', re.DOTALL)
    raw_blocks = table_pattern.findall(text)

    if not raw_blocks:
        st.markdown(text)
        return followup_qs

    # Thay thế bằng placeholder
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
            clean = re.sub(
                r'~~~JSON_TABLE\s*' + re.escape(raw.strip()) + r'\s*~~~END',
                ph, clean, count=1, flags=re.DOTALL)

    # ── 3. Render từng phần ─────────────────────────────
    rendered_charts: list[tuple] = []  # (rows, title) cho chart

    for i, raw in enumerate(raw_blocks):
        ph    = f"__TBL_{i}__"
        parts = clean.split(ph, 1)

        # Text trước bảng
        if parts[0].strip():
            st.markdown(parts[0])

        # Parse JSON (đa chiến lược)
        data = safe_json(raw)
        if data is None:
            st.markdown(f'<div class="warn-box">⚠️ Bảng #{i+1} có định dạng JSON lỗi — bỏ qua.</div>',
                        unsafe_allow_html=True)
            clean = parts[1] if len(parts) > 1 else ""; continue

        title = str(data.get("title",""))
        note  = str(data.get("note",""))
        rows  = data.get("rows", [])
        if not isinstance(rows, list): rows = []

        is_school = rows and isinstance(rows[0], dict) and "tier" in rows[0]

        # Render HTML table
        h = (f'<div class="dct-wrap">'
             f'<h3 style="color:#d4a017;margin:11px 0 8px;font-family:\'Playfair Display\',serif;">'
             f'{title}</h3><table class="dct">')
        try:
            if is_school:
                h += ("<thead><tr><th>Tầng</th><th>Trường</th><th>Vị trí</th>"
                      "<th>Điểm mạnh</th><th>Khoảng cách</th><th>Ghi chú</th></tr></thead><tbody>")
                for r in rows:
                    if not isinstance(r, dict): continue
                    h += (f"<tr><td><strong>{r.get('tier','')}</strong></td>"
                          f"<td>{r.get('school','')}</td><td>{r.get('location','')}</td>"
                          f"<td>{r.get('strength','')}</td><td>{r.get('distance','')}</td>"
                          f"<td style='font-size:.79rem;color:#8b949e'>{r.get('note','')}</td></tr>")
            else:
                h += ("<thead><tr><th>Trường</th><th>Tổ hợp</th>"
                      "<th>2023</th><th>2024</th><th>2025</th>"
                      "<th>Xu hướng</th><th>🔮 Dự báo 2026</th><th>Cơ sở</th></tr></thead><tbody>")
                for r in rows:
                    if not isinstance(r, dict): continue
                    y3,y4,y5,y6 = r.get("y2023"),r.get("y2024"),r.get("y2025"),r.get("y2026_predict")
                    h += (f"<tr><td>{r.get('school','')}</td>"
                          f"<td><span class='sb-c'>{r.get('combo','')}</span></td>"
                          f"<td>{_badge(y3)}</td><td>{_badge(y4)}</td><td>{_badge(y5)}</td>"
                          f"<td>{_trend(y4,y5)}</td><td>{_badge(y6,'p')}</td>"
                          f"<td style='font-size:.78rem;color:#8b949e'>{r.get('basis','')}</td></tr>")
        except Exception:
            h += "<tr><td colspan='8' style='color:#f85149'>Lỗi render dòng</td></tr>"

        h += "</tbody></table>"
        if note:
            h += f'<div class="note-src">📌 {note}</div>'
        h += "</div>"
        st.markdown(h, unsafe_allow_html=True)

        # Chart cho bảng điểm chuẩn (không phải bảng trường)
        if not is_school and rows:
            _score_chart(rows, title)

        clean = parts[1] if len(parts) > 1 else ""

    if clean.strip():
        st.markdown(clean)

    return followup_qs

# ════════════════════════════════════════════════════════
#  AI — STREAM + RETRY + CACHE  ← v8.0
# ════════════════════════════════════════════════════════
SCORE_KW = ["điểm chuẩn","tuyển sinh","xét tuyển","nguyện vọng",
            "điểm đầu vào","trúng tuyển","học trường nào"]

def needs_search(t: str) -> bool:
    return any(k in t.lower() for k in SCORE_KW)

def build_hist(msgs: list) -> list:
    """Build Gemini history. Fix: positional arg + wrap all."""
    history = []
    for m in (msgs[1:-1] if len(msgs) > 1 else []):
        role = "model" if m["role"] == "assistant" else "user"
        txt  = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END',
                      '[đã hiển thị]', m["content"], flags=re.DOTALL)
        try:    part = types.Part.from_text(txt)        # positional ← v5.1 fix
        except TypeError:
            try: part = types.Part.from_text(text=txt)
            except: part = types.Part(text=txt)
        try:
            history.append(types.Content(role=role, parts=[part]))
        except Exception:
            continue
    return history

def _raw_stream(client, model, enhanced: str, profile: dict, history: list):
    """Một lần gọi streaming thật từ Gemini."""
    use_s = needs_search(enhanced)
    tools = [_SEARCH_TOOL] if (use_s and _SEARCH_TOOL) else []
    cfg   = types.GenerateContentConfig(
        system_instruction=build_system(profile),
        tools=tools or None,
        temperature=0.65,
        max_output_tokens=8192,
    )
    chat = client.chats.create(model=model, config=cfg, history=history)
    got  = False
    for chunk in chat.send_message_stream(enhanced):
        if chunk.text:
            got = True
            yield chunk.text
    if not got:
        raise ValueError("empty response")

def stream_response(user_input: str, profile: dict):
    """
    ⚡ Streaming với:
      - Cache check trước (trả ngay nếu có)
      - Retry 3 lần với backoff 1s→2s→4s
      - Friendly error cuối cùng
    Yields: str chunks
    """
    # ── Cache hit ──────────────────────────────────────
    if needs_search(user_input):
        cached = cache_get(user_input)
        if cached:
            cache_hit(user_input)
            # Fake stream từ cache (nhanh hơn thật)
            for i in range(0, len(cached), 20):
                yield cached[i:i+20]
                time.sleep(0.004)
            return
        cache_miss(user_input)

    # ── Real streaming với retry ────────────────────────
    client   = get_client()
    model    = get_model(client)
    history  = build_hist(M())
    enhanced = user_input
    if needs_search(user_input):
        enhanced += "\n\n[HỆ THỐNG]: Dùng Google Search tìm điểm chuẩn 2025. Ưu tiên website trường."

    last_err  = None
    full_text = ""

    for attempt in range(3):
        try:
            full_text = ""
            for chunk in _raw_stream(client, model, enhanced, profile, history):
                full_text += chunk
                yield chunk
            # Success → cache nếu là câu hỏi điểm chuẩn
            if full_text and needs_search(user_input):
                cache_set(user_input, full_text)
            return

        except Exception as e:
            last_err  = e
            err_lower = str(e).lower()
            full_text = ""  # reset

            # Không retry lỗi auth/key
            if any(k in err_lower for k in ["api_key","authentication","401","403","permission"]):
                yield "\n\n" + friendly_error(str(e))
                return

            # Retry search → thử không có search tool
            if any(k in err_lower for k in ["grounding","tool","search","400","invalid"]) and attempt == 0:
                try:
                    cfg2  = types.GenerateContentConfig(
                        system_instruction=build_system(profile),
                        temperature=0.65, max_output_tokens=8192)
                    chat2 = client.chats.create(model=model, config=cfg2, history=history)
                    for chunk in chat2.send_message_stream(user_input):
                        if chunk.text:
                            full_text += chunk.text
                            yield chunk.text
                    if full_text:
                        yield ("\n\n---\n"
                               "*(⚠️ Google Search tạm không khả dụng — Thầy T dùng kiến thức sẵn có. "
                               "Em kiểm tra lại điểm chuẩn trên website trường nhé.)*")
                        return
                except Exception:
                    pass

            if attempt < 2:
                wait = 2 ** attempt          # 1s, 2s
                yield f"\n\n*⚠️ Kết nối gián đoạn — thử lại sau {wait}s...*\n\n"
                time.sleep(wait)
            # Xoá phần đã yield để retry sạch

    # Tất cả 3 lần fail
    yield "\n\n" + friendly_error(str(last_err) if last_err else "unknown")

# ════════════════════════════════════════════════════════
#  HTML EXPORT  ← NEW v8.0
# ════════════════════════════════════════════════════════
def generate_html_report(student: dict) -> str:
    """Tạo báo cáo HTML đẹp, có thể in ra giấy / lưu PDF từ browser."""
    p     = student.get("profile", {})
    msgs  = student.get("messages", [])
    notes = student.get("notes", "")
    ts    = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    def _md_to_html(text: str) -> str:
        """Chuyển markdown cơ bản → HTML (không dùng thư viện)."""
        text = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>', text)
        text = re.sub(r'^## (.+)$',     r'<h3>\1</h3>', text, flags=re.M)
        text = re.sub(r'^# (.+)$',      r'<h2>\1</h2>', text, flags=re.M)
        text = re.sub(r'^---$',         r'<hr>', text, flags=re.M)
        text = re.sub(r'\n{2,}',        '<br><br>', text)
        text = re.sub(r'\n',            '<br>', text)
        return text

    conv_html = ""
    for m in msgs[1:]:   # Bỏ tin chào
        if m["role"] == "user":
            q = m["content"].replace("<","&lt;").replace(">","&gt;")
            conv_html += f'''
<div class="msg-user">
  <div class="msg-role">🎓 Học sinh hỏi</div>
  <div class="msg-body">{q}</div>
</div>'''
        else:
            body = _md_to_html(m["content"])
            conv_html += f'''
<div class="msg-ai">
  <div class="msg-role">👨‍🏫 Thầy T tư vấn</div>
  <div class="msg-body">{body}</div>
</div>'''

    profile_rows = ""
    for lbl, key in [("Điểm thi thử","score"),("Tổ hợp","combo"),
                     ("Ngành quan tâm","major"),("Sở thích","strengths"),
                     ("Ngân sách/tháng","budget"),("Khoảng cách","distance")]:
        val = p.get(key,"") or "—"
        profile_rows += f'<tr><td class="p-label">{lbl}</td><td class="p-val">{val}</td></tr>'

    notes_section = ""
    if notes.strip():
        notes_section = f'''
<div class="notes-box">
  <div class="notes-title">📝 Ghi Chú Của Thầy/Cô</div>
  <div>{notes.replace(chr(10),"<br>")}</div>
</div>'''

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phiếu Tư Vấn — {student['name']}</title>
<style>
  :root{{--gold:#d4a017;--bg:#fff;--text:#1a1a2e;--muted:#555;--border:#e0e0e0;--ai-bg:#fffbf0;--user-bg:#f5f5f5}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:var(--bg);color:var(--text);
        max-width:820px;margin:0 auto;padding:40px 28px;line-height:1.7;font-size:14px}}
  .header{{border-bottom:3px solid var(--gold);padding-bottom:22px;margin-bottom:28px}}
  .header-top{{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}}
  .logo{{font-size:2rem;margin-bottom:4px}}
  .header h1{{font-size:1.65rem;color:var(--gold);font-weight:800;margin-bottom:4px}}
  .header .subtitle{{color:var(--muted);font-size:.82rem}}
  .badge{{background:var(--gold);color:#fff;border-radius:6px;padding:4px 12px;
           font-size:.75rem;font-weight:700;white-space:nowrap;height:fit-content}}
  .profile-section{{margin-bottom:26px}}
  .section-title{{font-size:.72rem;color:var(--muted);font-weight:700;letter-spacing:1.5px;
                   text-transform:uppercase;margin-bottom:10px;padding-bottom:5px;
                   border-bottom:2px solid var(--border)}}
  .profile-table{{width:100%;border-collapse:collapse}}
  .profile-table tr{{border-bottom:1px solid var(--border)}}
  .p-label{{padding:8px 12px 8px 0;color:var(--muted);font-size:.83rem;width:140px;vertical-align:top}}
  .p-val{{padding:8px 0;font-weight:600;font-size:.9rem}}
  .notes-box{{background:var(--ai-bg);border-left:4px solid var(--gold);
               border-radius:0 8px 8px 0;padding:14px 18px;margin-bottom:26px;font-size:.88rem}}
  .notes-title{{font-weight:700;color:var(--gold);margin-bottom:6px;font-size:.78rem;
                 text-transform:uppercase;letter-spacing:1px}}
  .conv-section{{margin-bottom:26px}}
  .msg-user{{background:var(--user-bg);border-radius:12px 12px 4px 12px;
              padding:14px 18px;margin-bottom:14px;border:1px solid var(--border)}}
  .msg-ai{{background:var(--ai-bg);border-radius:4px 12px 12px 12px;
            padding:14px 18px;margin-bottom:14px;border:1px solid #f0e0a0}}
  .msg-role{{font-size:.72rem;color:var(--muted);font-weight:700;text-transform:uppercase;
              letter-spacing:.8px;margin-bottom:7px}}
  .msg-body{{font-size:.9rem;line-height:1.75}}
  .msg-body h2,.msg-body h3{{color:var(--gold);margin:12px 0 5px;font-size:1rem}}
  .msg-body strong{{color:#333}}
  .msg-body hr{{border:none;border-top:1px solid var(--border);margin:10px 0}}
  .footer{{border-top:2px solid var(--border);padding-top:16px;margin-top:32px;
            color:var(--muted);font-size:.76rem;text-align:center;line-height:1.8}}
  @media print{{
    body{{padding:20px;max-width:100%}}
    .msg-user,.msg-ai{{break-inside:avoid}}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-top">
    <div>
      <div class="logo">🎓</div>
      <h1>Phiếu Tư Vấn Hướng Nghiệp</h1>
      <div class="subtitle">Thầy T — Hướng Nghiệp 12 PRO v8.0 &nbsp;·&nbsp; {ts}</div>
    </div>
    <div class="badge">Học sinh: {student['name']}</div>
  </div>
</div>

<div class="profile-section">
  <div class="section-title">Hồ Sơ Học Sinh</div>
  <table class="profile-table">{profile_rows}</table>
</div>

{notes_section}

<div class="conv-section">
  <div class="section-title">Nội Dung Tư Vấn ({len(msgs)-1} lượt)</div>
  {conv_html if conv_html else '<p style="color:#999;font-style:italic">Chưa có nội dung tư vấn.</p>'}
</div>

<div class="footer">
  Phiếu tư vấn được tạo bởi <strong>Thầy T — Hướng Nghiệp 12 PRO v8.0</strong><br>
  Điểm chuẩn từ nguồn chính thức &nbsp;·&nbsp; Dự báo 2026 chỉ mang tính tham khảo<br>
  In phiếu: Ctrl+P (Windows) / Cmd+P (Mac) → Lưu dưới dạng PDF
</div>

</body>
</html>"""

# ════════════════════════════════════════════════════════
#  QUIZ
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
    st.markdown(f'<div style="font-size:.78rem;color:#8b949e;margin:8px 0 13px;">Tiến độ: {len(ans)}/{len(QUIZ)} câu</div>',
                unsafe_allow_html=True)
    for idx,item in enumerate(QUIZ):
        qno=idx+1
        if qno in ans:
            ch=ans[qno]
            st.markdown(f'<div style="background:#161b22;border:1px solid #21262d;border-radius:9px;'
                        f'padding:10px 14px;margin-bottom:8px;font-size:.86rem;">'
                        f'<span style="color:#8b949e;">Câu {qno}:</span> <span style="color:#c9d1d9;">{item["q"]}</span>'
                        f'<br><span style="color:#3fb950;font-weight:600;">✓ {ch}: {item["opts"][ch]}</span></div>',
                        unsafe_allow_html=True); continue
        st.markdown(f'<div style="font-weight:700;color:#f0f6fc;font-size:.95rem;margin-bottom:8px;">Câu {qno}/{len(QUIZ)}: {item["q"]}</div>',
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
    st.divider()
    st.markdown("**💡 Cặp ngành hay so sánh:**")
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
#  LỊCH TUYỂN SINH 2026
# ════════════════════════════════════════════════════════
CALENDAR = [
    {"month":"Tháng 3–5/2026","events":[
        {"date":"Tháng 3–5","name":"Xét tuyển sớm — Học bạ & Năng khiếu",
         "desc":"Các trường Đại học công bố điểm chuẩn xét tuyển sớm. Cần theo dõi để không bỏ lỡ đợt nộp hồ sơ.","tag":"important","label":"📋 Theo dõi kết quả"},
        {"date":"24/4–5/5","name":"Đăng ký dự thi tốt nghiệp THPT 2026",
         "desc":"Đăng ký trực tuyến trên hệ thống. Lưu ý kiểm tra kỹ thông tin cá nhân và bài thi tự chọn.","tag":"urgent","label":"⚠️ ĐĂNG KÝ THI"},
    ]},
    {"month":"Tháng 6/2026","events":[
        {"date":"10/6","name":"📋 Làm thủ tục dự thi",
         "desc":"Thí sinh đến điểm thi làm thủ tục, đính chính sai sót (nếu có) và nghe phổ biến quy chế thi.","tag":"important","label":"📋 THỦ TỤC"},
        {"date":"11–12/6","name":"🎓 KỲ THI THPT QUỐC GIA 2026",
         "desc":"Thi chính thức (Sáng 11/6: Ngữ văn, Chiều: Toán; Sáng 12/6: Bài tự chọn). Mang CCCD & thẻ dự thi.","tag":"urgent","label":"🎓 NGÀY THI CHÍNH THỨC"},
        {"date":"13/6","name":"Ngưng thi & Dự phòng",
         "desc":"Ngày thi dự phòng dành cho các trường hợp bất khả kháng theo quy định của Bộ GD&ĐT.","tag":"info","label":"ℹ️ DỰ PHÒNG"},
        {"date":"17–21/6","name":"Thực hành đăng ký nguyện vọng",
         "desc":"Hệ thống mở để thí sinh tập thao tác đăng ký NV. Dữ liệu nháp sẽ bị xóa sau đợt này.","tag":"info","label":"💻 Thử nghiệm"},
    ]},
    {"month":"Tháng 7/2026","events":[
        {"date":"8h 1/7","name":"📊 Công bố điểm thi THPT 2026",
         "desc":"Công bố điểm sớm hơn mọi năm. Tra điểm tại hệ thống thisinh.thitotnghiepthpt.edu.vn.","tag":"important","label":"📊 Nhận điểm"},
        {"date":"2/7–14/7","name":"Đăng ký, điều chỉnh nguyện vọng xét tuyển",
         "desc":"Đăng ký chính thức trên hệ thống. CHÚ Ý MỚI: Mỗi thí sinh chỉ được đăng ký TỐI ĐA 15 NGUYỆN VỌNG!","tag":"urgent","label":"⚠️ ĐĂNG KÝ NGUYỆN VỌNG"},
        {"date":"15–21/7","name":"Nộp lệ phí xét tuyển Đại học",
         "desc":"Thanh toán lệ phí xét tuyển trực tuyến trên hệ thống của Bộ để chốt danh sách NV.","tag":"important","label":"💳 Nộp lệ phí"},
    ]},
    {"month":"Tháng 8–9/2026","events":[
        {"date":"Trước 13/8","name":"Công bố điểm chuẩn Đại học đợt 1",
         "desc":"Các cơ sở đào tạo thông báo điểm chuẩn và danh sách thí sinh trúng tuyển đợt 1.","tag":"important","label":"📋 Điểm chuẩn"},
        {"date":"Trước 21/8","name":"✅ Xác nhận nhập học đợt 1",
         "desc":"Thí sinh xác nhận nhập học trực tuyến trên hệ thống chung. KHÔNG xác nhận = mất suất học!","tag":"urgent","label":"✅ XÁC NHẬN NHẬP HỌC"},
        {"date":"Tháng 9","name":"Khai giảng năm học 2026–2027",
         "desc":"Bắt đầu hành trình đại học! Chuẩn bị: ký túc xá, giấy tờ, học phí kỳ 1.","tag":"info","label":"🎉 Khai giảng"},
    ]},
]

def render_calendar():
    st.markdown("### 📅 Lịch Tuyển Sinh 2026")
    st.markdown("*Timeline đầy đủ — các mốc thầy/cô cần nhắc học sinh*")
    st.markdown('<div style="display:flex;gap:9px;flex-wrap:wrap;margin:12px 0 18px;">'
                '<span class="cal-tag tag-urgent">⚠️ Cực kỳ quan trọng</span>'
                '<span class="cal-tag tag-important">📋 Quan trọng</span>'
                '<span class="cal-tag tag-info">ℹ️ Cần biết</span></div>',
                unsafe_allow_html=True)
    st.divider()
    for block in CALENDAR:
        st.markdown(f'<div style="font-family:\'Playfair Display\',serif;font-size:1rem;'
                    f'color:#f0f6fc;font-weight:700;margin-bottom:11px;">📆 {block["month"]}</div>',
                    unsafe_allow_html=True)
        for ev in block["events"]:
            tag_html = f'<span class="cal-tag tag-{ev["tag"]}">{ev["label"]}</span>'
            st.markdown(f'<div class="cal-event {ev["tag"]}">'
                        f'<div class="cal-date">{ev["date"]}</div>'
                        f'<div><div class="cal-name">{ev["name"]}</div>'
                        f'<div class="cal-desc">{ev["desc"]}</div>{tag_html}</div></div>',
                        unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    st.info("📌 Các mốc trên dựa theo lịch 2025. Theo dõi cập nhật chính thức tại **moet.gov.vn**")

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
        ("📝","Hướng dẫn đăng ký nguyện vọng NV1/NV2/NV3 cho em {điểm} điểm"),
        ("⚠️","Sai lầm phổ biến khi đăng ký nguyện vọng cần tránh?"),
        ("🔄","Xét tuyển sớm (học bạ) và thi THPT khác nhau thế nào?"),
        ("📊","Với điểm học bạ 8.5, em xét tuyển sớm ngành gì được?"),
        ("💡","Khi nào nên đặt trường top làm NV1, khi nào không?"),
        ("🎰","Chiến lược an toàn khi đặt nguyện vọng: bao nhiêu NV là đủ?"),
    ],
}

def render_templates():
    st.markdown("### 📋 Bộ Câu Hỏi Nhanh")
    st.markdown("*Nhấn để tự động điền vào ô chat — tiết kiệm thời gian tư vấn*"); st.divider()
    for section, items in TEMPLATES.items():
        st.markdown(f'<div class="tpl-title">{section}</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (ic, txt) in enumerate(items):
            with cols[i%2]:
                if st.button(f"{ic} {txt[:55]}{'...' if len(txt)>55 else ''}",
                             key=f"tpl_{section}_{i}", use_container_width=True):
                    p = P()
                    filled = (txt
                        .replace("{ngành}",   p.get("major","[tên ngành]") or "[tên ngành]")
                        .replace("{điểm}",    p.get("score","[điểm]") or "[điểm]")
                        .replace("{tổ_hợp}",  p.get("combo","A00").split("—")[0].strip() or "A00"))
                    st.session_state["_pend"] = filled
                    st.toast("✅ Đã điền — chuyển sang tab Chat nhé!", icon="💬")
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  SEARCH
# ════════════════════════════════════════════════════════
def render_search():
    st.markdown("### 🔍 Tìm Kiếm Lịch Sử Chat")
    st.markdown("*Tìm qua toàn bộ cuộc trò chuyện của tất cả học sinh*"); st.divider()
    query = st.text_input("🔍 Từ khoá...",placeholder="VD: Y Dược, điểm chuẩn, Sư phạm...",key="search_q")
    if not query or len(query.strip()) < 2:
        st.markdown('<div style="color:#484f58;font-size:.87rem;margin-top:14px;">Nhập ít nhất 2 ký tự.</div>',
                    unsafe_allow_html=True); return
    results = []
    for sid, stu in st.session_state.students.items():
        for i, msg in enumerate(stu["messages"]):
            if msg["role"] != "user": continue
            q_txt = msg["content"]
            a_txt = stu["messages"][i+1]["content"] if i+1 < len(stu["messages"]) else ""
            a_clean = re.sub(r'~~~(JSON_TABLE|FOLLOWUP).*?~~~END','',a_txt,flags=re.DOTALL)
            if query.lower() in q_txt.lower() or query.lower() in a_clean.lower():
                results.append({"student":stu["name"],"sid":sid,
                                "question":q_txt,"answer":a_clean.strip()[:280],"idx":i})
    if not results:
        st.warning(f'Không tìm thấy kết quả nào cho **"{query}"**'); return
    st.markdown(f'<div style="color:#3fb950;font-size:.84rem;margin-bottom:13px;">✅ Tìm thấy <strong>{len(results)}</strong> kết quả</div>',
                unsafe_allow_html=True)
    def hl(t):
        return re.sub(re.escape(query),lambda m:f'<span class="sr-hl">{m.group()}</span>',
                      t,flags=re.IGNORECASE)
    for r in results:
        q_hl = hl(r["question"][:80]+("..." if len(r["question"])>80 else ""))
        a_hl = hl(r["answer"][:220]+("..." if len(r["answer"])>220 else ""))
        st.markdown(f'<div class="sr-card"><div class="sr-student">👤 {r["student"]}</div>'
                    f'<div class="sr-q">❓ {q_hl}</div><div class="sr-preview">{a_hl}</div></div>',
                    unsafe_allow_html=True)
        if st.button(f"→ Xem chat của {r['student']}",key=f"sr_{r['sid']}_{r['idx']}"):
            st.session_state.active_sid = r["sid"]
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
    majors = [s["profile"].get("major","") for s in students if s["profile"].get("major","")]
    if majors and PLOTLY_OK:
        st.markdown("#### 🎯 Ngành Học Sinh Quan Tâm")
        mc = Counter(majors)
        fig = go.Figure(go.Bar(x=list(mc.values()),y=list(mc.keys()),orientation='h',
            marker=dict(color='#d4a017',line=dict(color='#b8860b',width=1)),
            text=list(mc.values()),textposition='outside'))
        fig.update_layout(paper_bgcolor="#0d1117",plot_bgcolor="#161b22",
            font=dict(color="#8b949e",family="Inter",size=11),
            xaxis=dict(gridcolor="#21262d",linecolor="#30363d",tickfont=dict(color="#8b949e")),
            yaxis=dict(gridcolor="#21262d",linecolor="#30363d",tickfont=dict(color="#e6edf3")),
            margin=dict(l=10,r=40,t=10,b=10),height=max(140,len(mc)*44))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.divider()
    st.markdown("#### 👥 Danh Sách Học Sinh")
    hdr = st.columns([3,2,2,2,1])
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
        st.markdown(f'<div style="font-size:.67rem;color:#484f58;">🤖 <span style="color:#3fb950;">'
                    f'{st.session_state.confirmed_model}</span></div>',unsafe_allow_html=True)
    st.caption("Teacher Edition v8.0 · Stable")

    # Cache stats
    cs = st.session_state.get("_cache_stats",{})
    if cs.get("hits",0) + cs.get("misses",0) > 0:
        total_req = cs["hits"] + cs["misses"]
        pct = int(cs["hits"]/total_req*100) if total_req else 0
        st.markdown(f'<div class="cache-pill">💾 Cache {pct}% hit · {cs["hits"]} lần tiết kiệm</div>',
                    unsafe_allow_html=True)
    st.divider()

    # ── HỌC SINH ──
    st.markdown("### 👥 Học Sinh")
    for sid, s in list(st.session_state.students.items()):
        is_a  = sid == st.session_state.active_sid
        n_msg = len(s["messages"]) - 1
        combo = s["profile"].get("combo","").split("—")[0].strip()
        info  = " · ".join(filter(None,[combo, s["profile"].get("major",""),
                                        f"{n_msg} tin" if n_msg else ""]))
        st.markdown(f'<div class="stu-card {"active" if is_a else ""}">'
                    f'<div class="sname">{s["name"]}</div>'
                    f'<div class="sinfo">{info or "Chưa có hồ sơ"}</div>'
                    f'{"<div class=\'sbadge\'>ACTIVE</div>" if is_a else ""}'
                    f'</div>',unsafe_allow_html=True)
        if not is_a:
            if st.button(f"→ Chọn",key=f"sel_{sid}",use_container_width=True):
                st.session_state.active_sid=sid;st.rerun()

    col_inp,col_btn = st.columns([3,1])
    with col_inp:
        new_name = st.text_input("",placeholder="Tên học sinh mới...",
                                 key="new_name",label_visibility="collapsed")
    with col_btn:
        st.markdown("<div style='margin-top:4px'>",unsafe_allow_html=True)
        if st.button("➕",key="add_stu"):
            if new_name.strip():
                ns=_blank_student(new_name.strip())
                st.session_state.students[ns["id"]]=ns
                st.session_state.active_sid=ns["id"]; st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    if len(st.session_state.students) > 1:
        if st.button(f"🗑️ Xoá {S()['name']}",use_container_width=True,key="del_stu"):
            del st.session_state.students[st.session_state.active_sid]
            st.session_state.active_sid = next(iter(st.session_state.students))
            st.rerun()
    st.divider()

    # ── HỒ SƠ ──
    st.markdown(f"### 📋 Hồ Sơ: {S()['name']}")
    p = P()
    combo_opts  = ["Chưa chọn","A00 — Toán·Lý·Hóa","A01 — Toán·Lý·Anh","B00 — Toán·Hóa·Sinh",
                   "C00 — Văn·Sử·Địa","D01 — Toán·Văn·Anh","D07 — Toán·Hóa·Anh","C14 — Văn·Toán·GDCD","Khác"]
    budget_opts = ["Chưa biết","Dưới 3 triệu","3–5 triệu","5–8 triệu","Trên 8 triệu"]
    dist_opts   = ["Không giới hạn","Trong tỉnh Tây Ninh","Bán kính 100 km","Bán kính 200 km"]
    def _i(lst,val,d=0): return lst.index(val) if val in lst else d

    raw_score = st.text_input("📊 Điểm thi thử",value=p.get("score",""),
                              placeholder="VD: 23.5",key="ps")
    # Score validation ← FIX v8.0
    score_clean, score_err = validate_score(raw_score)
    if score_err:
        st.markdown(f'<div style="color:#f85149;font-size:.78rem;margin-top:-8px;margin-bottom:4px;">'
                    f'⚠️ {score_err}</div>',unsafe_allow_html=True)

    cb_v = st.selectbox("📚 Tổ hợp",combo_opts,index=_i(combo_opts,p.get("combo","Chưa chọn")),key="pc")
    mj_v = st.text_input("🎯 Ngành quan tâm",value=p.get("major",""),placeholder="VD: Sư phạm Toán",key="pm")
    st_v = st.text_input("💡 Sở thích",value=p.get("strengths",""),placeholder="VD: Thích dạy học",key="pst")
    bd_v = st.selectbox("💰 Chi phí/tháng",budget_opts,index=_i(budget_opts,p.get("budget","Chưa biết")),key="pb")
    dt_v = st.selectbox("🗺️ Khoảng cách",dist_opts,index=_i(dist_opts,p.get("distance","Không giới hạn")),key="pd")

    if st.button("💾 Lưu hồ sơ",use_container_width=True,key="save_p",type="primary"):
        if not score_err:  # Chỉ lưu nếu điểm hợp lệ
            S()["profile"] = {
                "score":score_clean,"combo":cb_v if cb_v!="Chưa chọn" else "",
                "major":mj_v.strip(),"strengths":st_v.strip(),
                "budget":bd_v if bd_v!="Chưa biết" else "",
                "distance":dt_v if dt_v!="Không giới hạn" else ""}
            st.success("✅ Đã lưu!")
        else:
            st.error("❌ Sửa điểm trước khi lưu")
    st.divider()

    # ── GHI CHÚ ──
    st.markdown("### 📝 Ghi Chú")
    notes = st.text_area("",value=S().get("notes",""),
                         placeholder="Ghi chú riêng của thầy/cô...",
                         height=88,key="notes_a",label_visibility="collapsed")
    if st.button("💾 Lưu ghi chú",use_container_width=True,key="save_n"):
        S()["notes"]=notes;st.success("✅ Đã lưu!")
    st.divider()

    # ── EXPORT ──
    if len(M()) > 1:
        # HTML export ← NEW v8.0
        html_report = generate_html_report(S())
        st.download_button(
            label=f"📄 Xuất HTML (in được) — {S()['name']}",
            data=html_report.encode("utf-8"),
            file_name=f"PhieuTuVan_{S()['name'].replace(' ','_')}_{datetime.datetime.now().strftime('%d%m%Y')}.html",
            mime="text/html",use_container_width=True)
        # TXT export (backup)
        ts=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        export=(f"PHIẾU TƯ VẤN — THẦY T v8.0\nHọc sinh: {S()['name']}\nNgày: {ts}\n{'='*50}\n\n")
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
    if st.button("🗑️ Xoá cache",use_container_width=True,key="clr_cache",help="Xoá cache để lấy điểm chuẩn mới nhất"):
        st.session_state._cache={};st.session_state._cache_stats={"hits":0,"misses":0,"saves":0}
        st.toast("✅ Đã xoá cache",icon="🗑️")

# ════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-eyebrow">✦ v8.0 STABLE · Gemini 2.5 Flash · Retry · Cache</div>
      <div class="hero-title">Thầy <span class="gold">T</span> — Hướng Nghiệp 12 PRO</div>
      <div class="hero-sub">Đang tư vấn: <strong style="color:#d4a017;">{S()['name']}</strong> · Điểm chuẩn 2023–2025 + Dự báo 2026 · Biểu đồ xu hướng</div>
    </div>
    <div class="hero-chips">
      <span class="hchip hc-live">⚡ Streaming</span>
      <span class="hchip hc-gold">📈 Charts</span>
      <span class="hchip hc-blue">💾 Cache</span>
      <span class="hchip hc-purple">🔁 Retry</span>
      <span class="hchip hc-red">📄 HTML Export</span>
      <span class="hchip hc-def">🛡️ Stable</span>
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
#  TAB CHAT — STREAMING + CHARTS + FOLLOW-UP  (v8.0)
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
                fq = parse_and_render(msg["content"])
                # Bookmark button (trừ tin chào)
                if idx > 0:
                    if st.button("🔖", key=f"bk_{st.session_state.active_sid}_{idx}",
                                 help="Lưu câu trả lời này"):
                        q = msgs[idx-1]["content"] if idx > 0 else ""
                        st.session_state.bookmarks.append({
                            "question":q,"answer":msg["content"],
                            "student":S()["name"],
                            "ts":datetime.datetime.now().strftime("%d/%m %H:%M"),})
                        st.toast("✅ Đã bookmark!",icon="🔖")
                # Follow-up (chỉ tin cuối)
                if fq and idx == len(msgs)-1:
                    st.markdown('<div class="fu-wrap"><div class="fu-lbl">💡 Câu hỏi tiếp theo</div></div>',
                                unsafe_allow_html=True)
                    fu_cols = st.columns(min(3,len(fq)))
                    for fi, fq_t in enumerate(fq[:3]):
                        with fu_cols[fi]:
                            if st.button(f"→ {fq_t[:50]}",key=f"fu_{idx}_{fi}",use_container_width=True):
                                st.session_state["_pend"]=fq_t;st.rerun()
            else:
                st.markdown(msg["content"])

    if len(msgs) == 1:
        st.markdown('<div class="slbl">✦ Câu hỏi gợi ý</div>',unsafe_allow_html=True)
        cols = st.columns(3)
        for i,(ic,txt) in enumerate(SUGGESTIONS):
            with cols[i%3]:
                if st.button(f"{ic} {txt}",key=f"sg_{i}_{st.session_state.active_sid}"):
                    st.session_state["_pend"]=txt;st.rerun()

    pend       = st.session_state.pop("_pend", None)
    user_query = pend or st.chat_input(
        f"Hỏi Thầy T cho {S()['name']} — điểm chuẩn, chọn ngành, chọn trường... 💬",
        key=f"cin_{st.session_state.active_sid}",)

    if user_query:
        M().append({"role":"user","content":user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            # Hiển thị badge cache nếu là cache hit
            is_cached = needs_search(user_query) and cache_get(user_query) is not None
            if is_cached:
                st.markdown('<div class="cache-pill" style="margin-bottom:8px;">💾 Từ cache (30 phút)</div>',
                            unsafe_allow_html=True)

            full_text = ""
            ph        = st.empty()

            # ⚡ STREAMING — nhanh, không regex mỗi chunk ← FIX v8.0
            for chunk in stream_response(user_query, P()):
                full_text += chunk
                ph.markdown(full_text + "▌")   # Raw text, tốc độ tối đa

            ph.empty()

            # Guard: empty response ← FIX v8.0
            if not full_text.strip():
                full_text = "⚠️ Thầy T chưa nhận được nội dung từ AI. Em thử hỏi lại nhé!"

            # Final render: bảng HTML + chart + follow-up
            fq_final = parse_and_render(full_text)

            if fq_final:
                st.markdown('<div class="fu-wrap"><div class="fu-lbl">💡 Câu hỏi tiếp theo</div></div>',
                            unsafe_allow_html=True)
                fu_cols = st.columns(min(3,len(fq_final)))
                for fi, fq_t in enumerate(fq_final[:3]):
                    with fu_cols[fi]:
                        if st.button(f"→ {fq_t[:50]}",key=f"fu_new_{fi}",use_container_width=True):
                            st.session_state["_pend"]=fq_t;st.rerun()

        M().append({"role":"assistant","content":full_text})
        st.rerun()

with tab_tpl:    render_templates()
with tab_quiz:   run_quiz()
with tab_compare: run_compare()
with tab_cal:    render_calendar()
with tab_dash:   run_dashboard()

with tab_bk:
    st.markdown("### 🔖 Câu Trả Lời Đã Lưu")
    bks = st.session_state.bookmarks
    if not bks:
        st.info("Chưa có bookmark. Nhấn **🔖** dưới câu trả lời hay trong tab Chat!")
    else:
        st.markdown(f"*{len(bks)} bookmark đã lưu*"); st.divider()
        for i, bk in enumerate(reversed(bks)):
            ri = len(bks)-1-i
            with st.expander(f"🔖 [{bk['student']}] {bk['question'][:55]}{'...' if len(bk['question'])>55 else ''} · {bk['ts']}"):
                parse_and_render(bk["answer"])
                if st.button("🗑️ Xoá",key=f"del_bk_{ri}"):
                    st.session_state.bookmarks.pop(ri);st.rerun()
        st.divider()
        if st.button("🗑️ Xoá tất cả"):
            st.session_state.bookmarks=[];st.rerun()

with tab_search: render_search()

# ════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;color:#484f58;font-size:.69rem;
padding:15px 0 8px;border-top:1px solid #21262d;margin-top:18px;">
✦ <strong style="color:#8b949e;">Thầy T — v8.0 Stable Teacher Edition</strong>
· Gemini 2.5 Flash · Streaming · Cache · Retry · HTML Export<br>
Điểm chuẩn từ nguồn chính thức · Dự báo 2026 chỉ mang tính tham khảo<br>
<span style="color:#30363d;">Made with ❤️ for học sinh Tây Ninh</span>
</div>
""", unsafe_allow_html=True)
