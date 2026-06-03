import streamlit as st
from streamlit_extras.let_it_rain import rain
from datetime import date, timedelta, datetime
from io import BytesIO
import time
from db import (load, get_conn, load_table, hard_delete, soft_delete, set_active,
                get_vitri_options, get_congty_options, get_monan_options, get_monan_options_for_vitri,
                get_nhanvien_options,
                insert_datmon, insert_congty, insert_vitri, insert_nhanvien, insert_monan,
                update_datmon, update_congty, update_vitri, update_nhanvien, update_monan,
                update_user_password, toggle_admin, get_sidebar,
                get_config, set_config, get_chu_ky_hom_nay, get_thucdon, insert_thucdon, delete_thucdon,
                get_thucdon_hom_nay, get_vitri_detail, check_duplicate_order,
                update_thucdon, get_thucdon_available, finish_thucdon_today)
from auth import create_session, validate_session, delete_session

st.set_page_config(page_title="Báo Cáo", page_icon="🍽️", layout="wide", initial_sidebar_state="auto")

st.markdown("""
<style>
    header { display: none !important; }
    .block-container { padding-top: 1rem !important; }
    [data-testid="collapsedControl"],
    [data-testid="stSidebarToggleButton"] { display: none !important; }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        padding: 1px 8px !important;
        font-size: 0.75rem !important;
        min-height: 0 !important;
        height: auto !important;
        line-height: 1.3 !important;
    }
    [data-testid="stSidebar"] hr { margin: 3px 0 !important; }

    /* Desktop: pin sidebar open */
    @media (min-width: 768px) {
        [data-testid="stSidebar"] {
            transform: none !important;
            visibility: visible !important;
            min-width: 220px !important;
            max-width: 220px !important;
        }
    }

    /* Mobile: hide sidebar, show toggle labels */
    #_mob_tog { display: none; }
    #_mob_open, #_mob_close {
        position: fixed; top: 8px; left: 8px; z-index: 999999;
        background: #EE1C25; color: white; border-radius: 6px;
        padding: 8px 14px; font-size: 20px; cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,.35); user-select: none;
        display: none;
    }
    @media (max-width: 767px) {
        #_mob_open { display: block; }
        [data-testid="stSidebar"] {
            display: none !important;
            min-width: unset !important;
            max-width: unset !important;
        }
    }
    body:has(#_mob_tog:checked) [data-testid="stSidebar"] {
        display: block !important;
        transform: none !important;
        visibility: visible !important;
    }
    body:has(#_mob_tog:checked) #_mob_open { display: none !important; }
    body:has(#_mob_tog:checked) #_mob_close { display: block !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def resolve_image(url: str) -> str | None:
    if not url or not isinstance(url, str):
        return None
    if any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return url
    try:
        import requests
        from bs4 import BeautifulSoup
        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("meta", property="og:image")
        return tag["content"] if tag else None
    except Exception:
        return None


def check_login(username, password):
    c = get_conn()
    cursor = c.cursor()
    cursor.execute(
        "SELECT \"TaiKhoan\", \"TenTaiKhoan\", \"Adm\" FROM dangnhap WHERE \"TaiKhoan\" = %s AND \"MatKhau\" = %s AND \"TrangThai\" = 'active'",
        (username, password)
    )
    row = cursor.fetchone()
    c.close()
    return row


@st.cache_data(ttl=3600)
def get_user_info(username):
    c = get_conn()
    cursor = c.cursor()
    cursor.execute("SELECT \"TenTaiKhoan\", \"Adm\" FROM dangnhap WHERE \"TaiKhoan\" = %s", (username,))
    row = cursor.fetchone()
    c.close()
    return row if row else (username, 0)


def register_user(username, display_name, password, ma_diadiem):
    from datetime import datetime
    c = get_conn()
    cursor = c.cursor()
    cursor.execute("SELECT \"TaiKhoan\" FROM dangnhap WHERE \"TaiKhoan\" = %s", (username,))
    if cursor.fetchone():
        c.close()
        return False, "Tài khoản đã tồn tại."
    now = datetime.now()
    cursor.execute(
        "INSERT INTO dangnhap (\"TaiKhoan\",\"TenTaiKhoan\",\"Adm\",\"MatKhau\",\"MaDiaDiem\",\"TrangThai\",\"NgayTao\",\"NguoiTao\",\"NgaySua\",\"NguoiSua\") VALUES (%s,%s,0,%s,%s,'active',%s,%s,%s,%s)",
        (username, display_name, password, ma_diadiem, now, username, now, username)
    )
    c.commit()
    c.close()
    return True, "Đăng ký thành công!"


# --- Restore session from token in URL ---
token = st.query_params.get("token")
if token and not st.session_state.get("logged_in"):
    username = validate_session(token)
    if username:
        st.session_state.logged_in = True
        st.session_state.username = username
        info = get_user_info(username)
        st.session_state.display_name = info[0]
        st.session_state.is_admin = bool(info[1])
        st.session_state.token = token

# --- Login screen ---
if not st.session_state.get("logged_in"):
    intended_page  = st.query_params.get("page", "datmon")
    intended_vitri = st.query_params.get("vitri", "")
    st.markdown("<div style='max-width:400px;margin:80px auto;'>", unsafe_allow_html=True)
    with st.form("login"):
        username = st.text_input("Tài Khoản")
        password = st.text_input("Mật Khẩu", type="password")
        submitted = st.form_submit_button("Đăng Nhập", use_container_width=True)
        if submitted:
            row = check_login(username, password)
            if row:
                token = create_session(username)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.display_name = row[1]
                st.session_state.is_admin = bool(row[2])
                st.session_state.token = token
                st.query_params["token"] = token
                st.query_params["page"] = intended_page if intended_page != "menu" else "datmon"
                if intended_vitri:
                    st.query_params["vitri"] = intended_vitri
                st.rerun()
            else:
                st.error("Tài khoản hoặc mật khẩu không đúng.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Shared state ---
current_page = st.query_params.get("page", "menu")
token = st.session_state.get("token", "")
is_admin = st.session_state.get("is_admin", False)
actor = st.session_state.get("username", "")
display_name = st.session_state.get("display_name", actor)



def inject_mobile_menu():
    st.markdown(
        '<input type="checkbox" id="_mob_tog">'
        '<label for="_mob_tog" id="_mob_open">☰</label>'
        '<label for="_mob_tog" id="_mob_close">✕</label>',
        unsafe_allow_html=True
    )


def top_header():
    inject_mobile_menu()
    if st.query_params.get("action") == "logout":
        delete_session(token)
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

    _, col_right = st.columns([5, 3])
    col_right.markdown(f"""
    <div style='display:flex; align-items:center; justify-content:flex-end; gap:12px; padding:4px 0;'>
        <a href='?token={token}&page={current_page}&action=logout'
           style='text-decoration:none; border:1px solid #ddd; border-radius:8px;
                  padding:6px 16px; color:#333; font-size:0.85rem; background:white;
                  font-weight:500; white-space:nowrap;'>
            Đăng Xuất
        </a>
        <div style='display:flex; align-items:center; gap:10px;'>
            <div style='background:linear-gradient(135deg,#EE1C25,#8B020A);
                        display:inline-flex; align-items:center; justify-content:center;
                        width:34px; height:34px; border-radius:8px;
                        box-shadow:0 2px 6px rgba(238,28,37,0.35);'>
                <span style='font-size:18px; line-height:1;'>🍽️</span>
            </div>
            <div>
                <div style='font-weight:800; font-size:0.9rem; color:#1a1a1a; line-height:1.2;'>Quản Lý Suất Ăn</div>
                <div style='font-size:0.75rem; color:#888;'>👤 {display_name}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_nav():
    nav = get_sidebar(actor)
    with st.sidebar:
        btn_idx = 0
        for section in nav:
            visible = [i for i in section["items"] if not i["admin"] or is_admin]
            if not visible:
                continue
            st.markdown(
                f"<div style='font-size:0.75rem;font-weight:700;color:#888;"
                f"letter-spacing:1px;padding:3px 4px 1px;'>{section['section']}</div>",
                unsafe_allow_html=True,
            )
            for item in visible:
                if st.button(item["label"], key=f"sb_{btn_idx}", use_container_width=True,
                             type="primary" if current_page == item["key"] else "secondary"):
                    st.query_params["page"] = item["key"]
                    st.query_params["token"] = token
                    st.rerun()
                btn_idx += 1
            st.divider()


if current_page == "menu":
    st.query_params["page"] = "datmon"
    st.query_params["token"] = token
    st.rerun()

# --- Đăng Ký page (admin only) ---
if current_page == "dangnhap":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h3>Đăng Ký Tài Khoản</h3>", unsafe_allow_html=True)
    st.markdown("<div style='max-width:480px;'>", unsafe_allow_html=True)
    locations = get_vitri_options()
    with st.form("register"):
        new_username = st.text_input("Tài Khoản")
        new_display  = st.text_input("Họ và Tên")
        new_location = st.selectbox("Địa Điểm", options=list(locations.keys()))
        new_password = st.text_input("Mật Khẩu", type="password")
        confirm_password = st.text_input("Xác Nhận Mật Khẩu", type="password")
        if st.form_submit_button("Đăng Ký", use_container_width=True):
            if not new_username or not new_display or not new_password:
                st.error("Vui lòng điền đầy đủ thông tin.")
            elif not new_username.isascii():
                st.error("Tài khoản chỉ được dùng chữ không dấu.")
            elif new_password != confirm_password:
                st.error("Mật khẩu không khớp.")
            else:
                ok, msg = register_user(new_username, new_display, new_password, locations[new_location])
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Quản Lý Tài Khoản page (admin only) ---
if current_page == "taikhoan":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>👥 Quản Lý Tài Khoản</h2>", unsafe_allow_html=True)

    raw_users = load_table("dangnhap", show_all=True)
    display_cols = {"TaiKhoan": "Tài Khoản", "TenTaiKhoan": "Họ và Tên",
                    "MaDiaDiem": "Địa Điểm", "Adm": "Admin", "TrangThai": "Trạng Thái"}
    df_display = raw_users[list(display_cols.keys())].rename(columns=display_cols)

    event = st.dataframe(df_display, use_container_width=True, hide_index=True,
                         on_select="rerun", selection_mode="single-row")

    selected_rows = event.selection.rows
    if not selected_rows:
        st.caption("Chọn một dòng để xem tùy chọn.")
    else:
        r = raw_users.iloc[selected_rows[0]]
        st.markdown(f"**Đang chỉnh sửa:** {r['TenTaiKhoan']} ({r['TaiKhoan']})")
        vitri_opts = get_vitri_options()

        tab_edit, tab_pwd, tab_status, tab_del = st.tabs(["✏️ Sửa thông tin", "🔑 Đặt lại mật khẩu", "🔄 Trạng thái", "🗑️ Xóa"])

        with tab_edit:
            vk = list(vitri_opts.keys())
            cv = next((k for k, v in vitri_opts.items() if v == r["MaDiaDiem"]), vk[0])
            with st.form("edit_taikhoan"):
                ten_e   = st.text_input("Họ và Tên", value=str(r["TenTaiKhoan"]))
                vitri_e = st.selectbox("Địa Điểm", vk, index=vk.index(cv))
                if st.form_submit_button("Lưu", use_container_width=True):
                    try:
                        update_nhanvien(r["TaiKhoan"], ten_e, vitri_opts[vitri_e], actor)
                        st.success("Đã cập nhật!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

        with tab_pwd:
            with st.form("reset_pwd"):
                new_pwd     = st.text_input("Mật khẩu mới", type="password")
                confirm_pwd = st.text_input("Xác nhận", type="password")
                if st.form_submit_button("Đặt lại", use_container_width=True):
                    if not new_pwd:
                        st.error("Nhập mật khẩu mới.")
                    elif new_pwd != confirm_pwd:
                        st.error("Mật khẩu không khớp.")
                    else:
                        try:
                            update_user_password(r["TaiKhoan"], new_pwd, actor)
                            st.success("Đã đặt lại!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

        with tab_status:
            with st.form("status_tk"):
                b1, b2 = st.columns(2)
                do_inactive = b1.form_submit_button("🚫 Vô hiệu hóa", use_container_width=True)
                do_active   = b2.form_submit_button("✅ Kích hoạt", use_container_width=True)
                try:
                    if do_inactive:
                        soft_delete("dangnhap", "TaiKhoan", r["TaiKhoan"], actor)
                        st.success("Đã vô hiệu hóa!")
                        st.rerun()
                    elif do_active:
                        set_active("dangnhap", "TaiKhoan", r["TaiKhoan"], actor)
                        st.success("Đã kích hoạt!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        with tab_del:
            st.warning(f"Bạn có chắc muốn xóa hẳn tài khoản **{r['TaiKhoan']}**? Hành động này không thể hoàn tác.")
            with st.form("del_tk"):
                if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                    try:
                        hard_delete("dangnhap", "TaiKhoan", r["TaiKhoan"])
                        st.success("Đã xóa!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

    st.stop()

# --- Thêm Công Ty page (admin only) ---
if current_page == "themcongty":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>➕ Thêm Công Ty</h2>", unsafe_allow_html=True)
    st.markdown("<div style='max-width:480px;'>", unsafe_allow_html=True)
    with st.form("them_congty"):
        ma      = st.text_input("Mã Công Ty")
        ten     = st.text_input("Tên Công Ty")
        dia_chi = st.text_input("Địa Chỉ")
        if st.form_submit_button("Thêm", use_container_width=True):
            if ma and ten:
                try:
                    insert_congty(ma, ten, dia_chi, "active", actor)
                    st.success("Đã thêm!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
            else:
                st.error("Vui lòng điền Mã và Tên công ty.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Quản Lý Công Ty page (admin only) ---
if current_page == "qlcongty":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>🏢 Quản Lý Công Ty</h2>", unsafe_allow_html=True)

    show_all_ct = st.toggle("Hiện tất cả (kể cả inactive)", key="show_all_qlcongty")
    raw_ct = load_table("congty", show_all=show_all_ct)
    display_cols_ct = {"MaCongTy": "Mã Công Ty", "TenCongTy": "Tên Công Ty",
                       "DiaChi": "Địa Chỉ", "TrangThai": "Trạng Thái",
                       "NgayTao": "Ngày Tạo", "NguoiTao": "Người Tạo",
                       "NgaySua": "Ngày Sửa", "NguoiSua": "Người Sửa"}
    df_ct = raw_ct[list(display_cols_ct.keys())].rename(columns=display_cols_ct)

    event_ct = st.dataframe(df_ct, use_container_width=True, hide_index=True,
                            on_select="rerun", selection_mode="single-row")

    buf_ct = BytesIO()
    raw_ct.to_excel(buf_ct, index=False)
    st.download_button("⬇️ Xuất Excel", buf_ct.getvalue(), file_name="congty.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    selected_ct = event_ct.selection.rows
    if not selected_ct:
        st.caption("Chọn một dòng để chỉnh sửa.")
    else:
        r = raw_ct.iloc[selected_ct[0]]
        st.markdown(f"**Đang chỉnh sửa:** {r['TenCongTy']} ({r['MaCongTy']})")

        tab_edit, tab_status, tab_del = st.tabs(["✏️ Sửa thông tin", "🔄 Trạng thái", "🗑️ Xóa"])

        with tab_edit:
            with st.form("ql_edit_congty"):
                e1, e2 = st.columns(2)
                ten_e     = e1.text_input("Tên Công Ty", value=str(r["TenCongTy"]))
                dia_chi_e = e2.text_input("Địa Chỉ", value=str(r["DiaChi"]) if r["DiaChi"] else "")
                if st.form_submit_button("Lưu", use_container_width=True):
                    try:
                        update_congty(r["MaCongTy"], ten_e, dia_chi_e, actor)
                        st.success("Đã cập nhật!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

        with tab_status:
            with st.form("ql_status_congty"):
                b1, b2 = st.columns(2)
                do_inactive = b1.form_submit_button("🚫 Vô hiệu hóa", use_container_width=True)
                do_active   = b2.form_submit_button("✅ Kích hoạt", use_container_width=True)
                try:
                    if do_inactive:
                        soft_delete("congty", "MaCongTy", r["MaCongTy"], actor)
                        st.success("Đã vô hiệu hóa!")
                        st.rerun()
                    elif do_active:
                        set_active("congty", "MaCongTy", r["MaCongTy"], actor)
                        st.success("Đã kích hoạt!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        with tab_del:
            st.warning(f"Bạn có chắc muốn xóa hẳn **{r['TenCongTy']}**? Hành động này không thể hoàn tác.")
            with st.form("ql_del_congty"):
                if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                    try:
                        hard_delete("congty", "MaCongTy", r["MaCongTy"])
                        st.success("Đã xóa!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
    st.stop()


# --- Thực Đơn Hôm Nay page ---
if current_page == "thucdon":
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 4px 0;'>📋 Thực Đơn Hôm Nay</h2>", unsafe_allow_html=True)
    df_hom_nay, chu_ky = get_thucdon_hom_nay()
    st.caption(f"{date.today().strftime('%d/%m/%Y')} — Ngày {chu_ky} trong chu kỳ 2 tuần")
    if df_hom_nay.empty:
        st.info("Chưa có thực đơn cho hôm nay.")
        st.stop()
    # Pre-warm image cache in parallel so the display loop is instant
    _img_urls = df_hom_nay["HinhAnh"].dropna().unique().tolist()
    if _img_urls:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=8) as _ex:
            list(_ex.map(resolve_image, _img_urls))
    locations = df_hom_nay["TenViTri"].unique().tolist()
    loc_sel = st.selectbox("Địa điểm", ["Tất cả"] + locations, label_visibility="collapsed")
    if loc_sel != "Tất cả":
        df_hom_nay = df_hom_nay[df_hom_nay["TenViTri"] == loc_sel]
        locations = [loc_sel]
    bua_order_list = ["Sáng", "Trưa", "Chiều"]
    for loc in locations:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#EE1C25,#b01018);color:white;
                    padding:12px 18px;border-radius:10px;margin:20px 0 14px 0;
                    display:flex;align-items:center;gap:10px;'>
            <span style='font-size:1.3rem;'>📍</span>
            <span style='font-size:1.1rem;font-weight:700;'>{loc}</span>
        </div>""", unsafe_allow_html=True)
        loc_df = df_hom_nay[df_hom_nay["TenViTri"] == loc]
        buas = [b for b in bua_order_list if b in loc_df["BuaAn"].values]
        cols = st.columns(len(buas))
        for i, bua in enumerate(buas):
            bua_df = loc_df[loc_df["BuaAn"] == bua]
            with cols[i]:
                for _, row in bua_df.iterrows():
                    don_gia_str = f"{int(row['DonGia']):,}".replace(",", ".")
                    img_url = resolve_image(row.get("HinhAnh"))
                    img_html = (
                        f'<img src="{img_url}" style="width:100%;height:170px;'
                        f'object-fit:cover;border-radius:10px 10px 0 0;display:block;">'
                        if img_url else
                        '<div style="width:100%;height:100px;background:#f5f5f5;'
                        'border-radius:10px 10px 0 0;display:flex;align-items:center;'
                        'justify-content:center;font-size:2rem;">🍽️</div>'
                    )
                    st.markdown(f"""
                    <div style='border:1px solid #eee;border-radius:10px;overflow:hidden;
                                box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:10px;'>
                        {img_html}
                        <div style='padding:12px 14px;'>
                            <div style='font-size:0.68rem;font-weight:700;color:#EE1C25;
                                        text-transform:uppercase;letter-spacing:1.2px;
                                        margin-bottom:5px;'>Bữa {bua}</div>
                            <div style='font-weight:700;font-size:1rem;color:#1a1a1a;
                                        margin-bottom:8px;line-height:1.3;'>{row['TenMonAn']}</div>
                            <span style='background:#EE1C25;color:white;padding:3px 12px;
                                         border-radius:20px;font-size:0.82rem;font-weight:600;'>
                                {don_gia_str} ₫
                            </span>
                        </div>
                    </div>""", unsafe_allow_html=True)
        st.markdown("<div style='margin:8px 0 4px;border-top:1px solid #eee;'></div>",
                    unsafe_allow_html=True)
    st.stop()

# --- Đặt Món (order) page ---
if current_page == "order":
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 4px 0;'>🛒 Đặt Món</h2>", unsafe_allow_html=True)

    ma_vitri = st.query_params.get("vitri", "")
    if not ma_vitri:
        vitri_opts = get_vitri_options()
        with st.form("pick_vitri"):
            vitri_sel = st.selectbox("Chọn căng tin", list(vitri_opts.keys()))
            if st.form_submit_button("Tiếp tục", use_container_width=True):
                st.query_params["vitri"] = vitri_opts[vitri_sel]
                st.rerun()
        st.stop()

    vitri_info = get_vitri_detail(ma_vitri)
    if not vitri_info:
        st.error("Địa điểm không hợp lệ.")
        st.stop()

    ten_vitri, ma_congty, *_ = vitri_info

    col_info, col_back = st.columns([5, 1])
    col_info.markdown(f"**{ten_vitri}** · {date.today().strftime('%d/%m/%Y')}")
    if col_back.button("↩ Quay lại", use_container_width=True):
        del st.query_params["vitri"]
        st.rerun()

    chu_ky = get_chu_ky_hom_nay()
    df_avail = get_thucdon_available(ma_vitri, chu_ky)

    # Only show meals whose start time has already passed (NULL = always available)
    now_time = datetime.now().time()
    if not df_avail.empty:
        df_avail = df_avail[df_avail["ThoiGianBatDau"].apply(
            lambda t: t is None or t <= now_time
        )].reset_index(drop=True)

    if df_avail.empty:
        st.info("Chưa có bữa ăn nào bắt đầu phục vụ.")
        st.stop()

    # Track which BuaAn the employee already ordered today
    already_ordered = {
        bua for bua in ["Sáng", "Trưa", "Chiều"]
        if check_duplicate_order(actor, date.today(), bua, ma_vitri)
    }
    if already_ordered:
        st.caption("Đã đặt: " + ", ".join(
            f"Bữa {b}" for b in ["Sáng", "Trưa", "Chiều"] if b in already_ordered
        ))

    bua_order = ["Sáng", "Trưa", "Chiều"]
    available_buas = [
        b for b in bua_order
        if b in df_avail["BuaAn"].values and b not in already_ordered
    ]

    if not available_buas:
        st.success("Bạn đã đặt tất cả các bữa ăn có sẵn hôm nay.")
        st.stop()

    for bua_an in available_buas:
        bua_df = df_avail[df_avail["BuaAn"] == bua_an]
        st.markdown(f"**Bữa {bua_an}**")
        price_lookup = dict(zip(bua_df["MaMonAn"], bua_df["DonGia"]))
        menu_options = {
            f"{r['TenMonAn']}  —  {int(r['DonGia']):,}".replace(",", "."): r["MaMonAn"]
            for _, r in bua_df.iterrows()
        }
        with st.form(f"order_form_{bua_an}"):
            sel_label = st.radio("Chọn món:", list(menu_options.keys()))
            if st.form_submit_button(f"✅ Đặt Bữa {bua_an}", use_container_width=True):
                ma_monan = menu_options[sel_label]
                don_gia = int(price_lookup[ma_monan])
                try:
                    insert_datmon(date.today(), ma_vitri, ma_congty, ma_monan, actor, 1, don_gia, actor, bua_an)
                    st.success(f"Đặt món thành công! **{sel_label.split('  —  ')[0]}** · Bữa {bua_an}")
                    st.balloons()
                except Exception as e:
                    st.error(f"Lỗi: {e}")
    st.stop()

# --- Quản Lý Thực Đơn page (admin only) ---
if current_page == "qlthucdon":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>📅 Quản Lý Thực Đơn</h2>", unsafe_allow_html=True)

    ref_str = get_config('ngay_bat_dau_chu_ky') or str(date.today())
    ref_date = date.fromisoformat(ref_str.strip())
    today_cycle = get_chu_ky_hom_nay()

    # Filters
    day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]
    day_labels = [
        f"{(ref_date + timedelta(days=i-1)).strftime('%d/%m')} ({day_names[(ref_date + timedelta(days=i-1)).weekday()]})"
        for i in range(1, 15)
    ]

    vitri_opts = get_vitri_options()
    col1, col2, col3 = st.columns(3)
    vitri_sel  = col1.selectbox("Địa Điểm", list(vitri_opts.keys()))
    chu_ky_sel = col2.selectbox("Ngày Chu Kỳ", day_labels, index=today_cycle - 1)

    ma_vitri = vitri_opts[vitri_sel]

    # Only show meals the location actually serves
    _c = get_conn(); _cur = _c.cursor()
    _cur.execute("SELECT \"BuaSang\", \"BuaTrua\", \"BuaChieu\" FROM vitri WHERE \"MaViTri\" = %s", (ma_vitri,))
    _vt = _cur.fetchone(); _c.close()
    bua_options = []
    if _vt:
        if _vt[0]: bua_options.append("Sáng")
        if _vt[1]: bua_options.append("Trưa")
        if _vt[2]: bua_options.append("Chiều")
    if not bua_options:
        st.warning("Địa điểm này chưa được cấu hình bữa ăn.")
        st.stop()
    bua_an_sel = col3.selectbox("Bữa Ăn", bua_options)
    chu_ky_ngay = day_labels.index(chu_ky_sel) + 1

    monan_opts, _ = get_monan_options_for_vitri(ma_vitri)

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm món"])

    with tab_list:
        show_all_td = st.toggle("Hiện tất cả (kể cả inactive)", key="show_all_qlthucdon")
        df_slot = get_thucdon(ma_vitri, chu_ky_ngay, bua_an_sel, show_all=show_all_td)
        all_codes = set(df_slot["MaMonAn"].tolist()) if not df_slot.empty else set()

        st.markdown(f"**{vitri_sel} · {chu_ky_sel} · Bữa {bua_an_sel}** — {len(df_slot)} món")

        if df_slot.empty:
            st.caption("Chưa có món nào trong khung giờ này.")
        else:
            disp_cols = {"TenMonAn": "Tên Món Ăn", "DonGia": "Đơn Giá",
                         "ThoiGianBatDau": "Giờ Bắt Đầu", "SoSuatDuKien": "Số Suất"}
            if show_all_td:
                disp_cols["TrangThai"] = "Trạng Thái"
            disp = df_slot[list(disp_cols.keys())].rename(columns=disp_cols)
            disp["Đơn Giá"] = disp["Đơn Giá"].apply(lambda x: f"{int(x):,}".replace(",", ".") if x is not None else x)
            event_td = st.dataframe(disp, use_container_width=True, hide_index=True,
                                    on_select="rerun", selection_mode="single-row")
            sel_td = event_td.selection.rows
            if sel_td:
                row_td = df_slot.iloc[sel_td[0]]
                st.markdown(f"**Đang chỉnh sửa:** {row_td['TenMonAn']}")

                tab_edit, tab_status, tab_del = st.tabs(["✏️ Sửa món", "🔄 Trạng thái", "🗑️ Xóa"])

                with tab_edit:
                    other_codes = all_codes - {row_td["MaMonAn"]}
                    available_edit = {k: v for k, v in monan_opts.items() if v not in other_codes}
                    cur_label = next((k for k, v in monan_opts.items() if v == row_td["MaMonAn"]), None)
                    edit_keys = list(available_edit.keys())
                    cur_idx = edit_keys.index(cur_label) if cur_label in edit_keys else 0
                    _ts = str(row_td.get("ThoiGianBatDau", "") or "")
                    _cur_time = datetime.strptime(_ts, "%H:%M").time() if _ts else None
                    try:
                        _ss_val = int(row_td["SoSuatDuKien"])
                    except (TypeError, ValueError):
                        _ss_val = 0
                    with st.form("edit_thucdon"):
                        sel_edit = st.selectbox("Món ăn", edit_keys, index=cur_idx)
                        tc1, tc2 = st.columns(2)
                        tgbd_e = tc1.time_input("Giờ Bắt Đầu", value=_cur_time)
                        so_suat_e = tc2.number_input("Số Suất Dự Kiến", min_value=0, step=1, value=_ss_val)
                        if st.form_submit_button("Lưu", use_container_width=True):
                            try:
                                update_thucdon(int(row_td["Id"]), available_edit[sel_edit], actor,
                                               tgbd_e, int(so_suat_e) if so_suat_e else None)
                                st.success("Đã cập nhật!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Lỗi: {e}")

                with tab_status:
                    with st.form("status_thucdon"):
                        b1, b2, b3 = st.columns(3)
                        do_done     = b1.form_submit_button("🏁 Kết thúc hôm nay", use_container_width=True)
                        do_inactive = b2.form_submit_button("🚫 Vô hiệu hóa", use_container_width=True)
                        do_active   = b3.form_submit_button("✅ Kích hoạt", use_container_width=True)
                        try:
                            if do_done:
                                finish_thucdon_today(ma_vitri, row_td["MaMonAn"], actor)
                                st.success("Đã kết thúc phục vụ hôm nay!")
                                st.rerun()
                            elif do_inactive:
                                soft_delete("thucdon", "Id", int(row_td["Id"]), actor)
                                st.success("Đã vô hiệu hóa!")
                                st.rerun()
                            elif do_active:
                                set_active("thucdon", "Id", int(row_td["Id"]), actor)
                                st.success("Đã kích hoạt!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

                with tab_del:
                    st.warning(f"Xóa hẳn **{row_td['TenMonAn']}** khỏi thực đơn? Hành động này không thể hoàn tác.")
                    with st.form("del_thucdon"):
                        if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                            try:
                                delete_thucdon(int(row_td["Id"]))
                                st.success("Đã xóa!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Lỗi: {e}")

    with tab_add:
        df_slot_add = get_thucdon(ma_vitri, chu_ky_ngay, bua_an_sel)
        all_codes_add = set(df_slot_add["MaMonAn"].tolist()) if not df_slot_add.empty else set()
        active_codes = set(df_slot_add[df_slot_add["TrangThai"] == "active"]["MaMonAn"].tolist()) if not df_slot_add.empty else set()
        MAX_CHOICES = 3
        if len(active_codes) >= MAX_CHOICES:
            st.caption(f"✅ Đã có {len(active_codes)} món cho khung giờ này (tối đa {MAX_CHOICES}). Chuyển sang tab Danh sách để chỉnh sửa.")
        else:
            available = {k: v for k, v in monan_opts.items() if v not in all_codes_add}
            if available:
                with st.form("add_thucdon"):
                    sel_add = st.selectbox("Thêm món vào thực đơn", list(available.keys()))
                    ac1, ac2 = st.columns(2)
                    tgbd_add = ac1.time_input("Giờ Bắt Đầu", value=None)
                    so_suat_add = ac2.number_input("Số Suất Dự Kiến", min_value=0, step=1, value=0)
                    if st.form_submit_button("➕ Thêm", use_container_width=True):
                        try:
                            insert_thucdon(ma_vitri, chu_ky_ngay, bua_an_sel, available[sel_add], actor,
                                           tgbd_add, int(so_suat_add) if so_suat_add else None)
                            st.success("Đã thêm!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
            else:
                st.caption("Không còn món ăn khả dụng cho khung giờ này.")
    st.stop()

# --- Thêm Món Ăn page (admin only) ---
if current_page == "themmonan":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>➕ Thêm Món Ăn</h2>", unsafe_allow_html=True)
    st.markdown("<div style='max-width:480px;'>", unsafe_allow_html=True)
    with st.form("them_monan"):
        ma       = st.text_input("Mã Món Ăn")
        ten      = st.text_input("Tên Món Ăn")
        don_gia  = st.number_input("Đơn Giá", min_value=0, step=1000)
        hinh_anh = st.text_input("Link Hình Ảnh (URL)")
        if st.form_submit_button("Thêm", use_container_width=True):
            if ma and ten:
                try:
                    insert_monan(ma, ten, don_gia, "active", actor, resolve_image(hinh_anh) or hinh_anh)
                    st.success("Đã thêm!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
            else:
                st.error("Vui lòng điền Mã và Tên món ăn.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Quản Lý Món Ăn page (admin only) ---
if current_page == "qlmonan":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>🍱 Quản Lý Món Ăn</h2>", unsafe_allow_html=True)

    show_all_mn = st.toggle("Hiện tất cả (kể cả inactive)", key="show_all_qlmonan")
    raw_mn = load_table("monan", show_all=show_all_mn)
    display_cols_mn = {"MaMonAn": "Mã Món Ăn", "TenMonAn": "Tên Món Ăn",
                       "DonGia": "Đơn Giá", "TrangThai": "Trạng Thái",
                       "NgayTao": "Ngày Tạo", "NguoiTao": "Người Tạo",
                       "NgaySua": "Ngày Sửa", "NguoiSua": "Người Sửa"}
    df_mn = raw_mn[list(display_cols_mn.keys())].rename(columns=display_cols_mn)
    df_mn["Đơn Giá"] = df_mn["Đơn Giá"].apply(lambda x: f"{int(x):,}".replace(",", ".") if x is not None else x)

    event_mn = st.dataframe(df_mn, use_container_width=True, hide_index=True,
                            on_select="rerun", selection_mode="single-row")

    buf_mn = BytesIO()
    raw_mn.to_excel(buf_mn, index=False)
    st.download_button("⬇️ Xuất Excel", buf_mn.getvalue(), file_name="monan.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    selected_mn = event_mn.selection.rows
    if not selected_mn:
        st.caption("Chọn một dòng để chỉnh sửa.")
    else:
        r = raw_mn.iloc[selected_mn[0]]
        st.markdown(f"**Đang chỉnh sửa:** {r['TenMonAn']} ({r['MaMonAn']})")

        tab_edit, tab_status, tab_del = st.tabs(["✏️ Sửa thông tin", "🔄 Trạng thái", "🗑️ Xóa"])

        with tab_edit:
            with st.form("ql_edit_monan"):
                e1, e2 = st.columns(2)
                ten_e     = e1.text_input("Tên Món Ăn", value=str(r["TenMonAn"]))
                don_gia_e = e2.number_input("Đơn Giá", min_value=0, step=1000, value=int(r["DonGia"]))
                hinh_anh_e = st.text_input("Link Hình Ảnh (URL)", value=str(r["HinhAnh"]) if r["HinhAnh"] else "")
                img_preview = resolve_image(hinh_anh_e)
                if img_preview:
                    st.image(img_preview, width=160)
                if st.form_submit_button("Lưu", use_container_width=True):
                    try:
                        update_monan(r["MaMonAn"], ten_e, don_gia_e, actor, resolve_image(hinh_anh_e) or hinh_anh_e)
                        st.success("Đã cập nhật!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

        with tab_status:
            with st.form("ql_status_monan"):
                b1, b2 = st.columns(2)
                do_inactive = b1.form_submit_button("🚫 Vô hiệu hóa", use_container_width=True)
                do_active   = b2.form_submit_button("✅ Kích hoạt", use_container_width=True)
                try:
                    if do_inactive:
                        soft_delete("monan", "MaMonAn", r["MaMonAn"], actor)
                        st.success("Đã vô hiệu hóa!")
                        st.rerun()
                    elif do_active:
                        set_active("monan", "MaMonAn", r["MaMonAn"], actor)
                        st.success("Đã kích hoạt!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        with tab_del:
            st.warning(f"Bạn có chắc muốn xóa hẳn **{r['TenMonAn']}**? Hành động này không thể hoàn tác.")
            with st.form("ql_del_monan"):
                if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                    try:
                        hard_delete("monan", "MaMonAn", r["MaMonAn"])
                        st.success("Đã xóa!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
    st.stop()

# --- Thêm Địa Điểm page (admin only) ---
if current_page == "themvitri":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>➕ Thêm Địa Điểm</h2>", unsafe_allow_html=True)
    st.markdown("<div style='max-width:480px;'>", unsafe_allow_html=True)
    congty_opts_tv = get_congty_options()
    with st.form("them_vitri"):
        ma      = st.text_input("Mã Địa Điểm")
        ten     = st.text_input("Tên Địa Điểm")
        congty_sel = st.selectbox("Công Ty", list(congty_opts_tv.keys()))
        if st.form_submit_button("Thêm", use_container_width=True):
            if ma and ten:
                try:
                    insert_vitri(ma, ten, congty_opts_tv[congty_sel], "active", actor)
                    st.success("Đã thêm!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
            else:
                st.error("Vui lòng điền Mã và Tên địa điểm.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- Quản Lý Địa Điểm page (admin only) ---
if current_page == "qlvitri":
    if not is_admin:
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>📍 Quản Lý Địa Điểm</h2>", unsafe_allow_html=True)

    show_all_vt = st.toggle("Hiện tất cả (kể cả inactive)", key="show_all_qlvitri")
    raw_vt = load_table("vitri", show_all=show_all_vt)
    display_cols_vt = {"MaViTri": "Mã Địa Điểm", "TenViTri": "Tên Địa Điểm",
                       "MaCongTy": "Mã Công Ty", "BuaSang": "Sáng", "BuaTrua": "Trưa",
                       "BuaChieu": "Chiều", "TrangThai": "Trạng Thái",
                       "NgayTao": "Ngày Tạo", "NguoiTao": "Người Tạo",
                       "NgaySua": "Ngày Sửa", "NguoiSua": "Người Sửa"}
    df_vt = raw_vt[list(display_cols_vt.keys())].rename(columns=display_cols_vt)
    for col in ["Sáng", "Trưa", "Chiều"]:
        df_vt[col] = df_vt[col].apply(lambda x: "✓" if x else "")

    event_vt = st.dataframe(df_vt, use_container_width=True, hide_index=True,
                            on_select="rerun", selection_mode="single-row")

    buf_vt = BytesIO()
    raw_vt.to_excel(buf_vt, index=False)
    st.download_button("⬇️ Xuất Excel", buf_vt.getvalue(), file_name="vitri.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    selected_vt = event_vt.selection.rows
    if not selected_vt:
        st.caption("Chọn một dòng để chỉnh sửa.")
    else:
        r = raw_vt.iloc[selected_vt[0]]
        st.markdown(f"**Đang chỉnh sửa:** {r['TenViTri']} ({r['MaViTri']})")

        tab_edit, tab_status, tab_del = st.tabs(["✏️ Sửa thông tin", "🔄 Trạng thái", "🗑️ Xóa"])

        with tab_edit:
            congty_opts_ql = get_congty_options()
            ck = list(congty_opts_ql.keys())
            cc = next((k for k, v in congty_opts_ql.items() if v == r["MaCongTy"]), ck[0])
            with st.form("ql_edit_vitri"):
                e1, e2 = st.columns(2)
                ten_e    = e1.text_input("Tên Địa Điểm", value=str(r["TenViTri"]))
                congty_e = e2.selectbox("Công Ty", ck, index=ck.index(cc))
                st.markdown("**Bữa ăn phục vụ**")
                b1, b2, b3 = st.columns(3)
                sang_e  = b1.checkbox("Sáng",  value=bool(r["BuaSang"]))
                trua_e  = b2.checkbox("Trưa",  value=bool(r["BuaTrua"]))
                chieu_e = b3.checkbox("Chiều", value=bool(r["BuaChieu"]))
                if st.form_submit_button("Lưu", use_container_width=True):
                    try:
                        update_vitri(r["MaViTri"], ten_e, congty_opts_ql[congty_e], sang_e, trua_e, chieu_e, actor)
                        st.success("Đã cập nhật!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

        with tab_status:
            with st.form("ql_status_vitri"):
                b1, b2 = st.columns(2)
                do_inactive = b1.form_submit_button("🚫 Vô hiệu hóa", use_container_width=True)
                do_active   = b2.form_submit_button("✅ Kích hoạt", use_container_width=True)
                try:
                    if do_inactive:
                        soft_delete("vitri", "MaViTri", r["MaViTri"], actor)
                        st.success("Đã vô hiệu hóa!")
                        st.rerun()
                    elif do_active:
                        set_active("vitri", "MaViTri", r["MaViTri"], actor)
                        st.success("Đã kích hoạt!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        with tab_del:
            st.warning(f"Bạn có chắc muốn xóa hẳn **{r['TenViTri']}**? Hành động này không thể hoàn tác.")
            with st.form("ql_del_vitri"):
                if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                    try:
                        hard_delete("vitri", "MaViTri", r["MaViTri"])
                        st.success("Đã xóa!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
    st.stop()

top_header()
sidebar_nav()
selected_key = current_page if current_page in ["datmon", "congty", "diadiem", "nhanvien"] else "datmon"

page_titles = {
    "datmon":   "🍱 Đặt Món",
    "congty":   "🏢 Công Ty",
    "diadiem":  "📍 Địa Điểm",
    "nhanvien": "👤 Nhân Viên",
}
st.markdown(f"<h2 style='margin:8px 0 16px 0;'>{page_titles[selected_key]}</h2>", unsafe_allow_html=True)

# --- Page content ---
col1, col2, col3 = st.columns([2, 2, 5])
from_date = col1.date_input("Từ ngày", value=date.today())
to_date = col2.date_input("Đến ngày", value=date.today())
show_all = col3.toggle("Hiện tất cả (kể cả inactive)", key=f"show_all_{selected_key}")

proc_map = {
    "datmon":   "bc_datmon",
    "congty":   "bc_congty",
    "diadiem":  "bc_diadiem",
    "nhanvien": "bc_nhanvien",
}

df = load(proc_map[selected_key], from_date, to_date, show_all=show_all)

def _cw(col, series):
    mx = series.astype(str).str.len().max()
    return min(max(int(mx if mx == mx else 0) * 9, len(col) * 9, 80), 400)

col_cfg = {col: st.column_config.Column(width=_cw(col, df[col])) for col in df.columns}
st.dataframe(df, use_container_width=True, hide_index=True, column_config=col_cfg)

buf = BytesIO()
df.to_excel(buf, index=False)
st.download_button("⬇️ Xuất Excel", buf.getvalue(),
                   file_name=f"{selected_key}_{from_date}_{to_date}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
