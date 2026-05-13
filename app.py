from functools import wraps
import os
import sqlite3
from urllib.parse import parse_qs, urlparse

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "study-app-secret-key"
DATABASE = "database.db"


MIT_6100L_PLAYLIST = "https://www.youtube.com/playlist?list=PLUl4u3cNGP62A-ynp6v6-LGBCzeH3VAQB"
MIT_6100L_VIDEOS = [
    "Introduction to CS and Programming Using Python",
    "Strings, Input/Output, and Branching",
    "Iteration",
    "Loops over Strings, Guess-and-Check, and Binary",
    "Floats and Approximation Methods",
    "Bisection Search",
    "Decomposition, Abstraction, and Functions",
    "Functions as Objects",
    "Lambda Functions, Tuples, and Lists",
    "Lists and Mutability",
    "Aliasing and Cloning",
    "List Comprehension, Functions as Objects, Testing, and Debugging",
    "Exceptions and Assertions",
    "Dictionaries",
    "Recursion",
    "Recursion on Non-numerics",
    "Python Classes",
    "More Python Class Methods",
    "Inheritance",
    "Fitness Tracker Object-Oriented Programming Example",
    "Timing Programs and Counting Operations",
    "Big Oh and Theta",
    "Complexity Classes Examples",
    "Sorting Algorithms",
    "Plotting",
    "List Access, Hashing, Simulations, and Wrap-Up",
]
MAT301_PLAYLIST = "https://www.youtube.com/watch?v=-G8BlrD1X_8&list=PL9nkbpC3uJfoYZd7mgr66a0ZmvzFpyQpn"
MAT301_VIDEOS = [
    "Computation of Limits",
    "Derivatives using the definition via Limits",
    "The Chain Rule",
    "Implicit Differentiation",
    "Maxima and Minima",
    "Mean Value Theorem",
    "Limits at Infinity",
    "Optimization",
    "L'Hopital's Rule",
    "Newton's Method",
    "Antiderivatives",
]
CIS395_PLAYLIST = "https://www.youtube.com/playlist?list=PLBlnK6fEyqRi_CUQ-FXxgzKQ1dwr_ZJWZ"

ENG201_READINGS = [
    {
        "title": "The Metamorphosis",
        "author": "Franz Kafka",
        "theme": "Alienation, family obligation, and the fragile line between identity and social worth.",
        "url": "https://www.gutenberg.org/files/2542/2542-h/2542-h.htm",
    },
    {
        "title": "Anna Karenina",
        "author": "Leo Tolstoy",
        "theme": "Love, social pressure, moral conflict, and the personal cost of public judgment.",
        "url": "https://www.gutenberg.org/files/1399/1399-h/1399-h.htm",
    },
    {
        "title": "Girl",
        "author": "Jamaica Kincaid",
        "theme": "Voice, gender expectations, cultural instruction, and inherited rules for survival.",
        "url": "https://www.newyorker.com/magazine/1978/06/26/girl",
    },
    {
        "title": "I Only Came to Use the Phone",
        "author": "Gabriel Garcia Marquez",
        "theme": "Confinement, miscommunication, power, and the instability of truth inside institutions.",
        "url": "https://havenner.weebly.com/uploads/2/0/5/7/20575006/i_only_came_to_use_the_phone.pdf",
    },
    {
        "title": "Mother Tongue",
        "author": "Amy Tan",
        "theme": "Language, identity, family voice, and how power shapes whose English is respected.",
        "url": "https://sites.sandiego.edu/wp-fyw/files/2023/02/Mother-Tongue-by-Amy-Tan.pdf",
    },
]


COURSE_SEED = [
    {
        "code": "CIS395",
        "title": "Database Systems I",
        "description": "Build practical skills in database design, relational models, SQL, ER modeling, and database application projects.",
        "professor": ("Younes Benkarroum", "ybenkarroum@bmcc.cuny.edu", "F-1030L", "Mondays 2:00 PM - 3:00 PM and Wednesdays 10:30 AM - 11:30 AM"),
        "book_title": "Database Systems: A Practical Approach to Design, Implementation and Management, 6th Edition",
        "book_link": "https://sites.google.com/view/cis395",
        "video_title": "Database Systems Video Playlist",
        "video_url": CIS395_PLAYLIST,
        "videos": [
            ("Database Systems Playlist", CIS395_PLAYLIST),
        ],
        "help_text": "Ask for help with SQL queries, database design, and course assignments.",
        "quiz": [
            ("Which SQL command is used to read data from a table?", "SELECT", "INSERT", "DELETE", "UPDATE", "SELECT"),
            ("What does a primary key do?", "Stores images", "Uniquely identifies a row", "Deletes duplicates", "Runs Python code", "Uniquely identifies a row"),
        ],
        "materials": [
            ("CIS395 Syllabus", "Syllabus", "pdfs/cis395/CIS 395 - Syllabus.pdf", "Course syllabus with announcements, projects, labs, lectures, and class information."),
            ("CodeLab", "Lab Tool", "https://codelab.turingscraft.com/login", "Use class access code CUNY-32295-PEDC-63 for database practice."),
            ("SQLite Online", "Database Tool", "https://sqliteonline.com/", "Practice SQL queries directly in the browser."),
            ("Lecture 01 - Introduction to Databases", "Lecture", "pdfs/cis395/CIS395_01.pdf", "Local PDF for database concepts and course introduction."),
            ("Lecture 02 - The Relational Model", "Lecture", "pdfs/cis395/CIS395_02.pdf", "Local PDF for relational database concepts."),
            ("Lecture 03 - Relational Algebra", "Lecture", "pdfs/cis395/CIS395_03.pdf", "Local PDF for relational algebra practice."),
            ("Lecture 04 - Relational Calculus", "Lecture", "pdfs/cis395/CIS395_04.pdf", "Local PDF for relational calculus notes."),
            ("Lecture 05 - SQL Data Manipulation", "Lecture", "pdfs/cis395/CIS395_05.pdf", "Local PDF for SQL data manipulation."),
            ("Lecture 06 - SQL Data Definition", "Lecture", "pdfs/cis395/CIS395_06b.pdf", "Local PDF for SQL schema and table definitions."),
            ("Lecture 07 - ER Modeling", "Lecture", "pdfs/cis395/CIS395_07b.pdf", "Local PDF for entity relationship modeling."),
            ("Lecture 08 - Database Design", "Lecture", "pdfs/cis395/CIS395_08.pdf", "Local PDF for database design concepts."),
            ("Lecture 09 - Normalization", "Lecture", "pdfs/cis395/CIS395_09b.pdf", "Local PDF for normalization and design practice."),
        ],
        "groups": [
            ("Database Builders Group", "Mondays at 6:00 PM", "Library Room 2", "Peer review for SQL exercises, labs, and weekly quizzes."),
        ],
    },
    {
        "code": "CSC203",
        "title": "Python Programming for Data Science",
        "description": "Learn Python programming foundations for data science using labs, lectures, CodeLab practice, and online coding tools.",
        "professor": ("Younes Benkarroum", "ybenkarroum@bmcc.cuny.edu", "F1030L", "Mondays 2:00 PM - 4:00 PM"),
        "book_title": "Intro to Python for Computer Science and Data Science, 1st Edition",
        "book_link": "https://www.pearson.com/en-us/subject-catalog/p/intro-to-python-for-computer-science-and-data-science-learning-to-program-with-ai-big-data-and-the-cloud/P200000003493",
        "video_title": "Ana Bell: Introduction to CS and Programming Using Python",
        "video_url": "https://www.youtube.com/watch?v=xAcTmDO6NTI",
        "videos": [
            (f"Lecture {index}: {title}", f"{MIT_6100L_PLAYLIST}&index={index}")
            for index, title in enumerate(MIT_6100L_VIDEOS, start=1)
        ],
        "help_text": "Get one-on-one support for assignments, debugging, and exam prep.",
        "quiz": [
            ("Which keyword defines a function in Python?", "for", "def", "class", "return", "def"),
            ("Which data type stores true or false values?", "string", "integer", "boolean", "list", "boolean"),
        ],
        "materials": [
            ("CodeLab", "Lab Tool", "https://codelab.turingscraft.com/login", "Use class access code CUNY-32883-FRSK-67 for Python lab practice."),
            ("Online Python Compiler", "Coding Tool", "https://www.programiz.com/python-programming/online-compiler/", "Run Python code in the browser while studying and testing examples."),
            ("CSC203 Syllabus", "Syllabus", "pdfs/csc203/CSC 203 - Syllabus.pdf", "Local PDF summary of syllabus, lecture chapters, labs, and class announcements."),
            ("Lecture Chapter 01", "Lecture", "pdfs/csc203/Chapter_01.pdf", "Local PDF for CSC203 Chapter 01."),
            ("Lecture Chapter 02", "Lecture", "pdfs/csc203/Chapter_02.pdf", "Local PDF for CSC203 Chapter 02."),
            ("Lecture Chapter 03", "Lecture", "pdfs/csc203/Chapter_03.pdf", "Local PDF for CSC203 Chapter 03."),
            ("Lecture Chapter 04", "Lecture", "pdfs/csc203/Chapter_04.pdf", "Local PDF for CSC203 Chapter 04."),
            ("Lecture Chapter 05", "Lecture", "pdfs/csc203/Chapter_05.pdf", "Local PDF for CSC203 Chapter 05."),
            ("Lecture Chapter 06", "Lecture", "pdfs/csc203/Chapter_06.pdf", "Local PDF for CSC203 Chapter 06."),
            ("Lecture Chapter 07", "Lecture", "pdfs/csc203/Chapter_07.pdf", "Local PDF for CSC203 Chapter 07."),
            ("Lecture Chapter 08", "Lecture", "pdfs/csc203/Chapter_08.pdf", "Local PDF for CSC203 Chapter 08."),
            ("Lecture Chapter 09", "Lecture", "pdfs/csc203/Chapter_09.pdf", "Local PDF for CSC203 Chapter 09."),
            ("Lecture Chapter 10", "Lecture", "pdfs/csc203/Chapter_10.pdf", "Local PDF for CSC203 Chapter 10."),
            ("Lecture Chapter 11", "Lecture", "pdfs/csc203/Chapter_11.pdf", "Local PDF for CSC203 Chapter 11."),
        ],
        "groups": [
            ("Python Pair Coders", "Tuesdays at 7:00 PM", "Online on Zoom", "Collaborative coding and live debugging practice."),
        ],
    },
    {
        "code": "ENG201",
        "title": "Advanced Composition",
        "description": "Improve thesis writing, argument structure, research habits, and revision skills.",
        "professor": ("Dr. Patrick Zwosta", "pm13zwos@alum.siena.edu", "By appointment", "By appointment; also Saturdays for 1 hour after class"),
        "book_title": "They Say / I Say",
        "book_link": "https://wwnorton.com/books/9780393538700",
        "video_title": "ENG201 Lecture Videos",
        "video_url": "https://www.youtube.com/watch?v=LaffA9EyUgo",
        "videos": [
            ("ENG201 Lecture 01", "https://www.youtube.com/watch?v=LaffA9EyUgo"),
            ("ENG201 Lecture 02", "https://www.youtube.com/watch?v=4FS7PibPxVM"),
            ("ENG201 Lecture 03", "https://www.youtube.com/watch?v=LgNN-6roFWw&t=7848s"),
        ],
        "help_text": "Ask for feedback on thesis statements, outlines, and essay organization.",
        "quiz": [
            ("What is the main claim of an essay called?", "Citation", "Thesis", "Appendix", "Footnote", "Thesis"),
            ("Which source detail is usually required in citations?", "Author", "Weather", "Room number", "Font size", "Author"),
        ],
        "materials": [
            ("ENG201 Syllabus", "Syllabus", "pdfs/eng201/syllabus.pdf", "Course schedule, expectations, policies, and major writing assignments."),
            ("Mother Tongue by Amy Tan", "Reading", "pdfs/eng201/Mother Tongue by Amy Tan.pdf", "Essay reading on language, identity, family voice, and how English is valued."),
            ("I Only Came to Use the Phone", "Reading", "pdfs/eng201/i_only_came_to_use_the_phone.pdf", "Short story reading about confinement, power, communication, and uncertainty."),
        ],
        "groups": [
            ("Writers Workshop", "Wednesdays at 5:30 PM", "Student Center", "Share drafts and get peer editing feedback."),
        ],
    },
    {
        "code": "MAT301",
        "title": "Calculus 1 MAT 301-1600",
        "description": "Study limits, derivatives, applications of derivatives, optimization, L'Hopital's Rule, Newton's Method, and antiderivatives.",
        "professor": ("Dr. Ivan Retamoso", "iretamoso@bmcc.cuny.edu", "BMCC Mathematics Department", "See MAT301 OpenLab schedule and syllabus"),
        "book_title": "Calculus Volume 1 by OpenStax",
        "book_link": "https://openlab.bmcc.cuny.edu/calculus-mat-301-1600-spring-2026/textbook/",
        "video_title": "Dr. Ivan Retamoso Calculus I Playlist",
        "video_url": "https://www.youtube.com/watch?v=-G8BlrD1X_8&list=PL9nkbpC3uJfoYZd7mgr66a0ZmvzFpyQpn",
        "videos": [
            (f"Video {index}: {title}", f"{MAT301_PLAYLIST}&index={index}")
            for index, title in enumerate(MAT301_VIDEOS, start=1)
        ],
        "help_text": "Request help for limits, derivatives, formulas, and practice exams.",
        "quiz": [
            ("What does a derivative measure?", "Area only", "Rate of change", "A citation style", "Database rows", "Rate of change"),
            ("What value does a limit describe?", "Behavior near a point", "A book title", "An email address", "A table name", "Behavior near a point"),
        ],
        "materials": [
            ("MAT301 OpenLab Course Site", "Syllabus", "pdfs/mat301-syllabus.pdf", "Local PDF summary of Spring 2026 MAT301 class info, announcements, exams, and resources."),
            ("Textbook", "Book", "pdfs/mat301-textbook.pdf", "Local PDF reference for the Calculus I textbook."),
            ("Worksheets", "Worksheet", "pdfs/mat301-worksheets.pdf", "Local PDF packet for MAT301 worksheets."),
            ("Lecture Notes", "Lecture", "pdfs/mat301-lecture-notes.pdf", "Local PDF packet for MAT301 lecture notes."),
            ("Recorded Lectures", "Lecture", "https://openlab.bmcc.cuny.edu/calculus-mat-301-1600-spring-2026/recorded-lectures/", "Recorded lectures from the Spring 2026 OpenLab course site."),
            ("Review for Exams", "Exam Review", "pdfs/mat301-review-for-exams.pdf", "Local PDF packet for MAT301 exam review."),
            ("Useful Links", "Reference", "https://openlab.bmcc.cuny.edu/calculus-mat-301-1600-spring-2026/useful-links/", "Useful calculus links from the MAT301 OpenLab site."),
            ("Useful Sheets and Formulas", "Formula Sheet", "pdfs/mat301-formula-sheets.pdf", "Local PDF packet with formulas and helpful references."),
            ("WeBWorK Login", "Homework", "https://webwork.bmcc.cuny.edu/webwork2/2026_Spring_MAT301_1600_Retamoso/", "Homework login for MAT301-1600 WeBWorK assignments."),
            ("DESMOS Scientific Calculator", "Calculator", "https://www.desmos.com/scientific", "Scientific calculator for calculus computations."),
            ("DESMOS Graphing Calculator", "Calculator", "https://www.desmos.com/calculator", "Graphing calculator for calculus practice."),
            ("Free Tutoring at BMCC", "Tutoring", "https://openlab.bmcc.cuny.edu/calculus-mat-301-1600-spring-2026/free-tutoring-at-bmcc/", "Tutoring information from the MAT301 OpenLab site."),
        ],
        "groups": [
            ("Calculus Accountability Team", "Thursdays at 6:30 PM", "Math Lab", "Weekly problem solving and quiz review."),
        ],
    },
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("student_id") is None:
            flash("Please log in to access your study dashboard.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def current_student():
    student_id = session.get("student_id")
    if not student_id:
        return None
    return get_db().execute(
        """
        SELECT student_id, first_name, last_name, emplid, email, phone, major
        FROM students
        WHERE student_id = ?
        """,
        (student_id,),
    ).fetchone()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            emplid TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            major TEXT NOT NULL,
            password_hash TEXT NOT NULL DEFAULT ''
        )
        """
    )
    ensure_student_columns(db)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS professors (
            professor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            office_location TEXT NOT NULL,
            office_hours TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS study_courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            professor_id INTEGER,
            code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            book_title TEXT NOT NULL,
            book_link TEXT NOT NULL,
            video_title TEXT NOT NULL,
            video_url TEXT NOT NULL,
            help_text TEXT NOT NULL,
            FOREIGN KEY (professor_id) REFERENCES professors(professor_id)
        )
        """
    )
    ensure_course_columns(db)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS course_materials (
            material_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            material_type TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS course_videos (
            video_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            display_order INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL UNIQUE,
            title TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_study_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS help_requests (
            help_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS study_groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            meeting_time TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS study_group_members (
            group_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_id, student_id),
            FOREIGN KEY (group_id) REFERENCES study_groups(group_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS study_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            session_date TEXT NOT NULL,
            session_time TEXT NOT NULL,
            meeting_type TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS study_session_members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, student_id),
            FOREIGN KEY (session_id) REFERENCES study_sessions(session_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tutoring_appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            appointment_time TEXT NOT NULL,
            topic TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Scheduled',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES study_courses(course_id)
        )
        """
    )
    seed_courses(db)
    seed_course_support(db)
    sync_course_materials(db)
    sync_course_video_resources(db)
    sync_course_professors(db)
    db.commit()


def ensure_student_columns(db):
    columns = {row["name"] for row in db.execute("PRAGMA table_info(students)").fetchall()}
    if "password_hash" not in columns:
        db.execute("ALTER TABLE students ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''")
    if "email" in columns:
        db.execute("UPDATE students SET email = LOWER(email)")


def ensure_course_columns(db):
    columns = {row["name"] for row in db.execute("PRAGMA table_info(study_courses)").fetchall()}
    if "professor_id" not in columns:
        db.execute("ALTER TABLE study_courses ADD COLUMN professor_id INTEGER")


def seed_courses(db):
    existing = db.execute("SELECT COUNT(*) AS total FROM study_courses").fetchone()["total"]
    if existing:
        return

    for course in COURSE_SEED:
        cursor = db.execute(
            """
            INSERT INTO study_courses
            (code, title, description, book_title, book_link, video_title, video_url, help_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                course["code"],
                course["title"],
                course["description"],
                course["book_title"],
                course["book_link"],
                course["video_title"],
                course["video_url"],
                course["help_text"],
            ),
        )
        course_id = cursor.lastrowid
        db.executemany(
            """
            INSERT INTO course_materials (course_id, title, material_type, url, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(course_id, title, material_type, url, description) for title, material_type, url, description in course["materials"]],
        )
        db.executemany(
            """
            INSERT INTO study_groups (course_id, name, meeting_time, location, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(course_id, name, meeting_time, location, description) for name, meeting_time, location, description in course["groups"]],
        )


def sync_course_materials(db):
    material_courses = {"CSC203", "CIS395", "ENG201"}
    for course_seed in COURSE_SEED:
        if course_seed["code"] not in material_courses:
            continue

        course = db.execute(
            "SELECT course_id FROM study_courses WHERE code = ?",
            (course_seed["code"],),
        ).fetchone()
        if course is None:
            continue

        db.execute("DELETE FROM course_materials WHERE course_id = ?", (course["course_id"],))
        db.executemany(
            """
            INSERT INTO course_materials (course_id, title, material_type, url, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (course["course_id"], title, material_type, url, description)
                for title, material_type, url, description in course_seed["materials"]
            ],
        )


def sync_course_video_resources(db):
    video_courses = {"CIS395", "ENG201"}
    for course_seed in COURSE_SEED:
        if course_seed["code"] not in video_courses:
            continue

        course = db.execute(
            "SELECT course_id FROM study_courses WHERE code = ?",
            (course_seed["code"],),
        ).fetchone()
        if course is None:
            continue

        db.execute(
            """
            UPDATE study_courses
            SET video_title = ?, video_url = ?
            WHERE course_id = ?
            """,
            (course_seed["video_title"], course_seed["video_url"], course["course_id"]),
        )
        db.execute("DELETE FROM course_videos WHERE course_id = ?", (course["course_id"],))
        db.executemany(
            """
            INSERT INTO course_videos (course_id, title, url, display_order)
            VALUES (?, ?, ?, ?)
            """,
            [
                (course["course_id"], title, url, index)
                for index, (title, url) in enumerate(course_seed.get("videos", []), start=1)
            ],
        )


def sync_course_professors(db):
    professor_courses = {"ENG201"}
    for course_seed in COURSE_SEED:
        if course_seed["code"] not in professor_courses:
            continue

        course = db.execute(
            "SELECT course_id, professor_id FROM study_courses WHERE code = ?",
            (course_seed["code"],),
        ).fetchone()
        if course is None:
            continue

        if course["professor_id"] is None:
            professor = db.execute(
                """
                INSERT INTO professors (name, email, office_location, office_hours)
                VALUES (?, ?, ?, ?)
                """,
                course_seed["professor"],
            )
            db.execute(
                "UPDATE study_courses SET professor_id = ? WHERE course_id = ?",
                (professor.lastrowid, course["course_id"]),
            )
        else:
            db.execute(
                """
                UPDATE professors
                SET name = ?, email = ?, office_location = ?, office_hours = ?
                WHERE professor_id = ?
                """,
                (*course_seed["professor"], course["professor_id"]),
            )


def seed_course_support(db):
    for course_seed in COURSE_SEED:
        course = db.execute(
            "SELECT course_id, professor_id FROM study_courses WHERE code = ?",
            (course_seed["code"],),
        ).fetchone()
        if course is None:
            continue

        if course["professor_id"] is None:
            professor = db.execute(
                """
                INSERT INTO professors (name, email, office_location, office_hours)
                VALUES (?, ?, ?, ?)
                """,
                course_seed["professor"],
            )
            db.execute(
                "UPDATE study_courses SET professor_id = ? WHERE course_id = ?",
                (professor.lastrowid, course["course_id"]),
            )

        quiz = db.execute(
            "SELECT quiz_id FROM quizzes WHERE course_id = ?",
            (course["course_id"],),
        ).fetchone()
        if quiz is None:
            quiz_cursor = db.execute(
                "INSERT INTO quizzes (course_id, title) VALUES (?, ?)",
                (course["course_id"], f"{course_seed['code']} Practice Quiz"),
            )
            quiz_id = quiz_cursor.lastrowid
        else:
            quiz_id = quiz["quiz_id"]

        question_count = db.execute(
            "SELECT COUNT(*) AS total FROM quiz_questions WHERE quiz_id = ?",
            (quiz_id,),
        ).fetchone()["total"]
        if question_count == 0:
            db.executemany(
                """
                INSERT INTO quiz_questions
                (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [(quiz_id, *question) for question in course_seed["quiz"]],
            )

        video_count = db.execute(
            "SELECT COUNT(*) AS total FROM course_videos WHERE course_id = ?",
            (course["course_id"],),
        ).fetchone()["total"]
        if video_count == 0:
            db.executemany(
                """
                INSERT INTO course_videos (course_id, title, url, display_order)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (course["course_id"], title, url, index)
                    for index, (title, url) in enumerate(course_seed.get("videos", []), start=1)
                ],
            )


def get_course(course_id):
    return get_db().execute(
        "SELECT * FROM study_courses WHERE course_id = ?",
        (course_id,),
    ).fetchone()


def youtube_embed_url(video_url):
    video_id = youtube_video_id(video_url)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"

    parsed = urlparse(video_url)
    playlist_id = parse_qs(parsed.query).get("list", [""])[0]
    if playlist_id and not parse_qs(parsed.query).get("v"):
        return f"https://www.youtube.com/embed/videoseries?list={playlist_id}"

    return None


def youtube_video_id(video_url):
    parsed = urlparse(video_url)
    if parsed.netloc.endswith("youtu.be"):
        video_id = parsed.path.strip("/")
    else:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    return video_id or None


def youtube_thumbnail_url(video_url):
    video_id = youtube_video_id(video_url)
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def build_ai_study_response(course, prompt):
    topic = prompt.strip()
    if not topic:
        topic = course["title"]

    # The API key stays outside the codebase; Flask reads it from the shell environment.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "The AI Study Assistant is almost ready. Set the OPENAI_API_KEY environment variable, "
            "restart the Flask app, and ask your question again.",
            False,
        )

    try:
        from openai import OpenAI, OpenAIError
    except ImportError:
        return (
            "The OpenAI Python package is not installed in this environment. Install it with "
            "`pip install openai`, then restart the Flask app.",
            False,
        )

    try:
        client = OpenAI(api_key=api_key)
        # Use the current OpenAI Python SDK Responses API to generate one structured study answer.
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=(
                "You are the BMCC StudyTogether AI Study Assistant. Give concise, practical, "
                "student-friendly help. Use the course code and title as context. Always format "
                "your answer with exactly these sections: Study Summary, Quiz Questions, Study Tips."
            ),
            input=(
                f"Course: {course['code']} - {course['title']}\n"
                f"Student question: {topic}"
            ),
            max_output_tokens=550,
        )
        answer = getattr(response, "output_text", "").strip()
        if not answer:
            answer = "I received your question, but the AI response was empty. Please try asking again."
        return answer, True
    except OpenAIError as error:
        return (
            "The AI Study Assistant could not reach OpenAI right now. Please check your API key, "
            f"network connection, or billing status. Details: {error}",
            False,
        )
    except Exception as error:
        return (
            "Something went wrong while asking the AI Study Assistant. Please try again in a moment. "
            f"Details: {error}",
            False,
        )


def save_ai_study_session(student_id, course_id, prompt, response):
    # Store every AI exchange so the course page can show previous questions and answers.
    db = get_db()
    db.execute(
        """
        INSERT INTO ai_study_sessions (student_id, course_id, prompt, response)
        VALUES (?, ?, ?, ?)
        """,
        (student_id, course_id, prompt, response),
    )
    db.commit()


def handle_ai_assistant_request(course_id, prompt):
    student = current_student()
    course = get_course(course_id)
    if course is None:
        flash("Course not found.", "error")
        return redirect(url_for("dashboard"))

    if not prompt:
        flash("Ask the AI study helper a course question first.", "error")
        return redirect(url_for("course_detail", course_id=course_id))

    response, ai_success = build_ai_study_response(course, prompt)
    save_ai_study_session(student["student_id"], course_id, prompt, response)
    if ai_success:
        flash("AI Study Assistant answered your question.", "success")
    else:
        flash("AI Study Assistant needs attention. See the message in Recent AI Notes.", "warning")
    return redirect(url_for("course_detail", course_id=course_id))


@app.context_processor
def inject_student():
    return {
        "logged_in_student": current_student(),
        "youtube_thumbnail_url": youtube_thumbnail_url,
    }


@app.route("/")
def home():
    courses = get_db().execute("SELECT * FROM study_courses ORDER BY code").fetchall()
    if session.get("student_id"):
        return redirect(url_for("dashboard"))
    return render_template("home.html", courses=courses)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        emplid = request.form["emplid"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        major = request.form["major"].strip()
        password = request.form["password"]

        if not all([first_name, last_name, emplid, email, phone, major, password]):
            flash("Please complete every registration field.", "error")
            return render_template("register.html")

        try:
            db = get_db()
            cursor = db.execute(
                """
                INSERT INTO students
                (first_name, last_name, emplid, email, phone, major, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    first_name,
                    last_name,
                    emplid,
                    email,
                    phone,
                    major,
                    generate_password_hash(password),
                ),
            )
            db.commit()
            session["student_id"] = cursor.lastrowid
            flash("Your student account is ready. Welcome to your study dashboard.", "success")
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("That email or student ID is already registered.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        student = get_db().execute(
            "SELECT * FROM students WHERE LOWER(email) = ?",
            (email,),
        ).fetchone()

        if student and student["password_hash"] and check_password_hash(student["password_hash"], password):
            session["student_id"] = student["student_id"]
            flash(f"Welcome back, {student['first_name']}.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    student = current_student()
    courses = db.execute(
        """
        SELECT c.*,
               EXISTS(
                   SELECT 1
                   FROM enrollments e
                   WHERE e.course_id = c.course_id AND e.student_id = ?
               ) AS is_enrolled
        FROM study_courses c
        ORDER BY c.code
        """,
        (student["student_id"],),
    ).fetchall()
    enrollments = db.execute(
        """
        SELECT c.code, c.title, e.created_at
        FROM enrollments e
        JOIN study_courses c ON c.course_id = e.course_id
        WHERE e.student_id = ?
        ORDER BY e.created_at DESC
        """,
        (student["student_id"],),
    ).fetchall()
    appointments = db.execute(
        """
        SELECT a.appointment_time, a.topic, a.status, c.code, c.title
        FROM tutoring_appointments a
        JOIN study_courses c ON c.course_id = a.course_id
        WHERE a.student_id = ?
        ORDER BY a.appointment_time
        """,
        (student["student_id"],),
    ).fetchall()
    help_requests = db.execute(
        """
        SELECT h.question, h.status, h.created_at, c.code
        FROM help_requests h
        JOIN study_courses c ON c.course_id = h.course_id
        WHERE h.student_id = ?
        ORDER BY h.created_at DESC
        """,
        (student["student_id"],),
    ).fetchall()
    groups = db.execute(
        """
        SELECT g.name, g.meeting_time, g.location, c.code
        FROM study_group_members gm
        JOIN study_groups g ON g.group_id = gm.group_id
        JOIN study_courses c ON c.course_id = g.course_id
        WHERE gm.student_id = ?
        ORDER BY c.code, g.name
        """,
        (student["student_id"],),
    ).fetchall()
    return render_template(
        "dashboard.html",
        student=student,
        courses=courses,
        enrollments=enrollments,
        appointments=appointments,
        help_requests=help_requests,
        groups=groups,
    )


@app.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    db = get_db()
    student = current_student()
    course = get_course(course_id)
    if course is None:
        flash("Course not found.", "error")
        return redirect(url_for("dashboard"))

    materials = db.execute(
        "SELECT * FROM course_materials WHERE course_id = ? ORDER BY material_id",
        (course_id,),
    ).fetchall()
    videos = db.execute(
        "SELECT * FROM course_videos WHERE course_id = ? ORDER BY display_order",
        (course_id,),
    ).fetchall()
    groups = db.execute(
        """
        SELECT g.*,
               EXISTS(
                   SELECT 1
                   FROM study_group_members gm
                   WHERE gm.group_id = g.group_id AND gm.student_id = ?
               ) AS joined
        FROM study_groups g
        WHERE g.course_id = ?
        ORDER BY g.group_id
        """,
        (student["student_id"], course_id),
    ).fetchall()
    is_enrolled = db.execute(
        "SELECT 1 FROM enrollments WHERE student_id = ? AND course_id = ?",
        (student["student_id"], course_id),
    ).fetchone() is not None
    professor = db.execute(
        """
        SELECT p.*
        FROM professors p
        JOIN study_courses c ON c.professor_id = p.professor_id
        WHERE c.course_id = ?
        """,
        (course_id,),
    ).fetchone()
    quiz = db.execute(
        "SELECT * FROM quizzes WHERE course_id = ?",
        (course_id,),
    ).fetchone()
    latest_quiz_attempt = None
    if quiz:
        latest_quiz_attempt = db.execute(
            """
            SELECT score, total_questions, created_at
            FROM quiz_attempts
            WHERE quiz_id = ? AND student_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (quiz["quiz_id"], student["student_id"]),
        ).fetchone()
    ai_sessions = db.execute(
        """
        SELECT prompt, response, created_at
        FROM ai_study_sessions
        WHERE course_id = ? AND student_id = ?
        ORDER BY created_at DESC
        LIMIT 3
        """,
        (course_id, student["student_id"]),
    ).fetchall()
    sessions = db.execute(
        """
        SELECT ss.*,
               s.first_name,
               s.last_name,
               EXISTS(
                   SELECT 1
                   FROM study_session_members ssm
                   WHERE ssm.session_id = ss.session_id AND ssm.student_id = ?
               ) AS joined
        FROM study_sessions ss
        JOIN students s ON s.student_id = ss.student_id
        WHERE ss.course_id = ? AND ss.session_date >= DATE('now')
        ORDER BY ss.session_date, ss.session_time
        """,
        (student["student_id"], course_id),
    ).fetchall()

    return render_template(
        "course_detail.html",
        course=course,
        materials=materials,
        videos=videos,
        readings=ENG201_READINGS if course["code"] == "ENG201" else [],
        groups=groups,
        sessions=sessions,
        is_enrolled=is_enrolled,
        professor=professor,
        quiz=quiz,
        latest_quiz_attempt=latest_quiz_attempt,
        ai_sessions=ai_sessions,
        video_embed_url=youtube_embed_url(course["video_url"]),
    )


@app.post("/courses/<int:course_id>/sessions/create")
@login_required
def create_study_session(course_id):
    student = current_student()
    if get_course(course_id) is None:
        flash("Course not found.", "error")
        return redirect(url_for("dashboard"))

    title = request.form["title"].strip()
    session_date = request.form["session_date"].strip()
    session_time = request.form["session_time"].strip()
    meeting_type = request.form["meeting_type"].strip()
    location = request.form["location"].strip()
    description = request.form["description"].strip()

    if meeting_type not in {"Online", "In Person"}:
        flash("Please choose Online or In Person for the meeting type.", "error")
        return redirect(url_for("course_detail", course_id=course_id))

    if not all([title, session_date, session_time, meeting_type, location, description]):
        flash("Please complete every study session field.", "error")
        return redirect(url_for("course_detail", course_id=course_id))

    db = get_db()
    db.execute(
        """
        INSERT INTO study_sessions
        (course_id, student_id, title, session_date, session_time, meeting_type, location, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            course_id,
            student["student_id"],
            title,
            session_date,
            session_time,
            meeting_type,
            location,
            description,
        ),
    )
    db.commit()
    flash("Study session created.", "success")
    return redirect(url_for("course_detail", course_id=course_id))


@app.post("/sessions/<int:session_id>/enroll")
@login_required
def enroll_study_session(session_id):
    student = current_student()
    db = get_db()
    study_session = db.execute(
        "SELECT session_id, course_id, student_id FROM study_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if study_session is None:
        flash("Study session not found.", "error")
        return redirect(url_for("dashboard"))

    if study_session["student_id"] == student["student_id"]:
        flash("You created this study session.", "info")
        return redirect(url_for("course_detail", course_id=study_session["course_id"]))

    db.execute(
        """
        INSERT OR IGNORE INTO study_session_members (session_id, student_id)
        VALUES (?, ?)
        """,
        (session_id, student["student_id"]),
    )
    db.commit()
    flash("You enrolled in the study session.", "success")
    return redirect(url_for("course_detail", course_id=study_session["course_id"]))


@app.post("/sessions/<int:session_id>/unenroll")
@login_required
def unenroll_study_session(session_id):
    student = current_student()
    db = get_db()
    study_session = db.execute(
        "SELECT session_id, course_id, student_id FROM study_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if study_session is None:
        flash("Study session not found.", "error")
        return redirect(url_for("dashboard"))

    db.execute(
        """
        DELETE FROM study_session_members
        WHERE session_id = ? AND student_id = ?
        """,
        (session_id, student["student_id"]),
    )
    db.commit()
    flash("You unenrolled from the study session.", "success")
    return redirect(url_for("course_detail", course_id=study_session["course_id"]))


@app.post("/courses/<int:course_id>/ai-helper")
@login_required
def ai_study_helper(course_id):
    # Backward-compatible route for older forms that still post to the course-specific URL.
    return handle_ai_assistant_request(course_id, request.form.get("prompt", "").strip())


@app.post("/ai-assistant")
@login_required
def ai_assistant():
    # Primary AI Study Assistant endpoint used by the course workspace.
    try:
        course_id = int(request.form.get("course_id", ""))
    except ValueError:
        flash("Choose a course before asking the AI Study Assistant.", "error")
        return redirect(url_for("dashboard"))

    prompt = request.form.get("prompt", "").strip()
    return handle_ai_assistant_request(course_id, prompt)


@app.route("/courses/<int:course_id>/quiz", methods=["GET", "POST"])
@login_required
def course_quiz(course_id):
    db = get_db()
    student = current_student()
    course = get_course(course_id)
    if course is None:
        flash("Course not found.", "error")
        return redirect(url_for("dashboard"))

    quiz = db.execute(
        "SELECT * FROM quizzes WHERE course_id = ?",
        (course_id,),
    ).fetchone()
    if quiz is None:
        flash("Quiz not found for this course.", "error")
        return redirect(url_for("course_detail", course_id=course_id))

    questions = db.execute(
        "SELECT * FROM quiz_questions WHERE quiz_id = ? ORDER BY question_id",
        (quiz["quiz_id"],),
    ).fetchall()
    score = None

    if request.method == "POST":
        score = 0
        for question in questions:
            selected = request.form.get(f"question_{question['question_id']}")
            if selected == question["correct_answer"]:
                score += 1
        db.execute(
            """
            INSERT INTO quiz_attempts (quiz_id, student_id, score, total_questions)
            VALUES (?, ?, ?, ?)
            """,
            (quiz["quiz_id"], student["student_id"], score, len(questions)),
        )
        db.commit()
        flash(f"Quiz submitted: {score} out of {len(questions)} correct.", "success")

    return render_template(
        "quiz.html",
        course=course,
        quiz=quiz,
        questions=questions,
        score=score,
    )


@app.post("/courses/<int:course_id>/enroll")
@login_required
def enroll(course_id):
    student = current_student()
    if get_course(course_id) is None:
        flash("Course not found.", "error")
        return redirect(url_for("dashboard"))

    try:
        db = get_db()
        db.execute(
            "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
            (student["student_id"], course_id),
        )
        db.commit()
        flash("You are now registered for this class.", "success")
    except sqlite3.IntegrityError:
        flash("You are already registered for this class.", "warning")
    return redirect(url_for("course_detail", course_id=course_id))


@app.post("/courses/<int:course_id>/help")
@login_required
def request_help(course_id):
    student = current_student()
    question = request.form["question"].strip()
    if not question:
        flash("Please describe the help you need.", "error")
        return redirect(url_for("course_detail", course_id=course_id))

    db = get_db()
    db.execute(
        """
        INSERT INTO help_requests (student_id, course_id, question)
        VALUES (?, ?, ?)
        """,
        (student["student_id"], course_id, question),
    )
    db.commit()
    flash("Your help request has been submitted.", "success")
    return redirect(url_for("course_detail", course_id=course_id))


@app.post("/groups/<int:group_id>/join")
@login_required
def join_group(group_id):
    student = current_student()
    db = get_db()
    group = db.execute("SELECT * FROM study_groups WHERE group_id = ?", (group_id,)).fetchone()
    if group is None:
        flash("Study group not found.", "error")
        return redirect(url_for("dashboard"))

    try:
        db.execute(
            "INSERT INTO study_group_members (group_id, student_id) VALUES (?, ?)",
            (group_id, student["student_id"]),
        )
        db.commit()
        flash("You joined the study group.", "success")
    except sqlite3.IntegrityError:
        flash("You are already a member of that group.", "warning")
    return redirect(url_for("course_detail", course_id=group["course_id"]))


@app.post("/courses/<int:course_id>/tutoring")
@login_required
def book_tutoring(course_id):
    student = current_student()
    appointment_time = request.form["appointment_time"].strip()
    topic = request.form["topic"].strip()

    if not appointment_time or not topic:
        flash("Please choose a tutoring time and topic.", "error")
        return redirect(url_for("course_detail", course_id=course_id))

    db = get_db()
    db.execute(
        """
        INSERT INTO tutoring_appointments (student_id, course_id, appointment_time, topic)
        VALUES (?, ?, ?, ?)
        """,
        (student["student_id"], course_id, appointment_time, topic),
    )
    db.commit()

    flash("Your free tutoring appointment is scheduled.", "success")
    return redirect(url_for("course_detail", course_id=course_id))


# DELETE tutoring appointment
@app.post("/appointments/<int:appointment_id>/delete")
@login_required
def delete_appointment(appointment_id):
    student = current_student()
    db = get_db()

    db.execute(
        """
        DELETE FROM tutoring_appointments
        WHERE appointment_id = ? AND student_id = ?
        """,
        (appointment_id, student["student_id"]),
    )
    db.commit()

    flash("Tutoring appointment canceled.", "success")
    return redirect(url_for("dashboard"))


# DELETE help request
@app.post("/help-requests/<int:help_request_id>/delete")
@login_required
def delete_help_request(help_request_id):
    student = current_student()
    db = get_db()

    db.execute(
        """
        DELETE FROM help_requests
        WHERE help_request_id = ? AND student_id = ?
        """,
        (help_request_id, student["student_id"]),
    )
    db.commit()

    flash("Help request deleted.", "success")
    return redirect(url_for("dashboard"))


# LEAVE study group
@app.post("/groups/<int:group_id>/leave")
@login_required
def leave_group(group_id):
    student = current_student()
    db = get_db()

    db.execute(
        """
        DELETE FROM study_group_members
        WHERE group_id = ? AND student_id = ?
        """,
        (group_id, student["student_id"]),
    )
    db.commit()

    flash("You left the study group.", "success")
    return redirect(url_for("dashboard"))


# UPDATE student profile
@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    student = current_student()

    if request.method == "POST":
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        major = request.form["major"].strip()

        if not all([first_name, last_name, email, phone, major]):
            flash("Please complete all profile fields.", "error")
            return render_template("edit_profile.html", student=student)

        try:
            db = get_db()

            db.execute(
                """
                UPDATE students
                SET first_name = ?, last_name = ?, email = ?, phone = ?, major = ?
                WHERE student_id = ?
                """,
                (
                    first_name,
                    last_name,
                    email,
                    phone,
                    major,
                    student["student_id"],
                ),
            )

            db.commit()

            flash("Profile updated successfully.", "success")
            return redirect(url_for("dashboard"))

        except sqlite3.IntegrityError:
            flash("That email is already used by another student.", "error")

    return render_template("edit_profile.html", student=student)


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5002)
