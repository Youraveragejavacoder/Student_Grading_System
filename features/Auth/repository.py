import sqlite3
from typing import Optional
from database.database import Database, get_connection


class AuthenticationRepository:
    def __init__(self, database: Optional[Database] = None):
        self.database = database
        self.db_path = database.db_path if database else None

    def _connection_kwargs(self) -> dict:
        return {"db_path": self.db_path} if self.db_path else {}

    def add(self, username: str, password_hash: str) -> bool:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password_hash),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            raise ValueError("Username is already taken.")
        except sqlite3.Error as err:
            raise RuntimeError(f"Database error during registration: {err}")

    def find_by_username(self, username: str) -> Optional[dict]:
        try:
            with get_connection(**self._connection_kwargs()) as conn:
                row = conn.execute(
                    "SELECT id, username, password, role FROM users WHERE username = ?",
                    (username,),
                ).fetchone()

                if row:
                    return dict(row)
                return None
        except sqlite3.Error as err:
            raise RuntimeError(f"Database error during lookup: {err}")
