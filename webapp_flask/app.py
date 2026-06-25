"""
SignTalk Pro — Web Version (Flask Backend)
Voice/Text to Sign Language Translator (ISL & ASL)
Full feature parity build: Login, History, Favorites, Quiz, Achievements,
Settings, Profile, GIF export support.

Run with: python app.py
Then open: http://localhost:5000
"""

import os
import random
import string
from functools import wraps

from flask import Flask, render_template, request, jsonify, session

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SIGNTALK_SECRET_KEY", "dev-secret-key-change-in-production")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "static", "images")

db.init_db()


# ───────────────────────── HELPERS ─────────────────────────

def clean_text(text):
    """Keep only letters, numbers and spaces, uppercase"""
    return "".join(c for c in text.upper() if c.isalnum() or c == " ")


def image_exists(letter, mode):
    """Check which extension the sign image uses"""
    folder = "isl_sign_images" if mode == "ISL" else "asl_sign_images"
    letter_lower = letter.lower()
    for ext in ["jpg", "jpeg", "png"]:
        path = os.path.join(ASSETS_DIR, folder, f"{letter_lower}.{ext}")
        if os.path.exists(path):
            return f"/static/images/{folder}/{letter_lower}.{ext}"
    return None


def available_letters(mode):
    """Return list of letters that actually have an image file, for quiz generation."""
    found = []
    for letter in string.ascii_uppercase:
        if image_exists(letter, mode):
            found.append(letter)
    return found


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401
        return f(*args, **kwargs)
    return wrapper


# ───────────────────────── PAGE ROUTE ─────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ───────────────────────── AUTH ROUTES ─────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    user = db.create_user(username, password)
    if not user:
        return jsonify({"error": "Username already taken"}), 409

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"user": user})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = db.verify_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"user": user})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"user": None})
    user = db.get_user_by_id(session["user_id"])
    return jsonify({"user": user})


# ───────────────────────── TRANSLATE ─────────────────────────

@app.route("/api/translate", methods=["POST"])
def translate():
    """Take text + mode, return list of sign image URLs"""
    data = request.get_json() or {}
    text = data.get("text", "")
    mode = data.get("mode", "ISL")

    cleaned = clean_text(text)
    signs = []

    for ch in cleaned:
        if ch == " ":
            signs.append({"char": " ", "image": None, "is_space": True})
        else:
            img_url = image_exists(ch, mode)
            signs.append({"char": ch, "image": img_url, "is_space": False})

    new_achievements = []
    if "user_id" in session and cleaned.strip():
        db.add_history(session["user_id"], cleaned, mode)
        new_achievements = db.check_and_grant_achievements(session["user_id"], "translation")

    return jsonify({
        "text": cleaned,
        "signs": signs,
        "mode": mode,
        "new_achievements": new_achievements
    })


# ───────────────────────── HISTORY ─────────────────────────

@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    return jsonify({"history": db.get_history(session["user_id"])})


@app.route("/api/history", methods=["DELETE"])
@login_required
def clear_history():
    db.clear_history(session["user_id"])
    return jsonify({"ok": True})


# ───────────────────────── FAVORITES ─────────────────────────

@app.route("/api/favorites", methods=["GET"])
@login_required
def get_favorites():
    return jsonify({"favorites": db.get_favorites(session["user_id"])})


@app.route("/api/favorites", methods=["POST"])
@login_required
def add_favorite():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    mode = data.get("mode", "ISL")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    added = db.add_favorite(session["user_id"], text, mode)
    new_achievements = []
    if added:
        new_achievements = db.check_and_grant_achievements(session["user_id"], "favorite")

    return jsonify({
        "added": added,
        "favorites": db.get_favorites(session["user_id"]),
        "new_achievements": new_achievements
    })


@app.route("/api/favorites/<int:favorite_id>", methods=["DELETE"])
@login_required
def remove_favorite(favorite_id):
    db.remove_favorite(session["user_id"], favorite_id)
    return jsonify({"favorites": db.get_favorites(session["user_id"])})


# ───────────────────────── SETTINGS ─────────────────────────

@app.route("/api/settings", methods=["GET"])
@login_required
def get_settings():
    return jsonify({"settings": db.get_settings(session["user_id"])})


@app.route("/api/settings", methods=["POST"])
@login_required
def update_settings():
    data = request.get_json() or {}
    updated = db.update_settings(session["user_id"], **data)
    return jsonify({"settings": updated})


# ───────────────────────── ACHIEVEMENTS ─────────────────────────

@app.route("/api/achievements", methods=["GET"])
@login_required
def get_achievements():
    earned = db.get_earned_achievements(session["user_id"])
    result = []
    for key, info in db.ACHIEVEMENT_DEFS.items():
        result.append({
            "key": key,
            "label": info["label"],
            "desc": info["desc"],
            "icon": info["icon"],
            "earned": key in earned,
            "earned_at": earned.get(key)
        })
    return jsonify({"achievements": result})


# ───────────────────────── QUIZ ─────────────────────────

@app.route("/api/quiz/question", methods=["GET"])
def quiz_question():
    mode = request.args.get("mode", "ISL")
    letters = available_letters(mode)

    if len(letters) < 4:
        return jsonify({"error": "Not enough sign images available for a quiz"}), 400

    correct = random.choice(letters)
    distractor_pool = [l for l in letters if l != correct]
    distractors = random.sample(distractor_pool, min(3, len(distractor_pool)))

    options = distractors + [correct]
    random.shuffle(options)

    return jsonify({
        "image": image_exists(correct, mode),
        "correct": correct,
        "options": options,
        "mode": mode
    })


@app.route("/api/quiz/submit", methods=["POST"])
def quiz_submit():
    data = request.get_json() or {}
    mode = data.get("mode", "ISL")
    score = int(data.get("score", 0))
    total = int(data.get("total", 0))

    new_achievements = []
    if "user_id" in session and total > 0:
        db.save_quiz_result(session["user_id"], mode, score, total)
        new_achievements = db.check_and_grant_achievements(
            session["user_id"], "quiz", {"score": score, "total": total}
        )

    return jsonify({"ok": True, "new_achievements": new_achievements})


@app.route("/api/quiz/stats", methods=["GET"])
@login_required
def quiz_stats():
    return jsonify({"results": db.get_quiz_stats(session["user_id"])})


# ───────────────────────── PROFILE ─────────────────────────

@app.route("/api/profile", methods=["GET"])
@login_required
def profile():
    user = db.get_user_by_id(session["user_id"])
    stats = db.get_profile_stats(session["user_id"])
    return jsonify({"user": user, "stats": stats})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)