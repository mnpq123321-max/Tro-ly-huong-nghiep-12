"""
╔══════════════════════════════════════════════════════════════════╗
║   THẦY T — HƯỚNG NGHIỆP 12 PRO  ·  v5.0 FINAL                 ║
║   Gemini 2.5 Flash · Google Search Grounding                    ║
║   Bảng điểm chuẩn đẹp · Dự báo 2026 · Quiz hướng nghiệp       ║
║   So sánh ngành · Tải phiếu tư vấn · Cá nhân hóa sâu          ║
╚══════════════════════════════════════════════════════════════════╝
Cách dùng:
  1. Tạo file .streamlit/secrets.toml  →  GEMINI_API_KEY = "your_key"
  2. pip install google-genai streamlit
  3. streamlit run app.py
"""

import streamlit as st
import datetime, re, json
from google import genai
from google.genai import types

# ════════════════════════════════════════════════════════
#  PAGE CONFIG  ←  PHẢI LÀ LỆNH STREAMLIT ĐẦU TIÊN
# ════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Thầy T — Hướng Nghiệp 12 PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════
#  TOÀN BỘ CSS  —  DARK PREMIUM THEME
# ════════════════════════════════════════════════════════
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap');

/* ── RESET & BASE ─────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d1117; min-height: 100vh; color: #e6edf3; }

/* ── SCROLLBAR ────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #58a6ff; }

/* ── SIDEBAR ──────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #010409 !important;
    border-right: 1px solid #21262d !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small { color: #8b949e !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e6edf3 !important;
    font-family: 'Playfair Display', serif !important;
}
[data-testid="stSidebar"] hr { border-color: #21262d !important; margin: 12px 0 !important; }

/* sidebar text inputs */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: #161b22 !important; border: 1px solid #30363d !important;
    color: #e6edf3 !important; border-radius: 8px !important;
    font-size: .88rem !important; transition: border-color .2s !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color: #d4a017 !important; box-shadow: 0 0 0 3px rgba(212,160,23,.12) !important;
}
/* sidebar selectbox */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #161b22 !important; border: 1px solid #30363d !important;
    color: #e6edf3 !important; border-radius: 8px !important;
}
/* sidebar primary button (Lưu hồ sơ) */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #d4a017 0%, #b8860b 100%) !important;
    border: none !important; color: #0d1117 !important;
    font-weight: 800 !important; border-radius: 10px !important;
    padding: 11px 0 !important; font-size: .88rem !important;
    letter-spacing: .4px !important; transition: all .2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(212,160,23,.4) !important;
}

/* ── MAIN AREA ────────────────────────────────────── */
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── HERO BANNER ──────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #010409 0%, #0d1117 50%, #121820 100%);
    border-bottom: 1px solid #21262d;
    padding: 26px 44px; position: relative; overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 350px; height: 350px; border-radius: 50%;
    background: radial-gradient(circle, rgba(212,160,23,.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-inner { display: flex; align-items: center; justify-content: space-between;
               gap: 20px; position: relative; z-index: 1; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(212,160,23,.1); border: 1px solid rgba(212,160,23,.28);
    color: #d4a017; border-radius: 20px; padding: 4px 14px;
    font-size: .67rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 10px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.05rem; font-weight: 900; color: #f0f6fc; line-height: 1.15;
}
.hero-title .gold { color: #d4a017; font-style: italic; }
.hero-sub { font-size: .83rem; color: #8b949e; margin-top: 6px; line-height: 1.6; }
.hero-chips { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.hchip {
    border-radius: 20px; padding: 5px 13px; font-size: .7rem;
    font-weight: 600; white-space: nowrap; letter-spacing: .3px;
}
.hc-def  { background: #161b22; border: 1px solid #30363d; color: #8b949e; }
.hc-live { background: rgba(35,197,94,.1); border: 1px solid rgba(35,197,94,.3); color: #3fb950; }
.hc-gold { background: rgba(212,160,23,.1); border: 1px solid rgba(212,160,23,.3); color: #d4a017; }
.hc-blue { background: rgba(88,166,255,.08); border: 1px solid rgba(88,166,255,.25); color: #79c0ff; }

/* ── TAB BAR ──────────────────────────────────────── */
[data-testid="stTabs"] [data-testid="stTab"] {
    background: transparent !important; color: #8b949e !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    font-weight: 600 !important; font-size: .88rem !important;
    padding: 10px 18px !important; transition: all .18s !important;
}
[data-testid="stTabs"] [data-testid="stTab"]:hover { color: #e6edf3 !important; }
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    color: #d4a017 !important;
    border-bottom: 2px solid #d4a017 !important;
}
[data-testid="stTabsContent"] { padding-top: 20px !important; }

/* ── CHAT MESSAGES ────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0 !important; margin-bottom: 22px !important;
}
/* User */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background: #1c2128 !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 13px 18px !important; font-size: .95rem !important;
    line-height: 1.7 !important; max-width: 76% !important; margin-left: auto !important;
}
/* Assistant */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    background: #161b22 !important; color: #c9d1d9 !important;
    border: 1px solid #21262d !important;
    border-radius: 4px 18px 18px 18px !important;
    padding: 22px 26px !important; font-size: .96rem !important;
    line-height: 1.88 !important; box-shadow: 0 4px 30px rgba(0,0,0,.35) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h1,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h3 {
    font-family: 'Playfair Display', serif !important;
    color: #f0f6fc !important; margin-top: 22px !important; margin-bottom: 8px !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) strong { color: #d4a017 !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) a     { color: #79c0ff !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) li    { margin-bottom: 5px; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) hr    { border-color: #21262d !important; margin: 16px 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) code  {
    background: #0d1117 !important; color: #79c0ff !important;
    border-radius: 4px; padding: 1px 7px; font-size: .87em; border: 1px solid #21262d;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) blockquote {
    border-left: 3px solid #30363d; padding-left: 14px;
    color: #8b949e; margin: 12px 0;
}

/* ── ĐIỂM CHUẨN TABLE ─────────────────────────────── */
.dct-wrap { overflow-x: auto; margin: 18px 0 8px; border-radius: 12px;
             border: 1px solid #21262d; }
.dct { width: 100%; border-collapse: collapse; font-size: .88rem; }
.dct thead tr { background: #010409; }
.dct thead th {
    padding: 12px 16px; text-align: left; font-weight: 700; white-space: nowrap;
    color: #d4a017; font-size: .7rem; letter-spacing: 1.2px; text-transform: uppercase;
    border-bottom: 1px solid #21262d;
}
.dct tbody tr { border-bottom: 1px solid #161b22; transition: background .12s; }
.dct tbody tr:last-child { border-bottom: none; }
.dct tbody tr:hover { background: rgba(212,160,23,.035); }
.dct td { padding: 11px 16px; color: #8b949e; vertical-align: middle; }
.dct td:first-child { color: #e6edf3; font-weight: 600; min-width: 200px; }
.dct td:nth-child(2) { min-width: 80px; }

/* score badges */
.sb-r { display:inline-block; background:#161b22; border:1px solid rgba(212,160,23,.5);
         color:#d4a017; border-radius:7px; padding:3px 11px; font-weight:700; font-size:.86rem; }
.sb-n { display:inline-block; background:#161b22; border:1px solid #30363d;
         color:#484f58; border-radius:7px; padding:3px 11px; font-size:.84rem; }
.sb-p { display:inline-block;
         background:linear-gradient(135deg,rgba(139,92,246,.2),rgba(124,58,237,.12));
         border:1px solid rgba(139,92,246,.45);
         color:#c4b5fd; border-radius:7px; padding:3px 11px; font-weight:700; font-size:.86rem; }
.sb-c { display:inline-block; background:#1c2128; border:1px solid #30363d;
         color:#8b949e; border-radius:5px; padding:2px 8px; font-size:.76rem; font-weight:600; }
.au { color:#3fb950; font-weight:700; }
.ad { color:#f85149; font-weight:700; }
.af { color:#8b949e; font-weight:700; }

/* note boxes */
.note-pred {
    background: rgba(139,92,246,.07); border: 1px solid rgba(139,92,246,.22);
    border-radius: 10px; padding: 12px 16px; margin-top: 12px;
    font-size: .81rem; color: #c4b5fd; line-height: 1.7;
}
.note-src {
    background: rgba(212,160,23,.05); border: 1px solid rgba(212,160,23,.18);
    border-radius: 10px; padding: 10px 15px; margin-top: 8px;
    font-size: .79rem; color: #8b949e; line-height: 1.65;
}

/* ── CHAT INPUT ───────────────────────────────────── */
[data-testid="stChatInput"] > div {
    background: #161b22 !important; border: 1.5px solid #30363d !important;
    border-radius: 16px !important; box-shadow: 0 4px 30px rgba(0,0,0,.35) !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #d4a017 !important;
    box-shadow: 0 4px 30px rgba(212,160,23,.12) !important;
}
[data-testid="stChatInput"] textarea {
    color: #e6edf3 !important; font-family: 'Inter', sans-serif !important;
    font-size: .95rem !important; background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #484f58 !important; }

/* ── SUGGESTION BUTTONS ───────────────────────────── */
div[data-testid="column"] .stButton > button {
    background: #161b22 !important; border: 1px solid #21262d !important;
    color: #8b949e !important; border-radius: 12px !important;
    font-size: .81rem !important; font-weight: 500 !important;
    text-align: left !important; padding: 12px 14px !important;
    width: 100% !important; min-height: 60px !important;
    line-height: 1.45 !important; transition: all .18s !important;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #d4a017 !important; background: rgba(212,160,23,.05) !important;
    color: #e6edf3 !important; transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(212,160,23,.12) !important;
}

/* ── QUIZ BUTTONS ─────────────────────────────────── */
.quiz-btn > button {
    background: #1c2128 !important; border: 1px solid #30363d !important;
    color: #c9d1d9 !important; border-radius: 10px !important;
    font-size: .88rem !important; font-weight: 500 !important;
    padding: 12px 18px !important; width: 100% !important;
    text-align: left !important; transition: all .16s !important;
    margin-bottom: 6px !important;
}
.quiz-btn > button:hover {
    border-color: #d4a017 !important; background: rgba(212,160,23,.08) !important;
    color: #d4a017 !important;
}

/* ── SIDEBAR STAT CARD ────────────────────────────── */
.sc { background:#161b22; border:1px solid #21262d; border-radius:10px;
       padding:11px 15px; margin-bottom:8px; }
.sc-l { font-size:.66rem; color:#8b949e; font-weight:700; letter-spacing:1.2px;
          text-transform:uppercase; }
.sc-v { font-size:1rem; color:#e6edf3; font-weight:700; margin-top:4px; }
.sc-v.g { color:#d4a017; }

/* ── COMPARE CARD ─────────────────────────────────── */
.cmp-wrap { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:16px 0; }
.cmp-card {
    background:#161b22; border:1px solid #21262d; border-radius:12px;
    padding:18px 20px;
}
.cmp-head { font-family:'Playfair Display',serif; font-size:1.05rem;
             color:#f0f6fc; font-weight:700; margin-bottom:10px; }
.cmp-row  { display:flex; justify-content:space-between; align-items:baseline;
             padding:5px 0; border-bottom:1px solid #21262d; font-size:.85rem; }
.cmp-row:last-child { border-bottom:none; }
.cmp-key  { color:#8b949e; }
.cmp-val  { color:#e6edf3; font-weight:600; }
.cmp-val.g { color:#3fb950; }
.cmp-val.r { color:#f85149; }
.cmp-val.y { color:#d4a017; }

/* ── PROGRESS / STEP ──────────────────────────────── */
.step-bar {
    display:flex; align-items:center; gap:8px;
    padding:13px 18px; background:#161b22; border:1px solid #21262d;
    border-radius:12px; margin-bottom:10px; font-size:.88rem; color:#8b949e;
}
.step-bar .ico { font-size:1.1rem; }
.step-bar .txt { flex:1; }
.step-bar .spin-anim {
    width:18px; height:18px; border:2.5px solid #21262d;
    border-top:2.5px solid #d4a017; border-radius:50%;
    animation:spin .7s linear infinite; flex-shrink:0;
}
@keyframes spin { to { transform:rotate(360deg); } }

/* ── MISC ─────────────────────────────────────────── */
#MainMenu, footer, header { visibility:hidden; }
[data-testid="stDecoration"] { display:none; }
hr { border-color:#21262d !important; }
.slbl { font-size:.66rem; font-weight:700; letter-spacing:2.5px;
         text-transform:uppercase; color:#484f58; margin:10px 0 14px; }
[data-testid="stDownloadButton"] > button {
    background:#161b22 !important; border:1px solid #30363d !important;
    color:#8b949e !important; border-radius:10px !important;
    font-size:.84rem !important; width:100% !important; transition:all .2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color:#d4a017 !important; color:#d4a017 !important;
    background:rgba(212,160,23,.05) !important;
}
[data-testid="stStatusWidget"] {
    background:#161b22 !important; border:1px solid #30363d !important;
    border-radius:12px !important; color:#e6edf3 !important;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  CẤU HÌNH
# ════════════════════════════════════════════════════════
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_MODEL   = "gemini-2.5-flash"

# ════════════════════════════════════════════════════════
#  SYSTEM PROMPT — NÃO CỦA THẦY T
# ════════════════════════════════════════════════════════
def build_system_prompt(profile: dict) -> str:
    base = """Bạn là **Thầy T** — chuyên gia tư vấn hướng nghiệp uy tín, thẳng thắn và cực kỳ cẩn thận với dữ liệu, 15 năm kinh nghiệm hướng dẫn học sinh THPT miền Nam, đặc biệt là Tây Ninh.

**Tính cách & Phong cách:**
- Thẳng thắn, đi thẳng vào vấn đề, không vòng vo dài dòng
- Ấm áp, đồng cảm nhưng không sáo rỗng
- Luôn trung thực: nếu không chắc chắn thì nói rõ "Thầy chưa tìm được dữ liệu chính xác"
- Không bao giờ bịa số điểm chuẩn

══════════════════════════════════════════
🔴 QUY TẮC BẮT BUỘC - VI PHẠM LÀ SAI
══════════════════════════════════════════
1. **Tìm kiếm thông tin:**
   - Luôn ưu tiên Google Search để lấy điểm chuẩn 2025 từ nguồn chính thức.
   - Thứ tự ưu tiên: Website trường → VnExpress → Tuổi Trẻ → Thanh Niên → tuyensinh247 → diemthi.com

2. **Không bao giờ bịa số:**
   - Nếu không tìm được điểm chuẩn chính xác → ghi `null` và thông báo rõ ràng với học sinh.
   - Không làm tròn sai, không lấy điểm ngành khác thay.

3. **BẮT BUỘC xuất ra JSON_TABLE cho 2 phần sau:**

**Phần Điểm Chuẩn:**
~~~JSON_TABLE
{
  "title": "Điểm Chuẩn Ngành Sư phạm Toán - Đại học Cần Thơ (2023-2026)",
  "note": "Nguồn: Website chính thức ĐH Cần Thơ 2025",
  "rows": [
    {
      "school": "Đại học Cần Thơ",
      "combo": "A00, A01, B08, D07",
      "y2023": 26.18,
      "y2024": 26.79,
      "y2025": 27.67,
      "y2026_predict": 28.0,
      "basis": "Tăng đều qua 3 năm, dự báo 2026 khoảng 28.0"
    }
  ]
}
~~~END

**Phần Bản Đồ Trường:**
~~~JSON_TABLE
{
  "title": "Bản Đồ Trường Gợi Ý Ngành Sư phạm Toán",
  "note": "Phân theo 4 tầng, khoảng cách từ Tây Ninh",
  "rows": [
    {
      "tier": "🥇 Đỉnh",
      "school": "Đại học Sư phạm TP.HCM",
      "location": "TP.HCM",
      "strength": "Trường sư phạm top đầu miền Nam",
      "distance": "~100km ~2h",
      "note": "Điểm chuẩn thường cao"
    }
  ]
}
~~~END

**Cấu trúc trả lời chuẩn:**
## 🔎 [Tên Ngành] — Thực Chất Là Gì?
## 📊 Điểm Chuẩn + Dự Báo 2026
[JSON_TABLE]
## 🏫 Bản Đồ Trường — Phân 4 Tầng Rõ Ràng
[JSON_TABLE]
## 🏠 Đời Sống Sinh Viên & 💼 Cơ Hội Việc Làm
## 🎯 Chiến Lược Nguyện Vọng

Kết thúc bằng một câu hỏi gợi mở để tiếp tục hội thoại.
"""
    
    # Tiêm hồ sơ cá nhân hóa
    if any(v for v in profile.values() if v and v.strip()):
        lines = ["\n══════════════════════════════════════════",
                 "👤 HỒ SƠ HỌC SINH:"]
        if profile.get("score"): lines.append(f"• Điểm thi thử: **{profile['score']}**")
        if profile.get("combo"): lines.append(f"• Tổ hợp: **{profile['combo']}**")
        if profile.get("major"): lines.append(f"• Ngành quan tâm: **{profile['major']}**")
        if profile.get("strengths"): lines.append(f"• Sở thích/thế mạnh: **{profile['strengths']}**")
        if profile.get("budget"): lines.append(f"• Ngân sách: **{profile['budget']}**")
        if profile.get("distance"): lines.append(f"• Khoảng cách: **{profile['distance']}**")
        lines.append("→ Dựa sát vào hồ sơ này để tư vấn phù hợp.")
        base += "\n".join(lines)
    
    return base

# ════════════════════════════════════════════════════════
#  GEMINI CLIENT
# ════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)

try:
    _client = get_client()
except Exception as e:
    st.error(f"❌ Không kết nối được Gemini API: {e}")
    st.stop()

_SEARCH = types.Tool(google_search=types.GoogleSearch())

def make_cfg(search: bool, profile: dict) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=build_system_prompt(profile),
        tools=[_SEARCH] if search else [],
        temperature=0.65,
        max_output_tokens=8192,
    )

# ════════════════════════════════════════════════════════
#  RENDER BẢNG ĐIỂM CHUẨN  (custom HTML đẹp)
# ════════════════════════════════════════════════════════
def _arr(a, b):
    if a is None or b is None: return '<span class="af">—</span>'
    d = round(b - a, 2)
    if d > 0.09:    return f'<span class="au">↑ +{d}</span>'
    elif d < -0.09: return f'<span class="ad">↓ {d}</span>'
    return '<span class="af">→ ổn định</span>'

def _sc(v, kind="r"):
    if v is None: return '<span class="sb-n">N/A</span>'
    return f'<span class="sb-{kind}">{v}</span>'

def render_tables(text: str):
    """Render cả bảng điểm chuẩn lẫn bảng trường đẹp hơn"""
    pat = r'~~~JSON_TABLE\s*(.*?)\s*~~~END'
    blocks = re.findall(pat, text, re.DOTALL)
    if not blocks: 
        return text, []
    
    htmls, clean = [], text
    for i, raw in enumerate(blocks):
        ph = f"__T{i}__"
        clean = re.sub(r'~~~JSON_TABLE\s*' + re.escape(raw) + r'\s*~~~END', 
                       ph, clean, count=1, flags=re.DOTALL)
        
        try:
            d = json.loads(raw.strip())
        except Exception:
            htmls.append(None); continue

        title = d.get("title", "Bảng thông tin")
        note = d.get("note", "")
        rows = d.get("rows", [])

        # === BẢNG TRƯỜNG (có cột "tier") ===
        if rows and any("tier" in str(row) for row in rows if isinstance(row, dict)):
            h = f'<div class="dct-wrap"><h3 style="color:#d4a017; margin:18px 0 12px 0; font-family:Playfair Display">{title}</h3>'
            h += '<table class="dct"><thead><tr><th>Tầng</th><th>Trường</th><th>Vị trí</th><th>Điểm mạnh</th><th>Khoảng cách từ TN</th><th>Ghi chú</th></tr></thead><tbody>'
            for r in rows:
                h += f'<tr><td><strong>{r.get("tier","")}</strong></td>'
                h += f'<td>{r.get("school","")}</td>'
                h += f'<td>{r.get("location","")}</td>'
                h += f'<td>{r.get("strength","")}</td>'
                h += f'<td>{r.get("distance","")}</td>'
                h += f'<td style="font-size:0.85rem;color:#8b949e">{r.get("note","")}</td></tr>'
        else:
            # === BẢNG ĐIỂM CHUẨN ===
            h = f'<div class="dct-wrap"><h3 style="color:#d4a017;margin:12px 0">{title}</h3><table class="dct">'
            h += '<thead><tr><th>Trường</th><th>Tổ hợp</th><th>2023</th><th>2024</th><th>2025</th><th>Xu hướng</th><th>🔮 Dự báo 2026</th><th>Cơ sở</th></tr></thead><tbody>'
            for r in rows:
                y3 = r.get("y2023")
                y4 = r.get("y2024")
                y5 = r.get("y2025")
                y6 = r.get("y2026_predict")
                h += (f'<tr><td>{r.get("school","")}</td>'
                      f'<td><span class="sb-c">{r.get("combo","")}</span></td>'
                      f'<td>{_sc(y3)}</td><td>{_sc(y4)}</td><td>{_sc(y5)}</td>'
                      f'<td>{_arr(y4,y5)}</td><td>{_sc(y6,"p")}</td>'
                      f'<td style="font-size:0.8rem;color:#8b949e">{r.get("basis","")}</td></tr>')

        h += '</tbody></table>'
        if note:
            h += f'<div class="note-src">📌 {note}</div>'
        h += '</div>'
        htmls.append(h)
    return clean, htmls

def show_msg(content: str):
    """Hiển thị message, chèn bảng HTML đúng vị trí."""
    clean, tables = render_tables(content)
    if not tables: st.markdown(content); return
    for i, tbl in enumerate(tables):
        ph = f"__T{i}__"
        parts = clean.split(ph, 1)
        if parts[0].strip(): st.markdown(parts[0])
        if tbl: st.markdown(tbl, unsafe_allow_html=True)
        else:   st.warning("⚠️ Không render được bảng (JSON lỗi định dạng).")
        clean = parts[1] if len(parts) > 1 else ""
    if clean.strip(): st.markdown(clean)

# ════════════════════════════════════════════════════════
#  QUIZ HƯỚNG NGHIỆP  (tính năng mới)
# ════════════════════════════════════════════════════════
QUIZ = [
    {
        "q": "Em thích làm việc với...",
        "opts": {
            "A": "Con số, dữ liệu, phân tích logic",
            "B": "Con người — dạy học, tư vấn, giao tiếp",
            "C": "Thiên nhiên, sinh vật, thực phẩm, môi trường",
            "D": "Máy móc, công nghệ, lập trình, hệ thống",
        }
    },
    {
        "q": "Điều em tự hào nhất ở bản thân là...",
        "opts": {
            "A": "Tư duy logic, giỏi giải quyết vấn đề",
            "B": "Kỹ năng giao tiếp, thuyết phục",
            "C": "Sự kiên nhẫn, tỉ mỉ, quan sát tốt",
            "D": "Sáng tạo, thích khám phá cái mới",
        }
    },
    {
        "q": "Sau này em muốn làm việc ở...",
        "opts": {
            "A": "Công ty, ngân hàng, cơ quan nhà nước",
            "B": "Trường học, bệnh viện, tổ chức phi lợi nhuận",
            "C": "Nông trại, phòng lab, nhà máy, môi trường",
            "D": "Công ty công nghệ, startup, làm freelance",
        }
    },
    {
        "q": "Môn học em thích nhất ở THPT là...",
        "opts": {
            "A": "Toán, Vật lý, Hóa học",
            "B": "Văn, Lịch sử, GDCD, Ngoại ngữ",
            "C": "Sinh học, Địa lý, Hóa học",
            "D": "Toán, Tin học, Vật lý",
        }
    },
    {
        "q": "Em lo ngại nhất điều gì khi chọn ngành?",
        "opts": {
            "A": "Điểm chuẩn quá cao, khó đậu",
            "B": "Ra trường khó xin việc",
            "C": "Học phí và chi phí sinh hoạt tốn kém",
            "D": "Sợ học không phù hợp với bản thân",
        }
    },
]

QUIZ_RESULT = {
    "A": {
        "group": "Kinh tế — Tài chính — Kế toán",
        "icon": "💼",
        "desc": "Em có tư duy phân tích tốt, phù hợp với các ngành như Kế toán, Tài chính Ngân hàng, Kinh tế, Quản trị kinh doanh.",
        "suggest": "Kế toán, Tài chính Ngân hàng, Kinh tế, Quản trị Kinh doanh",
        "schools": "UEH, ĐH Kinh Tế TPHCM, ĐH Tôn Đức Thắng, ĐH Văn Lang, ĐH Hutech",
    },
    "B": {
        "group": "Sư phạm — Y tế — Xã hội",
        "icon": "🏫",
        "desc": "Em có năng khiếu giao tiếp và muốn cống hiến cho cộng đồng — Sư phạm, Y tế, Công tác xã hội, Tâm lý học rất phù hợp.",
        "suggest": "Sư phạm các môn, Y tế cộng đồng, Tâm lý học, Công tác xã hội",
        "schools": "ĐH Sư Phạm TPHCM, ĐH Y Dược TPHCM, ĐH Cần Thơ, ĐH Tôn Đức Thắng",
    },
    "C": {
        "group": "Nông — Lâm — Môi trường — Thực phẩm",
        "icon": "🌿",
        "desc": "Em gần gũi với thiên nhiên và khoa học ứng dụng — Nông nghiệp, Thú y, Công nghệ Thực phẩm, Môi trường là lựa chọn tuyệt vời.",
        "suggest": "Nông nghiệp CNC, Thú y, Công nghệ Thực phẩm, Khoa học Môi trường",
        "schools": "ĐH Nông Lâm TPHCM, ĐH Cần Thơ, ĐH Bình Dương, ĐH Tài Nguyên Môi Trường",
    },
    "D": {
        "group": "Kỹ thuật — Công nghệ — CNTT",
        "icon": "💻",
        "desc": "Em có tư duy kỹ thuật và yêu thích sáng tạo — CNTT, Kỹ thuật Điện tử, Cơ khí, Xây dựng đang rất khan hiếm nhân lực.",
        "suggest": "Công nghệ Thông tin, Kỹ thuật Điện tử, Cơ khí, Xây dựng",
        "schools": "ĐH Bách Khoa TPHCM, ĐH CNTT ĐHQG, ĐH Sư Phạm Kỹ Thuật, ĐH Hutech",
    },
}

def run_quiz():
    st.markdown("### 🧭 Quiz Khám Phá Hướng Nghiệp")
    st.markdown("*5 câu hỏi ngắn — khoảng 2 phút — giúp em tìm ra nhóm ngành phù hợp nhất với bản thân*")
    st.divider()

    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_done" not in st.session_state:
        st.session_state.quiz_done = False

    if st.session_state.quiz_done:
        ans = st.session_state.quiz_answers
        from collections import Counter
        count = Counter(ans.values())
        top   = count.most_common(1)[0][0]
        res   = QUIZ_RESULT[top]

        st.success(f"✅ Hoàn thành! Thầy T đã phân tích câu trả lời của em.")
        st.markdown(f"""
<div style="background:#161b22;border:1px solid #d4a017;border-radius:14px;padding:22px 26px;margin:12px 0;">
  <div style="font-size:2rem;margin-bottom:8px;">{res['icon']}</div>
  <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:#f0f6fc;font-weight:700;margin-bottom:8px;">
    Nhóm ngành phù hợp: <span style="color:#d4a017;">{res['group']}</span>
  </div>
  <div style="color:#8b949e;line-height:1.75;font-size:.93rem;">{res['desc']}</div>
  <div style="margin-top:14px;padding-top:12px;border-top:1px solid #21262d;">
    <div style="font-size:.75rem;color:#8b949e;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Ngành cụ thể gợi ý</div>
    <div style="color:#c9d1d9;font-weight:600;">{res['suggest']}</div>
  </div>
  <div style="margin-top:10px;">
    <div style="font-size:.75rem;color:#8b949e;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Trường phù hợp gần Tây Ninh</div>
    <div style="color:#c9d1d9;font-weight:600;">{res['schools']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Làm lại quiz", use_container_width=True):
                st.session_state.quiz_answers = {}
                st.session_state.quiz_done    = False
                st.rerun()
        with col2:
            if st.button("💬 Hỏi Thầy T về nhóm ngành này", use_container_width=True):
                q = f"Thầy T ơi, em vừa làm quiz và kết quả là phù hợp với nhóm **{res['group']}**. Ngành {res['suggest'].split(',')[0].strip()} thì điểm chuẩn 2023–2025 bao nhiêu, và trường nào tốt nhất gần Tây Ninh?"
                st.session_state["_pend"] = q
                st.session_state.active_tab = 0
                st.rerun()
        return

    # Hiển thị từng câu
    answered = len(st.session_state.quiz_answers)
    total    = len(QUIZ)

    st.markdown(f'<div style="font-size:.8rem;color:#8b949e;margin-bottom:16px;">Tiến độ: {answered}/{total} câu</div>',
                unsafe_allow_html=True)

    prog_pct = answered / total
    st.progress(prog_pct)
    st.markdown("<br>", unsafe_allow_html=True)

    for idx, item in enumerate(QUIZ):
        qno = idx + 1
        if qno in st.session_state.quiz_answers:
            chosen = st.session_state.quiz_answers[qno]
            st.markdown(f'<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;'
                        f'padding:12px 16px;margin-bottom:10px;font-size:.88rem;">'
                        f'<span style="color:#8b949e;">Câu {qno}:</span> '
                        f'<span style="color:#c9d1d9;">{item["q"]}</span>'
                        f'<br><span style="color:#3fb950;font-weight:600;">✓ {chosen}: {item["opts"][chosen]}</span></div>',
                        unsafe_allow_html=True)
            continue

        # Câu chưa trả lời
        st.markdown(f'<div style="font-weight:700;color:#f0f6fc;font-size:.97rem;margin-bottom:10px;">'
                    f'Câu {qno}/{total}: {item["q"]}</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        opts_list = list(item["opts"].items())
        for j, (key, val) in enumerate(opts_list):
            with cols[j % 2]:
                if st.button(f"{key}. {val}", key=f"q{idx}_{key}", use_container_width=True):
                    st.session_state.quiz_answers[qno] = key
                    if len(st.session_state.quiz_answers) == total:
                        st.session_state.quiz_done = True
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        break  # Chỉ hiện 1 câu chưa trả lời tại một thời điểm

# ════════════════════════════════════════════════════════
#  SO SÁNH NGÀNH  (tính năng mới)
# ════════════════════════════════════════════════════════
def run_compare():
    st.markdown("### ⚖️ So Sánh Ngành Nghề")
    st.markdown("*Nhập 2 ngành muốn so sánh — Thầy T sẽ phân tích chi tiết cho em*")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        ng1 = st.text_input("🅰️ Ngành thứ nhất", placeholder="VD: Kế toán", key="cmp1")
    with col2:
        ng2 = st.text_input("🅱️ Ngành thứ hai", placeholder="VD: Tài chính Ngân hàng", key="cmp2")

    if st.button("🔍 So sánh ngay", use_container_width=True, type="primary"):
        if ng1.strip() and ng2.strip():
            q = (f"Thầy T ơi, em đang phân vân giữa ngành **{ng1.strip()}** và **{ng2.strip()}**. "
                 f"Thầy so sánh giúp em hai ngành này nhé: điểm chuẩn 2023–2025, cơ hội việc làm, "
                 f"mức lương, và ngành nào phù hợp hơn với học sinh Tây Ninh?")
            st.session_state["_pend"] = q
            st.session_state.active_tab = 0
            st.rerun()
        else:
            st.warning("⚠️ Em nhập đủ tên 2 ngành nhé!")

    st.divider()
    st.markdown("**💡 Cặp ngành hay được so sánh:**")
    pairs = [
        ("Kế toán", "Tài chính Ngân hàng"),
        ("CNTT", "Kỹ thuật Điện tử - Viễn thông"),
        ("Y khoa", "Dược học"),
        ("Sư phạm Toán", "Toán học ứng dụng"),
        ("Xây dựng", "Kiến trúc"),
        ("Nông nghiệp CNC", "Công nghệ Thực phẩm"),
    ]
    cols = st.columns(3)
    for i, (a, b) in enumerate(pairs):
        with cols[i % 3]:
            if st.button(f"⚖️ {a} vs {b}", key=f"cmp_pre_{i}", use_container_width=True):
                q = (f"Thầy T ơi, em đang phân vân giữa ngành **{a}** và **{b}**. "
                     f"Thầy so sánh giúp em hai ngành này: điểm chuẩn 2023–2025, "
                     f"cơ hội việc làm, mức lương, phù hợp với học sinh Tây Ninh không?")
                st.session_state["_pend"] = q
                st.session_state.active_tab = 0
                st.rerun()

# ════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎓 Thầy T")
    st.caption("Hướng Nghiệp 12 PRO · v5.0 · Tây Ninh & phía Nam")
    st.divider()

    st.markdown("### 📋 Hồ Sơ Của Em")
    st.caption("Điền để Thầy T tư vấn cá nhân hóa nhất có thể")

    if "profile" not in st.session_state:
        st.session_state.profile = {}
    p = st.session_state.profile

    combo_opts  = ["Chưa chọn","A00 — Toán·Lý·Hóa","A01 — Toán·Lý·Anh","B00 — Toán·Hóa·Sinh",
                   "C00 — Văn·Sử·Địa","D01 — Toán·Văn·Anh","D07 — Toán·Hóa·Anh",
                   "C14 — Văn·Toán·GDCD","Khác"]
    budget_opts = ["Chưa biết","Dưới 3 triệu","3–5 triệu","5–8 triệu","Trên 8 triệu"]
    dist_opts   = ["Không giới hạn","Trong tỉnh Tây Ninh","Bán kính 100 km","Bán kính 200 km"]

    def _i(lst, val, d=0): return lst.index(val) if val in lst else d

    score_v = st.text_input("📊 Điểm thi thử", value=p.get("score",""), placeholder="VD: 23.5")
    combo_v = st.selectbox("📚 Tổ hợp xét tuyển", combo_opts,
                           index=_i(combo_opts, p.get("combo","Chưa chọn")))
    major_v = st.text_input("🎯 Ngành quan tâm", value=p.get("major",""),
                            placeholder="VD: Sư phạm Toán")
    str_v   = st.text_input("💡 Sở thích / Thế mạnh", value=p.get("strengths",""),
                            placeholder="VD: Thích dạy học, giỏi Toán")
    bud_v   = st.selectbox("💰 Chi phí/tháng", budget_opts,
                           index=_i(budget_opts, p.get("budget","Chưa biết")))
    dst_v   = st.selectbox("🗺️ Khoảng cách", dist_opts,
                           index=_i(dist_opts, p.get("distance","Không giới hạn")))

    if st.button("💾  Lưu hồ sơ", use_container_width=True):
        st.session_state.profile = {
            "score":     score_v.strip(),
            "combo":     combo_v if combo_v != "Chưa chọn" else "",
            "major":     major_v.strip(),
            "strengths": str_v.strip(),
            "budget":    bud_v if bud_v != "Chưa biết" else "",
            "distance":  dst_v if dst_v != "Không giới hạn" else "",
        }
        st.success("✅ Thầy T đã ghi nhớ thông tin của em!")

    st.divider()

    # Stat cards
    sp = st.session_state.profile
    if any(v for v in sp.values() if v):
        st.markdown("**📌 Hồ Sơ Đang Dùng**")
        for lbl, key, gold in [("Điểm thi thử","score",True),("Tổ hợp","combo",False),
                                ("Ngành","major",False),("Ngân sách","budget",False)]:
            val = sp.get(key,"")
            if not val: continue
            display = val.split("—")[0].strip() if "—" in val else val
            cls = 'g' if gold else ''
            st.markdown(f'<div class="sc"><div class="sc-l">{lbl}</div>'
                        f'<div class="sc-v {cls}">{display}{"" if not gold else " điểm"}</div></div>',
                        unsafe_allow_html=True)
        st.divider()

    st.markdown("""<div style="font-size:.76rem;color:#484f58;line-height:2.2;">
🟢 <b style="color:#8b949e;">Google Search thời gian thực</b><br>
📊 <b style="color:#8b949e;">Điểm chuẩn 2023 · 2024 · 2025</b><br>
🔮 <b style="color:#8b949e;">Dự báo điểm chuẩn 2026</b><br>
🗺️ <b style="color:#8b949e;">Địa lý & đời sống từ Tây Ninh</b><br>
💼 <b style="color:#8b949e;">Nghề nghiệp & lộ trình lương</b><br>
🧭 <b style="color:#8b949e;">Quiz khám phá hướng nghiệp</b><br>
⚖️ <b style="color:#8b949e;">So sánh ngành trực tiếp</b>
</div>""", unsafe_allow_html=True)

    st.divider()

    # Tải phiếu tư vấn
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        ts = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        export = (f"PHIẾU TƯ VẤN HƯỚNG NGHIỆP — THẦY T (ẩn danh)\n"
                  f"Ngày: {ts}\n{'='*52}\n\n")
        for m in st.session_state.messages:
            role = "Học sinh" if m["role"]=="user" else "Thầy T"
            txt  = re.sub(r'~~~JSON_TABLE.*?~~~END','[Bảng điểm chuẩn]',
                          m["content"], flags=re.DOTALL)
            export += f"[{role}]\n{txt}\n\n{'—'*40}\n\n"
        st.download_button(
            label="📥 Tải phiếu tư vấn (.txt)",
            data=export.encode("utf-8"),
            file_name=f"PhieuTuVan_ThayCT_{datetime.datetime.now().strftime('%d%m%Y')}.txt",
            mime="text/plain", use_container_width=True,
        )

    if st.button("🗑️  Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("greeted", None)
        st.rerun()

# ════════════════════════════════════════════════════════
#  HERO BANNER
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-eyebrow">✦ v5.0 FINAL · Gemini 2.5 Flash · Google Search</div>
      <div class="hero-title">Thầy <span class="gold">T</span> — Hướng Nghiệp 12 PRO</div>
      <div class="hero-sub">Tư vấn cá nhân hóa · Điểm chuẩn 2023–2025 + Dự báo 2026 · Dành riêng học sinh Tây Ninh</div>
    </div>
    <div class="hero-chips">
      <span class="hchip hc-live">⚡ Google Search Realtime</span>
      <span class="hchip hc-gold">🔮 Dự báo 2026</span>
      <span class="hchip hc-blue">🧭 Quiz hướng nghiệp</span>
      <span class="hchip hc-def">⚖️ So sánh ngành</span>
      <span class="hchip hc-def">📥 Tải phiếu tư vấn</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  TABS ĐIỀU HƯỚNG
# ════════════════════════════════════════════════════════
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

tab_chat, tab_quiz, tab_compare = st.tabs([
    "💬 Chat với Thầy T",
    "🧭 Quiz Hướng Nghiệp",
    "⚖️ So Sánh Ngành",
])

# ════════════════════════════════════════════════════════
# TAB 1: CHAT
# ════════════════════════════════════════════════════════
with tab_chat:
    # Khởi tạo lịch sử
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "greeted" not in st.session_state:
        st.session_state.greeted = True
        st.session_state.messages.append({"role": "assistant", "content": (
            "Chào em! Thầy T đây. 👋\n\n"
            "Thầy biết giai đoạn này không dễ — vừa áp lực thi tốt nghiệp, "
            "vừa phải nghĩ đến chuyện chọn trường, chọn ngành cho cả tương lai. "
            "Đừng lo, thầy ở đây để đồng hành cùng em, từng bước thật cụ thể.\n\n"
            "---\n\n"
            "**Thầy T giúp được em:**\n\n"
            "📊 **Điểm chuẩn thực tế 2023–2024–2025** — tra cứu trực tiếp, bảng rõ ràng\n\n"
            "🔮 **Dự báo điểm chuẩn 2026** — tính từ xu hướng thực tế\n\n"
            "🏫 **Top trường phù hợp phân 4 tầng** theo điểm số của em\n\n"
            "🗺️ **Thông tin sống thực tế** — khoảng cách từ Tây Ninh, ký túc xá, chi phí\n\n"
            "💼 **Nghề nghiệp & lương thực tế** — không phải lý thuyết\n\n"
            "🎯 **Chiến thuật nguyện vọng** NV1/NV2/NV3 cụ thể\n\n"
            "---\n\n"
            "👉 Em hãy điền **Hồ Sơ** ở thanh trái, "
            "hoặc thử **Quiz Hướng Nghiệp** để biết mình hợp với nhóm ngành nào trước nhé!\n\n"
            "Cứ hỏi thẳng vào vấn đề — thầy không thích vòng vo. 👇"
        )})

    # Hiển thị lịch sử chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                show_msg(msg["content"])
            else:
                st.markdown(msg["content"])

    # Gợi ý nhanh
    if len(st.session_state.messages) == 1:
        st.markdown('<div class="slbl">✦ Câu hỏi gợi ý — nhấn để bắt đầu ngay</div>',
                    unsafe_allow_html=True)
        sugs = [
            ("🏥","Điểm chuẩn Y Dược TP.HCM 2023–2025 và dự báo 2026?"),
            ("💻","CNTT: trường nào gần Tây Ninh, bảng điểm chuẩn 3 năm?"),
            ("📐","Sư phạm Toán ĐH Cần Thơ: điểm chuẩn + việc làm"),
            ("⚙️","Kỹ thuật Xây dựng phía Nam: bảng điểm chuẩn 2023–2026"),
            ("🌿","Nông nghiệp CNC: trường tốt, điểm chuẩn, nghề gì?"),
            ("💰","Tài chính Ngân hàng: học ở đâu, ra trường lương bao nhiêu?"),
        ]
        cols = st.columns(3)
        for i, (ic, txt) in enumerate(sugs):
            with cols[i % 3]:
                if st.button(f"{ic} {txt}", key=f"sg{i}"):
                    st.session_state["_pend"] = txt
                    st.rerun()

    # ================== HÀM HỖ TRỢ ==================
    SCORE_KW = ["điểm chuẩn","tuyển sinh","xét tuyển","nguyện vọng","điểm đầu vào",
                "trúng tuyển","học trường nào","điểm chuẩn"]

    def needs_search(t: str) -> bool:
        return any(k in t.lower() for k in SCORE_KW)

    def build_hist(msgs: list) -> list:
        hist = []
        # Bỏ câu chào đầu tiên của Thầy T và tin nhắn hiện tại
        valid_msgs = msgs[1:-1] if len(msgs) > 1 else []
        
        for m in valid_msgs:
            role = "model" if m["role"] == "assistant" else "user"
            txt = re.sub(r'~~~JSON_TABLE.*?~~~END', '[bảng điểm chuẩn]', 
                         m["content"], flags=re.DOTALL)
            hist.append(types.Content(
                role=role, 
                parts=[types.Part(text=txt)]
            ))
        return hist

    def call_ai(user_input: str, profile: dict) -> str:
        history = build_hist(st.session_state.messages)
        use_search = needs_search(user_input)
        
        enhanced = user_input
        if use_search:
            enhanced += "\n\n[LỆNH HỆ THỐNG]: Dùng Google Search tìm điểm chuẩn 2025 ngay. Tìm website chính thức trước."

        try:
            cfg = make_cfg(use_search, profile)
            chat = _client.chats.create(model=GEMINI_MODEL, config=cfg, history=history)
            return chat.send_message(enhanced).text
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}\n\nEm thử hỏi lại nhé!"

    # ================== CHAT INPUT ==================
    STEPS_SEARCH = [
        ("🔍", "Kết nối Google Search...", "Đang mở hệ thống tìm kiếm"),
        ("📡", "Tìm điểm chuẩn 2025 từ nguồn chính thức...", "Website trường + báo lớn"),
        ("📊", "Tổng hợp dữ liệu 2023–2024–2025...", "Đối chiếu nhiều nguồn"),
        ("🔮", "Tính dự báo điểm chuẩn 2026...", "Phân tích xu hướng 3 năm"),
        ("✍️", "Soạn bài tư vấn cá nhân hóa...", "Vui lòng chờ xíu nhé em ☕"),
    ]
    STEPS_BASIC = [
        ("💭", "Thầy T đang phân tích câu hỏi...", ""),
        ("✍️", "Soạn nội dung tư vấn...", "Vui lòng chờ xíu nhé em ☕"),
    ]

    pend = st.session_state.pop("_pend", None)
    user_query = pend or st.chat_input(
        "Em hỏi Thầy T gì cũng được — điểm chuẩn, chọn ngành, chọn trường... 💬",
        key="cin"
    )

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            use_s = needs_search(user_query)
            steps = STEPS_SEARCH if use_s else STEPS_BASIC
            ph = st.empty()
            
            for ico, main, sub in steps:
                sub_html = f'<br><span style="font-size:.78rem;color:#8b949e;">{sub}</span>' if sub else ''
                ph.markdown(f'''
                    <div class="step-bar">
                        <span class="ico">{ico}</span>
                        <span class="txt">
                            <strong style="color:#e6edf3">{main}</strong>{sub_html}
                        </span>
                        <span class="spin-anim"></span>
                    </div>
                ''', unsafe_allow_html=True)
                import time
                time.sleep(0.55)
            
            ph.empty()

            profile = st.session_state.get("profile", {})
            reply = call_ai(user_query, profile)
            show_msg(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ════════════════════════════════════════════════════════
#  TAB 2: QUIZ
# ════════════════════════════════════════════════════════
with tab_quiz:
    run_quiz()

# ════════════════════════════════════════════════════════
#  TAB 3: SO SÁNH NGÀNH
# ════════════════════════════════════════════════════════
with tab_compare:
    run_compare()

# ════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;color:#484f58;font-size:.72rem;
padding:20px 0 12px;border-top:1px solid #21262d;margin-top:24px;">
✦ <strong style="color:#8b949e;">Thầy T — Hướng Nghiệp 12 PRO v5.0 FINAL</strong>
· Gemini 2.5 Flash + Google Search Grounding · Dự báo 2026<br>
Điểm chuẩn từ nguồn chính thức · Dự báo 2026 chỉ mang tính tham khảo định hướng<br>
<span style="color:#30363d;">Made with ❤️ for học sinh Tây Ninh — Thầy T (ẩn danh)</span>
</div>
""", unsafe_allow_html=True)
