import streamlit as st

# Cấu hình trang ứng dụng
st.set_page_config(
    page_title="Tính Lãi Tiết Kiệm Pro",
    page_icon="💰",
    layout="centered"
)

# Tiêu đề ứng dụng
st.title("💰 Ứng Dụng Tính Lãi Gửi Tiết Kiệm")
st.write("Ứng dụng giúp bạn dễ dàng tính toán và so sánh lãi đơn, lãi kép theo các hình thức nhận lãi khác nhau.")

st.markdown("---")

# --- PHẦN NHẬP DỮ LIỆU TỪ NƯỜI DÙNG ---
st.subheader("📋 Nhập thông tin khoản gửi")

# Bố trí các ô nhập liệu bằng cột cho gọn đẹp
col1, col2 = st.columns(2)

with col1:
    so_tien_goc = st.number_input(
        "Số tiền gửi gốc (VNĐ):", 
        min_value=0, 
        value=100000000, 
        step=1000000,
        format="%d"
    )
    
    ky_han_thang = st.number_input(
        "Kỳ hạn gửi (tháng):", 
        min_value=1, 
        value=12, 
        step=1
    )

with col2:
    lai_suat_nam = st.number_input(
        "Lãi suất gửi (% / năm):", 
        min_value=0.0, 
        max_value=100.0, 
        value=6.0, 
        step=0.1
    )
    
    hinh_thuc_lanh = st.selectbox(
        "Hình thức lãnh lãi:",
        options=["Lãnh lãi theo tháng", "Lãnh lãi theo quý", "Lãnh lãi cuối kỳ"]
    )

# Chọn phương thức tính lãi (Lãi đơn hoặc Lãi kép)
loai_lai = st.radio(
    "Chọn phương thức tính lãi:",
    options=["Lãi đơn (Lãi không nhập gốc)", "Lãi kép (Lãi nhập gốc định kỳ)"],
    horizontal=True
)

st.markdown("---")

# --- PHẦN XỬ LÝ LOGIC TÍNH TOÁN ---

# Quy đổi lãi suất năm về lãi suất tháng
lai_suat_thang = (lai_suat_nam / 100) / 12

# Xác định chu kỳ nhận lãi (số tháng của mỗi kỳ)
if hinh_thuc_lanh == "Lãnh lãi theo tháng":
    so_thang_chu_ky = 1
elif hinh_thuc_lanh == "Lãnh lãi theo quý":
    so_thang_chu_ky = 3
else:  # Cuối kỳ
    so_thang_chu_ky = ky_han_thang

# Tổng số lần nhận lãi trong suốt kỳ hạn
so_lan_nhan_lai = ky_han_thang // so_thang_chu_ky
thang_du = ky_han_thang % so_thang_chu_ky  # Phần tháng dư ra nếu kỳ hạn không chia hết cho chu kỳ

# Tính toán theo loại lãi suất
if "Lãi đơn" in loai_lai:
    # Lãi đơn: Tiền lãi mỗi chu kỳ tính trên vốn gốc ban đầu
    tien_lai_dinh_ky = so_tien_goc * lai_suat_thang * so_thang_chu_ky
    tong_tien_lai = tien_lai_dinh_ky * so_lan_nhan_lai
    
    # Cộng dồn tiền lãi của những tháng dư (nếu có)
    if thang_du > 0:
        tong_tien_lai += so_tien_goc * lai_suat_thang * thang_du
        
    tong_goc_va_lai = so_tien_goc + tong_tien_lai

else:
    # Lãi kép: Tiền lãi được cộng dồn vào gốc sau mỗi chu kỳ
    if hinh_thuc_lanh == "Lãnh lãi cuối kỳ":
        # Nếu lãnh cuối kỳ thì bản chất lãi đơn hay lãi kép trên cùng 1 kỳ hạn là như nhau
        tong_goc_va_lai = so_tien_goc * (1 + lai_suat_thang * ky_han_thang)
        tong_tien_lai = tong_goc_va_lai - so_tien_goc
        tien_lai_dinh_ky = tong_tien_lai  # Chỉ nhận 1 lần duy nhất
    else:
        # Lãi kép định kỳ (Theo tháng hoặc Theo quý)
        lai_suat_chu_ky = lai_suat_thang * so_thang_chu_ky
        tong_goc_va_lai = so_tien_goc * ((1 + lai_suat_chu_ky) ** so_lan_nhan_lai)
        
        # Nếu có tháng dư chưa đủ 1 chu kỳ, tính tiếp lãi đơn cho số tháng dư đó
        if thang_du > 0:
            tong_goc_va_lai = tong_goc_va_lai * (1 + lai_suat_thang * thang_du)
            
        tong_tien_lai = tong_goc_va_lai - so_tien_goc
        # Đối với lãi kép, tiền lãi tăng dần theo thời gian, tính trung bình định kỳ để tham khảo
        tien_lai_dinh_ky = tong_tien_lai / so_lan_nhan_lai if so_lan_nhan_lai > 0 else tong_tien_lai


# --- PHẦN HIỂN THỊ KẾT QUẢ ---
st.subheader("📊 Kết quả tính toán")

# Định dạng hiển thị tiền tệ VNĐ gọn gàng
def format_vnd(amount):
    return f"{amount:,.0f} VNĐ"

# Hiển thị số liệu dạng thẻ (Metrics)
col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    if hinh_thuc_lanh == "Lãnh lãi cuối kỳ":
        st.metric(label="Tiền lãi cuối kỳ", value=format_vnd(tien_lai_dinh_ky))
    else:
        label_dinh_ky = "Lãi mỗi tháng (Ước tính)" if hinh_thuc_lanh == "Lãnh lãi theo tháng" else "Lãi mỗi quý (Ước tính)"
        # Nếu là lãi kép, ghi chú rõ là trung bình vì số tiền nhận thực tế tăng dần
        if "Lãi kép" in loai_lai:
            label_dinh_ky += " [TB]"
        st.metric(label=label_dinh_ky, value=format_vnd(tien_lai_dinh_ky))

with col_res2:
    st.metric(label="Tổng tiền lãi nhận được", value=format_vnd(tong_tien_lai), delta=f"+{(tong_tien_lai/so_tien_goc)*100:.2f}%")

with col_res3:
    st.metric(label="Tổng số tiền (Gốc + Lãi)", value=format_vnd(tong_goc_va_lai))

# Bảng tóm tắt thông tin rõ ràng cho người dùng
st.markdown("### 📝 Tóm tắt khoản vay")
st.markdown(f"""
- **Số vốn gốc ban đầu:** {format_vnd(so_tien_goc)}
- **Kỳ hạn gửi:** {ky_han_thang} tháng (~ {ky_han_thang/12:.1f} năm)
- **Lãi suất áp dụng:** {lai_suat_nam}% / năm
- **Phương thức nhận lãi:** `{hinh_thuc_lanh}` áp dụng công thức `{loai_lai.split(' ')[0]}`.
""")

if thang_du > 0 and hinh_thuc_lanh != "Lãnh lãi cuối kỳ":
    st.warning(f"⚠️ Lưu ý: Kỳ hạn {ky_han_thang} tháng không chia hết cho chu kỳ gửi. Hệ thống đã tự động tính {so_lan_nhan_lai} chu kỳ trọn vẹn và cộng dồn lãi đơn cho {thang_du} tháng dư còn lại.")

st.markdown("---")
st.caption("Ứng dụng được phát triển trên nền tảng Streamlit. Kết quả mang tính chất tham khảo dựa trên công thức toán học chuẩn.")
