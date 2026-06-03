import os
import psycopg2
import pandas as pd
import streamlit as st
from datetime import datetime

def _now():
    return datetime.now().replace(microsecond=0)


def _get_db_url():
    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        return os.environ.get("DATABASE_URL", "")


def get_conn():
    return psycopg2.connect(_get_db_url())


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

# --- Report queries (replaces SQL Server stored procedures) ---

_REPORT_QUERIES = {
    "bc_datmon": """
        SELECT d."Ngay", d."MaDiaDiem", v."TenViTri" AS "TenDiaDiem",
               d."MaMonAn", m."TenMonAn", d."MaNhanVien",
               dn."TenTaiKhoan" AS "TenNhanVien",
               d."SoLuong", d."DonGia", d."ThanhTien",
               d."MaCongTy", c."TenCongTy" {trangThai}
        FROM datmon d
        LEFT JOIN vitri v ON d."MaDiaDiem" = v."MaViTri"
        LEFT JOIN monan m ON d."MaMonAn" = m."MaMonAn"
        LEFT JOIN dangnhap dn ON d."MaNhanVien" = dn."TaiKhoan"
        LEFT JOIN congty c ON d."MaCongTy" = c."MaCongTy"
        WHERE d."Ngay" BETWEEN %s AND %s {status}
        ORDER BY d."Ngay" DESC
    """,
    "bc_congty": """
        SELECT c."MaCongTy", c."TenCongTy",
               COUNT(d."Id") AS "SoDon",
               COALESCE(SUM(d."DonGia"), 0) AS "DonGia",
               COALESCE(SUM(d."ThanhTien"), 0) AS "ThanhTien"
        FROM congty c
        LEFT JOIN datmon d ON c."MaCongTy" = d."MaCongTy"
            AND d."Ngay" BETWEEN %s AND %s {status_join}
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
            AND d."Ngay" BETWEEN %s AND %s {status_join}
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
            AND d."Ngay" BETWEEN %s AND %s {status_join}
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
        params = [str(from_date), str(to_date)]
    else:
        status_join = "" if show_all else "AND d.\"TrangThai\" = 'active'"
        query = template.format(status_join=status_join)
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
    return df


# --- Lookup helpers for dropdowns ---

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
        'WHERE m."TrangThai"=\'active\' AND vm."MaViTri"=%s ORDER BY m."MaMonAn"',
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


# --- Direct table reads ---

def load_table(table, show_all=False):
    c = get_conn()
    where = "" if show_all else "WHERE \"TrangThai\"='active'"
    df = pd.read_sql(f'SELECT * FROM "{table}" {where}', c)
    c.close()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M")
        elif df[col].dtype == "float64" and not df[col].dropna().empty and df[col].dropna().apply(float.is_integer).all():
            df[col] = df[col].astype("Int64")
    return df


# --- Delete ---

def hard_delete(table, pk_col, pk_val):
    c = get_conn()
    cur = c.cursor()
    cur.execute(f'DELETE FROM "{table}" WHERE "{pk_col}"=%s', (pk_val,))
    c.commit()
    c.close()


def _set_trangthai(table, pk_col, pk_val, status, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        f'UPDATE "{table}" SET "TrangThai"=%s, "NgaySua"=%s, "NguoiSua"=%s WHERE "{pk_col}"=%s',
        (status, _now(), actor, pk_val)
    )
    c.commit()
    c.close()


def soft_delete(table, pk_col, pk_val, actor):
    _set_trangthai(table, pk_col, pk_val, "inactive", actor)


def set_active(table, pk_col, pk_val, actor):
    _set_trangthai(table, pk_col, pk_val, "active", actor)


# --- Updates ---

def update_datmon(id_val, ngay, ma_diadiem, ma_monan, ma_nhanvien, so_luong, don_gia, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE datmon SET "Ngay"=%s,"MaDiaDiem"=%s,"MaMonAn"=%s,"MaNhanVien"=%s,'
        '"SoLuong"=%s,"DonGia"=%s,"ThanhTien"=%s,"NgaySua"=%s,"NguoiSua"=%s WHERE "Id"=%s',
        (ngay, ma_diadiem, ma_monan, ma_nhanvien, so_luong, don_gia, so_luong * don_gia, _now(), actor, id_val)
    )
    c.commit()
    c.close()


def update_congty(ma_congty, ten_congty, dia_chi, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE congty SET "TenCongTy"=%s,"DiaChi"=%s,"NgaySua"=%s,"NguoiSua"=%s WHERE "MaCongTy"=%s',
        (ten_congty, dia_chi, _now(), actor, ma_congty)
    )
    c.commit()
    c.close()


def update_vitri(ma_vitri, ten_vitri, ma_congty, bua_sang, bua_trua, bua_chieu, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE vitri SET "TenViTri"=%s,"MaCongTy"=%s,"BuaSang"=%s,"BuaTrua"=%s,"BuaChieu"=%s,'
        '"NgaySua"=%s,"NguoiSua"=%s WHERE "MaViTri"=%s',
        (ten_vitri, ma_congty, bua_sang, bua_trua, bua_chieu, _now(), actor, ma_vitri)
    )
    c.commit()
    c.close()


def update_nhanvien(tai_khoan, ten_tai_khoan, ma_diadiem, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE dangnhap SET "TenTaiKhoan"=%s,"MaDiaDiem"=%s,"NgaySua"=%s,"NguoiSua"=%s WHERE "TaiKhoan"=%s',
        (ten_tai_khoan, ma_diadiem, _now(), actor, tai_khoan)
    )
    c.commit()
    c.close()


# --- Inserts ---

@st.cache_data(ttl=300)
def get_vitri_detail(ma_vitri):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'SELECT "TenViTri","MaCongTy","BuaSang","BuaTrua","BuaChieu" FROM vitri WHERE "MaViTri"=%s',
        (ma_vitri,)
    )
    row = cur.fetchone()
    c.close()
    return row


def check_duplicate_order(ma_nhanvien, ngay, bua_an, ma_diadiem):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'SELECT COUNT(*) FROM datmon WHERE "MaNhanVien"=%s AND "Ngay"::date=%s AND "BuaAn"=%s AND "MaDiaDiem"=%s AND "TrangThai"=\'active\'',
        (ma_nhanvien, str(ngay), bua_an, ma_diadiem)
    )
    count = cur.fetchone()[0]
    c.close()
    return count > 0


def insert_datmon(ngay, ma_diadiem, ma_congty, ma_monan, ma_nhanvien, so_luong, don_gia, actor, bua_an=''):
    thanh_tien = so_luong * don_gia
    now = _now()
    id_val = f"ORD-{ngay.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO datmon ("Id","Ngay","MaDiaDiem","MaCongTy","MaMonAn","MaNhanVien","SoLuong","DonGia","ThanhTien","BuaAn","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") '
        'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\'active\',%s,%s,%s,%s)',
        (id_val, ngay, ma_diadiem, ma_congty, ma_monan, ma_nhanvien, so_luong, don_gia, thanh_tien, bua_an, now, actor, now, actor)
    )
    c.commit()
    c.close()
    get_thucdon_available.clear()
    get_thucdon_hom_nay.clear()


def insert_congty(ma_congty, ten_congty, dia_chi, trang_thai, actor):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO congty ("MaCongTy","TenCongTy","DiaChi","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
        (ma_congty, ten_congty, dia_chi, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def insert_vitri(ma_vitri, ten_vitri, ma_congty, trang_thai, actor):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO vitri ("MaViTri","TenViTri","MaCongTy","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
        (ma_vitri, ten_vitri, ma_congty, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def insert_nhanvien(tai_khoan, ten_tai_khoan, mat_khau, ma_diadiem, trang_thai, actor):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO dangnhap ("TaiKhoan","TenTaiKhoan","Adm","MatKhau","MaDiaDiem","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (%s,%s,0,%s,%s,%s,%s,%s,%s,%s)',
        (tai_khoan, ten_tai_khoan, mat_khau, ma_diadiem, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def insert_monan(ma_monan, ten_monan, don_gia, trang_thai, actor, hinh_anh=""):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO monan ("MaMonAn","TenMonAn","DonGia","HinhAnh","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (ma_monan, ten_monan, don_gia, hinh_anh or None, trang_thai, now, actor, now, actor)
    )
    c.commit()
    c.close()


def update_monan(ma_monan, ten_monan, don_gia, actor, hinh_anh=""):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE monan SET "TenMonAn"=%s,"DonGia"=%s,"HinhAnh"=%s,"NgaySua"=%s,"NguoiSua"=%s WHERE "MaMonAn"=%s',
        (ten_monan, don_gia, hinh_anh or None, _now(), actor, ma_monan)
    )
    c.commit()
    c.close()


def update_user_password(tai_khoan, new_password, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE dangnhap SET "MatKhau"=%s,"NgaySua"=%s,"NguoiSua"=%s WHERE "TaiKhoan"=%s',
        (new_password, _now(), actor, tai_khoan)
    )
    c.commit()
    c.close()


def toggle_admin(tai_khoan, adm_val, actor):
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE dangnhap SET "Adm"=%s,"NgaySua"=%s,"NguoiSua"=%s WHERE "TaiKhoan"=%s',
        (adm_val, _now(), actor, tai_khoan)
    )
    c.commit()
    c.close()


@st.cache_data(ttl=300)
def get_config(key):
    c = get_conn()
    cur = c.cursor()
    cur.execute('SELECT "GiaTri" FROM config WHERE "CauHinh"=%s', (key,))
    row = cur.fetchone()
    c.close()
    return row[0] if row else None


def set_config(key, value):
    c = get_conn()
    cur = c.cursor()
    cur.execute('UPDATE config SET "GiaTri"=%s WHERE "CauHinh"=%s', (value, key))
    c.commit()
    c.close()


def get_chu_ky_hom_nay():
    from datetime import date
    ref_str = get_config('ngay_bat_dau_chu_ky')
    if not ref_str:
        return 1
    ref = date.fromisoformat(ref_str.strip())
    return ((date.today() - ref).days % 14) + 1


@st.cache_data(ttl=120)
def get_thucdon(ma_vitri, chu_ky_ngay, show_all=False):
    status_filter = "" if show_all else "AND t.\"TrangThai\"='active'"
    c = get_conn()
    df = pd.read_sql(
        f'SELECT t."Id",t."MaMonAn",t."TrangThai",t."ThoiGianBatDau",t."SoSuatDuKien",'
        f'm."TenMonAn",m."DonGia" '
        f'FROM thucdon t JOIN monan m ON t."MaMonAn"=m."MaMonAn" '
        f'WHERE t."MaViTri"=%s AND t."ChuKyNgay"=%s {status_filter}',
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
        'WHERE t."ChuKyNgay"=%s AND t."MaViTri"!=%s AND t."TrangThai"=\'active\'',
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
        "VALUES (%s,%s,'',%s,%s,%s,'active',%s,%s,%s,%s)",
        (ma_vitri, chu_ky_ngay, ma_monan, thoi_gian, so_suat, now, actor, now, actor)
    )
    c.commit()
    c.close()
    _clear_thucdon_cache()


@st.cache_data(ttl=60)
def get_thucdon_available(ma_vitri, chu_ky_ngay):
    from datetime import date as _date
    today = str(_date.today())
    c = get_conn()
    df = pd.read_sql(
        'SELECT t."Id",t."MaMonAn",t."ThoiGianBatDau",t."SoSuatDuKien",'
        'm."TenMonAn",m."DonGia" '
        'FROM thucdon t '
        'JOIN monan m ON t."MaMonAn"=m."MaMonAn" '
        'LEFT JOIN menu mn ON mn."Ngay"=%s '
        '    AND mn."MaDiaDiem"=t."MaViTri" AND mn."MaMonAn"=t."MaMonAn" '
        'LEFT JOIN ('
        '    SELECT "MaDiaDiem","MaMonAn",COUNT(*) AS cnt '
        '    FROM datmon '
        '    WHERE "Ngay"=CURRENT_DATE AND "TrangThai"=\'active\' '
        '    GROUP BY "MaDiaDiem","MaMonAn"'
        ') oc ON oc."MaDiaDiem"=t."MaViTri" AND oc."MaMonAn"=t."MaMonAn" '
        'WHERE t."MaViTri"=%s AND t."ChuKyNgay"=%s '
        "AND t.\"TrangThai\"='active' "
        "AND (mn.\"TrangThai\" IS NULL OR mn.\"TrangThai\"!='done') "
        'AND (t."SoSuatDuKien" IS NULL OR t."SoSuatDuKien"=0 '
        '     OR COALESCE(oc.cnt,0) < t."SoSuatDuKien") '
        'ORDER BY m."TenMonAn"',
        c, params=[today, ma_vitri, chu_ky_ngay]
    )
    c.close()

    def _td_to_time(val):
        if val is None:
            return None
        if hasattr(val, 'total_seconds'):
            secs = int(val.total_seconds())
            h, rem = divmod(secs, 3600)
            m = rem // 60
            return datetime(2000, 1, 1, h, m).time()
        if hasattr(val, 'hour'):
            return val
        return None

    df["ThoiGianBatDau"] = df["ThoiGianBatDau"].apply(_td_to_time)
    return df


def finish_thucdon_today(ma_vitri, ma_monan, actor):
    from datetime import date as _date
    today = _date.today()
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'INSERT INTO menu ("Ngay","MaDiaDiem","MaMonAn","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua") '
        "VALUES (%s,%s,%s,'done',%s,%s,%s,%s) "
        'ON CONFLICT ("Ngay","MaDiaDiem","MaMonAn") DO UPDATE '
        'SET "TrangThai"=\'done\',\"NgaySua\"=%s,\"NguoiSua\"=%s',
        (today, ma_vitri, ma_monan, now, actor, now, actor, now, actor)
    )
    c.commit()
    c.close()
    get_thucdon_available.clear()
    get_thucdon_hom_nay.clear()


@st.cache_data(ttl=120)
def get_thucdon_hom_nay():
    chu_ky = get_chu_ky_hom_nay()
    from datetime import date as _date
    today = str(_date.today())
    c = get_conn()
    df = pd.read_sql(
        'SELECT v."TenViTri",m."TenMonAn",m."DonGia",m."HinhAnh" '
        'FROM thucdon t '
        'JOIN monan m ON t."MaMonAn"=m."MaMonAn" '
        'JOIN vitri v ON t."MaViTri"=v."MaViTri" '
        'LEFT JOIN menu mn ON mn."Ngay"=%s '
        '    AND mn."MaDiaDiem"=t."MaViTri" AND mn."MaMonAn"=t."MaMonAn" '
        'LEFT JOIN ('
        '    SELECT "MaDiaDiem","MaMonAn",COUNT(*) AS cnt '
        '    FROM datmon '
        '    WHERE "Ngay"=CURRENT_DATE AND "TrangThai"=\'active\' '
        '    GROUP BY "MaDiaDiem","MaMonAn"'
        ') oc ON oc."MaDiaDiem"=t."MaViTri" AND oc."MaMonAn"=t."MaMonAn" '
        "WHERE t.\"ChuKyNgay\"=%s AND t.\"TrangThai\"='active' "
        "AND (mn.\"TrangThai\" IS NULL OR mn.\"TrangThai\"!='done') "
        'AND (t."SoSuatDuKien" IS NULL OR t."SoSuatDuKien"=0 '
        '     OR COALESCE(oc.cnt,0) < t."SoSuatDuKien") '
        'ORDER BY v."TenViTri",m."TenMonAn"',
        c, params=[today, chu_ky]
    )
    c.close()
    return df, chu_ky


def update_thucdon(id_val, ma_monan, actor, thoi_gian=None, so_suat=None):
    now = _now()
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'UPDATE thucdon SET "MaMonAn"=%s,"ThoiGianBatDau"=%s,"SoSuatDuKien"=%s,"NgaySua"=%s,"NguoiSua"=%s WHERE "Id"=%s',
        (ma_monan, thoi_gian, so_suat, now, actor, id_val)
    )
    c.commit()
    c.close()
    _clear_thucdon_cache()


def delete_thucdon(id_val):
    c = get_conn()
    cur = c.cursor()
    cur.execute('DELETE FROM thucdon WHERE "Id"=%s', (id_val,))
    c.commit()
    c.close()
    _clear_thucdon_cache()


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
        return _sidebar_fallback()


def _sidebar_fallback():
    return [
        {
            "section": "Báo Cáo",
            "items": [
                {"label": "🍱 Đặt Món",   "key": "datmon",   "admin": False},
                {"label": "🏢 Công Ty",   "key": "congty",   "admin": False},
                {"label": "📍 Địa Điểm",  "key": "diadiem",  "admin": False},
                {"label": "👤 Nhân Viên", "key": "nhanvien", "admin": False},
            ],
        },
        {
            "section": "Thực Đơn",
            "items": [
                {"label": "📋 Thực Đơn Hôm Nay", "key": "thucdon", "admin": False},
                {"label": "🛒 Đặt Món",           "key": "order",   "admin": False},
            ],
        },
        {
            "section": "Đặt Món",
            "items": [
                {"label": "📋 Quản Lý Đặt Món", "key": "qldatmon",   "admin": True},
                {"label": "➕ Thêm Đặt Món",     "key": "themdatmon", "admin": True},
            ],
        },
        {
            "section": "Thực Đơn",
            "items": [
                {"label": "📅 Quản Lý Thực Đơn", "key": "qlthucdon",   "admin": True},
                {"label": "➕ Thêm Thực Đơn",     "key": "themthucdon", "admin": True},
            ],
        },
        {
            "section": "Món Ăn",
            "items": [
                {"label": "🍱 Món Ăn",      "key": "qlmonan",   "admin": True},
                {"label": "➕ Thêm Món Ăn", "key": "themmonan", "admin": True},
            ],
        },
        {
            "section": "Địa Điểm",
            "items": [
                {"label": "📍 Địa Điểm",     "key": "qlvitri",   "admin": True},
                {"label": "➕ Thêm Địa Điểm","key": "themvitri", "admin": True},
            ],
        },
        {
            "section": "Công Ty",
            "items": [
                {"label": "🏢 Công Ty",     "key": "qlcongty",  "admin": True},
                {"label": "➕ Thêm Công Ty","key": "themcongty","admin": True},
            ],
        },
        {
            "section": "Tài Khoản",
            "items": [
                {"label": "👥 Tài Khoản", "key": "taikhoan",  "admin": True},
                {"label": "📝 Đăng Ký",   "key": "dangnhap",  "admin": True},
            ],
        },
    ]
