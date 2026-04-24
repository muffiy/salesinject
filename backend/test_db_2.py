import psycopg2

passwords = ["Xcapofficem7.%2F%2F", "xcapofficem7.%2F%2F"]
success = False

for pwd in passwords:
    try:
        url = f"postgresql://postgres:{pwd}@db.thdibwoiyhbonrzttsgj.supabase.co:5432/postgres"
        conn = psycopg2.connect(url, connect_timeout=5)
        print(f"Direct connection OK with password starting with: {pwd[0]}")
        with open(".env", "w") as f:
             f.write(f'DATABASE_URL="{url}"\n')
        conn.close()
        success = True
        break
    except Exception as e:
        print(f"Failed for {pwd[0]}: {e}")

if not success:
    print("All direct connections failed.")
