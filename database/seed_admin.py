from getpass import getpass

from app import create_app
from app.services.admin_service import AdminService
from app.utils.validation import ValidationError


def seed_admin():
    """Create an initial admin account interactively."""
    app = create_app()
    with app.app_context():
        full_name = input("Full name: ").strip()
        email = input("Email: ").strip().lower()
        password = getpass("Password: ").strip()
        confirm_password = getpass("Confirm password: ").strip()

        if not full_name or not email or not password:
            print("Name, email, and password are required.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        try:
            admin = AdminService.create_admin(full_name=full_name, email=email, password=password)
        except ValidationError as exc:
            print(exc.errors["email"][0])
            return
        print(f"Admin created successfully: {admin.email}")


if __name__ == "__main__":
    seed_admin()
