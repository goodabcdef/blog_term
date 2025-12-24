# Database Schema (ERD)

## 1. Users
- id (PK), email, hashed_password, role, created_at

## 2. Posts
- id (PK), title, content, owner_id (FK), view_count, created_at
- 관계: User(N:1), Comments(1:N), Likes(1:N), Tags(N:N)

## 3. Comments
- id (PK), content, post_id (FK), owner_id (FK)

## 4. Tags & PostTags
- Tag: id, name
- PostTags: post_id, tag_id (Many-to-Many)

## 5. Likes
- id, user_id (FK), post_id (FK)
