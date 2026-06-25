"""
SignTalk Pro — Database Module
Handles SQLite storage for users, history, favorites, achievements, and settings.
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "app.db")


def get_db():
    """Open a new database connection with row access by column name."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            mode TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            mode TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER PRIMARY KEY,
            sound_enabled INTEGER NOT NULL DEFAULT 1,
            default_speed REAL NOT NULL DEFAULT 1.0,
            default_mode TEXT NOT NULL DEFAULT 'ISL',
            theme_color TEXT NOT NULL DEFAULT '#3b82f6',
            dark_mode INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements_earned (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_key TEXT NOT NULL,
            earned_at TEXT NOT NULL,
            UNIQUE(user_id, achievement_key),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mode TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ───────────────────────── USERS ─────────────────────────

def create_user(username, password):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), datetime.now().isoformat())
        )
        conn.commit()
        user = conn.execute("SELECT id, username FROM users WHERE username = ?", (username,)).fetchone()
        # Create default settings row for the new user
        conn.execute("INSERT INTO settings (user_id) VALUES (?)", (user["id"],))
        conn.commit()
        return {"id": user["id"], "username": user["username"]}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and check_password_hash(user["password_hash"], password):
        return {"id": user["id"], "username": user["username"]}
    return None


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT id, username, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


# ───────────────────────── HISTORY ─────────────────────────

def add_history(user_id, text, mode):
    conn = get_db()
    conn.execute(
        "INSERT INTO history (user_id, text, mode, created_at) VALUES (?, ?, ?, ?)",
        (user_id, text, mode, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_history(user_id, limit=200):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, text, mode, created_at FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_history(user_id):
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) AS c FROM history WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row["c"]


def clear_history(user_id):
    conn = get_db()
    conn.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ───────────────────────── FAVORITES ─────────────────────────

def add_favorite(user_id, text, mode):
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM favorites WHERE user_id = ? AND text = ? AND mode = ?",
        (user_id, text, mode)
    ).fetchone()
    if existing:
        conn.close()
        return False
    conn.execute(
        "INSERT INTO favorites (user_id, text, mode, created_at) VALUES (?, ?, ?, ?)",
        (user_id, text, mode, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return True


def get_favorites(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, text, mode, created_at FROM favorites WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_favorite(user_id, favorite_id):
    conn = get_db()
    conn.execute("DELETE FROM favorites WHERE user_id = ? AND id = ?", (user_id, favorite_id))
    conn.commit()
    conn.close()


# ───────────────────────── SETTINGS ─────────────────────────

def get_settings(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        conn.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = conn.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row)


def update_settings(user_id, **kwargs):
    allowed = {"sound_enabled", "default_speed", "default_mode", "theme_color", "dark_mode"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return get_settings(user_id)

    conn = get_db()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [user_id]
    conn.execute(f"UPDATE settings SET {set_clause} WHERE user_id = ?", values)
    conn.commit()
    conn.close()
    return get_settings(user_id)


# ───────────────────────── ACHIEVEMENTS ─────────────────────────

ACHIEVEMENT_DEFS = {
    "first_translation": {"label": "First Steps", "desc": "Complete your first translation", "icon": "🎉"},
    "ten_translations":  {"label": "Getting Fluent", "desc": "Complete 10 translations", "icon": "🔥"},
    "fifty_translations": {"label": "Sign Master", "desc": "Complete 50 translations", "icon": "🏆"},
    "first_favorite":    {"label": "Bookmarked", "desc": "Save your first favorite", "icon": "⭐"},
    "both_modes":        {"label": "Bilingual", "desc": "Use both ISL and ASL", "icon": "🌐"},
    "quiz_complete":     {"label": "Quiz Taker", "desc": "Complete a quiz", "icon": "📝"},
    "quiz_perfect":      {"label": "Perfect Score", "desc": "Get a perfect score on a quiz", "icon": "💯"},
    "daily_goal":        {"label": "Goal Crusher", "desc": "Hit your daily goal of 10 translations", "icon": "🎯"},
}


def get_earned_achievements(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT achievement_key, earned_at FROM achievements_earned WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return {r["achievement_key"]: r["earned_at"] for r in rows}


def grant_achievement(user_id, key):
    """Insert an achievement if not already earned. Returns True if newly granted."""
    if key not in ACHIEVEMENT_DEFS:
        return False
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO achievements_earned (user_id, achievement_key, earned_at) VALUES (?, ?, ?)",
            (user_id, key, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_and_grant_achievements(user_id, event, context=None):
    """
    Call after key actions (translation, favorite, quiz) to check which
    achievements newly unlock. Returns a list of newly granted achievement keys.
    """
    context = context or {}
    newly_granted = []

    if event == "translation":
        total = count_history(user_id)
        if total >= 1 and grant_achievement(user_id, "first_translation"):
            newly_granted.append("first_translation")
        if total >= 10 and grant_achievement(user_id, "ten_translations"):
            newly_granted.append("ten_translations")
        if total >= 50 and grant_achievement(user_id, "fifty_translations"):
            newly_granted.append("fifty_translations")
        if total >= 10 and grant_achievement(user_id, "daily_goal"):
            newly_granted.append("daily_goal")

        conn = get_db()
        modes = conn.execute(
            "SELECT DISTINCT mode FROM history WHERE user_id = ?", (user_id,)
        ).fetchall()
        conn.close()
        mode_set = {m["mode"] for m in modes}
        if {"ISL", "ASL"}.issubset(mode_set) and grant_achievement(user_id, "both_modes"):
            newly_granted.append("both_modes")

    elif event == "favorite":
        if grant_achievement(user_id, "first_favorite"):
            newly_granted.append("first_favorite")

    elif event == "quiz":
        if grant_achievement(user_id, "quiz_complete"):
            newly_granted.append("quiz_complete")
        if context.get("score") == context.get("total") and context.get("total", 0) > 0:
            if grant_achievement(user_id, "quiz_perfect"):
                newly_granted.append("quiz_perfect")

    return newly_granted


# ───────────────────────── QUIZ ─────────────────────────

def save_quiz_result(user_id, mode, score, total):
    conn = get_db()
    conn.execute(
        "INSERT INTO quiz_results (user_id, mode, score, total, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, mode, score, total, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_quiz_stats(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT mode, score, total, created_at FROM quiz_results WHERE user_id = ? ORDER BY id DESC LIMIT 20",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ───────────────────────── PROFILE STATS ─────────────────────────

def get_profile_stats(user_id):
    conn = get_db()
    history_count = conn.execute(
        "SELECT COUNT(*) AS c FROM history WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]
    favorites_count = conn.execute(
        "SELECT COUNT(*) AS c FROM favorites WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]
    quiz_count = conn.execute(
        "SELECT COUNT(*) AS c FROM quiz_results WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]
    best_quiz = conn.execute(
        "SELECT MAX(score) AS best FROM quiz_results WHERE user_id = ?", (user_id,)
    ).fetchone()["best"]
    achievements_count = conn.execute(
        "SELECT COUNT(*) AS c FROM achievements_earned WHERE user_id = ?", (user_id,)
    ).fetchone()["c"]
    conn.close()
    return {
        "history_count": history_count,
        "favorites_count": favorites_count,
        "quiz_count": quiz_count,
        "best_quiz_score": best_quiz or 0,
        "achievements_count": achievements_count,
    }
