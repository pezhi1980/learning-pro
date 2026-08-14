"""
create_admin.py — Run this script to create an admin user in Supabase.
Usage: python create_admin.py
"""

import os
import sys

# Fix Unicode output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────
# 🔧 FILL IN YOUR VALUES HERE
# ─────────────────────────────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_FIRST_NAME = os.getenv("ADMIN_FIRST_NAME", "Admin")
ADMIN_LAST_NAME = os.getenv("ADMIN_LAST_NAME", "User")

# ─────────────────────────────────────────────────────────────

from supabase import create_client

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print(f"Creating admin user: {ADMIN_EMAIL}")

# Step 1: Create auth user
try:
    res = sb.auth.admin.create_user({
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "email_confirm": True,  # skip email confirmation
        "user_metadata": {
            "first_name": ADMIN_FIRST_NAME,
            "last_name": ADMIN_LAST_NAME,
        }
    })
    user_id = res.user.id
    print(f"✅ Auth user created: {user_id}")
except Exception as e:
    print(f"[!] Auth user might already exist: {e}")
    # Try to get existing user
    users = sb.auth.admin.list_users()
    user_id = None
    for u in users:
        if u.email == ADMIN_EMAIL:
            user_id = u.id
            print(f"Found existing user: {user_id}")
            break
    if not user_id:
        print("❌ Could not find or create user. Exiting.")
        exit(1)

# Step 2: Upsert profile with role = 'admin'
try:
    sb.table("profiles").upsert({
        "id": user_id,
        "first_name": ADMIN_FIRST_NAME,
        "last_name": ADMIN_LAST_NAME,
        "role": "admin",
        "native_language": "fa",
    }).execute()
    print("✅ Profile set with role = 'admin'")
except Exception as e:
    print(f"❌ Failed to set profile: {e}")
    exit(1)

print()
print("=" * 50)
print("🎉 Admin user ready!")
print(f"   Email:    {ADMIN_EMAIL}")
print(f"   Password: {ADMIN_PASSWORD}")
print(f"   Role:     admin")
print("=" * 50)
print()
print("Now open http://localhost:8080 and login with these credentials.")
