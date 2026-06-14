import sys
sys.path.append('src')
from core.database_manager import DatabaseManager

# Initialize database
db = DatabaseManager("database/app.db")

# Test user creation
success, user_id = db.create_user("testuser", "test@email.com", "password123", "Test User")
print(f"User created: {success}, ID: {user_id}")

# Test authentication
auth, uid, name = db.authenticate_user("testuser", "password123")
print(f"Authentication: {auth}, User: {name}")