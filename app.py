"""
╔══════════════════════════════════════════════════════════════════╗
║   TRỢ LÝ HƯỚNG NGHIỆP 12 PRO  —  v5.0 (Bản Thực Chiến Nước Rút)  ║
║   Engine: Gemini 2.5 Flash + Google Search Grounding             ║
║   Tính năng mới: Đa Tab, Máy đo tỷ lệ đậu, Bản đồ chiến lược     ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import datetime
import google.generativeai as genai

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PAGE CONFIG (Phải là lệnh đầu tiên)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Hướng Nghiệp 12 PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSS - GIAO DIỆN HIỆN ĐẠI BẢN 5.0 (Tối ưu Tabs & Nút bấm)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Fraunces:wght@700;900&display=swap');

/* ── BASE ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: #f4f7f6;
    min-height: 100vh;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #1f2937 !important;
    width: 320px !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small { color: #9ca3af !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] hr { border-color: #374151 !important; margin: 14px 0 !important; }

[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #f3f4f6 !important;
    border-radius: 8px !important;
}

/* Nút chính */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.5) !important;
}

/* Nút phụ (bắt bằng text nội dung thay vì kind) */
[data-testid="stSidebar"] .stButton > button:contains("📥 Tải phiếu tư vấn"),
[data-testid="stSidebar"] .stButton > button:contains("🗑️ Reset Hệ thống") {
    background: transparent !important;
    color: #9ca3af !important;
    border: 1px solid #4b5563 !important;
}
[data-testid="stSidebar"] .stButton > button:contains("📥 Tải phiếu tư vấn"):hover,
[data-testid="stSidebar"] .stButton > button:contains("🗑️ Reset Hệ thống"):hover {
     background: #1f2937 !important;
     color: #f3f4f6 !important;
}


/* ── TOP BANNER ── */
.top-banner {
    background: linear-gradient(120deg, #1e3a8a, #312e81, #4c1d95);
    padding: 30px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 3px solid #f59e0b;
    border-radius: 0 0 20px 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.banner-eyebrow {
    font-size: 0.75rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: #fcd34d; margin-bottom: 6px;
}
.banner-title {
    font-family: 'Fraunces', serif; font-size: 2.2rem; font-weight: 900; color: #ffffff; line-height: 1.2; letter-spacing: -0.5px;
}
.banner-title em { color: #f59e0b; font-style: normal; }
.banner-desc { font-size: 0.9rem; color: #cbd5e1; margin-top: 5px; }

/* ── TABS NÂNG CẤP ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 24px;
    padding: 0 24px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0 0;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
    font-weight: 600;
    font-size: 1.05rem;
    color: #4b5563;
}
.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    border-bottom: 3px solid #2563eb !important;
}

/* ── CHAT AREA ── */
[data-testid="stChatMessage"] {
    background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; margin-bottom: 25px !important;
}
[data-testid="stChatMessageAvatarUser"] { background-color: #3b82f6 !important; }
[data-testid="stChatMessageAvatarAssistant"] { background-color: #f59e0b !important; }

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #1e3a8a, #2563eb) !important; color: #ffffff !important; border-radius: 20px 20px 4px 20px !important; padding: 15px 22px !important; font-size: 1rem !important;
}
/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    background: #ffffff !important; color: #1f2937 !important; border-radius: 4px 20px 20px 20px !important; padding: 24px 28px !important; font-size: 1.05rem !important; border: 1px solid #e5e7eb !important;
}

/* Bảng điểm chuẩn có cột Đánh giá */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) table {
    width: 100% !important; border-collapse: separate !important; border-spacing: 0; border-radius: 10px; overflow: hidden; font-size: 0.95rem !important; margin: 20px 0 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) th {
    background: #1e3a8a !important; color: #ffffff !important; padding: 12px !important; font-weight: 700 !important; text-align: center !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) td {
    padding: 12px !important; border-bottom: 1px solid #f3f4f6 !important; text-align: center !important; background: #ffffff !important;
}

/* ── QUICK ACTION BUTTONS ── */
.quick-action-btn button {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    color: #374151 !important;
    border-radius: 20px !important;
    padding: 8px 16px !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.quick-action-btn button:hover {
    background: #eff6ff !important;
    border-color: #3b82f6 !important;
    color: #1d4ed8 !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CẤU HÌNH API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Chưa tìm thấy mã API trong Két sắt (Secrets) của Streamlit.")
    st.stop()

# Khởi tạo thư viện
genai.configure(api_key=GEMINI_API_KEY)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SYSTEM PROMPT V5.0 (Ép đo lường tỷ lệ đậu & Nhấn mạnh thời gian)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_system_prompt(profile: dict) -> str:
    base_prompt = """Bạn là **Thầy T** — một chuyên gia tư vấn hướng nghiệp xuất sắc, giấu tên, có 15 năm kinh nghiệm đồng hành cùng học sinh THPT tại Việt Nam. 
ĐẶC BIỆT LƯU Ý: Hiện tại đang là **Tháng 5 năm 2026**. Kỳ thi THPT Quốc gia chỉ còn hơn 1 tháng nữa. Lời khuyên của bạn phải mang tính THỰC CHIẾN, KHẨN TRƯƠNG và CHIẾN LƯỢC.

══════════════════════════════════════════════
🔴 CỖ MÁY ĐO LƯỜNG TỶ LỆ ĐẬU (LỆNH TỐI CAO)
══════════════════════════════════════════════
1. BẮT BUỘC DÙNG GOOGLE SEARCH: Tra cứu điểm chuẩn chính xác 2023, 2024, 2025. Tuyệt đối cấm bịa điểm.
2. BẢNG PHÂN TÍCH 5 CỘT (CẤU TRÚC BẮT BUỘC):
   Dựa vào ĐIỂM THI THỬ của học sinh (nếu có cung cấp), bạn PHẢI đối chiếu với điểm Dự báo 2026 và đưa ra nhãn đánh giá rủi ro ở cột thứ 5.
   | Tổ hợp | 2023 | 2024 | 2025 | Dự báo 2026 | Tỷ lệ đậu (So với điểm thử) |
   |--------|------|------|------|-------------|-----------------------------|
   | A00    | 24.5 | 24.8 | 25.1 | Tăng ~0.5đ  | 🔴 Rủi ro (Thiếu 1.5đ)      |
   
   *Tiêu chí dán nhãn:*
   - 🟢 **An toàn:** Điểm thi thử cao hơn điểm dự báo từ 1.5 điểm trở lên.
   - 🟡 **Vừa sức:** Điểm thi thử ngang bằng hoặc chênh lệch +/- 0.5 điểm.
   - 🔴 **Rủi ro (Cần cố gắng):** Điểm thi thử thấp hơn điểm dự báo > 1 điểm.

3. NHẬN ĐỊNH VÀ CHIẾN LƯỢC: Dưới bảng điểm, Thầy T phải phân tích thẳng thắn. Nếu rủi ro, phải "tạt gáo nước lạnh" cảnh tỉnh học sinh tập trung cày cuốc môn yếu trong 1 tháng cuối, hoặc gợi ý trường khác an toàn hơn.

══════════════════════════════════════════════
📋 CẤU TRÚC BÀI TƯ VẤN
══════════════════════════════════════════════
## 🌟 Giải mã Ngành học
## 📊 Máy Quét Tỷ Lệ Đậu (Bảng 5 cột)
## 🏫 Các trường Phương án B (Nếu trường mục tiêu quá rủi ro)
## 💼 Bức tranh Việc làm
## 🎯 Lệnh Hành Động Tháng 5 (Chiến lược 30 ngày cuối)

🗣️ PHONG CÁCH: Xưng "Thầy T", gọi "em". Thực tế, thẳng thắn nhưng vẫn động viên. Dùng icon.
"""
    
    if any(profile.values()):
        profile_str = "\n══════════════════════════════════════════════\n"
        profile_str += "👤 HỒ SƠ CỦA HỌC SINH ĐANG CHAT (DÙNG ĐỂ ĐO LƯỜNG TỶ LỆ ĐẬU):\n"
        if profile.get("score"): profile_str += f"- Điểm thi thử hiện tại: {profile['score']} điểm\n"
        if profile.get("combo") and profile["combo"] != "Chưa chọn": profile_str += f"- Tổ hợp môn: {profile['combo']}\n"
        if profile.get("major"): profile_str += f"- Ngành quan tâm: {profile['major']}\n"
        if profile.get("strengths"): profile_str += f"- Thế mạnh/Sở thích: {profile['strengths']}\n"
        profile_str += "=> LỆNH: Hãy lấy điểm thi thử này để tính toán cột Tỷ lệ đậu.\n"
        base_prompt += profile_str

    return base_prompt

def get_model(profile):
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=build_system_prompt(profile),
        tools=[{"google_search": {}}]
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("## 🎓 Hướng Nghiệp 12 PRO")
    st.caption("Thầy T · Phiên bản 5.0 (Thực Chiến)")
    st.divider()

    st.markdown("### 📋 Hồ Sơ Xét Tuyển")

    if "profile" not in st.session_state:
        st.session_state.profile = {}

    p = st.session_state.profile
    combo_opts = ["Chưa chọn", "A00 — Toán · Lý · Hóa", "A01 — Toán · Lý · Anh", "B00 — Toán · Hóa · Sinh", "C00 — Văn · Sử · Địa", "D01 — Toán · Văn · Anh", "Khác"]
    
    score_input = st.text_input("📊 Điểm thi thử (Gần nhất)", placeholder="VD: 24.5", value=p.get("score", ""))
    combo_input = st.selectbox("📚 Tổ hợp môn", combo_opts, index=combo_opts.index(p.get("combo", "Chưa chọn")) if p.get("combo") in combo_opts else 0)
    major_input = st.text_input("🎯 Ngành mục tiêu", placeholder="VD: Marketing", value=p.get("major", ""))
    strengths_input = st.text_input("💡 Môn học mạnh nhất", placeholder="VD: Toán, Anh", value=p.get("strengths", ""))

    if st.button("💾 Khóa Hồ Sơ", use_container_width=True):
        st.session_state.profile = {
            "score": score_input.strip(),
            "combo": combo_input if combo_input != "Chưa chọn" else "",
            "major": major_input.strip(),
            "strengths": strengths_input.strip(),
        }
        st.success("✅ Thầy T đã nạp hồ sơ của em vào hệ thống.")

    st.divider()

    # FIX LỖI Ở ĐÂY: XÓA THUỘC TÍNH kind="secondary"
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        chat_content = f"PHPHIẾU TƯ VẤN V5.0 (THẦY T)\nNgày xuất: {datetime.datetime.now().strftime('%d/%m/%Y')}\n" + "="*40 + "\n\n"
        for m in st.session_state.messages:
            role = "Học sinh" if m["role"] == "user" else "Thầy T"
            chat_content += f"{role}:\n{m['content']}\n\n{'-'*40}\n"
        st.download_button(label="📥 Tải phiếu tư vấn (.txt)", data=chat_content, file_name="Tu_Van_Thay_T.txt", mime="text/plain", use_container_width=True)
        
    # FIX LỖI Ở ĐÂY: XÓA THUỘC TÍNH kind="secondary"
    if st.button("🗑️ Reset Hệ thống", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("strategy_map", None)
        st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BANNER MAIN APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="top-banner">
  <div class="banner-left">
    <div class="banner-eyebrow">🎓 Phiên bản 5.0 · Đếm ngược THPTQG 2026</div>
    <div class="banner-title">Cùng <em>Thầy T</em> Bứt Phá Tháng Cuối</div>
    <div class="banner-desc">Đo lường rủi ro · Phân tích tỷ lệ đậu · Bản đồ chiến lược 30 ngày</div>
  </div>
  <div class="banner-right">
    <span class="banner-chip live">⚡ Google Search Realtime</span>
    <span class="banner-chip">📈 Máy quét Rủi ro</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MULTI-TAB UI (ĐA TAB)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab1, tab2 = st.tabs(["💬 Trò chuyện cùng Thầy T", "🗺️ Bản đồ Chiến lược"])

# ----------------- TAB 1: CHAT -----------------
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": (
            "Chào em! 👋 Thầy là **Thầy T**. \n\n"
            "Chỉ còn hơn 1 tháng nữa là bước vào kỳ thi THPT Quốc gia 2026 rồi. Đây không còn là lúc để mơ mộng nữa, mà phải **Đo lường và Chiến lược**.\n\n"
            "Em hãy điền điểm thi thử bên trái, rồi hỏi thầy bất kỳ trường nào. Thầy sẽ kích hoạt **Máy quét Tỷ lệ đậu** để cho em biết em đang ở mức 🟢 An Toàn, 🟡 Vừa Sức hay 🔴 Rủi Ro nhé!"
        )})

    # Hiển thị tin nhắn
    for msg in st.session_state.messages:
        avatar_icon = "🙋" if msg["role"] == "user" else "🧑‍🏫"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

    # Xử lý nhập liệu từ Quick Buttons
    quick_query = None
    if len(st.session_state.messages) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🤖 Quét tỷ lệ đậu ngành em chọn", key="q1", use_container_width=True): quick_query = "Thầy T ơi, dựa vào điểm thi thử của em ở thanh bên, hãy quét tỷ lệ đậu ngành em đang nhắm tới giúp em với!"
        with col2:
            if st.button("🏫 Gợi ý các trường An Toàn", key="q2", use_container_width=True): quick_query = "Điểm của em hiện tại khá chênh vênh. Thầy gợi ý cho em vài trường lấy điểm thấp hơn 1-2 điểm để làm phương án An Toàn nhé."
        with col3:
            if st.button("📈 Dự báo phổ điểm 2026", key="q3", use_container_width=True): quick_query = "Thầy đánh giá xu hướng ra đề và dự báo phổ điểm khối em chọn năm 2026 này sẽ tăng hay giảm?"

    user_query = st.chat_input("Hỏi Thầy T điểm chuẩn, đo lường rủi ro... 💬")
    
    # Ưu tiên query từ button, nếu không có thì lấy từ input
    final_query = quick_query if quick_query else user_query

    if final_query:
        enhanced_input = final_query + "\n\n[LỆNH HỆ THỐNG]: Bắt buộc lướt web lấy điểm chuẩn. Tính toán Rủi ro theo Điểm thi thử. Kẻ bảng 5 cột có cột Tỷ lệ đậu."

        st.session_state.messages.append({"role": "user", "content": final_query})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(final_query)

        with st.chat_message("assistant", avatar="🧑‍🏫"):
            with st.status("🔍 Thầy T đang khởi động Máy quét dữ liệu...", expanded=True) as status:
                st.write("📡 Trích xuất điểm thi thử của em...")
                st.write("🌐 Đang tải dữ liệu điểm chuẩn 2023-2025 từ Internet...")
                st.write("🧮 Đang đối chiếu rủi ro và tính tỷ lệ đậu...")
                
                profile = st.session_state.get("profile", {})
                model = get_model(profile)
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    
                try:
                    chat = model.start_chat(history=history)
                    response = chat.send_message(enhanced_input)
                    reply = response.text
                    status.update(label="✅ Thầy đã tính toán xong!", state="complete", expanded=False)
                except Exception as e:
                    reply = f"❌ Xin lỗi em, hệ thống tra cứu mạng đang quá tải: `{e}`. Em thử hỏi lại nhé!"
                    status.update(label="❌ Lỗi hệ thống", state="error", expanded=False)
                
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ----------------- TAB 2: BẢN ĐỒ CHIẾN LƯỢC -----------------
with tab2:
    st.markdown("### 🗺️ BẢN ĐỒ CHIẾN LƯỢC NƯỚC RÚT (THÁNG 5/2026)")
    st.info("Tính năng này sẽ tổng hợp toàn bộ hồ sơ của em để vạch ra một lộ trình ôn tập và đăng ký nguyện vọng tối ưu nhất trong 30 ngày cuối.")
    
    p = st.session_state.get("profile", {})
    if not p.get("score") or not p.get("major"):
        st.warning("⚠️ Em cần nhập ít nhất **Điểm thi thử** và **Ngành mục tiêu** ở thanh bên trái, sau đó bấm 'Khóa Hồ Sơ' để Thầy T có thể vẽ Bản đồ nhé.")
    else:
        if st.button("🚀 Kích hoạt vẽ Bản đồ Chiến lược", type="primary"):
            with st.spinner("⏳ Thầy T đang phác thảo chiến lược riêng cho em..."):
                prompt_strategy = f"""
                Dựa vào hồ sơ học sinh: Điểm thi thử {p['score']}, Khối {p['combo']}, Ngành {p['major']}, Môn mạnh {p['strengths']}.
                Hãy vẽ một "Bản đồ Chiến lược Nước rút Tháng 5/2026" siêu chi tiết gồm:
                1. Chẩn đoán lâm sàng: Điểm mạnh, điểm yếu hiện tại.
                2. Chiến thuật xếp 3 lớp nguyện vọng (Đỉnh cao - Vừa sức - Trụ hạng).
                3. Lộ trình ôn tập 30 ngày cuối (chia theo tuần).
                Dùng Markdown đẹp, giọng văn như một vị tướng quân ra lệnh xuất trận.
                """
                try:
                    model_str = genai.GenerativeModel(model_name="gemini-2.5-flash")
                    res = model_str.generate_content(prompt_strategy)
                    st.session_state.strategy_map = res.text
                except Exception as e:
                    st.error("Có lỗi tạo bản đồ, em thử lại nhé!")

        if "strategy_map" in st.session_state:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(st.session_state.strategy_map)
