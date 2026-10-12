from database import SessionLocal
from models import User
from auth import hash_password

# Create database session
db = SessionLocal()

# Check if admin already exists
admin = db.query(User).filter(
    User.email == "admin@gmail.com"
).first()


if admin:
    print("Admin already exists")

else:
    new_admin = User(
        name="Admin",
        email="admin@gmail.com",
        password=hash_password("admin123"),
        role="admin"
    )
    db.add(new_admin)
    db.commit()
    print("Admin created successfully")
    
db.close()