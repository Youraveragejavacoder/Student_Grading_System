import sqlite3
from typing import Optional
from database.database import Database, get_connection


class AuthenticationRepository:
    def __init__(self, database: Optional[Database] = None):
        self.database = database
        self.db_path = database.db_path if database else None

    def _connection_kwargs(self) -> dict:
        return {"db_path": self.db_path} if self.db_path else {}

    def add(self, username: str, password_hash: str, role: str = "teacher") -> bool:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password_hash, role),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            raise ValueError("Username is already taken.")
        except sqlite3.Error as err:
            raise RuntimeError(f"Database error during registration: {err}")

    def ensure_admin(self, password_hash: str) -> None:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                conn.execute(
                    "UPDATE users SET role = 'teacher' WHERE role = 'admin' AND username <> 'Admin'"
                )
                conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, 'admin') "
                    "ON CONFLICT(username) DO UPDATE SET password = excluded.password, role = 'admin'",
                    ("Admin", password_hash),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO teachers (username, name) "
                    "SELECT username, username FROM users WHERE role = 'teacher'"
                )
                conn.execute("DELETE FROM teachers WHERE username = 'Admin'")
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not provision the administrator account: {err}") from err

    def add_teacher(self, username: str, name: str, password_hash: str) -> bool:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, 'teacher')",
                    (username, password_hash),
                )
                conn.execute(
                    "INSERT INTO teachers (username, name) VALUES (?, ?)",
                    (username, name),
                )
                return True
        except sqlite3.IntegrityError as err:
            raise ValueError("That teacher username is already in use.") from err
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not register teacher: {err}") from err

    def find_by_username(self, username: str) -> Optional[dict]:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                row = conn.execute(
                    "SELECT u.id, u.username, u.password, u.role, "
                    "COALESCE(t.name, u.username) AS display_name "
                    "FROM users AS u LEFT JOIN teachers AS t ON t.username = u.username "
                    "WHERE u.username = ?",
                    (username,),
                ).fetchone()

                if row:
                    return dict(row)
                return None
        except sqlite3.Error as err:
            raise RuntimeError(f"Database error during lookup: {err}")

    def list_by_role(self, role: str) -> list[dict]:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                rows = conn.execute(
                    "SELECT u.id, u.username, u.role, t.name "
                    "FROM users AS u LEFT JOIN teachers AS t ON t.username = u.username "
                    "WHERE u.role = ? ORDER BY t.name COLLATE NOCASE, u.username",
                    (role,),
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as err:
            raise RuntimeError(f"Database error while listing accounts: {err}") from err

    def remove_by_id_and_role(self, user_id: int, role: str) -> None:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                conn.execute(
                    "DELETE FROM users WHERE id = ? AND role = ?",
                    (user_id, role),
                )
        except sqlite3.Error as err:
            raise RuntimeError(f"Database error while removing account: {err}") from err
