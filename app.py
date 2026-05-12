import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from google import genai
from google.genai import types

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. CẤU HÌNH GIAO DIỆN & CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Hướng Nghiệp 12 PRO",
    page_icon="🎓",
    layout="wide",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f7fb;
}

.hero {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    padding: 2rem;
    border-radius: 24px;
    color: white;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
}

.hero h1 { margin: 0; font-weight: 800; font-size: 2.2rem; }
.hero p { margin-top: 5px; font-size: 1.1rem; opacity: 0.9; }

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

[data-testid="stChatMessage"] {
    border-radius: 20px !important;
    padding: 16px !important;
    background: white;
    border: 1px solid #e2e8f0;
    margin-bottom: 12px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. KHỞI TẠO & XỬ LÝ DATABASE (SQLite)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DB_PATH = "admissions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school TEXT, major TEXT, combo TEXT,
        score_2023 REAL, score_2024 REAL, score_2025 REAL,
        tuition TEXT, city TEXT, dorm TEXT, career TEXT
    )
    """)
    
    # Kiểm tra xem có dữ liệu chưa
    cur.execute("SELECT COUNT(*) FROM admissions")
    if cur.fetchone()[0] == 0:
        sample_data = [
            ("ĐH CNTT - ĐHQG HCM", "Công nghệ thông tin", "A00,A01", 27.1, 27.5, 27.8, "35-45 triệu/năm", "TP.HCM", "Có KTX", "Software Engineer, AI"),
            ("ĐH Khoa học Tự nhiên", "Khoa học máy tính", "A00,A01", 28.0, 28.2, 28.4, "30-40 triệu/năm", "TP.HCM", "Có KTX", "AI Research, Data"),
            ("ĐH Cần Thơ", "Thú y", "B00", 24.5, 24.8, 25.1, "22-28 triệu/năm", "Cần Thơ", "Có KTX", "Bác sĩ thú y"),
            ("ĐH Đồng Tháp", "Sư phạm Toán", "A00", 23.5, 24.0, 24.5, "Miễn học phí", "Đồng Tháp", "Có KTX", "Giáo viên THPT"),
        ]
        cur.executemany("""
            INSERT INTO admissions (school, major, combo, score_2023, score_2024, score_2025, tuition, city, dorm, career) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        conn.commit()
    conn.close()

# Khởi chạy DB
init_db()

def search_major(keyword):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM admissions WHERE major LIKE ?", conn, params=[f"%{keyword}%"])
    conn.close()
    return df

def get_all_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM admissions", conn)
    conn.close()
    return df

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. THUẬT TOÁN DỰ BÁO VÀ CHẤM ĐIỂM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def predict_score(score23, score24, score25):
    """Sử dụng Hồi quy tuyến tính (Linear Regression) để dự báo điểm 2026"""
    x = np.array([2023, 2024, 2025])
    y = np.array([score23, score24, score25])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * 2026 + intercept
    return min(round(prediction, 2), 30.0) # Không quá 30 điểm

def classify_chance(student_score, predicted_score):
    diff = student_score - predicted_score
    if diff >= 1.0: return "🟢 An toàn"
    elif diff >= -0.5: return "🟡 Vừa sức"
    else: return "🔴 Rủi ro"

def recommend_schools(student_score, combo):
    df = get_all_data()
    recommendations = []
    for _, row in df.iterrows():
        # Lọc cơ bản theo tổ hợp
        if combo in row["combo"] or combo == "Khác":
            predicted = predict_score(row["score_2023"], row["score_2024"], row["score_2025"])
            status = classify_chance(student_score, predicted)
            recommendations.append({
                "school": row["school"], "major": row["major"],
                "predicted": predicted, "status": status,
                "tuition": row["tuition"], "city": row["city"]
            })
    return recommendations

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. THIẾT KẾ GIAO DIỆN (UI COMPONENTS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown(
    """<div class='hero'>
        <h1>🎓 HƯỚNG NGHIỆP 12 PRO</h1>
        <p>Hệ thống AI Tư vấn Tuyển sinh & Dự báo điểm chuẩn 2026</p>
    </div>""", unsafe_allow_html=True
)

with st.sidebar:
    st.header("📋 Hồ sơ học sinh")
    score = st.number_input("Điểm thi thử hiện tại", min_value=0.0, max_value=30.0, value=24.0, step=0.25)
    combo = st.selectbox("Tổ hợp xét tuyển", ["A00", "A01", "B00", "D01", "C00", "Khác"])
    favorite_major = st.text_input("Ngành quan tâm nhất", value="Công nghệ thông tin")
    
    st.divider()
    st.markdown("**Thống kê Hồ sơ:**")
    c1, c2 = st.columns(2)
    c1.metric("Điểm của em", f"{score}đ")
    c2.metric("Tổ hợp", combo)
    if st.button("🗑️ Xóa lịch sử trò chuyện AI", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. HIỂN THỊ PHÂN TÍCH & BIỂU ĐỒ TRỰC QUAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.subheader("🎯 Cỗ máy Đo lường Mức độ Phù hợp")
recommendations = recommend_schools(score, combo)

if recommendations:
    cols = st.columns(min(len(recommendations), 3))
    for idx, rec in enumerate(recommendations[:3]):
        with cols[idx]:
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='color: #1e40af; margin-top:0;'>{rec['school']}</h4>
                <b>Ngành:</b> {rec['major']}<br>
                <b>Dự báo 2026:</b> {rec['predicted']} đ<br>
                <b>Tỷ lệ đậu:</b> {rec['status']}<br>
                <b>Học phí:</b> {rec['tuition']}<br>
                <b>Khu vực:</b> {rec['city']}
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Chưa tìm thấy trường phù hợp trong cơ sở dữ liệu mẫu. Hãy hỏi Chatbot AI bên dưới nhé!")

st.divider()

st.subheader("📈 Phân tích Xu hướng Điểm chuẩn")
df_search = search_major(favorite_major)

if not df_search.empty:
    row = df_search.iloc[0]
    pred = predict_score(row['score_2023'], row['score_2024'], row['score_2025'])
    status = classify_chance(score, pred)

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Dự báo 2026 ({row['school']})", f"{pred} đ", f"{round(pred - row['score_2025'], 2)} đ so với 2025")
    m2.metric("Khả năng đậu của em", status)
    m3.metric("Học phí tham khảo", row['tuition'])

    # Vẽ biểu đồ
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[2023, 2024, 2025, 2026], 
        y=[row['score_2023'], row['score_2024'], row['score_2025'], pred],
        mode='lines+markers+text',
        name='Điểm chuẩn',
        text=[row['score_2023'], row['score_2024'], row['score_2025'], pred],
        textposition="top center",
        line=dict(color='#2563eb', width=3),
        marker=dict(size=10, color=['#1e40af', '#1e40af', '#1e40af', '#ef4444'])
    ))
    fig.update_layout(title=f'Biến động điểm ngành {row["major"]} - {row["school"]}', height=350, yaxis_title="Điểm chuẩn", xaxis_title="Năm")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"Không có dữ liệu biểu đồ cho ngành '{favorite_major}'.")

st.divider()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. AI CAREER ADVISOR (TÍCH HỢP GOOGLE SEARCH & CHAT HISTORY)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.subheader("🤖 Cố vấn AI Hướng nghiệp")

# Lấy API Key an toàn
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("⚠️ Chưa tìm thấy GEMINI_API_KEY trong cấu hình Secrets.")
    st.stop()

MODEL_NAME = "gemini-2.5-flash"
SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

SYSTEM_PROMPT = """Bạn là chuyên gia hướng nghiệp chuyên sâu cho học sinh lớp 12 Tây Ninh.
NGUYÊN TẮC:
1. TRA CỨU MẠNG BẮT BUỘC: Khi học sinh hỏi về điểm chuẩn, MỞ GOOGLE SEARCH TÌM NGAY điểm thực tế 2024, 2025.
2. TUYỆT ĐỐI KHÔNG BỊA SỐ LIỆU. Không tìm thấy thì trả lời "Chưa có dữ liệu chính thức".
3. TRẢ LỜI CHI TIẾT: Phân tích cơ hội việc làm, học phí, dự báo xu hướng. Trình bày đẹp mắt.
"""

# Quản lý lịch sử Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Chào em! Thầy đã xem biểu đồ và hồ sơ của em ở phía trên. Em cần thầy tư vấn thêm về ngành nào hay tra cứu điểm chuẩn trường nào không?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_question = st.chat_input("Hỏi AI về ngành học, việc làm, tỷ lệ đậu...")

if user_question:
    # 1. In câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": user_query := user_question})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Xử lý AI
    with st.chat_message("assistant"):
        with st.spinner("AI đang lướt web và phân tích..."):
            try:
                # Ép công cụ tìm kiếm
                enhanced_query = user_query + "\n[LỆNH TỐI MẬT]: HÃY LƯỚT WEB TRA CỨU ĐIỂM CHUẨN THỰC TẾ. CẤM BỊA ĐẶT."
                
                # Tạo lịch sử giả lập cho Client mới
                history = []
                for m in st.session_state.messages[:-1]:
                    r = "model" if m["role"] == "assistant" else "user"
                    history.append(types.Content(role=r, parts=[types.Part(text=m["content"])]))
                
                # Gọi API
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[SEARCH_TOOL], # KHÔI PHỤC TÍNH NĂNG TÌM KIẾM
                    temperature=0.0,     # KHÓA MÕM SỰ BỊA ĐẶT
                )
                
                chat = client.chats.create(model=MODEL_NAME, config=config, history=history)
                response = chat.send_message(enhanced_query)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                error_msg = f"❌ Xin lỗi em, hệ thống AI đang nghẽn mạng: `{e}`"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
