import pandas as pd
from sqlalchemy import create_engine, text

NEON_URL = (
    "postgresql://neondb_owner:npg_TXFWz1b2PYcR"
    "@ep-shiny-cell-aoiymiow-pooler.c-2.ap-southeast-1.aws.neon.tech"
    "/neondb?sslmode=require&channel_binding=require"
)

# Try ODBC Driver 17 first, fall back to 18
try:
    MS_URL = (
        "mssql+pyodbc://localhost/qlsuatan"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )
    ms_engine = create_engine(MS_URL)
    with ms_engine.connect() as _:
        pass
except Exception:
    MS_URL = (
        "mssql+pyodbc://localhost/qlsuatan"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&trusted_connection=yes&TrustServerCertificate=yes"
    )
    ms_engine = create_engine(MS_URL)

pg_engine = create_engine(NEON_URL)

# Get all tables from Neon public schema
with pg_engine.connect() as conn:
    result = conn.execute(text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
        "ORDER BY table_name"
    ))
    tables = [row[0] for row in result]

print(f"Found {len(tables)} tables: {tables}\n")

success, failed = [], []

for table in tables:
    print(f"  Migrating [{table}]... ", end="", flush=True)
    try:
        df = pd.read_sql(f'SELECT * FROM "{table}"', pg_engine)
        df.to_sql(table, ms_engine, if_exists="replace", index=False)
        print(f"OK  ({len(df)} rows)")
        success.append(table)
    except Exception as e:
        print(f"FAILED\n    -> {e}")
        failed.append(table)

print(f"\nDone. {len(success)} succeeded, {len(failed)} failed.")
if failed:
    print(f"Failed tables: {failed}")
