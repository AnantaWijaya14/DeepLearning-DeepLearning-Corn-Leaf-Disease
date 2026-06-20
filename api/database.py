import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "predictions.db"

DB_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            prediction TEXT,
            confidence REAL,
            created_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def insert_prediction(filename, prediction, confidence):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions (filename, prediction, confidence, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            filename,
            prediction,
            float(confidence),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


def get_prediction_history(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, filename, prediction, confidence, created_at
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row[0],
            "filename": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "created_at": row[4]
        })

    return history