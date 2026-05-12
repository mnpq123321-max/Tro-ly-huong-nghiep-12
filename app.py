"""
╔══════════════════════════════════════════════════════════════════╗
║   TRỢ LÝ HƯỚNG NGHIỆP 12 PRO  —  v3.5 (Bản Nâng Cấp Hoàn Hảo)    ║
║   Engine: Gemini 2.5 Flash + Google Search Grounding             ║
║   Dành cho học sinh lớp 12, Tây Ninh & khu vực phía Nam          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import datetime
from google import genai
from google.genai import types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE CONFIG (Phải là lệnh Streamlit đầu tiên)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Hướng Nghiệp 12 PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TOÀN BỘ CSS — GIAO DIỆN HOÀN TOÀN MỚI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Fraunces:wght@700;900&display=swap');

/* ── BASE ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: #f8f7f4;
    min-height: 100vh;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0f1923 !important;
    border-right: 1px solid #1e2d3d !important;
    width: 320px !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small { color: #a8b9cc !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] hr { border-color: #1e2d3d !important; margin: 14px 0 !important; }

/* sidebar inputs */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: #1a2738 !important;
    border: 1px solid #2a3f55 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1a2738 !important;
    border: 1px solid #2a3f55 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #f5a623, #e8821a) !important;
    border: none !important;
    color: #0f1923 !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(245,166,35,0.3) !important;
}

/* Nút phụ trong sidebar (Xóa lịch sử, Tải file) */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: #1a2738 !important;
    color: #a8b9cc !important;
    border: 1px solid #2a3f55 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: #2a3f55 !important;
    color: #ffffff !important;
}

/* ── MAIN CONTENT ── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── TOP BANNER ── */
.top-banner {
    background: #0f1923;
    padding: 22px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e2d3d;
}
.banner-eyebrow {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #f5a623;
    margin-bottom: 4px;
}
.banner-title {
    font-family: 'Fraunces', serif;
    font-size: 1.9rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.1;
    letter-spacing: -0.5px;
}
.banner-title em { color: #f5a623; font-style: normal; }
.banner-desc {
    font-size: 0.85rem;
    color: #647d96;
    margin-top: 4px;
}
.banner-right {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
}
.banner-chip {
    background: #1a2738;
    border: 1px solid #2a3f55;
    color: #a8b9cc;
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 0.76rem;
    font-weight: 600;
    white-space: nowrap;
}
.banner-chip.live {
    background: rgba(34,197,94,0.12);
    border-color: rgba(34,197,94,0.35);
    color: #4ade80;
}

/* ── CHAT AREA ── */
.chat-wrap {
    max-width: 820px;
    margin: 0 auto;
    padding: 32px 24px 120px;
}

/* ── MESSAGE BUBBLES ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-bottom: 20px !important;
}

/* user bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background: #0f1923 !important;
    color: #e2e8f0 !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 14px 18px !important;
    font-size: 0.97rem !important;
    line-height: 1.7 !important;
    max-width: 80% !important;
    margin-left: auto !important;
}

/* assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    color: #1a2738 !important;
    border-radius: 4px 18px 18px 18px !important;
    padding: 20px 24px !important;
    font-size: 0.97rem !important;
    line-height: 1.85 !important;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06) !important;
    border: 1px solid #e8e8e4 !important;
}

/* markdown inside assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h1,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) h3 {
    color: #0f1923 !important;
    font-family: 'Fraunces', serif !important;
    margin-top: 20px !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) strong {
    color: #0f1923 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) table {
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: 0.9rem !important;
    margin: 12px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) th {
    background: #0f1923 !important;
    color: #f5a623 !important;
    padding: 8px 12px !important;
    font-weight: 700 !important;
    text-align: left !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) td {
    padding: 8px 12px !important;
    border-bottom: 1px solid #e8e8e4 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) tr:nth-child(even) td {
    background: #f8f7f4 !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] > div {
    background: #ffffff !important;
    border: 2px solid #ddd9d0 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #f5a623 !important;
    box-shadow: 0 4px 24px rgba(245,166,35,0.15) !important;
}
[data-testid="stChatInput"] textarea {
    color: #0f1923 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.97rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #a8b9cc !important; }

/* ── SUGGESTION BUTTONS ── */
div[data-testid="column"] .stButton > button {
    background: #ffffff !important;
    border: 1.5px solid #e0dcd4 !important;
    color: #2d3748 !important;
    border-radius: 12px !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    text-align: left !important;
    padding: 11px 14px !important;
    width: 100% !important;
    line-height: 1.4 !important;
    min-height: 60px !important;
    transition: all 0.18s ease !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #f5a623 !important;
    background: #fffbf0 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(245,166,35,0.15) !important;
}

/* ── SECTION LABEL ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #a8b9cc;
    margin-bottom: 12px;
    margin-top: 4px;
}

/* ── SIDEBAR STAT CARD ── */
.stat-card {
    background: #1a2738;
    border: 1px solid #2a3f55;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.stat-card-label { font-size: 0.72rem; color: #647d96; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.stat-card-value { font-size: 1.05rem; color: #e2e8f0; font-weight: 700; margin-top: 3px; }
.stat-card-value.highlight { color: #f5a623; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── DIVIDER ── */
hr { border-color: #e8e4dc !important; }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CẤU HÌNH API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GEMINI_API_KEY = "AIzaSyCSZo3_0Rw9gn7sDdK-7cyEAt74swvtt5M"
GEMINI_MODEL   = "gemini-2.5-flash"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HÀM TẠO DYNAMIC SYSTEM PROMPT (Tiêm Hồ sơ vào Hệ thống)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_system_prompt(profile: dict) -> str:
    base_prompt = """Bạn là **Thầy Minh** — chuyên gia tư vấn hướng nghiệp 15 năm kinh nghiệm, gắn bó với học sinh THPT tại Tây Ninh và miền Nam Việt Nam. Bạn nói chuyện ấm áp, chân thành như người thầy thực sự — không máy móc, không khô khan.

══════════════════════════════════════════════
🔴 QUY TẮC SỐ 1: TRA CỨU ĐIỂM CHUẨN CHÍNH XÁC
══════════════════════════════════════════════
Bất cứ khi nào học sinh hỏi về điểm chuẩn, bạn PHẢI:
① Tìm kiếm điểm chuẩn năm 2025 TRƯỚC: ưu tiên website tuyển sinh chính thức của trường, báo Tuổi Trẻ, VnExpress. Điểm chuẩn 2025 đã công bố vào tháng 8 năm 2025.
② Tìm tiếp điểm chuẩn 2024 và 2023.
③ Tổng hợp thành BẢNG SO SÁNH 3 NĂM theo mẫu:
| Tổ hợp | 2023 | 2024 | 2025 | Xu hướng |
|--------|------|------|------|----------|
| A00    | X.XX | X.XX | X.XX | ↑/↓/→    |
④ Dưới bảng, nhận xét xu hướng tăng/giảm và lời khuyên tự lượng sức.
⚠️ TUYỆT ĐỐI KHÔNG BỊA SỐ. Nếu không tìm được, ghi "N/A — chưa tìm thấy nguồn chính thức".

══════════════════════════════════════════════
📋 CẤU TRÚC BÀI TƯ VẤN CHUẨN (600–1200 chữ)
══════════════════════════════════════════════
## 🌟 Tổng Quan Ngành
## 📊 Bảng Điểm Chuẩn 3 Năm (2023 – 2024 – 2025)
## 🏫 Top Trường Phù Hợp — Phân Tầng Rõ Ràng (Xuất sắc / Tốt / Vừa tầm / An toàn)
## 🗺️ Khoảng Cách & Đời Sống Sinh Viên (từ Tây Ninh)
## 💼 Cơ Hội Nghề Nghiệp & Mức Lương
## 🎯 Chiến Thuật Đặt Nguyện Vọng (Dựa sát vào điểm số học sinh cung cấp)

══════════════════════════════════════════════
🗣️ PHONG CÁCH GIAO TIẾP
══════════════════════════════════════════════
• Luôn xưng "thầy", gọi "em".
• Ấm áp, đồng cảm, kết thúc bằng 1 câu hỏi gợi mở.
• Dùng icon vừa đủ (4–6 icon/đoạn).

══════════════════════════════════════════════
📍 DỮ LIỆU ĐỊA LÝ (từ Tây Ninh)
══════════════════════════════════════════════
• TP.HCM: ~100 km · ~2h xe máy | Bình Dương: ~70 km | Cần Thơ: ~200 km
"""
    
    # Tiêm hồ sơ học sinh vào System Prompt để AI luôn ghi nhớ
    if any(profile.values()):
        profile_str = "\n══════════════════════════════════════════════\n"
        profile_str += "👤 THÔNG TIN HỒ SƠ HỌC SINH ĐANG TRÒ CHUYỆN:\n"
        if profile.get("score"): profile_str += f"- Điểm thi thử hiện tại: {profile['score']} điểm\n"
        if profile.get("combo") and profile["combo"] != "Chưa chọn": profile_str += f"- Tổ hợp môn: {profile['combo']}\n"
        if profile.get("major"): profile_str += f"- Ngành đang quan tâm: {profile['major']}\n"
        if profile.get("strengths"): profile_str += f"- Thế mạnh/Sở thích: {profile['strengths']}\n"
        if profile.get("budget") and profile["budget"] != "Chưa biết": profile_str += f"- Ngân sách dự kiến: {profile['budget']}/tháng\n"
        if profile.get("distance") and profile["distance"] != "Không giới hạn": profile_str += f"- Khoảng cách mong muốn: {profile['distance']}\n"
        profile_str += "=> Lệnh Bắt Buộc: Thầy Minh hãy dựa sát vào thông tin này để tư vấn trường VỪA TẦM ĐIỂM và PHÙ HỢP TÀI CHÍNH cho em học sinh này.\n"
        
        base_prompt += profile_str

    return base_prompt

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KHỞI TẠO GEMINI CLIENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_resource(show_spinner=False)
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

try:
    gemini_client = get_gemini_client()
except Exception as e:
    st.error(f"❌ Không kết nối được Gemini API: {e}")
    st.stop()

# Tool config
SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

def make_config(use_search: bool, profile: dict) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=build_system_prompt(profile),
        tools=[SEARCH_TOOL] if use_search else [],
        temperature=0.65,
        max_output_tokens=8192,
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SIDEBAR — HỒ SƠ HỌC SINH & TÍNH NĂNG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("## 🎓 Hướng Nghiệp 12 PRO")
    st.caption("Tây Ninh & Khu vực phía Nam · Cập nhật 2025")
    st.divider()

    st.markdown("### 📋 Hồ Sơ Của Em")
    st.caption("Điền để thầy tư vấn chuẩn xác nhất")

    if "profile" not in st.session_state:
        st.session_state.profile = {}

    p = st.session_state.profile
    
    # Tối ưu danh sách Options
    combo_opts = ["Chưa chọn", "A00 — Toán · Lý · Hóa", "A01 — Toán · Lý · Anh", "B00 — Toán · Hóa · Sinh", "C00 — Văn · Sử · Địa", "D01 — Toán · Văn · Anh", "D07 — Toán · Hóa · Anh", "C14 — Văn · Toán · GDCD", "Khác"]
    budget_opts = ["Chưa biết", "Dưới 3 triệu", "3–5 triệu", "5–8 triệu", "Trên 8 triệu"]
    dist_opts = ["Không giới hạn", "Trong tỉnh Tây Ninh", "Bán kính 100 km", "Bán kính 200 km"]

    score_input = st.text_input("📊 Điểm thi thử", placeholder="VD: 23.5", value=p.get("score", ""))
    combo_input = st.selectbox("📚 Tổ hợp xét tuyển", combo_opts, index=combo_opts.index(p.get("combo", "Chưa chọn")) if p.get("combo") in combo_opts else 0)
    major_input = st.text_input("🎯 Ngành quan tâm", placeholder="VD: Sư phạm Toán", value=p.get("major", ""))
    strengths_input = st.text_input("💡 Sở thích/Thế mạnh", placeholder="VD: Thích giao tiếp, học giỏi Toán", value=p.get("strengths", ""))
    budget_input = st.selectbox("💰 Chi phí/tháng", budget_opts, index=budget_opts.index(p.get("budget", "Chưa biết")) if p.get("budget") in budget_opts else 0)
    dist_input = st.selectbox("🗺️ Khoảng cách", dist_opts, index=dist_opts.index(p.get("distance", "Không giới hạn")) if p.get("distance") in dist_opts else 0)

    if st.button("💾  Lưu hồ sơ", use_container_width=True):
        st.session_state.profile = {
            "score": score_input.strip(),
            "combo": combo_input if combo_input != "Chưa chọn" else "",
            "major": major_input.strip(),
            "strengths": strengths_input.strip(),
            "budget": budget_input if budget_input != "Chưa biết" else "",
            "distance": dist_input if dist_input != "Không giới hạn" else "",
        }
        st.success("✅ Đã lưu! Thầy đã ghi nhớ thông tin của em.")

    st.divider()

    # Hiển thị tóm tắt Hồ sơ
    if any(p.values()):
        st.markdown("**📌 Hồ Sơ Hiện Tại**")
        if p.get("score"):
            st.markdown(f"<div class='stat-card'><div class='stat-card-label'>Điểm thi thử</div><div class='stat-card-value highlight'>{p['score']} điểm</div></div>", unsafe_allow_html=True)
        if p.get("combo"):
            st.markdown(f"<div class='stat-card'><div class='stat-card-label'>Tổ hợp</div><div class='stat-card-value'>{p['combo'].split('—')[0].strip()}</div></div>", unsafe_allow_html=True)
        if p.get("major"):
            st.markdown(f"<div class='stat-card'><div class='stat-card-label'>Ngành quan tâm</div><div class='stat-card-value'>{p['major']}</div></div>", unsafe_allow_html=True)
        st.divider()

    st.markdown("""<div style="font-size:0.78rem; color:#647d96; line-height:1.8;">
    🔍 <b style="color:#a8b9cc;">Google Search thời gian thực</b><br>
    📅 <b style="color:#a8b9cc;">Điểm chuẩn 2023–2025</b><br>
    🗺️ <b style="color:#a8b9cc;">Thông tin địa lý từ Tây Ninh</b>
    </div>""", unsafe_allow_html=True)

    st.divider()
    
    # Tính năng MỚI: Tải phiếu tư vấn
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        chat_content = f"PHPHIẾU TƯ VẤN HƯỚNG NGHIỆP PRO\nNgày: {datetime.datetime.now().strftime('%d/%m/%Y')}\n" + "="*40 + "\n\n"
        for m in st.session_state.messages:
            role = "Học sinh" if m["role"] == "user" else "Thầy Minh"
            chat_content += f"{role}:\n{m['content']}\n\n{'-'*40}\n"
            
        st.download_button(
            label="📥 Tải phiếu tư vấn (.txt)",
            data=chat_content,
            file_name="Phieu_Tu_Van_Huong_Nghiep_12.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("greeted", None)
        st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BANNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="top-banner">
  <div class="banner-left">
    <div class="banner-eyebrow">🎓 Phiên bản 3.5 PRO · Gemini 2.5 Flash</div>
    <div class="banner-title">Trợ Lý <em>Hướng Nghiệp</em> 12 PRO</div>
    <div class="banner-desc">Tư vấn cá nhân hóa · Điểm chuẩn thực tế · Dành riêng học sinh Tây Ninh</div>
  </div>
  <div class="banner-right">
    <span class="banner-chip live">⚡ Google Search Realtime</span>
    <span class="banner-chip">📊 Dữ liệu 2023–2025</span>
    <span class="banner-chip">💼 Lộ trình việc làm</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LỊCH SỬ HỘI THOẠI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if "messages" not in st.session_state:
    st.session_state.messages = []

if "greeted" not in st.session_state:
    st.session_state.greeted = True
    st.session_state.messages.append({"role": "assistant", "content": (
        "Chào em! 👋 Thầy là **Thầy Minh** — chuyên gia tư vấn hướng nghiệp, "
        "đã đồng hành cùng hàng trăm bạn học sinh THPT ở Tây Ninh và khu vực miền Nam.\n\n"
        "Thầy hiểu giai đoạn này áp lực lắm — vừa lo thi tốt nghiệp, vừa băn khoăn không biết "
        "chọn ngành gì, trường nào cho phù hợp. Đừng lo, thầy sẽ đi cùng em từng bước! 💪\n\n"
        "---\n\n"
        "**Thầy giúp được em:**\n"
        "- 📊 **Điểm chuẩn chính xác 3 năm (2023–2024–2025)** của bất kỳ trường, ngành nào\n"
        "- 🏫 **Top trường phù hợp nhất** phân tầng theo mức điểm thi thử của em\n"
        "- 🗺️ **Khoảng cách từ Tây Ninh**, ký túc xá, chi phí sống thực tế\n"
        "- 💼 **Cơ hội việc làm & mức lương** sau khi ra trường\n"
        "- 🎯 **Chiến thuật đặt nguyện vọng** thông minh, an toàn\n\n"
        "---\n\n"
        "👉 Em hãy điền **Hồ Sơ** ở thanh bên trái để thầy tư vấn sát với lực học của em nhất nhé!\n\n"
        "Hoặc em cứ hỏi thẳng vào vấn đề — nhấn một gợi ý bên dưới để bắt đầu. 👇"
    )})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GỢI Ý NHANH (Chỉ hiện khi chưa có chat)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if len(st.session_state.messages) == 1:
    st.markdown('<div class="section-label">💬 Bắt đầu bằng một trong các câu hỏi gợi ý</div>', unsafe_allow_html=True)
    suggestions = [
        ("🏥", "Điểm chuẩn Y khoa ĐH Y Dược TP.HCM 2023–2025 là bao nhiêu?"),
        ("💻", "Ngành CNTT nên học trường nào gần Tây Ninh? Điểm chuẩn ra sao?"),
        ("📐", "Sư phạm Toán ĐH Cần Thơ: điểm chuẩn 3 năm và cơ hội việc làm"),
        ("⚙️", "Kỹ thuật Xây dựng học ở đâu phía Nam? So sánh điểm chuẩn 2023–2025"),
        ("🌿", "Nông nghiệp công nghệ cao: trường nào tốt, điểm chuẩn bao nhiêu?"),
        ("💰", "Kế toán vs Tài chính Ngân hàng — nên chọn ngành nào, trường nào?"),
    ]
    cols = st.columns(3)
    for i, (icon, text) in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(f"{icon}  {text}", key=f"sg_{i}"):
                st.session_state["_pending"] = text
                st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  XỬ LÝ LỘ TRÌNH PROMPT & TÌM KIẾM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORE_KEYWORDS = ["điểm chuẩn", "tuyển sinh", "xét tuyển", "nguyện vọng", "đăng ký", "nộp hồ sơ", "điểm đầu vào", "bao nhiêu điểm", "điểm xét", "trúng tuyển"]

def needs_score_search(text: str) -> bool:
    return any(k in text.lower() for k in SCORE_KEYWORDS)

def build_gemini_history(messages: list) -> list:
    history = []
    for m in messages[:-1]:
        role = "model" if m["role"] == "assistant" else "user"
        history.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    return history

def call_ai(user_input: str, profile: dict) -> str:
    history = build_gemini_history(st.session_state.messages)
    use_search = needs_score_search(user_input)
    
    # Lệnh ép buộc công cụ tìm kiếm hoạt động mạnh
    enhanced_input = user_input
    if use_search:
        enhanced_input += "\n\n[LỆNH HỆ THỐNG]: Hãy dùng Google Search tra cứu ngay điểm chuẩn 2025, 2024 của trường/ngành học sinh vừa hỏi."

    # Gọi API với Search
    if use_search:
        try:
            cfg = make_config(use_search=True, profile=profile)
            chat = gemini_client.chats.create(model=GEMINI_MODEL, config=cfg, history=history)
            resp = chat.send_message(enhanced_input)
            return resp.text
        except Exception:
            pass # Chuyển sang fallback

    # Gọi API Fallback (Không Search)
    try:
        cfg = make_config(use_search=False, profile=profile)
        chat = gemini_client.chats.create(model=GEMINI_MODEL, config=cfg, history=history)
        resp = chat.send_message(enhanced_input)
        suffix = "\n\n---\n> ⚠️ *Hệ thống tìm kiếm trực tuyến tạm thời bận. Thầy tư vấn từ kiến thức chuyên sâu — em nhớ xác minh điểm chuẩn trên website chính thức của trường trước khi nộp hồ sơ nhé!*" if use_search else ""
        return resp.text + suffix
    except Exception as e:
        return f"❌ Xin lỗi em, hệ thống gặp sự cố: `{e}`\n\nEm thử lại sau vài phút nhé!"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  XỬ LÝ CHAT INPUT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pending = st.session_state.pop("_pending", None)
user_query = pending or st.chat_input("Em hỏi gì cũng được — điểm chuẩn 2025, ngành học, trường, nghề nghiệp... 💬", key="chat_input_main")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        # Tối ưu giao diện Loading bằng st.status nhìn cực kỳ xịn xò
        with st.status("🔍 Thầy đang lướt web tra cứu dữ liệu mới nhất...", expanded=True) as status:
            st.write("📡 Phân tích hồ sơ cá nhân...")
            st.write("🌐 Đang kết nối hệ thống tìm kiếm 2025...")
            profile = st.session_state.get("profile", {})
            reply = call_ai(user_query, profile)
            status.update(label="✅ Đã phân tích xong!", state="complete", expanded=False)
            
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FOOTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div style="text-align:center; color:#a8b9cc; font-size:0.76rem; padding:28px 0 20px; border-top:1px solid #e8e4dc; margin-top:24px;">
    🎓 <strong>Hướng Nghiệp 12 PRO v3.5</strong> · Powered by Gemini 2.5 Flash + Google Search<br>
    Điểm chuẩn được tra cứu từ đề án tuyển sinh chính thức · Luôn xác minh lại trước khi nộp hồ sơ<br>
    <span style="color:#647d96;">Made with ❤️ for học sinh Tây Ninh</span>
</div>
""", unsafe_allow_html=True)