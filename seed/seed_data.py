import random
from sqlalchemy.orm import Session
from src.database import SessionLocal, engine, Base
from src.models.user import User
from src.models.blog import Post, Comment, Tag
from src.core.security import get_password_hash

# DB 연결
db = SessionLocal()

def seed():
    print("🌱 Seeding data...")

    # 1. Users (10명 생성)
    users = []
    for i in range(10):
        email = f"user{i}@example.com"
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            u = User(
                email=email, 
                hashed_password=get_password_hash("password123"),
                role="ROLE_ADMIN" if i == 0 else "ROLE_USER"
            )
            db.add(u)
            users.append(u)
    db.commit()
    print(f"✅ Users created.")

    # Users 다시 조회 (ID 확보용)
    users = db.query(User).all()

    # 2. Tags (5개 생성)
    tag_names = ["Python", "FastAPI", "Docker", "JCloud", "Life"]
    tags = []
    for name in tag_names:
        t = db.query(Tag).filter(Tag.name == name).first()
        if not t:
            t = Tag(name=name)
            db.add(t)
            tags.append(t)
    db.commit()
    tags = db.query(Tag).all()
    print(f"✅ Tags created.")

    # 3. Posts (200개 생성 - 핵심 요구사항)
    for i in range(200):
        owner = random.choice(users)
        post = Post(
            title=f"Term Project Post Title #{i}",
            content=f"This is a dummy content for post #{i}. We need 200 items.",
            owner_id=owner.id,
            view_count=random.randint(0, 1000)
        )
        # 태그 랜덤 추가
        post.tags.append(random.choice(tags))
        db.add(post)
    
    db.commit()
    print(f"✅ 200 Posts created.")

    # 4. Comments (50개 생성)
    posts = db.query(Post).limit(50).all()
    for p in posts:
        c = Comment(
            content=f"Nice post! {random.randint(1, 100)}",
            post_id=p.id,
            owner_id=random.choice(users).id
        )
        db.add(c)
    db.commit()
    print(f"✅ Comments created.")
    print("🎉 Seeding Completed!")

if __name__ == "__main__":
    seed()