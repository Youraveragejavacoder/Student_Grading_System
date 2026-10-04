import sqlite3
from pathlib import Path
from typing import Optional


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "grading_system.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Open the application's one canonical SQLite database."""
    path = Path(db_path or DEFAULT_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class Database:
    """Create and validate the schema used by all repositories."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.init_db()

    @staticmethod
    def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
        return {
            row["name"]
            for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        }

    @staticmethod
    def _primary_key_columns(conn: sqlite3.Connection, table_name: str) -> list[str]:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        return [row["name"] for row in sorted(rows, key=lambda row: row["pk"]) if row["pk"]]

    @staticmethod
    def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        return row is not None

    @staticmethod
    def _table_is_empty(conn: sqlite3.Connection, table_name: str) -> bool:
        return conn.execute(f"SELECT 1 FROM {table_name} LIMIT 1").fetchone() is None

    @staticmethod
    def _create_users_table(conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin'
            )
            """
        )

    @staticmethod
    def _create_students_table(conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _create_grades_table(conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE grades (
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                score REAL NOT NULL,
                PRIMARY KEY (student_id, subject),
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON DELETE CASCADE
            )
            """
        )

    def _ensure_users_table(self, conn: sqlite3.Connection) -> None:
        if not self._table_exists(conn, "users"):
            self._create_users_table(conn)
            return

        columns = self._table_columns(conn, "users")
        required = {"username", "password"}
        if not required.issubset(columns):
            raise RuntimeError(
                "The users table has an unsupported schema. Back up the database "
                "before migrating it."
            )

        if "role" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'admin'")

    def _ensure_students_table(self, conn: sqlite3.Connection) -> None:
        if not self._table_exists(conn, "students"):
            self._create_students_table(conn)
            return

        columns = self._table_columns(conn, "students")
        primary_key = self._primary_key_columns(conn, "students")
        is_current = columns == {"student_id", "name"} and primary_key == ["student_id"]
        if is_current:
            return

        if not self._table_is_empty(conn, "students"):
            raise RuntimeError(
                "The existing students table uses an older schema and contains data. "
                "Back up or migrate that data before starting the app."
            )

        conn.execute("DROP TABLE students")
        self._create_students_table(conn)

    def _ensure_grades_table(self, conn: sqlite3.Connection) -> None:
        if not self._table_exists(conn, "grades"):
            self._create_grades_table(conn)
            return

        columns = self._table_columns(conn, "grades")
        primary_key = self._primary_key_columns(conn, "grades")
        is_current = (
            columns == {"student_id", "subject", "score"}
            and primary_key == ["student_id", "subject"]
        )
        if is_current:
            return

        if not self._table_is_empty(conn, "grades"):
            raise RuntimeError(
                "The existing grades table uses an older schema and contains data. "
                "Back up or migrate that data before starting the app."
            )

        conn.execute("DROP TABLE grades")
        self._create_grades_table(conn)

    def init_db(self) -> None:
        try:
            with get_connection(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = OFF")
                self._ensure_users_table(conn)
                self._ensure_students_table(conn)
                self._ensure_grades_table(conn)
                conn.execute("PRAGMA foreign_keys = ON")
        except (sqlite3.Error, RuntimeError) as err:
            if isinstance(err, RuntimeError):
                raise
            raise RuntimeError(f"Database initialization failed: {err}") from err
