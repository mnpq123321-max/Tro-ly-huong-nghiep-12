import streamlit as st
import datetime
from google import genai
from google.genai import types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CẤU HÌNH GIAO DIỆN CƠ BẢN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Hướng Nghiệp 12 PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSS - LÀM ĐẸP GIAO DIỆN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Fraunces:wght@700;900&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: #f8f7f4; }
.top-banner {
    background: linear-gradient(135deg, #0f1923, #1a2738);
    padding: 25px 48px;
    border-radius: 0 0 20px 20px;
    margin-bottom: 20px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.banner-title { font-family: 'Fraunces', serif; font-size: 2.2rem; font-weight: 900; margin-bottom: 5px;}
.banner-desc { font-size: 1rem; color: #a8b9cc; }
[data-testid="stChatMessage"] { background: white !important; border-radius: 15px !important; padding: 15px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important; margin-bottom: 15px !important; border: 1px solid #e8e8e4 !important;}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: #eef2f6 !important; border: 1px solid #d5e1ed !important;}
table { width: 100% !important; border-collapse: collapse !important; margin: 15px 0 !important; }
th { background: #0f1923 !important; color: #f5a623 !important; padding: 10px !important; text-align: center !important; }
td { padding: 10px !important; border-bottom: 1px solid #e8e8e4 !important; text-align: center !important;}
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CẤU HÌNH API BẢO MẬT (LẤY TỪ KÉT SẤT)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("❌ Thầy ơi, thầy chưa cất mã API vào Két sắt (Secrets) của Streamlit rồi. Thầy vào Settings -> Secrets để dán mã vào nhé!")
    st.stop()

GEMINI_MODEL = "gemini-2.5-flash"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BỘ NÃO AI - KỶ LUẬT THÉP VÀ DỰ BÁO 2026
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_system_prompt(profile: dict) -> str:
    base_prompt = """Bạn là **Thầy T** — một chuyên gia tư vấn hướng nghiệp bí ẩn nhưng vô cùng uyên bác, tâm lý, chuyên tư vấn cho học sinh lớp 12 tại miền Nam.

🔴 KỶ LUẬT DỮ LIỆU ĐIỂM CHUẨN (TUYỆT ĐỐI TUÂN THỦ):
1. BẮT BUỘC SỬ DỤNG CÔNG CỤ TÌM KIẾM (GOOGLE SEARCH) ĐỂ TRA CỨU ĐIỂM CHUẨN CHÍNH XÁC CỦA NĂM 2024 VÀ 2025 TRƯỚC KHI TRẢ LỜI.
2. KHÔNG ĐƯỢC TỰ BỊA ĐẶT HOẶC ĐOÁN MÒ ĐIỂM CHUẨN DƯỚI BẤT KỲ HÌNH THỨC NÀO.
3. CẢNH GIÁC "ĐIỂM SÀN": Phân biệt cực kỳ rõ ràng giữa "Điểm sàn/Điểm nhận hồ sơ" (thường rất thấp, 15-18 điểm) và "Điểm chuẩn trúng tuyển". CHỈ ĐƯỢC LẤY ĐIỂM CHUẨN TRÚNG TUYỂN.
4. Nếu tra cứu không thấy dữ liệu chính thức của một trường/ngành, BẮT BUỘC ghi rõ: "N/A - Chưa có dữ liệu chính thức". TUYỆT ĐỐI KHÔNG tự điền một con số ngẫu nhiên.
5. XÁC MINH KÉP: Hãy kiểm tra kỹ lại kết quả tìm kiếm của bạn. Ví dụ: Ngành Thú y ĐH Cần Thơ điểm chuẩn các năm gần đây thường ở mức cao (thường trên 23-24 điểm), không thể ở mức 18-19 điểm. NẾU CON SỐ TÌM ĐƯỢC QUÁ THẤP HOẶC VÔ LÝ so với mặt bằng chung của ngành đó ở một trường lớn, HÃY BÁO LỖI HOẶC TỪ CHỐI ĐƯA SỐ LIỆU.

📋 CẤU TRÚC TƯ VẤN BẮT BUỘC (Trình bày đẹp, dài và sâu sắc):
1. **Phân tích ngành:** Học gì? Hợp với ai?
2. **Bảng Điểm Chuẩn & Dự Báo (Kẻ bảng 4 cột y hệt mẫu này):**
| Trường/Ngành | Điểm 2023 | Điểm 2024 | Điểm 2025 | Dự báo 2026 (Xu hướng) |
|---|---|---|---|---|
| (Tên trường) | X.X | Y.Y | Z.Z | Tăng/Giảm nhẹ khoảng 0.5đ do... |
*(Bắt buộc phải có cột Dự báo 2026 và phân tích tại sao lại dự báo như vậy)*
3. **Đời sống & Khoảng cách:** Gợi ý trường gần nơi học sinh sống (nếu có thông tin). KTX, học phí.
4. **Cơ hội việc làm:** Ra trường làm gì? Lương bao nhiêu?
5. **Đo lường Tỷ lệ đậu:** So sánh điểm thi thử của học sinh với điểm dự báo 2026 để kết luận: 🟢 An Toàn, 🟡 Vừa Sức, hay 🔴 Rủi Ro.

🗣️ PHONG CÁCH: Xưng "thầy", gọi "em". Rất chuyên nghiệp, thấu hiểu.
"""
    
    # Ép hồ sơ học sinh vào não AI
    if any(profile.values()):
        base_prompt += "\n\n👤 HỒ SƠ CỦA EM HỌC SINH ĐANG HỎI:\n"
        if profile.get("score"): base_prompt += f"- Điểm thi thử: {profile['score']}\n"
        if profile.get("combo"): base_prompt += f"- Tổ hợp: {profile['combo']}\n"
        base_prompt += "=> Bắt buộc dùng Điểm thi thử này để Rà soát Tỷ lệ đậu cho em ấy."

    return base_prompt

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KHỞI TẠO HỆ THỐNG MỚI (TẠM BIỆT LỖI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.cache_resource(show_spinner=False)
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

client = get_gemini_client()
# Khai báo công cụ tìm kiếm theo chuẩn SDK mới nhất (Cái này chữa dứt điểm lỗi)
SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

def make_config(use_search: bool, profile: dict):
    return types.GenerateContentConfig(
        system_instruction=build_system_prompt(profile),
        tools=[SEARCH_TOOL] if use_search else [],
        temperature=0.0, # ÉP VỀ 0.0 ĐỂ DẬP TẮT HOÀN TOÀN SỰ BỊA ĐẶT, CÓ SAO NÓI VẬY
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SIDEBAR & GIAO DIỆN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("## 📋 Hồ Sơ Của Em")
    if "profile" not in st.session_state:
        st.session_state.profile = {}
    p = st.session_state.profile

    score_input = st.text_input("📊 Điểm thi thử", value=p.get("score", ""))
    combo_input = st.selectbox("📚 Tổ hợp", ["Chưa chọn", "A00", "A01", "B00", "C00", "D01", "D07", "Khác"], index=0)
    
    if st.button("💾 Lưu hồ sơ", use_container_width=True):
        st.session_state.profile = {"score": score_input, "combo": combo_input}
        st.success("✅ Đã lưu để Thầy T phân tích!")

    st.divider()
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        chat_data = "PHIẾU TƯ VẤN - THẦY T\n" + "="*30 + "\n"
        for m in st.session_state.messages:
            chat_data += f"{m['role'].upper()}: {m['content']}\n\n"
        st.download_button("📥 Tải phiếu tư vấn", chat_data, "Phieu_Tu_Van.txt", use_container_width=True)

    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("""
<div class="top-banner">
    <div class="banner-title">🎓 TRỢ LÝ HƯỚNG NGHIỆP 12 PRO</div>
    <div class="banner-desc">Cố vấn chiến lược: Thầy T. — Dự báo điểm chuẩn 2026 & Đo lường tỷ lệ đậu</div>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  XỬ LÝ TRÒ CHUYỆN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [{"role": "assistant", "content": "Chào em! Thầy là **Thầy T**. Thầy ở đây để giúp em lướt web lấy điểm chuẩn thật, dự báo điểm 2026 và đo lường tỷ lệ đậu cho em. Em định thi ngành gì nào?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_query := st.chat_input("Hỏi Thầy T về ngành, trường, điểm chuẩn..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.status("🔍 Thầy T đang rà soát dữ liệu mạng và tính toán dự báo 2026...", expanded=True) as status:
            try:
                # Chuyển đổi lịch sử chat
                history = [types.Content(role="model" if m["role"] == "assistant" else "user", parts=[types.Part(text=m["content"])]) for m in st.session_state.messages[:-1]]
                
                # Gọi AI với Search Tool MỚI
                cfg = make_config(True, st.session_state.profile)
                chat = client.chats.create(model=GEMINI_MODEL, config=cfg, history=history)
                response = chat.send_message(user_query + "\n[LỆNH BÍ MẬT]: BẮT BUỘC tra cứu Google lấy điểm chuẩn. Kẻ bảng 4 cột có DỰ BÁO 2026. Chấm tỷ lệ đậu.")
                reply = response.text
                
                status.update(label="✅ Phân tích hoàn tất!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="⚠️ Lỗi kết nối", state="error", expanded=False)
                reply = f"❌ Đã xảy ra lỗi mạng: `{e}`. Em vui lòng F5 tải lại trang nhé."
                
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
