#!/usr/bin/env python3
"""
Initialize the PSI service with users.
Run this script to create user accounts.
"""

import os
import sys
from database import Database

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python init_user.py <username> <password> [role]")
        print("Role can be 'user' (default) or 'admin'")
        print("")
        print("Examples:")
        print("  python init_user.py john_doe mypassword123        # Creates regular user")
        print("  python init_user.py admin adminpass456 admin     # Creates admin user")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) == 4 else "user"

    # Validate role
    if role not in ["user", "admin"]:
        print("❌ Role must be 'user' or 'admin'")
        sys.exit(1)

    # Initialize database
    db = Database()

    # Create user
    try:
        if db.create_user(username, password, role):
            print(f"✅ {role.capitalize()} user '{username}' created successfully!")
            if role == "admin":
                print("🔑 This user has admin privileges and can view all sessions.")
            else:
                print("👤 This is a regular user with standard privileges.")
            print("You can now log in to the web dashboard.")
        else:
            print(f"❌ Failed to create user '{username}' (user may already exist)")
            sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()