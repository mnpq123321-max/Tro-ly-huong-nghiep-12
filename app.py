import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="Trợ Lý Hướng Nghiệp 12 PRO",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        font-weight: bold;
        margin-bottom: 5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 35px;
        font-style: italic;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .stMarkdown p {
        line-height: 1.8;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>🎓 TRỢ LÝ HƯỚNG NGHIỆP 12 PRO</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Chuyên gia tư vấn chọn trường, chọn ngành - Dữ liệu thực tế 2024/2025</div>", unsafe_allow_html=True)

# Lấy API Key từ "Két sắt" của Streamlit để bảo mật tuyệt đối
API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-1.5-flash" 

SYSTEM_PROMPT = """
Bạn là một "Siêu Cố Vấn Hướng Nghiệp" dành riêng cho học sinh lớp 12 tại Việt Nam.
Bạn có kiến thức chuyên sâu về tất cả các trường Đại học, Cao đẳng và xu hướng thị trường lao động.

NHIỆM VỤ TỐI THƯỢNG:
1. TRA CỨU THỰC TẾ: Khi học sinh hỏi về điểm chuẩn, bạn PHẢI sử dụng công cụ tìm kiếm để lấy điểm chuẩn năm 2024 mới nhất. Tuyệt đối không dùng dữ liệu cũ 2023 nếu đã có bản 2024.
2. TRẢ LỜI CỰC KỲ CHI TIẾT: Mỗi câu trả lời phải là một bài phân tích chuyên sâu (từ 500-1000 chữ). Phải mang tính thuyết phục cao.
3. CẤU TRÚC BÀI TƯ VẤN:
   - 🌟 Phần 1: Phân tích đặc thù ngành học (Học gì? Tố chất nào phù hợp? Tại sao nên chọn?).
   - 📈 Phần 2: Danh sách các trường đào tạo tốt nhất kèm ĐIỂM CHUẨN 2024 thực tế.
   - 💼 Phần 3: Bức tranh nghề nghiệp (Làm ở đâu? Lương bao nhiêu? Cơ hội thăng tiến thế nào?).
   - 🎯 Phần 4: Lời khuyên chiến lược về việc đặt nguyện vọng và ôn thi hiệu quả.

VĂN PHONG: Nhiệt tình, truyền cảm hứng, sử dụng biểu tượng cảm xúc (icon) sinh động, trình bày rõ ràng bằng các gạch đầu dòng và in đậm thông tin quan trọng.
"""

try:
    genai.configure(api_key=API_KEY)
    
    # Thiết lập mô hình AI có tính năng tìm kiếm Google
    model_with_search = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
        tools=[{"google_search": {}}]
    )
    
    # Mô hình dự phòng (không có search) để dùng khi gặp lỗi mạng
    model_fallback = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Em muốn hỏi gì về hướng nghiệp? (VD: Điểm chuẩn Sư phạm Toán 2024 ĐH Đồng Tháp)"):
        # Lưu câu hỏi người dùng
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # AI trả lời
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown("🔍 *Thầy đang lướt web tra cứu điểm chuẩn thực tế 2024/2025 và phân tích...*")
            
            try:
                # Ưu tiên dùng model có tra cứu Internet
                response = model_with_search.generate_content(user_query)
                final_text = response.text
                
                status_placeholder.empty()
                st.markdown(final_text)
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                
            except Exception as e:
                # Nếu Google Search bị lỗi, tự động chuyển sang dùng kiến thức nội tại
                status_placeholder.empty()
                st.warning("⚠️ Hệ thống tra cứu trực tuyến đang bận nhẹ. Thầy sẽ tư vấn cho em dựa trên kinh nghiệm chuyên gia của thầy ngay đây!")
                
                fallback_response = model_fallback.generate_content(user_query)
                st.markdown(fallback_response.text)
                st.session_state.messages.append({"role": "assistant", "content": fallback_response.text})

except Exception as init_error:
    st.error(f"Lỗi khởi tạo hệ thống: {init_error}")
