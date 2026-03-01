import os
import sys
import subprocess
import getpass
import sqlalchemy

# ── paths ──────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE   = os.path.join(BASE_DIR, "ERP_database.sql")
SEED_FILE     = os.path.join(BASE_DIR, "fill_database.sql")


# ── helpers ────────────────────────────────────────────────────────────────
def separator():
    print("=" * 55)

def run_sql_file(host, port, user, password, filepath):
    """Execute a .sql file using the mysql CLI."""
    cmd = [
        "mysql",
        f"-h{host}",
        f"-P{port}",
        f"-u{user}",
        f"-p{password}",
        "--default-character-set=utf8mb4",
    ]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                capture_output=True,
                text=True,
            )
        if result.returncode != 0:
            print(f"\n[ERROR] MySQL returned an error:")
            print(result.stderr)
            return False
        return True
    except FileNotFoundError:
        print("\n[ERROR] 'mysql' command not found.")
        print("  Make sure MySQL client is installed and added to PATH.")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

def verify_connection(host, port, user, password):
    """Verify DB was created successfully using SQLAlchemy."""
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/erp"
    try:
        engine = sqlalchemy.create_engine(url)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        engine.dispose()
        return True
    except Exception as e:
        print(f"\n[ERROR] Could not connect after setup: {e}")
        return False


# ── main ───────────────────────────────────────────────────────────────────
def main():
    separator()
    print("       ERP — Database Setup Utility")
    separator()

    # ── connection info ────────────────────────────────────────────────────
    print("\nMySQL connection settings (press Enter for defaults):\n")
    host     = input("  Host     [localhost] : ").strip() or "localhost"
    port     = input("  Port     [3306]      : ").strip() or "3306"
    user     = input("  User     [root]      : ").strip() or "root"
    password = getpass.getpass("  Password             : ")

    # ── mode choice ────────────────────────────────────────────────────────
    separator()
    print("\nChoose setup mode:\n")
    print("  [1]  Empty database   — schema only, no data")
    print("  [2]  With fake data   — schema + sample data for development")
    print("  [0]  Cancel\n")

    choice = input("Your choice: ").strip()

    if choice == "0":
        print("\nCancelled. Nothing was done.")
        sys.exit(0)

    if choice not in ("1", "2"):
        print("\n[ERROR] Invalid choice. Exiting.")
        sys.exit(1)

    # ── confirmation ───────────────────────────────────────────────────────
    separator()
    mode_label = "EMPTY database" if choice == "1" else "database WITH FAKE DATA"
    print(f"\n  ⚠  This will DROP and recreate the 'erp' database ({mode_label}).")
    confirm = input("  Type 'yes' to confirm: ").strip().lower()

    if confirm != "yes":
        print("\nCancelled. Nothing was done.")
        sys.exit(0)

    # ── execute ────────────────────────────────────────────────────────────
    separator()
    print(f"\n[1/{'2' if choice == '2' else '1'}] Running schema file...")
    print(f"      → {SCHEMA_FILE}")

    ok = run_sql_file(host, port, user, password, SCHEMA_FILE)
    if not ok:
        print("\n[FAILED] Schema creation failed. Aborting.")
        sys.exit(1)

    print("      ✓ Schema created successfully.")

    # verify connection after schema created
    if verify_connection(host, port, user, password):
        print("      ✓ Connection to 'erp' database verified.")

    if choice == "2":
        print(f"\n[2/2] Running seed data file...")
        print(f"      → {SEED_FILE}")

        ok = run_sql_file(host, port, user, password, SEED_FILE)
        if not ok:
            print("\n[FAILED] Seed data insertion failed.")
            sys.exit(1)

        print("      ✓ Fake data inserted successfully.")

    # ── done ───────────────────────────────────────────────────────────────
    separator()
    print("\n  ✓ Database setup complete!\n")
    if choice == "2":
        print("  Users created (password = 1234):")
        print("    admin, admin2, karim, sara, youssef, fatima, hamid\n")
    separator()


if __name__ == "__main__":
    main()