import asyncio

import sys
import os

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.app.database import async_session_factory, Base, engine
from server.app.models.user import User, UserRole
from server.app.services.auth_service import register_user
from server.app.models.user import User

async def create_admin():
    print("Checking database schemas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Connecting to database...")
    async with async_session_factory() as db:
        try:
            user, _, _ = await register_user(db, "admin@jarvis.com", "Admin123!", "System Admin")
            user.role = UserRole.ADMIN
            user.plan = "enterprise"
            await db.commit()
            print("\nSuccessfully created Admin User!")
            print("ID (Email): admin@jarvis.com")
            print("Password:   Admin123!")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("\nAdmin User already exists!")
                print("ID (Email): admin@jarvis.com")
                print("Password:   Admin123!")
            else:
                print(f"\nFailed to create admin: {e}")

if __name__ == "__main__":
    asyncio.run(create_admin())
