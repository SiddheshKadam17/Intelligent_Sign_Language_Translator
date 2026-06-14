import sqlite3
import bcrypt
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="database/app.db"):
        """Initialize database connection and create tables if not exist"""
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Create and return database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Create all necessary tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Translation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translation_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                input_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                translation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_seconds REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phrase TEXT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP,
                translations_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User Management Functions
    def create_user(self, username, email, password, full_name=""):
        """Register a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, full_name))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return True, user_id
        except sqlite3.IntegrityError:
            return False, "Username or email already exists"
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, username, password):
        """Verify user credentials"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, password_hash, full_name FROM users 
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, password_hash, full_name = result
                if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                    self.update_last_login(user_id)
                    return True, user_id, full_name
            
            return False, None, None
        except Exception as e:
            return False, None, str(e)
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    # Translation History Functions
    def add_translation(self, user_id, input_text, translated_text, duration=0):
        """Save translation to history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO translation_history 
                (user_id, input_text, translated_text, duration_seconds)
                VALUES (?, ?, ?, ?)
            ''', (user_id, input_text, translated_text, duration))
            
            conn.commit()
            history_id = cursor.lastrowid
            conn.close()
            return True, history_id
        except Exception as e:
            return False, str(e)
    
    def get_user_history(self, user_id, limit=50):
        """Get user's translation history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT history_id, input_text, translated_text, 
                   translation_date, duration_seconds
            FROM translation_history
            WHERE user_id = ?
            ORDER BY translation_date DESC
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_history(self, user_id, search_term):
        """Search in translation history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT history_id, input_text, translated_text, 
                   translation_date, duration_seconds
            FROM translation_history
            WHERE user_id = ? AND (
                input_text LIKE ? OR translated_text LIKE ?
            )
            ORDER BY translation_date DESC
        ''', (user_id, f'%{search_term}%', f'%{search_term}%'))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def delete_history_item(self, history_id):
        """Delete a specific history item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM translation_history WHERE history_id = ?', (history_id,))
        conn.commit()
        conn.close()
    
    # Favorites Functions
    def add_favorite(self, user_id, phrase):
        """Add phrase to favorites"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorites (user_id, phrase)
                VALUES (?, ?)
            ''', (user_id, phrase))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def get_favorites(self, user_id):
        """Get user's favorite phrases"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT favorite_id, phrase, added_date
            FROM favorites
            WHERE user_id = ?
            ORDER BY added_date DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def remove_favorite(self, favorite_id):
        """Remove phrase from favorites"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM favorites WHERE favorite_id = ?', (favorite_id,))
        conn.commit()
        conn.close()
    
    # Statistics Functions
    def get_user_stats(self, user_id):
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total translations
        cursor.execute('''
            SELECT COUNT(*) FROM translation_history WHERE user_id = ?
        ''', (user_id,))
        total_translations = cursor.fetchone()[0]
        
        # Total duration
        cursor.execute('''
            SELECT SUM(duration_seconds) FROM translation_history WHERE user_id = ?
        ''', (user_id,))
        total_duration = cursor.fetchone()[0] or 0
        
        # Translations today
        cursor.execute('''
            SELECT COUNT(*) FROM translation_history 
            WHERE user_id = ? AND DATE(translation_date) = DATE('now')
        ''', (user_id,))
        today_translations = cursor.fetchone()[0]
        
        # Most translated words (top 5)
        cursor.execute('''
            SELECT input_text, COUNT(*) as count
            FROM translation_history
            WHERE user_id = ?
            GROUP BY input_text
            ORDER BY count DESC
            LIMIT 5
        ''', (user_id,))
        popular_words = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_translations': total_translations,
            'total_duration': total_duration,
            'today_translations': today_translations,
            'popular_words': popular_words
        }
    
    # Session Management
    def create_session(self, user_id):
        """Create new login session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (user_id) VALUES (?)
        ''', (user_id,))
        
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id
    
    def close_session(self, session_id, translations_count):
        """Close login session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET logout_time = CURRENT_TIMESTAMP, translations_count = ?
            WHERE session_id = ?
        ''', (translations_count, session_id))
        
        conn.commit()
        conn.close()