import pyodbc
import numpy as np
from datetime import datetime

TOTAL_ROWS = 800_000
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

cursor.execute('SELECT COUNT(*) FROM monan')
next_id = cursor.fetchone()[0] + 1

INSERT_SQL = """
INSERT INTO monan
    ("MaMonAn","TenMonAn","DonGia","HinhAnh","TrangThai","NgayTao","NguoiTao","NgaySua","NguoiSua")
VALUES (?,?,?,?,?,?,?,?,?)
"""

rng       = np.random.default_rng(99)
don_gias  = [20000, 25000, 30000, 35000, 40000, 45000, 50000]
trang_thai = ["active", "active", "active", "inactive"]
prefixes  = ["Cơm", "Phở", "Bún", "Mì", "Bánh", "Xôi", "Cháo", "Lẩu", "Bò", "Gà", "Heo", "Cá", "Tôm", "Rau"]
suffixes  = ["đặc biệt", "thường", "số 1", "số 2", "cao cấp", "bình dân", "truyền thống", "mới", "thập cẩm", "ngon"]
now_dt    = datetime.now()

print(f"Seeding {TOTAL_ROWS:,} rows in chunks of {CHUNK_SIZE:,}...")

written = 0
chunk_num = 0

while written < TOTAL_ROWS:
    n = min(CHUNK_SIZE, TOTAL_ROWS - written)

    rows = []
    for i in range(n):
        idx    = next_id + written + i
        prefix = prefixes[rng.integers(0, len(prefixes))]
        suffix = suffixes[rng.integers(0, len(suffixes))]
        ten    = f"{prefix} {suffix} {idx}"
        dg     = int(don_gias[rng.integers(0, len(don_gias))])
        tt     = trang_thai[rng.integers(0, len(trang_thai))]
        rows.append((
            f"MN-{idx}",
            ten, dg, None, tt,
            now_dt, "seed", now_dt, "seed",
        ))

    cursor.executemany(INSERT_SQL, rows)
    conn.commit()

    written   += n
    chunk_num += 1
    print(f"  chunk {chunk_num}: {written:,} / {TOTAL_ROWS:,}")

cursor.close()
conn.close()
print("Done.")
