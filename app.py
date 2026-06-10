import streamlit as st
from streamlit_extras.let_it_rain import rain
from datetime import date, timedelta, datetime, time as _time, timezone
from io import BytesIO
import time
import pandas as pd
from db import (load, get_conn, load_table, hard_delete, soft_delete, set_active,
                get_vitri_options, get_congty_options, get_monan_options, get_monan_options_for_vitri,
                get_nhanvien_options,
                insert_datmon, insert_congty, insert_vitri, insert_nhanvien, insert_monan,
                update_datmon, update_congty, update_vitri, update_nhanvien, update_monan,
                update_user_password, toggle_admin, get_sidebar,
                get_config, set_config, upsert_config, get_chu_ky_hom_nay, get_thucdon, insert_thucdon, delete_thucdon,
                get_thucdon_hom_nay, get_vitri_detail,
                update_thucdon, get_thucdon_available, finish_thucdon_today,
                get_pending_order, confirm_pending_order, cancel_pending_order,
                get_phanquyen_grid, save_phanquyen, get_user_perm)
from auth import create_session, validate_session, delete_session

_VN_TZ = timezone(timedelta(hours=7))

import streamlit.components.v1 as _components
import os as _os
_qrscanner = _components.declare_component(
    "qrcode_scanner",
    path=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "qrscanner")
)

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
        st.session_state.phanquyen = {} if bool(info[1]) else get_user_perm(username)

# --- Login screen ---
if not st.session_state.get("logged_in"):
    intended_page  = st.query_params.get("page", "thucdon")
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
                st.session_state.phanquyen = {} if bool(row[2]) else get_user_perm(username)
                st.query_params["token"] = token
                st.query_params["page"] = intended_page if intended_page != "menu" else "thucdon"
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
phanquyen = st.session_state.get("phanquyen", {})


def _perm(page_key, field="access"):
    if is_admin:
        return True
    if page_key in ("thucdon", "order") and field == "access":
        return True
    if not phanquyen:
        return True
    return phanquyen.get(page_key, {}).get(field, False)



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
            _public = {"thucdon", "order"}
            _explicit = {k for k, v in phanquyen.items() if v.get("access")} if phanquyen else set()
            visible = [i for i in section["items"] if (i["key"] in _public or i["key"] in _explicit or not i["admin"] or is_admin) and _perm(i["key"])]
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

# --- Đăng Ký page (redirect to taikhoan) ---
if current_page == "dangnhap":
    st.query_params["page"] = "taikhoan"
    st.rerun()

# --- Quản Lý Tài Khoản page (admin only) ---
if current_page == "taikhoan":
    if not _perm("taikhoan"):
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
            if not _perm("taikhoan", "edit"):
                st.warning("Bạn không có quyền sửa.")
            else:
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
            if not _perm("taikhoan", "edit"):
                st.warning("Bạn không có quyền đặt lại mật khẩu.")
            else:
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
            if not _perm("taikhoan", "edit"):
                st.warning("Bạn không có quyền thay đổi trạng thái.")
            else:
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
            if not _perm("taikhoan", "delete"):
                st.warning("Bạn không có quyền xóa.")
            else:
                st.warning(f"Bạn có chắc muốn xóa hẳn tài khoản **{r['TaiKhoan']}**? Hành động này không thể hoàn tác.")
                with st.form("del_tk"):
                    if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                        try:
                            hard_delete("dangnhap", "TaiKhoan", r["TaiKhoan"])
                            st.success("Đã xóa!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

    st.divider()
    if st.button("📝 Đăng Ký Tài Khoản Mới", key="btn_add_tk", use_container_width=True):
        st.session_state["_show_add_tk"] = not st.session_state.get("_show_add_tk", False)
    if st.session_state.get("_show_add_tk", False):
        if not _perm("taikhoan", "new"):
            st.warning("Bạn không có quyền thêm tài khoản mới.")
        else:
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
                            st.session_state["_show_add_tk"] = False
                        else:
                            st.error(msg)

    st.stop()

# --- Phân Quyền page (admin only) ---
if current_page == "qlphanquyen":
    if not _perm("qlphanquyen"):
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>🔐 Phân Quyền Tài Khoản</h2>", unsafe_allow_html=True)

    nv_opts = get_nhanvien_options()
    selected_name = st.selectbox("Chọn tài khoản", list(nv_opts.keys()), key="pq_user_sel")
    selected_tk = nv_opts[selected_name]

    df_pq = get_phanquyen_grid(selected_tk).copy()
    for col in ["access_yn", "new_yn", "edit_yn", "delete_yn"]:
        df_pq[col] = df_pq[col].astype(bool)

    st.caption(f"Cấu hình quyền cho: **{selected_name}** ({selected_tk})")

    _pq_readonly = not _perm("qlphanquyen", "edit")
    edited = st.data_editor(
        df_pq[["controller", "title", "access_yn", "new_yn", "edit_yn", "delete_yn"]],
        column_config={
            "controller": st.column_config.TextColumn("Controller", disabled=True, width="small"),
            "title": st.column_config.TextColumn("Menu", disabled=True),
            "access_yn": st.column_config.CheckboxColumn("Truy cập", disabled=_pq_readonly),
            "new_yn": st.column_config.CheckboxColumn("Thêm mới", disabled=_pq_readonly),
            "edit_yn": st.column_config.CheckboxColumn("Sửa", disabled=_pq_readonly),
            "delete_yn": st.column_config.CheckboxColumn("Xóa", disabled=_pq_readonly),
        },
        hide_index=True,
        use_container_width=True,
        key=f"pq_editor_{selected_tk}",
    )

    if _perm("qlphanquyen", "edit"):
        if st.button("💾 Lưu Phân Quyền", type="primary", use_container_width=True):
            try:
                rows = edited[["controller", "access_yn", "new_yn", "edit_yn", "delete_yn"]].to_dict("records")
                save_phanquyen(selected_tk, rows)
                st.success("Đã lưu phân quyền!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")
    st.stop()

# --- Thêm Công Ty page (redirect) ---
if current_page == "themcongty":
    st.query_params["page"] = "qlcongty"
    st.rerun()

# --- Quản Lý Công Ty page (admin only) ---
if current_page == "qlcongty":
    if not _perm("qlcongty"):
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
            if not _perm("qlcongty", "edit"):
                st.warning("Bạn không có quyền sửa.")
            else:
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
            if not _perm("qlcongty", "edit"):
                st.warning("Bạn không có quyền thay đổi trạng thái.")
            else:
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
            if not _perm("qlcongty", "delete"):
                st.warning("Bạn không có quyền xóa.")
            else:
                st.warning(f"Bạn có chắc muốn xóa hẳn **{r['TenCongTy']}**? Hành động này không thể hoàn tác.")
                with st.form("ql_del_congty"):
                    if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                        try:
                            hard_delete("congty", "MaCongTy", r["MaCongTy"])
                            st.success("Đã xóa!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

    st.divider()
    if st.button("➕ Thêm Công Ty Mới", key="btn_add_ct", use_container_width=True):
        st.session_state["_show_add_ct"] = not st.session_state.get("_show_add_ct", False)
    if st.session_state.get("_show_add_ct", False):
        if not _perm("qlcongty", "new"):
            st.warning("Bạn không có quyền thêm mới.")
        else:
            with st.form("them_congty"):
                ma      = st.text_input("Mã Công Ty")
                ten     = st.text_input("Tên Công Ty")
                dia_chi = st.text_input("Địa Chỉ")
                if st.form_submit_button("Thêm", use_container_width=True):
                    if ma and ten:
                        try:
                            insert_congty(ma, ten, dia_chi, "active", actor)
                            st.success("Đã thêm!")
                            st.session_state["_show_add_ct"] = False
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
                    else:
                        st.error("Vui lòng điền Mã và Tên công ty.")
    st.stop()


# --- Thực Đơn Hôm Nay page ---
if current_page == "thucdon":
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 4px 0;'>📋 Thực Đơn Hôm Nay</h2>", unsafe_allow_html=True)
    df_hom_nay, chu_ky = get_thucdon_hom_nay()
    st.caption(f"{date.today().strftime('%d/%m/%Y')}")
    if not df_hom_nay.empty:
        _now_vn = datetime.now(tz=_VN_TZ).time()
        df_hom_nay = df_hom_nay[df_hom_nay["ThoiGianBatDau"].apply(
            lambda t: not isinstance(t, _time) or t <= _now_vn
        )].reset_index(drop=True)
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
    for loc in locations:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#EE1C25,#b01018);color:white;
                    padding:12px 18px;border-radius:10px;margin:20px 0 14px 0;
                    display:flex;align-items:center;gap:10px;'>
            <span style='font-size:1.3rem;'>📍</span>
            <span style='font-size:1.1rem;font-weight:700;'>{loc}</span>
        </div>""", unsafe_allow_html=True)
        loc_df = df_hom_nay[df_hom_nay["TenViTri"] == loc]
        cols = st.columns(3)
        for i, (_, row) in enumerate(loc_df.iterrows()):
            don_gia_str = f"{int(row['DonGia']):,}".replace(",", ".")
            img_url = resolve_image(row.get("HinhAnh"))
            img_html = (
                f'<a href="{img_url}" target="_blank" rel="noopener noreferrer">'
                f'<img src="{img_url}" style="width:100%;height:130px;'
                f'object-fit:cover;border-radius:10px 10px 0 0;display:block;cursor:pointer;">'
                f'</a>'
                if img_url else
                '<div style="width:100%;height:100px;background:#f5f5f5;'
                'border-radius:10px 10px 0 0;display:flex;align-items:center;'
                'justify-content:center;font-size:2rem;">🍽️</div>'
            )
            with cols[i % 3]:
                st.markdown(f"""
                <div style='border:1px solid #eee;border-radius:10px;overflow:hidden;
                            box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:10px;'>
                    {img_html}
                    <div style='padding:12px 14px;'>
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

    # Success screen shown after QR confirm + rerun
    if st.session_state.get("order_success"):
        _s = st.session_state.pop("order_success")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border:2px solid #a5d6a7;
                    border-radius:16px;padding:32px 24px;margin:24px 0;text-align:center;'>
            <div style='font-size:3.5rem;margin-bottom:10px;'>✅</div>
            <div style='font-size:1.5rem;font-weight:800;color:#2e7d32;margin-bottom:10px;'>Đặt Món Thành Công!</div>
            <div style='font-size:1.1rem;color:#1a1a1a;font-weight:600;margin-bottom:4px;'>{_s['ten_monan']}</div>
            <div style='font-size:0.9rem;color:#555;margin-bottom:12px;'>📍 {_s['ten_vitri']}</div>
            <div style='display:inline-block;background:#2e7d32;color:white;padding:5px 20px;
                        border-radius:20px;font-size:1rem;font-weight:700;'>{_s['don_gia']} ₫</div>
        </div>""", unsafe_allow_html=True)
        st.balloons()
        if st.button("🛒 Đặt món mới", type="primary", use_container_width=True):
            st.rerun()
        st.stop()

    col_info, col_back = st.columns([5, 1])
    col_info.markdown(f"**{ten_vitri}** · {date.today().strftime('%d/%m/%Y')}")
    if col_back.button("↩ Quay lại", use_container_width=True):
        del st.query_params["vitri"]
        st.rerun()

    chu_ky = get_chu_ky_hom_nay()
    df_avail = get_thucdon_available(ma_vitri, chu_ky)

    # Only show meals whose start time has already passed (NULL = always available)
    # Use Vietnam time (UTC+7) since stored start times are entered in local time
    now_time = datetime.now(tz=_VN_TZ).time()
    if not df_avail.empty:
        df_avail = df_avail[df_avail["ThoiGianBatDau"].apply(
            lambda t: not isinstance(t, _time) or t <= now_time
        )].reset_index(drop=True)

    if df_avail.empty:
        st.info("Chưa có bữa ăn nào bắt đầu phục vụ.")
        st.stop()

    # If user already has a pending order for this location, show the scan screen
    _pending = get_pending_order(actor)
    if _pending and _pending[1] == ma_vitri:
        _p_id, _p_vitri, _p_monan, _p_gia, _p_ten_monan, _p_ten_vitri = _pending
        don_gia_fmt = f"{int(_p_gia):,}".replace(",", ".")
        st.success(f"Đơn đã được tạo — quét mã QR tại căng tin để xác nhận.")
        st.markdown(f"**Món:** {_p_ten_monan} &nbsp;·&nbsp; **{don_gia_fmt} ₫**")
        st.markdown("**📷 Hướng camera vào mã QR tại căng tin:**")

        from urllib.parse import urlparse, parse_qs
        scanned = _qrscanner(key=f"qr_scan_{_p_id}")
        if scanned:
            try:
                _params = parse_qs(urlparse(scanned).query)
                _vitri_scanned = _params.get("vitri", [None])[0]
            except Exception:
                _vitri_scanned = None
            if not _vitri_scanned:
                st.error("QR code không hợp lệ.")
            elif _vitri_scanned != _p_vitri:
                _vinfo = get_vitri_detail(_vitri_scanned)
                _ten_scan = _vinfo[0] if _vinfo else _vitri_scanned
                st.error(f"❌ Sai căng tin! Bạn đã chọn **{_p_ten_vitri}** nhưng quét QR tại **{_ten_scan}**.")
            else:
                confirm_pending_order(_p_id, actor)
                st.session_state["order_success"] = {
                    "ten_monan": _p_ten_monan,
                    "don_gia": don_gia_fmt,
                    "ten_vitri": _p_ten_vitri,
                }
                st.rerun()

        if st.button("❌ Hủy đơn", type="secondary"):
            cancel_pending_order(actor)
            st.rerun()
        st.stop()

    if _pending and _pending[1] != ma_vitri:
        st.warning(f"Bạn có đơn đang chờ tại **{_pending[5]}**. Đặt món mới sẽ hủy đơn cũ.")

    # Pre-warm image cache (once per location per session)
    _warm_key = f"_imgs_warmed_{ma_vitri}"
    if _warm_key not in st.session_state:
        _order_imgs = df_avail["HinhAnh"].dropna().unique().tolist()
        if _order_imgs:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=8) as _ex:
                list(_ex.map(resolve_image, _order_imgs))
        st.session_state[_warm_key] = True

    sel_key = f"order_sel_{ma_vitri}"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = None

    def _pick(k, v):
        st.session_state[k] = v

    cols = st.columns(3)
    for i, (_, row) in enumerate(df_avail.iterrows()):
        img_url = resolve_image(row.get("HinhAnh"))
        don_gia_str = f"{int(row['DonGia']):,}".replace(",", ".")
        is_sel = st.session_state[sel_key] == row["MaMonAn"]
        border = "2px solid #EE1C25" if is_sel else "1px solid #eee"
        img_html = (
            f'<img src="{img_url}" style="width:100%;height:130px;'
            f'object-fit:cover;border-radius:10px 10px 0 0;display:block;">'
            if img_url else
            '<div style="width:100%;height:100px;background:#f  5f5f5;'
            'border-radius:10px 10px 0 0;display:flex;align-items:center;'
            'justify-content:center;font-size:2rem;">🍽️</div>'
        )
        with cols[i % 3]:
            st.markdown(f"""
            <div style='border:{border};border-radius:10px;overflow:hidden;
                        box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:6px;'>
                {img_html}
                <div style='padding:10px 14px;'>
                    <div style='font-weight:700;font-size:1rem;color:#1a1a1a;
                                margin-bottom:6px;line-height:1.3;'>{row['TenMonAn']}</div>
                    <span style='background:#EE1C25;color:white;padding:3px 12px;
                                 border-radius:20px;font-size:0.82rem;font-weight:600;'>
                        {don_gia_str} ₫
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)
            st.button(
                "✓ Đã chọn" if is_sel else "Chọn",
                key=f"pick_{row['MaMonAn']}",
                type="primary" if is_sel else "secondary",
                use_container_width=True,
                on_click=_pick,
                args=(sel_key, row["MaMonAn"]),
            )

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    ma_monan_sel = st.session_state.get(sel_key)
    if ma_monan_sel:
        sel_row = df_avail[df_avail["MaMonAn"] == ma_monan_sel].iloc[0]
        don_gia_sel = int(sel_row["DonGia"])
        st.markdown(f"**Đã chọn:** {sel_row['TenMonAn']} — {don_gia_sel:,} ₫".replace(",", "."))
        if st.button("✅ Đặt Món", use_container_width=True, type="primary"):
            try:
                cancel_pending_order(actor)
                insert_datmon(date.today(), ma_vitri, ma_congty, ma_monan_sel, actor, 1, don_gia_sel, actor, '', trang_thai='pending')
                st.session_state[sel_key] = None
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")
    else:
        st.caption("Chọn một món để đặt.")
    st.stop()

# --- QR Confirm page ---
if current_page == "qrconfirm":
    top_header()
    sidebar_nav()

    ma_vitri_qr = st.query_params.get("vitri", "")
    if not ma_vitri_qr:
        st.error("QR code không hợp lệ.")
        st.stop()

    vitri_info_qr = get_vitri_detail(ma_vitri_qr)
    if not vitri_info_qr:
        st.error("Địa điểm không hợp lệ.")
        st.stop()

    ten_vitri_qr = vitri_info_qr[0]
    pending = get_pending_order(actor)

    if not pending:
        st.warning("Bạn chưa có đơn nào đang chờ. Vui lòng chọn món trước.")
        if st.button("🛒 Đặt Món", type="primary"):
            st.query_params["page"] = "order"
            st.query_params["vitri"] = ma_vitri_qr
            st.rerun()
        st.stop()

    p_id, p_vitri, p_monan, p_gia, p_ten_monan, p_ten_vitri = pending

    if p_vitri != ma_vitri_qr:
        st.error(
            f"❌ Sai căng tin!\n\n"
            f"Bạn đã chọn **{p_ten_vitri}** nhưng đang quét QR tại **{ten_vitri_qr}**.\n\n"
            f"Vui lòng quét đúng mã QR tại **{p_ten_vitri}**."
        )
        st.stop()

    confirm_pending_order(p_id, actor)
    don_gia_str = f"{int(p_gia):,}".replace(",", ".")
    st.markdown(f"<h2 style='margin:8px 0 4px 0;'>✅ Đặt Món Thành Công!</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;"
        f"padding:18px 20px;margin:16px 0;font-size:1rem;'>"
        f"<b>{p_ten_monan}</b> &nbsp;·&nbsp; {don_gia_str} ₫<br>"
        f"<span style='color:#555;'>📍 {ten_vitri_qr}</span></div>",
        unsafe_allow_html=True,
    )
    st.balloons()
    st.stop()


# --- Quản Lý Đặt Món page (admin only) ---
if current_page == "qldatmon":
    if not _perm("qldatmon"):
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>📋 Quản Lý Đặt Món</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    from_d = col1.date_input("Từ ngày", value=date.today(), format="DD/MM/YYYY")
    to_d   = col2.date_input("Đến ngày", value=date.today(), format="DD/MM/YYYY")
    show_all_dm = st.toggle("Hiện tất cả (kể cả inactive)", key="show_all_qldatmon")

    status_filter = "" if show_all_dm else "AND d.\"TrangThai\"='active'"
    _c = get_conn()
    raw_dm = pd.read_sql(
        f'SELECT d."Id",d."Ngay",d."MaDiaDiem",v."TenViTri",d."MaMonAn",m."TenMonAn",'
        f'd."MaNhanVien",dn."TenTaiKhoan",d."BuaAn",d."SoLuong",d."DonGia",d."ThanhTien",d."TrangThai" '
        f'FROM datmon d '
        f'LEFT JOIN vitri v ON d."MaDiaDiem"=v."MaViTri" '
        f'LEFT JOIN monan m ON d."MaMonAn"=m."MaMonAn" '
        f'LEFT JOIN dangnhap dn ON d."MaNhanVien"=dn."TaiKhoan" '
        f'WHERE d."Ngay" BETWEEN %s AND %s {status_filter} '
        f'ORDER BY d."Ngay" DESC,d."NgayTao" DESC',
        _c, params=[str(from_d), str(to_d)]
    )
    _c.close()

    disp_dm = raw_dm[["Ngay","TenViTri","TenMonAn","TenTaiKhoan","SoLuong","DonGia","ThanhTien","TrangThai"]].rename(columns={
        "Ngay": "Ngày", "TenViTri": "Địa Điểm", "TenMonAn": "Tên Món",
        "TenTaiKhoan": "Nhân Viên", "SoLuong": "SL",
        "DonGia": "Đơn Giá", "ThanhTien": "Thành Tiền", "TrangThai": "Trạng Thái"
    })
    disp_dm["Ngày"] = pd.to_datetime(disp_dm["Ngày"]).dt.strftime("%d/%m/%Y")
    disp_dm["SL"] = disp_dm["SL"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    for col in ["Đơn Giá", "Thành Tiền"]:
        disp_dm[col] = disp_dm[col].apply(lambda x: f"{int(x):,}".replace(",", ".") if pd.notna(x) else x)

    event_dm = st.dataframe(disp_dm, use_container_width=True, hide_index=True,
                            on_select="rerun", selection_mode="single-row")

    buf_dm = BytesIO()
    raw_dm.to_excel(buf_dm, index=False)
    st.download_button("⬇️ Xuất Excel", buf_dm.getvalue(), file_name=f"datmon_{from_d}_{to_d}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    sel_dm = event_dm.selection.rows
    if not sel_dm:
        st.caption("Chọn một dòng để chỉnh sửa.")
    else:
        r = raw_dm.iloc[sel_dm[0]]
        st.markdown(f"**Đang chỉnh sửa:** {r['TenMonAn']} — {r['TenTaiKhoan']} ({pd.Timestamp(r['Ngay']).strftime('%d/%m/%Y')})")

        vitri_opts_dm   = get_vitri_options()
        monan_opts_dm, prices_dm = get_monan_options()
        nv_opts_dm      = get_nhanvien_options()

        tab_edit, tab_status, tab_del = st.tabs(["✏️ Sửa", "🔄 Trạng thái", "🗑️ Xóa"])

        with tab_edit:
            if not _perm("qldatmon", "edit"):
                st.warning("Bạn không có quyền sửa.")
            else:
                vk = list(vitri_opts_dm.keys())
                cv = next((k for k, v in vitri_opts_dm.items() if v == r["MaDiaDiem"]), vk[0])
                mk = list(monan_opts_dm.keys())
                cm = next((k for k, v in monan_opts_dm.items() if v == r["MaMonAn"]), mk[0])
                nk = list(nv_opts_dm.keys())
                cn = next((k for k, v in nv_opts_dm.items() if v == r["MaNhanVien"]), nk[0])
                with st.form("edit_datmon"):
                    e1, e2 = st.columns(2)
                    ngay_e  = e1.date_input("Ngày", value=r["Ngay"].date() if hasattr(r["Ngay"], "date") else r["Ngay"], format="DD/MM/YYYY")
                    vitri_e = e2.selectbox("Địa Điểm", vk, index=vk.index(cv))
                    e3, e4  = st.columns(2)
                    monan_e = e3.selectbox("Món Ăn", mk, index=mk.index(cm))
                    nv_e    = e4.selectbox("Nhân Viên", nk, index=nk.index(cn))
                    e5, e6  = st.columns(2)
                    sl_e    = e5.number_input("Số Lượng", min_value=1, step=1, value=int(r["SoLuong"]))
                    dg_e    = e6.number_input("Đơn Giá", min_value=0, step=1000, value=int(r["DonGia"]))
                    if st.form_submit_button("Lưu", use_container_width=True):
                        try:
                            update_datmon(r["Id"], ngay_e, vitri_opts_dm[vitri_e],
                                          monan_opts_dm[monan_e], nv_opts_dm[nv_e],
                                          sl_e, dg_e, actor)
                            st.success("Đã cập nhật!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

        with tab_status:
            if not _perm("qldatmon", "edit"):
                st.warning("Bạn không có quyền thay đổi trạng thái.")
            else:
                with st.form("status_datmon"):
                    b1, b2 = st.columns(2)
                    do_inactive = b1.form_submit_button("🚫 Vô hiệu hóa", use_container_width=True)
                    do_active   = b2.form_submit_button("✅ Kích hoạt", use_container_width=True)
                    try:
                        if do_inactive:
                            soft_delete("datmon", "Id", r["Id"], actor)
                            st.success("Đã vô hiệu hóa!")
                            st.rerun()
                        elif do_active:
                            set_active("datmon", "Id", r["Id"], actor)
                            st.success("Đã kích hoạt!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

        with tab_del:
            if not _perm("qldatmon", "delete"):
                st.warning("Bạn không có quyền xóa.")
            else:
                st.warning("Xóa hẳn đơn này? Hành động này không thể hoàn tác.")
                with st.form("del_datmon"):
                    if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                        try:
                            hard_delete("datmon", "Id", r["Id"])
                            st.success("Đã xóa!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

    st.divider()
    if st.button("➕ Thêm Đặt Món Mới", key="btn_add_dm", use_container_width=True):
        st.session_state["_show_add_dm"] = not st.session_state.get("_show_add_dm", False)
    if st.session_state.get("_show_add_dm", False):
        if not _perm("qldatmon", "new"):
            st.warning("Bạn không có quyền thêm mới.")
        else:
            vitri_opts_tdm = get_vitri_options()
            nv_opts_tdm    = get_nhanvien_options()
            col1, col2 = st.columns(2)
            ngay_add  = col1.date_input("Ngày", value=date.today(), format="DD/MM/YYYY", key="add_dm_ngay")
            vitri_add = col2.selectbox("Địa Điểm", list(vitri_opts_tdm.keys()), key="add_dm_vitri")
            ma_vitri_add     = vitri_opts_tdm[vitri_add]
            vitri_detail_add = get_vitri_detail(ma_vitri_add)
            ma_congty_add    = vitri_detail_add[1] if vitri_detail_add else None
            monan_opts_tdm, prices_tdm = get_monan_options_for_vitri(ma_vitri_add)
            with st.form("them_datmon"):
                e1, e2 = st.columns(2)
                monan_add = e1.selectbox("Món Ăn", list(monan_opts_tdm.keys()))
                nv_add    = e2.selectbox("Nhân Viên", list(nv_opts_tdm.keys()))
                e3, e4 = st.columns(2)
                sl_add = e3.number_input("Số Lượng", min_value=1, step=1, value=1)
                ma_monan_tdm = monan_opts_tdm.get(monan_add)
                default_gia  = int(prices_tdm.get(ma_monan_tdm, 0)) if ma_monan_tdm else 0
                dg_add = e4.number_input("Đơn Giá", min_value=0, step=1000, value=default_gia)
                if st.form_submit_button("➕ Thêm", use_container_width=True):
                    try:
                        insert_datmon(ngay_add, ma_vitri_add, ma_congty_add,
                                      monan_opts_tdm[monan_add], nv_opts_tdm[nv_add],
                                      sl_add, dg_add, actor, '')
                        st.success("Đã thêm!")
                        st.session_state["_show_add_dm"] = False
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
    st.stop()


# --- Thêm Đặt Món page (redirect) ---
if current_page == "themdatmon":
    st.query_params["page"] = "qldatmon"
    st.rerun()



# --- Quản Lý Thực Đơn page (admin only) ---
if current_page == "qlthucdon":
    if not _perm("qlthucdon"):
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>📅 Quản Lý Thực Đơn</h2>", unsafe_allow_html=True)

    ref_str = get_config('ngay_bat_dau_chu_ky') or str(date.today())
    ref_date = date.fromisoformat(ref_str.strip())
    today_cycle = get_chu_ky_hom_nay()
    day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]
    day_labels = [
        f"{(ref_date + timedelta(days=i-1)).strftime('%d/%m')} ({day_names[(ref_date + timedelta(days=i-1)).weekday()]})"
        for i in range(1, 15)
    ]

    vitri_opts = get_vitri_options()
    col1, col2 = st.columns(2)
    vitri_sel  = col1.selectbox("Địa Điểm", list(vitri_opts.keys()), key="td_vitri_sel")
    chu_ky_sel = col2.selectbox("Ngày Chu Kỳ", day_labels, index=today_cycle - 1, key="td_ck_sel")
    ma_vitri    = vitri_opts[vitri_sel]
    chu_ky_ngay = day_labels.index(chu_ky_sel) + 1
    monan_opts, _ = get_monan_options_for_vitri(ma_vitri)

    show_all_td = st.toggle("Hiện tất cả (kể cả inactive)", key="show_all_qlthucdon")
    df_slot = get_thucdon(ma_vitri, chu_ky_ngay, show_all=show_all_td)
    all_codes = set(df_slot["MaMonAn"].tolist()) if not df_slot.empty else set()

    st.markdown(f"**{vitri_sel} · {chu_ky_sel}** — {len(df_slot)} món")

    if df_slot.empty:
        st.caption("Chưa có món nào trong khung giờ này.")
    else:
        disp_cols = {"TenMonAn": "Tên Món Ăn", "DonGia": "Đơn Giá",
                     "ThoiGianBatDau": "Giờ Bắt Đầu", "SoSuatDuKien": "Số Suất"}
        if show_all_td:
            disp_cols["TrangThai"] = "Trạng Thái"
        disp = df_slot[list(disp_cols.keys())].rename(columns=disp_cols)
        disp["Đơn Giá"] = disp["Đơn Giá"].apply(lambda x: f"{int(x):,}".replace(",", ".") if x is not None else x)
        disp["Số Suất"] = disp["Số Suất"].apply(lambda x: str(int(x)) if pd.notna(x) and x is not None else "")
        event_td = st.dataframe(disp, use_container_width=True, hide_index=True,
                                on_select="rerun", selection_mode="single-row")
        sel_td = event_td.selection.rows
        if sel_td:
            row_td = df_slot.iloc[sel_td[0]]
            st.markdown(f"**Đang chỉnh sửa:** {row_td['TenMonAn']}")

            tab_edit, tab_status, tab_del = st.tabs(["✏️ Sửa món", "🔄 Trạng thái", "🗑️ Xóa"])

            with tab_edit:
                if not _perm("qlthucdon", "edit"):
                    st.warning("Bạn không có quyền sửa.")
                else:
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
                if not _perm("qlthucdon", "edit"):
                    st.warning("Bạn không có quyền thay đổi trạng thái.")
                else:
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
                if not _perm("qlthucdon", "delete"):
                    st.warning("Bạn không có quyền xóa.")
                else:
                    st.warning(f"Xóa hẳn **{row_td['TenMonAn']}** khỏi thực đơn? Hành động này không thể hoàn tác.")
                    with st.form("del_thucdon"):
                        if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                            try:
                                delete_thucdon(int(row_td["Id"]))
                                st.success("Đã xóa!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Lỗi: {e}")

    st.divider()
    if st.button("➕ Thêm Món Vào Thực Đơn", key="btn_add_td", use_container_width=True):
        st.session_state["_show_add_td"] = not st.session_state.get("_show_add_td", False)
    if st.session_state.get("_show_add_td", False):
        df_slot_add = get_thucdon(ma_vitri, chu_ky_ngay)
        all_codes_add = set(df_slot_add["MaMonAn"].tolist()) if not df_slot_add.empty else set()
        available = {k: v for k, v in monan_opts.items() if v not in all_codes_add}
        if not _perm("qlthucdon", "new"):
            st.warning("Bạn không có quyền thêm mới.")
        elif available:
            with st.form("add_thucdon"):
                sel_add = st.selectbox("Món ăn", list(available.keys()))
                ac1, ac2 = st.columns(2)
                tgbd_add = ac1.time_input("Giờ Bắt Đầu", value=None)
                so_suat_add = ac2.number_input("Số Suất Dự Kiến", min_value=0, step=1, value=0)
                if st.form_submit_button("➕ Thêm", use_container_width=True):
                    try:
                        insert_thucdon(ma_vitri, chu_ky_ngay, available[sel_add], actor,
                                       tgbd_add, int(so_suat_add) if so_suat_add else None)
                        st.success("Đã thêm!")
                        st.session_state["_show_add_td"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
        else:
            st.caption("Không còn món ăn khả dụng cho ngày này.")
    st.stop()

# --- Thêm Thực Đơn page (redirect) ---
if current_page == "themthucdon":
    st.query_params["page"] = "qlthucdon"
    st.rerun()

# --- Thêm Món Ăn page (redirect) ---
if current_page == "themmonan":
    st.query_params["page"] = "qlmonan"
    st.rerun()

# --- Quản Lý Món Ăn page (admin only) ---
if current_page == "qlmonan":
    if not _perm("qlmonan"):
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
            if not _perm("qlmonan", "edit"):
                st.warning("Bạn không có quyền sửa.")
            else:
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
            if not _perm("qlmonan", "edit"):
                st.warning("Bạn không có quyền thay đổi trạng thái.")
            else:
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
            if not _perm("qlmonan", "delete"):
                st.warning("Bạn không có quyền xóa.")
            else:
                st.warning(f"Bạn có chắc muốn xóa hẳn **{r['TenMonAn']}**? Hành động này không thể hoàn tác.")
                with st.form("ql_del_monan"):
                    if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                        try:
                            hard_delete("monan", "MaMonAn", r["MaMonAn"])
                            st.success("Đã xóa!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

    st.divider()
    if st.button("➕ Thêm Món Ăn Mới", key="btn_add_mn", use_container_width=True):
        st.session_state["_show_add_mn"] = not st.session_state.get("_show_add_mn", False)
    if st.session_state.get("_show_add_mn", False):
        if not _perm("qlmonan", "new"):
            st.warning("Bạn không có quyền thêm mới.")
        else:
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
                            st.session_state["_show_add_mn"] = False
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
                    else:
                        st.error("Vui lòng điền Mã và Tên món ăn.")
    st.stop()

# --- Thêm Địa Điểm page (redirect) ---
if current_page == "themvitri":
    st.query_params["page"] = "qlvitri"
    st.rerun()

# --- Quản Lý Địa Điểm page (admin only) ---
if current_page == "qlvitri":
    if not _perm("qlvitri"):
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
            if not _perm("qlvitri", "edit"):
                st.warning("Bạn không có quyền sửa.")
            else:
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
            if not _perm("qlvitri", "edit"):
                st.warning("Bạn không có quyền thay đổi trạng thái.")
            else:
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
            if not _perm("qlvitri", "delete"):
                st.warning("Bạn không có quyền xóa.")
            else:
                st.warning(f"Bạn có chắc muốn xóa hẳn **{r['TenViTri']}**? Hành động này không thể hoàn tác.")
                with st.form("ql_del_vitri"):
                    if st.form_submit_button("🗑️ Xóa hẳn", use_container_width=True):
                        try:
                            hard_delete("vitri", "MaViTri", r["MaViTri"])
                            st.success("Đã xóa!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

    st.divider()
    if st.button("➕ Thêm Địa Điểm Mới", key="btn_add_vt", use_container_width=True):
        st.session_state["_show_add_vt"] = not st.session_state.get("_show_add_vt", False)
    if st.session_state.get("_show_add_vt", False):
        if not _perm("qlvitri", "new"):
            st.warning("Bạn không có quyền thêm mới.")
        else:
            congty_opts_tv = get_congty_options()
            with st.form("them_vitri"):
                ma         = st.text_input("Mã Địa Điểm")
                ten        = st.text_input("Tên Địa Điểm")
                congty_sel = st.selectbox("Công Ty", list(congty_opts_tv.keys()))
                if st.form_submit_button("Thêm", use_container_width=True):
                    if ma and ten:
                        try:
                            insert_vitri(ma, ten, congty_opts_tv[congty_sel], "active", actor)
                            st.success("Đã thêm!")
                            st.session_state["_show_add_vt"] = False
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
                    else:
                        st.error("Vui lòng điền Mã và Tên địa điểm.")
    st.stop()

# --- Quản Lý Mã QR page (admin only) ---
if current_page == "qlqr":
    if not _perm("qlqr"):
        st.error("Không có quyền truy cập.")
        st.stop()
    top_header()
    sidebar_nav()
    st.markdown("<h2 style='margin:8px 0 16px 0;'>📱 Mã QR Căng Tin</h2>", unsafe_allow_html=True)

    try:
        import qrcode as _qrcode
    except ImportError:
        st.error("Cần cài đặt thư viện qrcode: `pip install qrcode[pil]`")
        st.stop()

    saved_url = get_config('app_url') or ""
    base_url = st.text_input("URL ứng dụng (dùng để tạo QR)", value=saved_url,
                              placeholder="https://your-app.streamlit.app")
    if base_url and base_url != saved_url:
        upsert_config('app_url', base_url)

    if not base_url:
        st.info("Nhập URL ứng dụng ở trên để tạo mã QR.")
        st.stop()

    vitri_list = load_table("vitri", show_all=False)
    cols_qr = st.columns(3)
    for i, (_, row) in enumerate(vitri_list.iterrows()):
        ma = row["MaViTri"]
        ten = row["TenViTri"]
        url = f"{base_url.rstrip('/')}/?page=qrconfirm&vitri={ma}"
        qr = _qrcode.QRCode(version=1, box_size=10, border=4,
                             error_correction=_qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()
        with cols_qr[i % 3]:
            st.markdown(f"**{ten}**")
            st.image(img_bytes, use_container_width=True)
            st.download_button("⬇️ Tải QR", img_bytes,
                               file_name=f"qr_{ma}.png", mime="image/png",
                               key=f"dl_qr_{ma}", use_container_width=True)
    st.stop()


top_header()
sidebar_nav()
selected_key = current_page if current_page in ["datmon", "congty", "diadiem", "nhanvien"] else "datmon"
if not _perm(selected_key):
    st.error("Không có quyền truy cập.")
    st.stop()

page_titles = {
    "datmon":   "🍱 Đặt Món",
    "congty":   "🏢 Công Ty",
    "diadiem":  "📍 Địa Điểm",
    "nhanvien": "👤 Nhân Viên",
}
st.markdown(f"<h2 style='margin:8px 0 16px 0;'>{page_titles[selected_key]}</h2>", unsafe_allow_html=True)

# --- Page content ---
col1, col2 = st.columns(2)
from_date = col1.date_input("Từ ngày", value=date.today(), format="DD/MM/YYYY")
to_date = col2.date_input("Đến ngày", value=date.today(), format="DD/MM/YYYY")
show_all = st.toggle("Hiện tất cả (kể cả inactive)", key="show_all_report")

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
