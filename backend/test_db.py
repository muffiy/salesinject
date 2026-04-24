import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:Xcapofficem7.%2F@db.mtvgvkgynjuszpofhuym.supabase.co:5432/postgres")
    print("Direct connection OK!")
    conn.close()
except Exception as e:
    print(f"Direct connection failed: {e}")
