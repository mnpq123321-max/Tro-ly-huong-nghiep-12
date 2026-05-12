import streamlit as st
import pandas as pd
import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types

# 1. CẤU HÌNH TRANG (Bắt buộc phải gọi đầu tiên)
st.set_page_config(
    page_title="Hướng Nghiệp 12 PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CẤU HÌNH GIAO DIỆN & CSS (Tối ưu UI/UX)
def apply_custom_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
            .stApp { background-color: #F9FAFB; }
            
            /* Sidebar Styling */
            [data-testid="stSidebar"] {
                background-color: #111827 !important;
                border-right: 1px solid #1F2937;
            }
            [data-testid="stSidebar"] * { color: #D1D5DB !important; }
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                color: #F9FAFB !important; font-weight: 600;
            }
            [data-testid="stSidebar"] hr { border-color: #374151 !important; }
            
            /* Buttons */
            .stButton > button {
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
                color: white !important; border: none !important;
                border-radius: 8px !important; font-weight: 600 !important;
                transition: all 0.3s ease !important; width: 100%;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
            }

            /* Secondary Button for clear chat */
            button[kind="secondary"] {
                background: transparent !important;
                border: 1px solid #4B5563 !important;
                color: #9CA3AF !important;
            }
            button[kind="secondary"]:hover {
                background: #374151 !important;
                color: white !important;
            }

            /* Chat Bubbles */
            [data-testid="stChatMessage"] { background-color: transparent !important; border-bottom: none !important; }
            
            /* User Message */
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
                background-color: #E0E7FF !important; color: #1E1B4B !important;
                border-radius: 16px 16px 4px 16px; padding: 1rem 1.25rem;
            }
            
            /* Assistant Message */
            [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
                background-color: #FFFFFF !important; color: #111827 !important;
                border-radius: 4px 16px 16px 16px; padding: 1.25rem;
                border: 1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            }
            
            /* Chat Input */
            [data-testid="stChatInput"] {
                border-radius: 12px !important; border: 1px solid #D1D5DB !important;
            }
        </style>
    """, unsafe_allow_html=True)

# 3. DATA SCHEMAS (Ép AI trả về JSON chuẩn, loại bỏ lỗi regex)
class ScoreRow(BaseModel):
    school: str = Field(description="Tên trường đại học")
    major_combo: str = Field(description="Ngành/Khối thi")
    y2023: Optional[float] = Field(None, description="Điểm chuẩn 2023")
    y2024: Optional[float] = Field(None, description="Điểm chuẩn 2024")
    y2025: Optional[float] = Field(None, description="Điểm chuẩn 2025")
    y2026_predict: Optional[float] = Field(None, description="Dự báo 2026")
    basis: str = Field(description="Ngắn gọn: Lý do dự báo")

class ScoreTable(BaseModel):
    title: str = Field(description="Tiêu đề bảng (vd: Điểm chuẩn ngành IT miền Nam)")
    rows: List[ScoreRow]

class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(description="Điểm mạnh của học sinh")
    weaknesses: List[str] = Field(description="Điểm yếu cần khắc phục")
    opportunities: List[str] = Field(description="Cơ hội ngành nghề")
    threats: List[str] = Field(description="Thách thức/Rủi ro")

class CareerRoadmapStep(BaseModel):
    phase: str = Field(description="Giai đoạn (vd: Năm 1-2, Mới ra trường)")
    action: str = Field(description="Hành động cần làm")

class AICounselorResponse(BaseModel):
    """Schema tổng mà AI bắt buộc phải tuân theo khi trả lời"""
    counseling_text: str = Field(description="Lời tư vấn chính bằng ngôn ngữ tự nhiên, Markdown. Trả lời trực tiếp câu hỏi.")
    score_table: Optional[ScoreTable] = Field(None, description="Bảng điểm chuẩn (chỉ tạo nếu user hỏi về điểm/trường).")
    swot: Optional[SWOTAnalysis] = Field(None, description="Phân tích SWOT (chỉ tạo nếu user băn khoăn chọn ngành).")
    roadmap: Optional[List[CareerRoadmapStep]] = Field(None, description="Lộ trình (chỉ tạo nếu user hỏi tương lai, việc làm).")

# 4. SYSTEM PROMPT & AI SETUP
SYSTEM_PROMPT = """Bạn là Thầy Minh — chuyên gia tư vấn hướng nghiệp 15 năm kinh nghiệm dành cho học sinh THPT Việt Nam.
Giọng điệu: Ấm áp, thực tế, đi thẳng vào vấn đề, truyền cảm hứng nhưng không sáo rỗng.

NHIỆM VỤ:
1. Phân tích câu hỏi của học sinh kết hợp với Hồ sơ cá nhân (điểm, khối, sở thích) để đưa ra lời khuyên.
2. NẾU HỎI VỀ ĐIỂM/TRƯỜNG: BẮT BUỘC dùng công cụ Google Search tìm điểm chuẩn 2023-2025. Không được tự bịa số liệu.
3. CẤU TRÚC: Trả lời bằng cách điền vào schema JSON hệ thống yêu cầu. Chia rõ: Text tư vấn, Bảng điểm, SWOT, Roadmap.
4. LƯU Ý ĐỊA LÝ: Mặc định ưu tiên khu vực phía Nam (TP.HCM, Cần Thơ, Tây Ninh...) trừ khi học sinh có yêu cầu khác.
"""

# Khởi tạo Client: Cố gắng lấy từ Streamlit Secrets, nếu không có thì lấy từ Biến môi trường
API_KEY = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=API_KEY) if API_KEY else None

# 5. CORE LLM SERVICE (Gọi API Gemini)
def get_ai_response(user_input: str, profile: dict, chat_history: list) -> dict:
    if not client:
        return {
            "text": "❌ Lỗi: Hệ thống chưa được cấu hình GEMINI_API_KEY. Vui lòng thêm biến môi trường hoặc Streamlit Secrets trên Github.",
            "data": None
        }

    # Build context từ hồ sơ học sinh
    ctx = "THÔNG TIN HỒ SƠ HỌC SINH:\n"
    if profile.get('score'): ctx += f"- Điểm thi dự kiến/thực tế: {profile['score']}\n"
    if profile.get('combo') and profile['combo'] != "Chưa chọn": ctx += f"- Khối/Tổ hợp: {profile['combo']}\n"
    if profile.get('major'): ctx += f"- Ngành quan tâm: {profile['major']}\n"
    if profile.get('budget') and profile['budget'] != "Chưa biết": ctx += f"- Khả năng tài chính: {profile['budget']}/tháng\n"
    if profile.get('location'): ctx += f"- Khu vực ưu tiên: {profile['location']}\n"
    
    full_prompt = f"{ctx}\n\nCÂU HỎI MỚI CỦA HỌC SINH:\n{user_input}"
    
    # Format history cho Gemini SDK
    formatted_history = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        if text_content := msg.get("content_text", ""):
            formatted_history.append(types.Content(role=role, parts=[types.Part.from_text(text=text_content)]))

    # Kích hoạt Structured Output & Search Grounding
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.3, # Thấp để JSON ổn định
        response_mime_type="application/json",
        response_schema=AICounselorResponse,
        tools=[{"google_search": {}}] # Cấp quyền AI lên mạng search real-time
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=formatted_history + [full_prompt],
            config=config
        )
        # Tự động parse chuỗi JSON trả về thành Pydantic Object an toàn
        ai_data = AICounselorResponse.model_validate_json(response.text)
        return {"text": ai_data.counseling_text, "data": ai_data}
        
    except Exception as e:
        print(f"API Error: {e}")
        return {"text": f"❌ Xin lỗi em, thầy đang gặp chút trục trặc mạng. Em hỏi lại hoặc chi tiết hơn nhé!", "data": None}

# 6. UI RENDER COMPONENTS (Vẽ bảng, SWOT, Roadmap)
def render_score_table(table_data: ScoreTable):
    if not table_data or not table_data.rows: return
    st.markdown(f"#### 📊 {table_data.title}")
    
    data = []
    for r in table_data.rows:
        data.append({
            "Trường": r.school, "Khối/Ngành": r.major_combo,
            "2023": f"{r.y2023}" if r.y2023 else "-", "2024": f"{r.y2024}" if r.y2024 else "-",
            "2025": f"{r.y2025}" if r.y2025 else "-", "🔮 Dự báo 2026": f"{r.y2026_predict}" if r.y2026_predict else "-",
            "Nhận định": r.basis
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def render_swot(swot_data: SWOTAnalysis):
    if not swot_data: return
    st.markdown("#### 🧭 Phân Tích Mức Độ Phù Hợp (SWOT)")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**💪 Điểm mạnh (Strengths)**\n" + "\n".join([f"- {s}" for s in swot_data.strengths]))
        st.warning("**⚠️ Thách thức (Threats)**\n" + "\n".join([f"- {t}" for t in swot_data.threats]))
    with col2:
        st.error("**🎯 Điểm yếu (Weaknesses)**\n" + "\n".join([f"- {w}" for w in swot_data.weaknesses]))
        st.success("**🌟 Cơ hội (Opportunities)**\n" + "\n".join([f"- {o}" for o in swot_data.opportunities]))

def render_roadmap(roadmap_data: List[CareerRoadmapStep]):
    if not roadmap_data: return
    with st.expander("🗺️ Lộ trình phát triển đề xuất", expanded=True):
        for step in roadmap_data:
            st.markdown(f"**📍 {step.phase}**")
            st.markdown(f"👉 {step.action}")
            st.divider()

def render_ai_message(message_dict):
    """Hàm tổng hợp render toàn bộ nội dung của 1 tin nhắn AI"""
    st.markdown(message_dict.get("content_text", ""))
    
    # Xử lý phục hồi data từ JSON (khi load lại từ history) hoặc object gốc
    raw_data = message_dict.get("data")
    if not raw_data: return
    
    try:
        # Nếu là object Pydantic
        if isinstance(raw_data, AICounselorResponse):
            data_obj = raw_data
        # Nếu là dict (lấy từ session_state)
        elif isinstance(raw_data, dict):
            data_obj = AICounselorResponse(**raw_data)
        else:
            return
            
        if data_obj.score_table: render_score_table(data_obj.score_table)
        if data_obj.swot: render_swot(data_obj.swot)
        if data_obj.roadmap: render_roadmap(data_obj.roadmap)
    except Exception as e:
        print(f"Render component error: {e}")

# 7. HÀM MAIN VÀ VÒNG LẶP GIAO DIỆN
def main():
    apply_custom_theme()
    
    # Khởi tạo State
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content_text": "Chào em! 👋 Thầy là **Thầy Minh**. Thầy ở đây để giúp em chọn ngành, chọn trường, tra cứu điểm chuẩn và vạch ra lộ trình học tập. \n\n👉 Hãy điền **Hồ sơ của em** ở cột bên trái để thầy tư vấn chính xác nhất nhé!", 
            "data": None
        }]
    if "profile" not in st.session_state:
        st.session_state.profile = {"score": "", "combo": "Chưa chọn", "major": "", "budget": "Chưa biết", "location": "Phía Nam"}

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("## 🎓 Hướng Nghiệp 12 PRO")
        st.caption("AI Mentor - Powered by Gemini 2.5")
        st.divider()
        st.markdown("### 📋 Hồ Sơ Của Em")
        
        p = st.session_state.profile
        sc = st.text_input("📊 Điểm thi thử / Tích lũy", value=p.get("score"), placeholder="VD: 24.5")
        
        cb_opts = ["Chưa chọn", "A00 (Toán-Lý-Hóa)", "A01 (Toán-Lý-Anh)", "B00 (Toán-Hóa-Sinh)", "D01 (Toán-Văn-Anh)", "Khác"]
        cb = st.selectbox("📚 Khối / Tổ hợp", options=cb_opts, index=cb_opts.index(p.get("combo")) if p.get("combo") in cb_opts else 0)
        
        mj = st.text_input("🎯 Ngành đang quan tâm", value=p.get("major"), placeholder="VD: Công nghệ thông tin")
        
        bg_opts = ["Chưa biết", "Dưới 3 triệu", "3-5 triệu", "5-8 triệu", "Trên 8 triệu"]
        bg = st.selectbox("💰 Chi phí sinh hoạt (tháng)", options=bg_opts, index=bg_opts.index(p.get("budget")) if p.get("budget") in bg_opts else 0)
        
        loc = st.text_input("🗺️ Tỉnh/TP ưu tiên học", value=p.get("location"), placeholder="VD: TP.HCM, Cần Thơ...")
        
        if st.button("💾 Cập nhật Hồ Sơ"):
            st.session_state.profile = {"score": sc, "combo": cb, "major": mj, "budget": bg, "location": loc}
            st.success("✅ Đã cập nhật cho AI!")
            
        st.divider()
        if st.button("🗑️ Làm mới cuộc trò chuyện", type="secondary"):
            st.session_state.messages = st.session_state.messages[:1]
            st.rerun()

    # --- HEADER ---
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #E5E7EB; margin-bottom: 2rem;">
            <div style="background: linear-gradient(135deg, #4F46E5, #7C3AED); padding: 10px; border-radius: 12px; font-size: 24px;">🎓</div>
            <div>
                <h2 style="margin: 0; color: #111827;">AI Career Counselor</h2>
                <span style="color: #6B7280; font-size: 0.9rem;">Kết nối trực tiếp Google Search & Phân tích lộ trình</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- CHAT HISTORY ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content_text"])
            else:
                render_ai_message(msg)

    # --- CHAT INPUT ---
    if user_query := st.chat_input("Hỏi thầy bất cứ gì về ngành học, trường đại học, hay điểm chuẩn..."):
        if not API_KEY:
            st.error("⚠️ CẢNH BÁO: Chưa có GEMINI_API_KEY. Hãy thiết lập trong Streamlit Secrets (Github) hoặc file .env.")
            st.stop()
            
        st.session_state.messages.append({"role": "user", "content_text": user_query, "data": None})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.status("🤖 Thầy Minh đang suy nghĩ và tra cứu dữ liệu...", expanded=True) as status:
                st.write("Phân tích hồ sơ và câu hỏi...")
                st.write("Đang truy xuất CSDL Điểm chuẩn và Thông tin tuyển sinh mới nhất...")
                
                response_dict = get_ai_response(user_query, st.session_state.profile, st.session_state.messages[:-1])
                
                status.update(label="✅ Phân tích hoàn tất!", state="complete", expanded=False)
            
            # Hiển thị
            render_ai_message(response_dict)
            
            # Lưu lịch sử (Convert Pydantic sang Dict để stream safe)
            data_to_save = response_dict["data"].model_dump() if response_dict.get("data") else None
            st.session_state.messages.append({"role": "assistant", "content_text": response_dict["text"], "data": data_to_save})

if __name__ == "__main__":
    main()
