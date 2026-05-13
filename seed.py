from werkzeug.security import generate_password_hash

from app import app, get_db, init_db


STUDENTS = [
    ("Maria", "Lopez", "10000001", "maria.lopez@email.com", "9175551001", "Computer Science", "Password123"),
    ("Jason", "Chen", "10000002", "jason.chen@email.com", "9175551002", "Mathematics", "Password123"),
]


with app.app_context():
    init_db()
    db = get_db()
    for first_name, last_name, emplid, email, phone, major, password in STUDENTS:
        db.execute(
            """
            INSERT OR IGNORE INTO students
            (first_name, last_name, emplid, email, phone, major, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                first_name,
                last_name,
                emplid,
                email.lower(),
                phone,
                major,
                generate_password_hash(password),
            ),
        )
    db.commit()

print("Study app seed data is ready.")
