import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CẤU HÌNH TRANG & GIAO DIỆN MÀU SẮC CAO CẤP (CSS) ---
st.set_page_config(
    page_title="Công cụ Tính Lãi Tiết Kiệm",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nhúng CSS tùy biến để thay đổi giao diện theo phong cách Ngân hàng số năng động
st.markdown("""
<style>
    /* Nền ứng dụng và font chữ */
    .main {background-color: #F8FAFC;}
    html, body, [data-testid="stSidebar"] {font-family: 'Inter', system-ui, sans-serif;}
    
    /* Tùy chỉnh thanh điều hướng trái (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important; /* Màu xanh đen sang trọng */
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #E2E8F0 !important;
    }
    
    /* Tiêu đề chính */
    .main-title {
        color: #1E3A8A; 
        font-weight: 800; 
        font-size: 2.5rem;
        margin-bottom: 0.2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    .sub-title {color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;}

    /* Thẻ hiển thị chỉ số Metric tùy biến (Dashboard-style) */
    .metric-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 6px solid #059669; /* Vạch màu xanh lục bảo */
        margin-bottom: 1rem;
    }
    .metric-card.blue-variant {
        border-left: 6px solid #2563EB; /* Vạch màu xanh biển */
    }
    .metric-card.purple-variant {
        border-left: 6px solid #7C3AED; /* Vạch màu tím tài lộc */
    }
    .metric-label {font-size: 0.875rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em;}
    .metric-value {font-size: 1.75rem; font-weight: 700; color: #0F172A; margin-top: 0.25rem;}
    .metric-delta {font-size: 0.875rem; font-weight: 600; color: #059669; margin-top: 0.25rem;}

    /* Tùy chỉnh các Tab */
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {
        background-color: #E2E8F0;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
        color: #334155;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2563EB !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. TIÊU ĐỀ ỨNG DỤNG ---
st.markdown('<p class="main-title">💰 CÔNG CỤ TÍNH LÃI SUẤT TIẾT KIỆM</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Hệ thống phân tích dòng tiền, tối ưu hóa lợi nhuận tài chính cá nhân thông minh.</p>', unsafe_allow_html=True)

def chuyen_so_thanh_chu(so_tien):
    if so_tien >= 1000000000:
        return f"{so_tien / 1000000000:.2f} Tỷ đồng"
    elif so_tien >= 1000000:
        return f"{so_tien / 1000000:.1f} Triệu đồng"
    return f"{so_tien:,.0f} VNĐ"

# --- 3. THANH ĐIỀU HƯỚNG BÊN TRÁI (NHẬP LIỆU) ---
with st.sidebar:
    st.markdown("### 📊 THÔNG TIN KHOẢN GỬI")
    so_tien_goc = st.number_input(
        "Số tiền gửi gốc (VNĐ):", min_value=1000000, value=100000000, step=5000000, format="%d"
    )
    st.markdown(f"✍️ Bằng chữ: <span style='color:#F59E0B; font-weight:bold;'>{chuyen_so_thanh_chu(so_tien_goc)}</span>", unsafe_allow_html=True)
    
    ky_han_thang = st.number_input(
        "Kỳ hạn gửi (Tháng):", min_value=1, max_value=120, value=12, step=1
    )
    lai_suat_nam = st.number_input(
        "Lãi suất gửi (%/Năm):", min_value=0.0, max_value=20.0, value=6.0, step=0.05
    )
    hinh_thuc_lanh = st.selectbox(
        "Hình thức nhận lãi:", 
        options=["Nhận lãi định kỳ theo Tháng", "Nhận lãi định kỳ theo Quý", "Nhận lãi vào Cuối kỳ"]
    )
    
    if "Cuối kỳ" not in hinh_thuc_lanh:
        loai_lai = st.radio(
            "Phương thức tính lãi:", 
            options=["Lãi đơn (Rút tiền mặt định kỳ)", "Lãi kép (Lãi nhập gốc tích lũy)"]
        )
    else:
        loai_lai = st.radio(
            "Phương thức tính lãi:", 
            options=["Lãi đơn (Không nhập gốc)", "Lãi kép (Lãi nhập gốc cuối kỳ)"]
        )

# --- 4. XỬ LÝ LOGIC TÀI CHÍNH CHUẨN NGHIỆP VỤ ---
lai_suat_thang = (lai_suat_nam / 100) / 12

if "Tháng" in hinh_thuc_lanh:
    buoc_nhay = 1
elif "Quý" in hinh_thuc_lanh:
    buoc_nhay = 3
else:
    buoc_nhay = ky_han_thang

du_lieu_dong_tien = []
goc_tich_luy_kep = so_tien_goc
tong_lai_don_tich_luy = 0
tong_lai_kep_tich_luy = 0
lai_treo_chua_nhap_goc = 0

du_lieu_dong_tien.append({
    "Tháng": 0, "Vốn gốc (Lãi đơn)": so_tien_goc, "Tiền lãi tích lũy (Lãi đơn)": 0, "Tổng số tiền (Lãi đơn)": so_tien_goc,
    "Vốn gốc (Lãi kép)": so_tien_goc, "Tiền lãi tích lũy (Lãi kép)": 0, "Tổng số tiền (Lãi kép)": so_tien_goc, "Số tiền nhận định kỳ": 0
})

for thang in range(1, ky_han_thang + 1):
    # Lãi đơn
    lai_thang_nay_don = so_tien_goc * lai_suat_thang
    tong_lai_don_tich_luy += lai_thang_nay_don
    
    tien_rut_dinh_ky = 0
    if "Lãi đơn" in loai_lai and "Cuối kỳ" not in hinh_thuc_lanh:
        if thang % buoc_nhay == 0 or thang == ky_han_thang:
            thang_chua_tra = buoc_nhay if thang % buoc_nhay == 0 else (thang % buoc_nhay)
            tien_rut_dinh_ky = so_tien_goc * lai_suat_thang * thang_chua_tra

    # Lãi kép
    if "Cuối kỳ" in hinh_thuc_lanh:
        lai_thang_nay_kep = so_tien_goc * lai_suat_thang
        tong_lai_kep_tich_luy += lai_thang_nay_kep
        vong_goc_hien_tai_kep = so_tien_goc
    else:
        lai_thang_nay_kep = goc_tich_luy_kep * lai_suat_thang
        tong_lai_kep_tich_luy += lai_thang_nay_kep
        lai_treo_chua_nhap_goc += lai_thang_nay_kep
        vong_goc_hien_tai_kep = goc_tich_luy_kep
        
        if thang % buoc_nhay == 0 or thang == ky_han_thang:
            goc_tich_luy_kep += lai_treo_chua_nhap_goc
            lai_treo_chua_nhap_goc = 0

    du_lieu_dong_tien.append({
        "Tháng": thang,
        "Vốn gốc (Lãi đơn)": so_tien_goc,
        "Tiền lãi tích lũy (Lãi đơn)": tong_lai_don_tich_luy,
        "Tổng số tiền (Lãi đơn)": so_tien_goc + tong_lai_don_tich_luy,
        "Vốn gốc (Lãi kép)": vong_goc_hien_tai_kep,
        "Tiền lãi tích lũy (Lãi kép)": tong_lai_kep_tich_luy,
        "Tổng số tiền (Lãi kép)": so_tien_goc + tong_lai_kep_tich_luy,
        "Số tiền nhận định kỳ": tien_rut_dinh_ky if "Lãi đơn" in loai_lai else 0
    })

df_dong_tien = pd.DataFrame(du_lieu_dong_tien)
ket_qua_cuoi = df_dong_tien.iloc[-1]

if "Lãi đơn" in loai_lai:
    tong_lai_tra = ket_qua_cuoi["Tiền lãi tích lũy (Lãi đơn)"]
    tong_goc_lai = ket_qua_cuoi["Tổng số tiền (Lãi đơn)"]
    lai_dinh_ky_chuan = tong_lai_tra if "Cuối kỳ" in hinh_thuc_lanh else so_tien_goc * lai_suat_thang * buoc_nhay
else:
    tong_lai_tra = ket_qua_cuoi["Tiền lãi tích lũy (Lãi kép)"]
    tong_goc_lai = ket_qua_cuoi["Tổng số tiền (Lãi kép)"]
    lai_dinh_ky_chuan = 0

# --- 5. HIỂN THỊ KẾT QUẢ THEO PHONG CÁCH DASHBOARD ĐỔ BÓNG ---
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    label_text = "Lãi định kỳ" if "Cuối kỳ" not in hinh_thuc_lanh else "Lãi cuối kỳ"
    value_text = "0 VNĐ (Tự động nhập gốc)" if "Lãi kép" in loai_lai else f"{lai_dinh_ky_chuan:,.0f} VNĐ"
    st.markdown(f"""
    <div class="metric-card blue-variant">
        <div class="metric-label">💵 {label_text}</div>
        <div class="metric-value">{value_text}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📈 Tổng tiền lãi cả kỳ</div>
        <div class="metric-value" style="color: #059669;">{tong_lai_tra:,.0f} VNĐ</div>
        <div class="metric-delta">▲ Hiệu suất: +{(tong_lai_tra / so_tien_goc) * 100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card purple-variant">
        <div class="metric-label">💎 Tổng giá trị tất toán</div>
        <div class="metric-value" style="color: #7C3AED;">{tong_goc_lai:,.0f} VNĐ</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. TAB TRỰC QUAN HÓA DỮ LIỆU ---
tab_bieu_do, tab_lich_trinh = st.tabs(["📊 Biểu đồ tăng trưởng tài sản", "📋 Lịch trình dòng tiền chi tiết"])

with tab_bieu_do:
    st.subheader("So sánh xu hướng tích lũy: Lãi đơn vs Lãi kép")
    df_chart = df_dong_tien[["Tháng", "Tổng số tiền (Lãi đơn)", "Tổng số tiền (Lãi kép)"]].set_index("Tháng")
    df_chart.columns = ["Mô hình Lãi đơn", "Mô hình Lãi kép"]
    
    # Sử dụng line_chart của Streamlit (Tự động ăn theo theme màu rực rỡ)
    st.line_chart(df_chart, height=380)
    st.info("💡 Mẹo tài chính: Chu kỳ gửi càng dài kết hợp với phương thức Lãi kép sẽ tạo ra hiệu ứng kỳ quan thứ 8 - Tiền đẻ ra tiền với tốc độ vượt trội!")

with tab_lich_trinh:
    st.subheader("Bảng phân rã dòng tiền theo tiến độ chu kỳ")
    
    df_hien_thi = df_dong_tien[df_dong_tien["Tháng"] % buoc_nhay == 0].copy()
    if (ky_han_thang % buoc_nhay != 0) and (df_dong_tien.iloc[-1]["Tháng"] not in df_hien_thi["Tháng"].values):
        df_hien_thi = pd.concat([df_hien_thi, df_dong_tien.iloc[[-1]]])

    if "Lãi đơn" in loai_lai:
        df_view = df_hien_thi[["Tháng", "Vốn gốc (Lãi đơn)", "Tiền lãi tích lũy (Lãi đơn)", "Tổng số tiền (Lãi đơn)", "Số tiền nhận định kỳ"]].copy()
    else:
        df_view = df_hien_thi[["Tháng", "Vốn gốc (Lãi kép)", "Tiền lãi tích lũy (Lãi kép)", "Tổng số tiền (Lãi kép)", "Số tiền nhận định kỳ"]].copy()
        
    df_view.columns = ["Kỳ (Tháng)", "Tiền gốc gửi (VNĐ)", "Lãi tích lũy (VNĐ)", "Tổng giá trị tài sản (VNĐ)", "Tiền mặt thực nhận (VNĐ)"]
    
    # Hiển thị bảng dạng Interative đẹp mắt với các cột được highlight số
    st.dataframe(
        df_view.style.format({
            "Tiền gốc gửi (VNĐ)": "{:,.0f}",
            "Lãi tích lũy (VNĐ)": "{:,.0f}",
            "Tổng giá trị tài sản (VNĐ)": "{:,.0f}",
            "Tiền mặt thực nhận (VNĐ)": "{:,.0f}"
