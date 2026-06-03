-- ============================================================
-- Neon (PostgreSQL) schema for Quản Lý Suất Ăn
-- Run this once in your Neon SQL editor before deploying.
-- ============================================================

-- Companies
CREATE TABLE IF NOT EXISTS congty (
    "MaCongTy"  VARCHAR(50) PRIMARY KEY,
    "TenCongTy" VARCHAR(200) NOT NULL,
    "DiaChi"    TEXT,
    "TrangThai" VARCHAR(20) DEFAULT 'active',
    "NgayTao"   TIMESTAMP,
    "NguoiTao"  VARCHAR(100),
    "NgaySua"   TIMESTAMP,
    "NguoiSua"  VARCHAR(100)
);

-- Locations / canteens
CREATE TABLE IF NOT EXISTS vitri (
    "MaViTri"   VARCHAR(50) PRIMARY KEY,
    "TenViTri"  VARCHAR(200) NOT NULL,
    "MaCongTy"  VARCHAR(50) REFERENCES congty("MaCongTy"),
    "BuaSang"   BOOLEAN DEFAULT FALSE,
    "BuaTrua"   BOOLEAN DEFAULT FALSE,
    "BuaChieu"  BOOLEAN DEFAULT FALSE,
    "TrangThai" VARCHAR(20) DEFAULT 'active',
    "NgayTao"   TIMESTAMP,
    "NguoiTao"  VARCHAR(100),
    "NgaySua"   TIMESTAMP,
    "NguoiSua"  VARCHAR(100)
);

-- Food items
CREATE TABLE IF NOT EXISTS monan (
    "MaMonAn"   VARCHAR(50) PRIMARY KEY,
    "TenMonAn"  VARCHAR(200) NOT NULL,
    "DonGia"    NUMERIC(15,0) DEFAULT 0,
    "HinhAnh"   TEXT,
    "TrangThai" VARCHAR(20) DEFAULT 'active',
    "NgayTao"   TIMESTAMP,
    "NguoiTao"  VARCHAR(100),
    "NgaySua"   TIMESTAMP,
    "NguoiSua"  VARCHAR(100)
);

-- Junction: which food items are available at which location
CREATE TABLE IF NOT EXISTS vitri_monan (
    "MaViTri"  VARCHAR(50) REFERENCES vitri("MaViTri"),
    "MaMonAn"  VARCHAR(50) REFERENCES monan("MaMonAn"),
    PRIMARY KEY ("MaViTri", "MaMonAn")
);

-- Users / employees
CREATE TABLE IF NOT EXISTS dangnhap (
    "TaiKhoan"    VARCHAR(100) PRIMARY KEY,
    "TenTaiKhoan" VARCHAR(200) NOT NULL,
    "Adm"         SMALLINT DEFAULT 0,
    "MatKhau"     VARCHAR(200) NOT NULL,
    "MaDiaDiem"   VARCHAR(50) REFERENCES vitri("MaViTri"),
    "TrangThai"   VARCHAR(20) DEFAULT 'active',
    "NgayTao"     TIMESTAMP,
    "NguoiTao"    VARCHAR(100),
    "NgaySua"     TIMESTAMP,
    "NguoiSua"    VARCHAR(100)
);

-- Orders
CREATE TABLE IF NOT EXISTS datmon (
    "Id"         VARCHAR(50) PRIMARY KEY,
    "Ngay"       DATE NOT NULL,
    "MaDiaDiem"  VARCHAR(50) REFERENCES vitri("MaViTri"),
    "MaCongTy"   VARCHAR(50) REFERENCES congty("MaCongTy"),
    "MaMonAn"    VARCHAR(50) REFERENCES monan("MaMonAn"),
    "MaNhanVien" VARCHAR(100) REFERENCES dangnhap("TaiKhoan"),
    "SoLuong"    INTEGER DEFAULT 1,
    "DonGia"     NUMERIC(15,0) DEFAULT 0,
    "ThanhTien"  NUMERIC(15,0) DEFAULT 0,
    "BuaAn"      VARCHAR(20) DEFAULT '',
    "TrangThai"  VARCHAR(20) DEFAULT 'active',
    "NgayTao"    TIMESTAMP,
    "NguoiTao"   VARCHAR(100),
    "NgaySua"    TIMESTAMP,
    "NguoiSua"   VARCHAR(100)
);

-- 2-week rotating menu
CREATE TABLE IF NOT EXISTS thucdon (
    "Id"             SERIAL PRIMARY KEY,
    "MaViTri"        VARCHAR(50) REFERENCES vitri("MaViTri"),
    "ChuKyNgay"      SMALLINT NOT NULL,  -- 1-14
    "BuaAn"          VARCHAR(20) NOT NULL,
    "MaMonAn"        VARCHAR(50) REFERENCES monan("MaMonAn"),
    "ThoiGianBatDau" TIME,
    "SoSuatDuKien"   INTEGER,
    "TrangThai"      VARCHAR(20) DEFAULT 'active',
    "NgayTao"        TIMESTAMP,
    "NguoiTao"       VARCHAR(100),
    "NgaySua"        TIMESTAMP,
    "NguoiSua"       VARCHAR(100)
);

-- App configuration (key-value)
CREATE TABLE IF NOT EXISTS config (
    "CauHinh" VARCHAR(100) PRIMARY KEY,
    "GiaTri"  TEXT
);

-- Insert default cycle start date (change to your actual start date)
INSERT INTO config ("CauHinh","GiaTri")
VALUES ('ngay_bat_dau_chu_ky', CURRENT_DATE::TEXT)
ON CONFLICT ("CauHinh") DO NOTHING;

-- Sessions (replaces sessions.json)
CREATE TABLE IF NOT EXISTS sessions (
    "token"    VARCHAR(100) PRIMARY KEY,
    "username" VARCHAR(100) NOT NULL,
    "expiry"   TIMESTAMP NOT NULL
);

-- Index for fast session lookups
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions("token");
