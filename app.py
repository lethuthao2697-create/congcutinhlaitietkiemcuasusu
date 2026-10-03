import streamlit as st
import pandas as pd
import numpy as np

# Cấu hình trang tối giản, hiện đại
st.set_page_config(
    page_title="Cong cu Tinh Lai Tiet Kiem",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tối ưu giao diện bằng CSS (Ẩn menu thừa, bo góc các khối)
st.markdown("""
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    h1, h2, h3 {color: #1E3A8A; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;}
    div[data-testid="stMetricValue"] {font-size: 24px; font-weight: bold; color: #059669;}
    div[data-testid="stMetricLabel"] {font-size: 14px; color: #4B5563;}
    </style>
""", unsafe_allow_html=True)

# Tiêu đề chính chỉnh chu
st.title("CÔNG CỤ TÍNH TOÁN LÃI SUẤT TIẾT KIỆM")
st.write("Hệ thống hỗ trợ khách hàng lập kế hoạch tài chính và tối ưu hóa lợi nhuận từ khoản tiền gửi tích lũy.")
st.markdown("---")

# Hàm chuyển đổi số tiền thành chữ viết gọn để khách hàng dễ kiểm tra (Ví dụ: 100,000,000 -> 100 Triệu)
def chuyen_so_thanh_chu(so_tien):
    if so_tien >= 1000000000:
        return f"{so_tien / 1000000000:.2f} Tỷ đồng"
    elif so_tien >= 1000000:
        return f"{so_tien / 1000000:.1f} Triệu đồng"
    return f"{so_tien:,.0f} VNĐ"

# --- THANH ĐIỀU HƯỚNG BÊN TRÁI (NHẬP LIỆU) ---
with st.sidebar:
    st.subheader("THÔNG TIN KHOẢN GỬI")
    
    so_tien_goc = st.number_input(
        "Số tiền gửi (VNĐ):", 
        min_value=1000000, 
        value=100000000, 
        step=5000000,
        format="%d"
    )
    # Gợi ý bằng chữ ngay bên dưới ô nhập liệu giúp khách hàng không bị đếm nhầm chữ số 0
    st.caption(f"Số tiền bằng chữ: **{chuyen_so_thanh_chu(so_tien_goc)}**")
    
    ky_han_thang = st.number_input(
        "Kỳ hạn gửi (Tháng):", 
        min_value=1, 
        max_value=120, 
        value=12, 
        step=1
    )
    
    lai_suat_nam = st.number_input(
        "Lãi suất gửi (%/Năm):", 
        min_value=0.0, 
        max_value=20.0, 
        value=6.0, 
        step=0.05
    )
    
    hinh_thuc_lanh = st.selectbox(
        "Hình thức nhận lãi:",
        options=["Nhận lãi định kỳ theo Tháng", "Nhận lãi định kỳ theo Quý", "Nhận lãi vào Cuối kỳ"]
    )
    
    loai_lai = st.radio(
        "Phương thức tính lãi suất:",
        options=["Lãi đơn (Không nhập gốc)", "Lãi kép (Lãi nhập gốc)"]
    )

# --- PHẦN XỬ LÝ LOGIC VÀ LẬP LỊCH TRÌNH DÒNG TIỀN ---
lai_suat_thang = (lai_suat_nam / 100) / 12

# Xác định bước nhảy của chu kỳ nhận lãi (số tháng)
if "Tháng" in hinh_thuc_lanh:
    buoc_nhay = 1
    ten_chu_ky = "Tháng"
elif "Quý" in hinh_thuc_lanh:
    buoc_nhay = 3
    ten_chu_ky = "Quý"
else:
    buoc_nhay = ky_han_thang
    ten_chu_ky = "Cuối kỳ"

# Tính toán dòng tiền tăng trưởng qua từng tháng để vẽ biểu đồ và lập bảng
du_lieu_dong_tien = []
goc_tich_luy_don = so_tien_goc
goc_tich_luy_kep = so_tien_goc
tong_lai_don_tich_luy = 0
tong_lai_kep_tich_luy = 0

# Khởi tạo mốc ban đầu (Tháng 0)
du_lieu_dong_tien.append({
    "Tháng": 0,
    "Vốn gốc (Lãi đơn)": so_tien_goc,
    "Tiền lãi tích lũy (Lãi đơn)": 0,
    "Tổng số tiền (Lãi đơn)": so_tien_goc,
    "Vốn gốc (Lãi kép)": so_tien_goc,
    "Tiền lãi tích lũy (Lãi kép)": 0,
    "Tổng số tiền (Lãi kép)": so_tien_goc,
    "Số tiền nhận định kỳ": 0
})

for thang in range(1, ky_han_thang + 1):
    # 1. Tính toán cho Lãi Đơn
    lai_thang_nay_don = so_tien_goc * lai_suat_thang
    tong_lai_don_tich_luy += lai_thang_nay_don
    
    # 2. Tính toán cho Lãi Kép
    # Nếu chưa tới chu kỳ nhập gốc, gốc giữ nguyên, tiền lãi tạm tính trên gốc cũ
    if "Cuối kỳ" in hinh_thuc_lanh:
        # Lãi kép cuối kỳ bản chất giống lãi đơn trong suốt kỳ hạn, nhập gốc vào tháng cuối cùng
        if thang == ky_han_thang:
            tong_lai_kep_tich_luy = so_tien_goc * lai_suat_thang * ky_han_thang
            goc_tich_luy_kep = so_tien_goc + tong_lai_kep_tich_luy
        else:
            tong_lai_kep_tich_luy += so_tien_goc * lai_suat_thang
    else:
        # Nhập gốc định kỳ theo Tháng hoặc Quý
        lai_thang_nay_kep = goc_tich_luy_kep * lai_suat_thang
        tong_lai_kep_tich_luy += lai_thang_nay_kep
        if thang % buoc_nhay == 0:
            goc_tich_luy_kep = so_tien_goc + tong_lai_kep_tich_luy

    # Xác định số tiền khách hàng được rút ra thực tế tại mốc thời gian này
    tien_rut_dinh_ky = 0
    if thang % buoc_nhay == 0 or thang == ky_han_thang:
        if "Lãi đơn" in loai_lai:
            tien_rut_dinh_ky = so_tien_goc * lai_suat_thang * (buoc_nhay if thang % buoc_nhay == 0 else (thang % buoc_nhay))
        else:
            # Đối với lãi kép, nếu chọn nhận định kỳ tức là không nhập gốc (mâu thuẫn nghiệp vụ ngân hàng),
            # hệ thống hiển thị giá trị dòng tiền tương đương tăng trưởng.
            tien_rut_dinh_ky = (so_tien_goc + tong_lai_kep_tich_luy) - du_lieu_dong_tien[-1]["Tổng số tiền (Lãi kép)"]

    du_lieu_dong_tien.append({
        "Tháng": thang,
        "Vốn gốc (Lãi đơn)": so_tien_goc,
        "Tiền lãi tích lũy (Lãi đơn)": tong_lai_don_tich_luy,
        "Tổng số tiền (Lãi đơn)": so_tien_goc + tong_lai_don_tich_luy,
        "Vốn gốc (Lãi kép)": goc_tich_luy_kep if "Cuối kỳ" not in hinh_thuc_lanh else so_tien_goc,
        "Tiền lãi tích lũy (Lãi kép)": tong_lai_kep_tich_luy,
        "Tổng số tiền (Lãi kép)": so_tien_goc + tong_lai_kep_tich_luy,
        "Số tiền nhận định kỳ": tien_rut_dinh_ky if (thang % buoc_nhay == 0) else 0
    })

df_dong_tien = pd.DataFrame(du_lieu_dong_tien)

# Trích xuất kết quả cuối cùng dựa trên lựa chọn của người dùng
ket_qua_cuoi = df_dong_tien.iloc[-1]
if "Lãi đơn" in loai_lai:
    tong_lai_tra = ket_qua_cuoi["Tiền lãi tích lũy (Lãi đơn)"]
    tong_goc_lai = ket_qua_cuoi["Tổng số tiền (Lãi đơn)"]
    lai_dinh_ky_chuan = so_tien_goc * lai_suat_thang * buoc_nhay if "Cuối kỳ" not in hinh_thuc_lanh else tong_lai_tra
else:
    tong_lai_tra = ket_qua_cuoi["Tiền lãi tích lũy (Lãi kép)"]
    tong_goc_lai = ket_qua_cuoi["Tổng số tiền (Lãi kép)"]
    lai_dinh_ky_chuan = tong_lai_tra / (ky_han_thang // buoc_nhay) if "Cuối kỳ" not in hinh_thuc_lanh else tong_lai_tra

# --- PHẦN HIỂN THỊ KẾT QUẢ GIAO DIỆN CHÍNH ---
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.metric(
        label=f"Tiền lãi nhận định kỳ (Mỗi {buoc_nhay} tháng)" if "Cuối kỳ" not in hinh_thuc_lanh else "Tiền lãi nhận cuối kỳ", 
        value=f"{lai_dinh_ky_chuan:,.0f} VNĐ"
    )
with col_m2:
    st.metric(
        label="Tổng tiền lãi cả kỳ hạn", 
        value=f"{tong_lai_tra:,.0f} VNĐ",
        delta=f"Hiệu suất: +{(tong_lai_tra / so_tien_goc) * 100:.2f}%"
    )
with col_m3:
    st.metric(
        label="Tổng giá trị tất toán (Gốc + Lãi)", 
        value=f"{tong_goc_lai:,.0f} VNĐ"
    )

st.markdown("---")

# Tạo 2 Tab chức năng lớn: Biểu đồ tăng trưởng & Bảng lịch trình chi tiết
tab_bieu_do, tab_lich_trinh = st.tabs(["Biểu đồ tăng trưởng tài sản", "Lịch trình dòng tiền chi tiết"])

with tab_bieu_do:
    st.subheader("Xu hướng tăng trưởng: Lãi đơn vs Lãi kép")
    st.write("Biểu đồ thể hiện sự tích lũy tài sản của bạn qua thời gian (Đơn vị: VNĐ).")
    
    # Chuẩn bị dữ liệu vẽ biểu đồ gọn gàng
    df_chart = df_dong_tien[["Tháng", "Tổng số tiền (Lãi đơn)", "Tổng số tiền (Lãi kép)"]].set_index("Tháng")
    df_chart.columns = ["Mô hình Lãi đơn", "Mô hình Lãi kép"]
    
    st.line_chart(df_chart, height=350)
    st.caption("Mẹo tài chính: Khi kỳ hạn đủ dài, đường cong Lãi kép sẽ dốc lên nhanh hơn nhờ hiệu ứng lãi chồng lãi.")

with tab_lich_trinh:
    st.subheader("Bảng chi tiết dòng tiền qua các mốc thời gian")
    st.write("Khách hàng có thể theo dõi tiến độ tích lũy gốc và các mốc thời gian được rút tiền lãi.")
    
    # Lọc và tối ưu định dạng bảng hiển thị cho khách hàng dễ đọc
    df_hien_thi = df_dong_tien[df_dong_tien["Tháng"] % buoc_nhay == 0].copy() if "Cuối kỳ" not in hinh_thuc_lanh else df_dong_tien.iloc[[0, -1]].copy()
    
    if "Lãi đơn" in loai_lai:
        df_view = df_hien_thi[["Tháng", "Vốn gốc (Lãi đơn)", "Tiền lãi tích lũy (Lãi đơn)", "Tổng số tiền (Lãi đơn)", "Số tiền nhận định kỳ"]].copy()
    else:
        df_view = df_hien_thi[["Tháng", "Vốn gốc (Lãi kép)", "Tiền lãi tích lũy (Lãi kép)", "Tổng số tiền (Lãi kép)", "Số tiền nhận định kỳ"]].copy()
        
    df_view.columns = ["Kỳ (Tháng)", "Số tiền gốc (VNĐ)", "Lãi tích lũy (VNĐ)", "Tổng giá trị tài sản (VNĐ)", "Số tiền mặt được nhận (VNĐ)"]
    
    # Định dạng hiển thị dấu phẩy phân tách phần nghìn cho toàn bộ bảng
    st.dataframe(
        df_view.style.format({
            "Số tiền gốc (VNĐ)": "{:,.0f}",
            "Lãi tích lũy (VNĐ)": "{:,.0f}",
            "Tổng giá trị tài sản (VNĐ)": "{:,.0f}",
            "Số tiền mặt được nhận (VNĐ)": "{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
# Thông báo cảnh báo nghiệp vụ thông minh cho khách hàng nếu có tháng dư lẻ
thang_du = ky_han_thang % buoc_nhay
if thang_du > 0 and "Cuối kỳ" not in hinh_thuc_lanh:
    st.info(f"Thông báo hệ thống: Kỳ hạn bạn chọn ({ky_han_thang} tháng) có 1 phần dư lẻ là {thang_du} tháng so với chu kỳ lãnh lãi ({buoc_nhay} tháng). Hệ thống đã tự động kết chuyển phần lãi phát sinh của tháng dư này vào kỳ nhận cuối cùng để đảm bảo quyền lợi tối đa.")
