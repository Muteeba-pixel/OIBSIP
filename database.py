"""
database.py
===========
SQLite persistence layer for the Advanced BMI Calculator & Health Tracker.

Handles multi-user BMI records, historical queries, record deletion,
and graceful error handling with automatic transaction rollbacks.

OASIS Infobyte Python Programming Internship - Task 2
Author: OASIS Intern / Python Developer
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class DatabaseError(Exception):
    """Custom exception raised when a database read/write/connection operation fails."""
    pass


DEFAULT_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "bmi_records.db")


@contextmanager
def get_connection(db_path: str = DEFAULT_DB_PATH):
    """
    Context manager to establish, yield, and reliably close SQLite connection.
    Creates parent directories if they do not exist.

    Args:
        db_path: Path to the SQLite database file.

    Yields:
        sqlite3.Connection with Row factory enabled.

    Raises:
        DatabaseError: If connection cannot be established or handled.
    """
    parent_dir = os.path.dirname(db_path)
    if parent_dir and not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except OSError as exc:
            raise DatabaseError(f"Failed to create directory '{parent_dir}': {exc}") from exc

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to connect to database at '{db_path}': {exc}") from exc

    try:
        yield conn
    finally:
        try:
            conn.close()
        except sqlite3.Error:
            pass


def init_database(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initialize SQLite database schema and indices.
    Safe to call multiple times (idempotent).

    Raises:
        DatabaseError: If table creation fails.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bmi_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL COLLATE NOCASE,
        weight REAL NOT NULL,
        height REAL NOT NULL,
        bmi REAL NOT NULL,
        category TEXT NOT NULL,
        created_at TEXT NOT NULL,
        notes TEXT DEFAULT ''
    );
    """
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_user_created 
    ON bmi_records (user_name, created_at);
    """
    try:
        with get_connection(db_path) as conn:
            conn.execute(create_table_sql)
            conn.execute(create_index_sql)
            conn.commit()
    except sqlite3.Error as exc:
        raise DatabaseError(f"Database initialization failed: {exc}") from exc


def add_record(
    user_name: str,
    weight: float,
    height: float,
    bmi: float,
    category: str,
    created_at: Optional[str] = None,
    notes: str = "",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Insert a new BMI record into the database.

    Args:
        user_name: Name of the individual.
        weight: Weight in kg.
        height: Height in meters.
        bmi: Calculated BMI value.
        category: Classified BMI category.
        created_at: Timestamp string (defaults to current local time).
        notes: Optional user notes.
        db_path: Path to database.

    Returns:
        The auto-generated row ID of the inserted record.

    Raises:
        DatabaseError: If insertion fails.
    """
    clean_name = user_name.strip()
    if not clean_name:
        raise DatabaseError("Cannot save record without a user name.")

    if created_at is None:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    insert_sql = """
    INSERT INTO bmi_records (user_name, weight, height, bmi, category, created_at, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                insert_sql,
                (clean_name, float(weight), float(height), float(bmi), category, created_at, notes.strip())
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to save BMI record for '{clean_name}': {exc}") from exc


def get_users(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """
    Retrieve an alphabetically sorted list of unique usernames in the database.

    Returns:
        List of username strings.
    """
    query_sql = "SELECT DISTINCT user_name FROM bmi_records ORDER BY user_name COLLATE NOCASE ASC;"
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query_sql)
            rows = cursor.fetchall()
            return [row["user_name"] for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to fetch users list: {exc}") from exc


def get_user_records(
    user_name: str,
    order: str = "DESC",
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """
    Fetch all BMI records for a specific user.

    Args:
        user_name: Name of the user to filter records for.
        order: 'DESC' (newest first, ideal for tables) or 'ASC' (oldest first, ideal for charts).
        db_path: Path to database.

    Returns:
        List of dictionaries containing record fields.
    """
    clean_name = user_name.strip()
    direction = "ASC" if order.upper() == "ASC" else "DESC"
    query_sql = f"""
    SELECT id, user_name, weight, height, bmi, category, created_at, notes
    FROM bmi_records
    WHERE user_name = ? COLLATE NOCASE
    ORDER BY created_at {direction}, id {direction};
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query_sql, (clean_name,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to fetch records for '{clean_name}': {exc}") from exc


def delete_record(record_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Delete a specific BMI record by its unique database ID.

    Returns:
        True if record was deleted, False if record did not exist.
    """
    delete_sql = "DELETE FROM bmi_records WHERE id = ?;"
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(delete_sql, (record_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to delete record ID {record_id}: {exc}") from exc


def clear_user_history(user_name: str, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Delete all historical BMI records for a given user.

    Returns:
        Number of records deleted.
    """
    clean_name = user_name.strip()
    delete_sql = "DELETE FROM bmi_records WHERE user_name = ? COLLATE NOCASE;"
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(delete_sql, (clean_name,))
            conn.commit()
            return cursor.rowcount
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to clear history for '{clean_name}': {exc}") from exc


def get_user_statistics(user_name: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Compute aggregate summary statistics for a user's BMI trajectory.

    Returns:
        Dictionary with record count, latest BMI, min BMI, max BMI, and avg BMI.
    """
    records = get_user_records(user_name, order="ASC", db_path=db_path)
    if not records:
        return {
            "total_records": 0,
            "latest_bmi": None,
            "min_bmi": None,
            "max_bmi": None,
            "avg_bmi": None,
            "latest_category": None,
            "first_date": None,
            "latest_date": None,
        }

    bmis = [r["bmi"] for r in records]
    return {
        "total_records": len(records),
        "latest_bmi": records[-1]["bmi"],
        "min_bmi": min(bmis),
        "max_bmi": max(bmis),
        "avg_bmi": round(sum(bmis) / len(bmis), 2),
        "latest_category": records[-1]["category"],
        "first_date": records[0]["created_at"],
        "latest_date": records[-1]["created_at"],
    }
