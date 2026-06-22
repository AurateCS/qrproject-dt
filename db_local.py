import pyodbc
import pandas as pd
import streamlit as st
from datetime import datetime, date as _date

def _now():
    return datetime.now().replace(microsecond=0)


def _get_conn_str():
    for drv in ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]:
        try:
            extra = ";TrustServerCertificate=yes" if "18" in drv else ""
            cs = f"DRIVER={{{drv}}};SERVER=localhost;DATABASE=qlsuatan;Trusted_Connection=yes{extra};"
            pyodbc.connect(cs, timeout=3)
            return cs
        except Exception:
            continue
    raise RuntimeError("Cannot connect to local SQL Server. Is it running?")


@st.cache_resource
def _conn_str():
    return _get_conn_str()


def get_conn():
    return pyodbc.connect(_conn_str())


@st.cache_resource
def _ensure_datmon_distance_column():
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'IF COL_LENGTH(\'vitri\', \'Lat\') IS NULL '
        'ALTER TABLE vitri ADD "Lat" FLOAT NULL'
    )
    cur.execute(
        'IF COL_LENGTH(\'vitri\', \'Lng\') IS NULL '
        'ALTER TABLE vitri ADD "Lng" FLOAT NULL'
    )
    cur.execute(
        'IF COL_LENGTH(\'datmon\', \'UserLat\') IS NULL '
        'ALTER TABLE datmon ADD "UserLat" FLOAT NULL'
    )
    cur.execute(
        'IF COL_LENGTH(\'datmon\', \'UserLng\') IS NULL '
        'ALTER TABLE datmon ADD "UserLng" FLOAT NULL'
    )
    cur.execute(
        'IF COL_LENGTH(\'datmon\', \'KhoangCach\') IS NULL '
        'ALTER TABLE datmon ADD "KhoangCach" NUMERIC(15,2) NULL'
    )
    c.commit()
    c.close()


_ensure_datmon_distance_column()


column_labels = {
    "Id": "ID",
    "Ngay": "Ngày",
    "MaDiaDiem": "Mã Địa Điểm",
    "TenDiaDiem": "Tên Địa Điểm",
    "MaMonAn": "Mã Món Ăn",
    "TenMonAn": "Tên Món Ăn",
    "MaNhanVien": "Mã Nhân Viên",
    "TaiKhoan": "Tài Khoản",
    "TenTaiKhoan": "Tên Tài Khoản",
    "TenNhanVien": "Tên Nhân Viên",
    "SoDon": "Số Lượng",
    "SoLuong": "Số Lượng",
    "DonGia": "Đơn Giá",
    "ThanhTien": "Thành Tiền",
    "MaCongTy": "Mã Công Ty",
    "MaCongty": "Mã Công Ty",
    "TenCongTy": "Tên Công Ty",
    "TrangThai": "Trạng Thái",
}

price_columns = {"DonGia", "ThanhTien"}

_REPORT_QUERIES = {
    "bc_datmon": """
        SELECT d."Ngay", d."MaDiaDiem", v."TenViTri" AS "TenDiaDiem",
               d."MaMonAn", m."TenMonAn", d."MaNhanVien",
               dn."TenTaiKhoan" AS "TenNhanVien",
               d."SoLuong", d."DonGia", d."ThanhTien", d."KhoangCach",
               d."MaCongTy", c."TenCongTy" {trangThai}
        FROM datmon d
        LEFT JOIN vitri v ON d."MaDiaDiem" = v."MaViTri"
        LEFT JOIN monan m ON d."MaMonAn" = m."MaMonAn"
        LEFT JOIN dangnhap dn ON d."MaNhanVien" = dn."TaiKhoan"
        LEFT JOIN congty c ON d."MaCongTy" = c."MaCongTy"
        WHERE d."Ngay" BETWEEN ? AND ? {status}
        ORDER BY d."Ngay" DESC
    """,
    "bc_congty": """
        SELECT c."MaCongTy", c."TenCongTy",
               COUNT(d."Id") AS "SoDon",
               COALESCE(SUM(d."DonGia"), 0) AS "DonGia",
               COALESCE(SUM(d."ThanhTien"), 0) AS "ThanhTien"
        FROM congty c
        LEFT JOIN datmon d ON c."MaCongTy" = d."MaCongTy"
            AND d."Ngay" BETWEEN ? AND ? {status_join}
        {parent_status}
        GROUP BY c."MaCongTy", c."TenCongTy"
        ORDER BY c."MaCongTy"
    """,
    "bc_diadiem": """
        SELECT c."MaCongTy", c."TenCongTy",
               v."MaViTri" AS "MaDiaDiem", v."TenViTri" AS "TenDiaDiem",
               COUNT(d."Id") AS "SoDon",
               COALESCE(SUM(d."DonGia"), 0) AS "DonGia",
               COALESCE(SUM(d."ThanhTien"), 0) AS "ThanhTien"
        FROM vitri v
        LEFT JOIN congty c ON v."MaCongTy" = c."MaCongTy"
        LEFT JOIN datmon d ON v."MaViTri" = d."MaDiaDiem"
            AND d."Ngay" BETWEEN ? AND ? {status_join}
        {parent_status}
        GROUP BY c."MaCongTy", c."TenCongTy", v."MaViTri", v."TenViTri"
        ORDER BY v."MaViTri"
    """,
    "bc_nhanvien": """
        SELECT c."MaCongTy", c."TenCongTy",
               v."MaViTri" AS "MaDiaDiem", v."TenViTri" AS "TenDiaDiem",
               dn."TaiKhoan" AS "MaNhanVien", dn."TenTaiKhoan" AS "TenNhanVien",
               COUNT(d."Id") AS "SoDon",
               COALESCE(SUM(d."DonGia"), 0) AS "DonGia",
               COALESCE(SUM(d."ThanhTien"), 0) AS "ThanhTien"
        FROM dangnhap dn
        LEFT JOIN vitri v ON dn."MaDiaDiem" = v."MaViTri"
        LEFT JOIN congty c ON v."MaCongTy" = c."MaCongTy"
        LEFT JOIN datmon d ON dn."TaiKhoan" = d."MaNhanVien"
            AND d."Ngay" BETWEEN ? AND ? {status_join}
        {parent_status}
        GROUP BY c."MaCongTy", c."TenCongTy", v."MaViTri", v."TenViTri",
                 dn."TaiKhoan", dn."TenTaiKhoan"
        ORDER BY dn."TaiKhoan"
    """,
}


def load(proc, from_date, to_date, show_all=False):
    template = _REPORT_QUERIES[proc]
    if proc == "bc_datmon":
        status = "" if show_all else "AND d.\"TrangThai\" = 'active'"
        trang_thai_col = ', d."TrangThai"' if show_all else ""
        query = template.format(status=status, trangThai=trang_thai_col)
    else:
        status_join = "" if show_all else "AND d.\"TrangThai\" = 'active'"
        parent_col = {"bc_congty": 'c', "bc_diadiem": 'v', "bc_nhanvien": 'dn'}.get(proc, 'c')
        parent_status = "" if show_all else f"WHERE {parent_col}.\"TrangThai\" = 'active'"
        query = template.format(status_join=status_join, parent_status=parent_status)
    params = [str(from_date), str(to_date)]
    c = get_conn()
    df = pd.read_sql(query, c, params=params)
    c.close()
    df.rename(columns=column_labels, inplace=True)
    for col in price_columns:
        vn = column_labels.get(col, col)
        if vn in df.columns:
            df[vn] = df[vn].apply(lambda x: f"{int(x):,}".replace(",", ".") if pd.notna(x) else x)
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) else x)
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%d/%m/%Y")
        elif df[col].dtype == object:
            sample = df[col].dropna()
            if not sample.empty and hasattr(sample.iloc[0], "strftime"):
                df[col] = df[col].apply(lambda x: x.strftime("%d/%m/%Y") if x is not None and hasattr(x, "strftime") else x)
    return df


@st.cache_data(ttl=300)
def get_vitri_options():
    c = get_conn()
    df = pd.read_sql('SELECT "MaViTri", "TenViTri" FROM vitri WHERE "TrangThai"=\'active\' ORDER BY "MaViTri"', c)
    c.close()
    return dict(zip(df["TenViTri"], df["MaViTri"]))


@st.cache_data(ttl=300)
def get_congty_options():
    c = get_conn()
    df = pd.read_sql('SELECT "MaCongTy", "TenCongTy" FROM congty WHERE "TrangThai"=\'active\' ORDER BY "MaCongTy"', c)
    c.close()
    return dict(zip(df["TenCongTy"], df["MaCongTy"]))


@st.cache_data(ttl=300)
def get_monan_options():
    c = get_conn()
    df = pd.read_sql('SELECT "MaMonAn", "TenMonAn", "DonGia" FROM monan WHERE "TrangThai"=\'active\' ORDER BY "MaMonAn"', c)
    c.close()
    prices = dict(zip(df["MaMonAn"], df["DonGia"]))
    labels = dict(zip(df["TenMonAn"], df["MaMonAn"]))
    return labels, prices


@st.cache_data(ttl=300)
def get_monan_options_for_vitri(ma_vitri):
    c = get_conn()
    df = pd.read_sql(
        'SELECT m."MaMonAn", m."TenMonAn", m."DonGia" '
        'FROM monan m JOIN vitri_monan vm ON m."MaMonAn" = vm."MaMonAn" '
        'WHERE m."TrangThai"=\'active\' AND vm."MaViTri"=? ORDER BY m."MaMonAn"',
        c, params=[ma_vitri]
    )
    c.close()
    prices = dict(zip(df["MaMonAn"], df["DonGia"]))
    labels = dict(zip(df["TenMonAn"], df["MaMonAn"]))
    return labels, prices


@st.cache_data(ttl=300)
def get_nhanvien_options():
    c = get_conn()
    df = pd.read_sql('SELECT "TaiKhoan", "TenTaiKhoan" FROM dangnhap WHERE "TrangThai"=\'active\' ORDER BY "TaiKhoan"', c)
    c.close()
    return dict(zip(df["TenTaiKhoan"], df["TaiKhoan"]))


def load_table(table, show_all=False):
    c = get_conn()
    where = "" if show_all else "WHERE \"TrangThai\"='active'"
    df = pd.read_sql(f'SELECT * FROM "{table}" {where}', c)
    c.close()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%d/%m/%Y %H:%M")
        elif df[col].dtype == "float64" and not df[col].dropna().empty and df[col].dropna().apply(float.is_integer).all():
            df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) else "")
        elif df[col].dtype in ("int64", "int32", "int16", "Int64"):
            df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    return df


def hard_delete(table, pk_col, pk_val):
    c = get_conn()
    cur = c.cursor()
    cur.execute(f'DELETE FROM "{table}" WHERE "{pk_col}"=?', (pk_val,))
    c.commit()
    c.close()


def _set_trangthai(table, pk_col, pk_val, status, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        f'UPDATE "{table}" SET "TrangThai"=?, "NgaySua"=?, "NguoiSua"=? WHERE "{pk_col}"=?',
        (status, _now(), actor, pk_val)
    )
    c.commit()
    c.close()


def soft_delete(table, pk_col, pk_val, actor):
    _set_trangthai(table, pk_col, pk_val, "inactive", actor)


def set_active(table, pk_col, pk_val, actor):
    _set_trangthai(table, pk_col, pk_val, "active", actor)


def update_datmon(id_val, ngay, ma_diadiem, ma_monan, ma_nhanvien, so_luong, don_gia, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE datmon SET "Ngay"=?,"MaDiaDiem"=?,"MaMonAn"=?,"MaNhanVien"=?,'
        '"SoLuong"=?,"DonGia"=?,"ThanhTien"=?,"NgaySua"=?,"NguoiSua"=? WHERE "Id"=?',
        (ngay, ma_diadiem, ma_monan, ma_nhanvien, so_luong, don_gia, so_luong * don_gia, _now(), actor, id_val)
    )
    c.commit()
    c.close()


def update_congty(ma_congty, ten_congty, dia_chi, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE congty SET "TenCongTy"=?,"DiaChi"=?,"NgaySua"=?,"NguoiSua"=? WHERE "MaCongTy"=?',
        (ten_congty, dia_chi, _now(), actor, ma_congty)
    )
    c.commit()
    c.close()


def update_vitri(ma_vitri, ten_vitri, ma_congty, bua_sang, bua_trua, bua_chieu, lat, lng, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE vitri SET "TenViTri"=?,"MaCongTy"=?,"BuaSang"=?,"BuaTrua"=?,"BuaChieu"=?,'
        '"Lat"=?,"Lng"=?,"NgaySua"=?,"NguoiSua"=? WHERE "MaViTri"=?',
        (ten_vitri, ma_congty, bua_sang, bua_trua, bua_chieu, lat, lng, _now(), actor, ma_vitri)
    )
    c.commit()
    c.close()


def update_nhanvien(tai_khoan, ten_tai_khoan, ma_diadiem, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE dangnhap SET "TenTaiKhoan"=?,"MaDiaDiem"=?,"NgaySua"=?,"NguoiSua"=? WHERE "TaiKhoan"=?',
        (ten_tai_khoan, ma_diadiem, _now(), actor, tai_khoan)
    )
    c.commit()
    c.close()


@st.cache_data(ttl=300)
def get_vitri_detail(ma_vitri):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'SELECT "TenViTri","MaCongTy","BuaSang","BuaTrua","BuaChieu","Lat","Lng" FROM vitri WHERE "MaViTri"=?',
        (ma_vitri,)
    )
    row = cur.fetchone()
    c.close()
    return row


def check_duplicate_order(ma_nhanvien, ngay, bua_an, ma_diadiem):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'SELECT COUNT(*) FROM datmon WHERE "MaNhanVien"=? AND CAST("Ngay" AS DATE)=? AND "BuaAn"=? AND "MaDiaDiem"=? AND "TrangThai"=\'active\'',
        (ma_nhanvien, str(ngay), bua_an, ma_diadiem)
    )
    count = cur.fetchone()[0]
    c.close()
    return count > 0


def insert_datmon(ngay, ma_diadiem, ma_congty, ma_monan, ma_nhanvien, so_luong, don_gia, actor, bua_an='', trang_thai='active', user_lat=None, user_lng=None, khoang_cach=None):
    thanh_tien = so_luong * don_gia
    now = _now()
    id_val = f"ORD-{ngay.strftime('%Y%m%d')}-{now.strftime('%H%M%S%f')}"
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO datmon ("Id","Ngay","MaDiaDiem","MaCongTy","MaMonAn","MaNhanVien","SoLuong","DonGia","ThanhTien","BuaAn","TrangThai","UserLat","UserLng","KhoangCach","NgayTao","NguoiTao","NgaySua","NguoiSua") '
        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (id_val, ngay, ma_diadiem, ma_congty, ma_monan, ma_nhanvien, so_luong, don_gia, thanh_tien, bua_an, trang_thai, user_lat, user_lng, khoang_cach, now, actor, now, actor)
    )
    c.commit()
    c.close()
    if trang_thai == 'active':
        get_thucdon_available.clear()
        get_thucdon_hom_nay.clear()
    if trang_thai == 'pending':
        get_pending_order.clear()


@st.cache_data(ttl=30)
def get_pending_order(username):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'SELECT TOP 1 d."Id",d."MaDiaDiem",d."MaMonAn",d."DonGia",m."TenMonAn",v."TenViTri" '
        'FROM datmon d '
        'JOIN monan m ON d."MaMonAn"=m."MaMonAn" '
        'JOIN vitri v ON d."MaDiaDiem"=v."MaViTri" '
        'WHERE d."MaNhanVien"=? AND d."TrangThai"=\'pending\' '
        'ORDER BY d."NgayTao" DESC',
        (username,)
    )
    row = cur.fetchone()
    c.close()
    return row


def confirm_pending_order(id_val, actor):
    _set_trangthai("datmon", "Id", id_val, "active", actor)
    get_thucdon_available.clear()
    get_thucdon_hom_nay.clear()
    get_pending_order.clear()


def cancel_pending_order(username):
    c = get_conn()
    cur = c.cursor()
    cur.execute('DELETE FROM datmon WHERE "MaNhanVien"=? AND "TrangThai"=\'pending\'', (username,))
    c.commit()
    c.close()
    get_pending_order.clear()


def upsert_config(key, value):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'IF EXISTS (SELECT 1 FROM config WHERE "CauHinh"=?) '
        '    UPDATE config SET "GiaTri"=? WHERE "CauHinh"=? '
        'ELSE '
        '    INSERT INTO config ("CauHinh","GiaTri") VALUES (?,?)',
        (key, value, key, key, value)
    )
    c.commit()
    c.close()
    get_config.clear()


def insert_congty(ma_congty, ten_congty, dia_chi, trang_thai, actor):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO congty ("MaCongTy","TenCongTy","DiaChi","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (?,?,?,?,?,?,?,?)',
        (ma_congty, ten_congty, dia_chi, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def insert_vitri(ma_vitri, ten_vitri, ma_congty, trang_thai, actor, lat=None, lng=None):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO vitri ("MaViTri","TenViTri","MaCongTy","Lat","Lng","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (?,?,?,?,?,?,?,?,?,?)',
        (ma_vitri, ten_vitri, ma_congty, lat, lng, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def insert_nhanvien(tai_khoan, ten_tai_khoan, mat_khau, ma_diadiem, trang_thai, actor):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO dangnhap ("TaiKhoan","TenTaiKhoan","Adm","MatKhau","MaDiaDiem","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (?,?,0,?,?,?,?,?,?,?)',
        (tai_khoan, ten_tai_khoan, mat_khau, ma_diadiem, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def insert_monan(ma_monan, ten_monan, don_gia, trang_thai, actor, hinh_anh=""):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO monan ("MaMonAn","TenMonAn","DonGia","HinhAnh","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (?,?,?,?,?,?,?,?,?)',
        (ma_monan, ten_monan, don_gia, hinh_anh or None, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def update_monan(ma_monan, ten_monan, don_gia, actor, hinh_anh=""):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE monan SET "TenMonAn"=?,"DonGia"=?,"HinhAnh"=?,"NgaySua"=?,"NguoiSua"=? WHERE "MaMonAn"=?',
        (ten_monan, don_gia, hinh_anh or None, _now(), actor, ma_monan)
    )
    c.commit()
    c.close()


def update_user_password(tai_khoan, new_password, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE dangnhap SET "MatKhau"=?,"NgaySua"=?,"NguoiSua"=? WHERE "TaiKhoan"=?',
        (new_password, _now(), actor, tai_khoan)
    )
    c.commit()
    c.close()


def toggle_admin(tai_khoan, adm_val, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE dangnhap SET "Adm"=?,"NgaySua"=?,"NguoiSua"=? WHERE "TaiKhoan"=?',
        (adm_val, _now(), actor, tai_khoan)
    )
    c.commit()
    c.close()


@st.cache_data(ttl=300)
def get_config(key):
    c = get_conn()
    cur = c.cursor()
    cur.execute('SELECT "GiaTri" FROM config WHERE "CauHinh"=?', (key,))
    row = cur.fetchone()
    c.close()
    return row[0] if row else None


def set_config(key, value):
    c = get_conn()
    cur = c.cursor()
    cur.execute('UPDATE config SET "GiaTri"=? WHERE "CauHinh"=?', (value, key))
    c.commit()
    c.close()


def get_chu_ky_hom_nay():
    ref_str = get_config('ngay_bat_dau_chu_ky')
    if not ref_str:
        return 1
    from datetime import date
    ref = date.fromisoformat(ref_str.strip())
    return ((_date.today() - ref).days % 14) + 1


@st.cache_data(ttl=120)
def get_thucdon(ma_vitri, chu_ky_ngay, show_all=False):
    status_filter = "" if show_all else "AND t.\"TrangThai\"='active'"
    c = get_conn()
    df = pd.read_sql(
        f'SELECT t."Id",t."MaMonAn",t."TrangThai",t."ThoiGianBatDau",t."SoSuatDuKien",'
        f'm."TenMonAn",m."DonGia" '
        f'FROM thucdon t JOIN monan m ON t."MaMonAn"=m."MaMonAn" '
        f'WHERE t."MaViTri"=? AND t."ChuKyNgay"=? {status_filter}',
        c, params=[ma_vitri, chu_ky_ngay]
    )
    c.close()
    df["ThoiGianBatDau"] = df["ThoiGianBatDau"].apply(
        lambda x: x.strftime("%H:%M") if hasattr(x, "strftime") else ""
    )
    return df


@st.cache_data(ttl=60)
def get_monan_used_in_cycle(chu_ky_ngay, exclude_vitri):
    c = get_conn()
    df = pd.read_sql(
        'SELECT DISTINCT t."MaMonAn" FROM thucdon t '
        'WHERE t."ChuKyNgay"=? AND t."MaViTri"!=? AND t."TrangThai"=\'active\'',
        c, params=[chu_ky_ngay, exclude_vitri]
    )
    c.close()
    return set(df["MaMonAn"].tolist())


def _clear_thucdon_cache():
    get_thucdon.clear()
    get_thucdon_hom_nay.clear()
    get_thucdon_available.clear()
    get_monan_used_in_cycle.clear()


def insert_thucdon(ma_vitri, chu_ky_ngay, ma_monan, actor, thoi_gian=None, so_suat=None):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO thucdon ("MaViTri","ChuKyNgay","BuaAn","MaMonAn","ThoiGianBatDau","SoSuatDuKien","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") '
        "VALUES (?,?,?,?,?,?,'active',?,?,?,?)",
        (ma_vitri, chu_ky_ngay, '', ma_monan, thoi_gian, so_suat, now, actor, now, actor)
    )
    c.commit()
    c.close()
    _clear_thucdon_cache()


def _td_to_time(val):
    if val is None:
        return None
    if hasattr(val, 'total_seconds'):
        try:
            secs = int(val.total_seconds())
        except (TypeError, ValueError):
            return None
        h, rem = divmod(secs, 3600)
        m = rem // 60
        from datetime import datetime as _dt
        return _dt(2000, 1, 1, h, m).time()
    if hasattr(val, 'hour'):
        return val
    return None


@st.cache_data(ttl=60)
def get_thucdon_available(ma_vitri, chu_ky_ngay):
    today = str(_date.today())
    c = get_conn()
    df = pd.read_sql(
        'SELECT t."Id",t."MaMonAn",t."ThoiGianBatDau",t."SoSuatDuKien",'
        'm."TenMonAn",m."DonGia",m."HinhAnh" '
        'FROM thucdon t '
        'JOIN monan m ON t."MaMonAn"=m."MaMonAn" '
        'LEFT JOIN menu mn ON mn."Ngay"=? '
        '    AND mn."MaDiaDiem"=t."MaViTri" AND mn."MaMonAn"=t."MaMonAn" '
        'LEFT JOIN ('
        '    SELECT "MaDiaDiem","MaMonAn",COUNT(*) AS cnt '
        '    FROM datmon '
        '    WHERE CAST("Ngay" AS DATE)=CAST(GETDATE() AS DATE) AND "TrangThai"=\'active\' '
        '    GROUP BY "MaDiaDiem","MaMonAn"'
        ') oc ON oc."MaDiaDiem"=t."MaViTri" AND oc."MaMonAn"=t."MaMonAn" '
        'WHERE t."MaViTri"=? AND t."ChuKyNgay"=? '
        "AND t.\"TrangThai\"='active' "
        "AND (mn.\"TrangThai\" IS NULL OR mn.\"TrangThai\"!='done') "
        'AND (t."SoSuatDuKien" IS NULL OR t."SoSuatDuKien"=0 '
        '     OR COALESCE(oc.cnt,0) < t."SoSuatDuKien") '
        'ORDER BY m."TenMonAn"',
        c, params=[today, ma_vitri, chu_ky_ngay]
    )
    c.close()
    df["ThoiGianBatDau"] = df["ThoiGianBatDau"].apply(_td_to_time)
    return df


def finish_thucdon_today(ma_vitri, ma_monan, actor):
    today = _date.today()
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'IF EXISTS (SELECT 1 FROM menu WHERE "Ngay"=? AND "MaDiaDiem"=? AND "MaMonAn"=?) '
        '    UPDATE menu SET "TrangThai"=\'done\',"NgaySua"=?,"NguoiSua"=? '
        '    WHERE "Ngay"=? AND "MaDiaDiem"=? AND "MaMonAn"=? '
        'ELSE '
        '    INSERT INTO menu ("Ngay","MaDiaDiem","MaMonAn","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") '
        "    VALUES (?,?,?,'done',?,?,?,?)",
        (today, ma_vitri, ma_monan, now, actor, today, ma_vitri, ma_monan, today, ma_vitri, ma_monan, now, actor, now, actor)
    )
    c.commit()
    c.close()
    get_thucdon_available.clear()
    get_thucdon_hom_nay.clear()


@st.cache_data(ttl=120)
def get_thucdon_hom_nay():
    chu_ky = get_chu_ky_hom_nay()
    today = str(_date.today())
    c = get_conn()
    df = pd.read_sql(
        'SELECT v."TenViTri",m."TenMonAn",m."DonGia",m."HinhAnh",t."ThoiGianBatDau" '
        'FROM thucdon t '
        'JOIN monan m ON t."MaMonAn"=m."MaMonAn" '
        'JOIN vitri v ON t."MaViTri"=v."MaViTri" '
        'LEFT JOIN menu mn ON mn."Ngay"=? '
        '    AND mn."MaDiaDiem"=t."MaViTri" AND mn."MaMonAn"=t."MaMonAn" '
        'LEFT JOIN ('
        '    SELECT "MaDiaDiem","MaMonAn",COUNT(*) AS cnt '
        '    FROM datmon '
        '    WHERE CAST("Ngay" AS DATE)=CAST(GETDATE() AS DATE) AND "TrangThai"=\'active\' '
        '    GROUP BY "MaDiaDiem","MaMonAn"'
        ') oc ON oc."MaDiaDiem"=t."MaViTri" AND oc."MaMonAn"=t."MaMonAn" '
        "WHERE t.\"ChuKyNgay\"=? AND t.\"TrangThai\"='active' "
        "AND (mn.\"TrangThai\" IS NULL OR mn.\"TrangThai\"!='done') "
        'AND (t."SoSuatDuKien" IS NULL OR t."SoSuatDuKien"=0 '
        '     OR COALESCE(oc.cnt,0) < t."SoSuatDuKien") '
        'ORDER BY v."TenViTri",m."TenMonAn"',
        c, params=[today, chu_ky]
    )
    c.close()
    df["ThoiGianBatDau"] = df["ThoiGianBatDau"].apply(_td_to_time)
    return df, chu_ky


def update_thucdon(id_val, ma_monan, actor, thoi_gian=None, so_suat=None):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE thucdon SET "MaMonAn"=?,"ThoiGianBatDau"=?,"SoSuatDuKien"=?,"NgaySua"=?,"NguoiSua"=? WHERE "Id"=?',
        (ma_monan, thoi_gian, so_suat, now, actor, id_val)
    )
    c.commit()
    c.close()
    _clear_thucdon_cache()


def delete_thucdon(id_val):
    c = get_conn()
    cur = c.cursor()
    cur.execute('DELETE FROM thucdon WHERE "Id"=?', (id_val,))
    c.commit()
    c.close()
    _clear_thucdon_cache()


@st.cache_data(ttl=120)
def get_phanquyen_grid(tk):
    c = get_conn()
    cur = c.cursor()
    cur.execute('EXEC sp_get_phanquyen_grid ?', (tk,))
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    c.close()
    return pd.DataFrame([list(r) for r in rows], columns=cols)


def save_phanquyen(tk, rows):
    c = get_conn()
    cur = c.cursor()
    for row in rows:
        cur.execute(
            'IF EXISTS (SELECT 1 FROM phanquyen WHERE "TK"=? AND "controller"=?) '
            '    UPDATE phanquyen SET "access_yn"=?,"new_yn"=?,"edit_yn"=?,"delete_yn"=? '
            '    WHERE "TK"=? AND "controller"=? '
            'ELSE '
            '    INSERT INTO phanquyen ("TK","controller","access_yn","new_yn","edit_yn","delete_yn") '
            '    VALUES (?,?,?,?,?,?)',
            (tk, row["controller"],
             int(row["access_yn"]), int(row["new_yn"]), int(row["edit_yn"]), int(row["delete_yn"]),
             tk, row["controller"],
             tk, row["controller"],
             int(row["access_yn"]), int(row["new_yn"]), int(row["edit_yn"]), int(row["delete_yn"]))
        )
    c.commit()
    c.close()
    get_phanquyen_grid.clear()
    get_user_perm.clear()


@st.cache_data(ttl=120)
def get_user_perm(tk):
    c = get_conn()
    df = pd.read_sql(
        'SELECT "controller","access_yn","new_yn","edit_yn","delete_yn" '
        'FROM phanquyen WHERE "TK"=?',
        c, params=[tk]
    )
    c.close()
    return {
        row["controller"]: {
            "access": bool(row["access_yn"]),
            "new": bool(row["new_yn"]),
            "edit": bool(row["edit_yn"]),
            "delete": bool(row["delete_yn"]),
        }
        for _, row in df.iterrows()
    }


@st.cache_data(ttl=300)
def get_sidebar(username=''):
    try:
        c = get_conn()
        df = pd.read_sql(
            'SELECT "sidebar","sidebar_cha","controller","title","icon","adm" '
            'FROM sidebar WHERE "TrangThai"=\'active\' ORDER BY "sidebar"',
            c
        )
        c.close()
        df = df.where(pd.notna(df), None)
        sections = []
        parents = df[df["sidebar_cha"].isna()]
        for _, parent in parents.iterrows():
            children = df[df["sidebar_cha"] == parent["sidebar"]]
            items = []
            for _, child in children.iterrows():
                icon = "" if pd.isnull(child["icon"]) else str(child["icon"])
                label = f"{icon} {child['title']}".strip()
                items.append({
                    "label": label,
                    "key": child["controller"],
                    "id": child["sidebar"],
                    "admin": bool(child["adm"]),
                })
            if items:
                sections.append({"section": parent["title"], "items": items})
        return sections
    except Exception:
        from db import _sidebar_fallback
        return _sidebar_fallback()
