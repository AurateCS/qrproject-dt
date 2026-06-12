import os
import io
import csv
import numpy as np
import psycopg2
from datetime import date, timedelta

DB_URL = os.environ.get("DATABASE_URL", "")
if not DB_URL:
    DB_URL = (
        "postgresql://neondb_owner:npg_TXFWz1b2PYcR"
        "@ep-shiny-cell-aoiymiow-pooler.c-2.ap-southeast-1.aws.neon.tech"
        "/neondb?sslmode=require&channel_binding=require"
    )

TOTAL_ROWS = 1_000_000
CHUNK_SIZE = 100_000

conn   = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# Pull real FK values
cursor.execute('SELECT "MaViTri"  FROM vitri    WHERE "TrangThai"=\'active\'')
vitri_ids  = [r[0] for r in cursor.fetchall()]
cursor.execute('SELECT "MaCongTy" FROM congty   WHERE "TrangThai"=\'active\'')
congty_ids = [r[0] for r in cursor.fetchall()]
cursor.execute('SELECT "MaMonAn"  FROM monan    WHERE "TrangThai"=\'active\'')
monan_ids  = [r[0] for r in cursor.fetchall()]
cursor.execute('SELECT "TaiKhoan" FROM dangnhap WHERE "TrangThai"=\'active\'')
nv_ids     = [r[0] for r in cursor.fetchall()]

COLUMNS = [
    "Id",
    "Ngay", "MaDiaDiem", "MaCongTy", "MaMonAn", "MaNhanVien",
    "BuaAn", "SoLuong", "DonGia", "ThanhTien",
    "TrangThai", "NgayTao", "NguoiTao", "NgaySua", "NguoiSua",
]
_cols    = '","'.join(COLUMNS)
COPY_SQL = f'COPY datmon ("{_cols}") FROM STDIN WITH (FORMAT CSV)'

cursor.execute('SELECT COUNT(*) FROM datmon')
next_id = cursor.fetchone()[0] + 1

rng        = np.random.default_rng(42)
start      = date(2023, 1, 1)
days_range = (date.today() - start).days
bua_an     = ["Sáng", "Trưa", "Chiều"]
don_gias   = [25000, 30000, 35000, 40000, 45000]
now_str    = date.today().isoformat()

print(f"Seeding {TOTAL_ROWS:,} rows via COPY protocol in chunks of {CHUNK_SIZE:,}...")

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

    buf = io.StringIO()
    writer = csv.writer(buf)
    for i in range(n):
        ngay = (start + timedelta(days=int(offsets[i]))).isoformat()
        sl   = int(sls[i])
        dg   = int(dgs[i])
        writer.writerow([
            f"SEED-{next_id + written + i}",
            ngay, vitris[i], congties[i], monans[i], nvs[i],
            buas[i], sl, dg, sl * dg,
            "active", now_str, "seed", now_str, "seed",
        ])

    buf.seek(0)
    cursor.copy_expert(COPY_SQL, buf)
    conn.commit()

    written   += n
    chunk_num += 1
    print(f"  chunk {chunk_num}: {written:,} / {TOTAL_ROWS:,}")

cursor.close()
conn.close()
print("Done.")
