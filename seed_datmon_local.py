import pyodbc
import numpy as np
from datetime import date, timedelta, datetime

TOTAL_ROWS = 1_200_000
CHUNK_SIZE = 100_000

def get_conn():
    for drv in ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]:
        try:
            extra = ";TrustServerCertificate=yes" if "18" in drv else ""
            cs = f"DRIVER={{{drv}}};SERVER=localhost;DATABASE=qlsuatan;Trusted_Connection=yes{extra};"
            return pyodbc.connect(cs)
        except Exception:
            continue
    raise RuntimeError("Cannot connect to local SQL Server. Is it running?")

conn = get_conn()
cursor = conn.cursor()
cursor.fast_executemany = True

cursor.execute('SELECT "MaViTri"  FROM vitri    WHERE "TrangThai"=\'active\'')
vitri_ids  = [r[0] for r in cursor.fetchall()]
cursor.execute('SELECT "MaCongTy" FROM congty   WHERE "TrangThai"=\'active\'')
congty_ids = [r[0] for r in cursor.fetchall()]
cursor.execute('SELECT "MaMonAn"  FROM monan    WHERE "TrangThai"=\'active\'')
monan_ids  = [r[0] for r in cursor.fetchall()]
cursor.execute('SELECT "TaiKhoan" FROM dangnhap WHERE "TrangThai"=\'active\'')
nv_ids     = [r[0] for r in cursor.fetchall()]

cursor.execute('SELECT COUNT(*) FROM datmon')
next_id = cursor.fetchone()[0] + 1

INSERT_SQL = """
INSERT INTO datmon
    ("Id","Ngay","MaDiaDiem","MaCongTy","MaMonAn","MaNhanVien",
     "BuaAn","SoLuong","DonGia","ThanhTien",
     "TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua")
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""

rng        = np.random.default_rng(42)
start      = date(2023, 1, 1)
days_range = (date.today() - start).days
bua_an     = ["Sáng", "Trưa", "Chiều"]
don_gias   = [25000, 30000, 35000, 40000, 45000]
now_dt     = datetime.now()

print(f"Seeding {TOTAL_ROWS:,} rows via fast_executemany in chunks of {CHUNK_SIZE:,}...")

written = 0
chunk_num = 0

while written < TOTAL_ROWS:
    n = min(CHUNK_SIZE, TOTAL_ROWS - written)

    offsets  = rng.integers(0, days_range, size=n)
    vitris   = rng.choice(vitri_ids,  size=n)
    congties = rng.choice(congty_ids, size=n)
    monans   = rng.choice(monan_ids,  size=n)
    nvs      = rng.choice(nv_ids,     size=n)
    buas     = rng.choice(bua_an,     size=n)
    sls      = rng.integers(1, 5,     size=n)
    dgs      = rng.choice(don_gias,   size=n)

    rows = []
    for i in range(n):
        ngay = start + timedelta(days=int(offsets[i]))
        sl   = int(sls[i])
        dg   = int(dgs[i])
        rows.append((
            f"SEED-{next_id + written + i}",
            ngay, str(vitris[i]), str(congties[i]), str(monans[i]), str(nvs[i]),
            str(buas[i]), sl, dg, sl * dg,
            "active", now_dt, "seed", now_dt, "seed",
        ))

    cursor.executemany(INSERT_SQL, rows)
    conn.commit()

    written   += n
    chunk_num += 1
    print(f"  chunk {chunk_num}: {written:,} / {TOTAL_ROWS:,}")

cursor.close()
conn.close()
print("Done.")
