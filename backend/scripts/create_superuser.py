# backend/scripts/create_superuser.py
#
# Usage:
#   docker compose exec backend python scripts/create_superuser.py
#
# Run this once after initial deployment to create the first super admin.
# After that, super admins can promote other users via the API.

import sys
import os

# Add the backend root to the Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole


def create_superuser():
    """
    Creates a super admin user interactively.

    Prompts for an email address, then either:
    - Creates a new user with role=super_admin if the email is new
    - Promotes an existing user to super_admin if they already have an account

    The user still logs in via OTP — there is no password.
    """
    print("\n=== StudyBuddy Superuser Creation ===\n")

    email = input("Enter the super admin email address: ").strip().lower()

    if not email or "@" not in email:
        print("Error: Please enter a valid email address.")
        sys.exit(1)

    db: Session = SessionLocal()

    try:
        # Check if a user with this email already exists
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            if existing_user.role == UserRole.SUPER_ADMIN:
                print(f"\n{email} is already a super admin. Nothing to do.")
                return

            # Promote existing user to super admin
            existing_user.role = UserRole.SUPER_ADMIN
            db.commit()
            print(f"\nSuccess! {email} has been promoted to super admin.")
            print(f"User ID: {existing_user.id}")
            print(f"Previous role: was {existing_user.role.value}")

        else:
            # Create a new user with super_admin role
            new_user = User(
                email=email,
                auth_provider="email_otp",
                auth_subject_id=email,
                role=UserRole.SUPER_ADMIN,
                is_active=True,
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            print(f"\nSuccess! Super admin created.")
            print(f"Email:   {email}")
            print(f"User ID: {new_user.id}")
            print(f"Role:    {new_user.role.value}")

        print("\nThis user can now log in via OTP at the normal login page.")
        print("After logging in, they can promote other users via:")
        print("  PATCH /admin/users/promote\n")

    except Exception as e:
        db.rollback()
        print(f"\nError creating superuser: {e}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    create_superuser()