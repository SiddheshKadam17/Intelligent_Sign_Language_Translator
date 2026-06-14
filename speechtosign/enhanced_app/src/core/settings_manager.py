import sqlite3
import json
import os

class SettingsManager:
    """Manage user preferences and app settings"""
    
    def __init__(self, db_path="database/settings.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Create settings tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # User preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                theme TEXT DEFAULT 'light',
                color_scheme TEXT DEFAULT 'blue',
                font_size TEXT DEFAULT 'medium',
                animation_speed REAL DEFAULT 1.0,
                auto_save BOOLEAN DEFAULT 1,
                sound_enabled BOOLEAN DEFAULT 1,
                notifications_enabled BOOLEAN DEFAULT 1,
                language TEXT DEFAULT 'en',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # App settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                requirement INTEGER,
                points INTEGER DEFAULT 10
            )
        ''')
        
        # User achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER,
                achievement_id INTEGER,
                earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id)
            )
        ''')
        
        # Daily goals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_goals (
                goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                target_translations INTEGER DEFAULT 10,
                completed_translations INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.init_default_achievements()
    
    def init_default_achievements(self):
        """Create default achievements"""
        achievements = [
            ("First Steps", "Complete your first translation", "🎯", 1, 10),
            ("Getting Started", "Complete 10 translations", "🌟", 10, 20),
            ("Dedicated Learner", "Complete 50 translations", "💪", 50, 50),
            ("Sign Master", "Complete 100 translations", "🏆", 100, 100),
            ("Speed Demon", "Complete 5 translations in a day", "⚡", 5, 30),
            ("Consistent", "Use app 7 days in a row", "📅", 7, 50),
            ("Favorite Collector", "Save 10 favorites", "⭐", 10, 25),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for name, desc, icon, req, points in achievements:
            cursor.execute('''
                INSERT OR IGNORE INTO achievements 
                (name, description, icon, requirement, points) 
                VALUES (?, ?, ?, ?, ?)
            ''', (name, desc, icon, req, points))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id):
        """Get user preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            # Create default preferences
            cursor.execute('''
                INSERT INTO user_preferences (user_id) VALUES (?)
            ''', (user_id,))
            conn.commit()
            cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
        
        conn.close()
        
        return {
            'theme': result[1],
            'color_scheme': result[2],
            'font_size': result[3],
            'animation_speed': result[4],
            'auto_save': bool(result[5]),
            'sound_enabled': bool(result[6]),
            'notifications_enabled': bool(result[7]),
            'language': result[8]
        }
    
    def update_preference(self, user_id, key, value):
        """Update a single preference"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            UPDATE user_preferences 
            SET {key} = ? 
            WHERE user_id = ?
        ''', (value, user_id))
        
        conn.commit()
        conn.close()
    
    def get_achievements(self):
        """Get all achievements"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM achievements')
        achievements = cursor.fetchall()
        
        conn.close()
        return achievements
    
    def get_user_achievements(self, user_id):
        """Get user's earned achievements"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, ua.earned_date 
            FROM achievements a
            JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
            WHERE ua.user_id = ?
            ORDER BY ua.earned_date DESC
        ''', (user_id,))
        
        achievements = cursor.fetchall()
        conn.close()
        return achievements
    
    def award_achievement(self, user_id, achievement_id):
        """Award achievement to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_achievements (user_id, achievement_id) 
                VALUES (?, ?)
            ''', (user_id, achievement_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Already earned
    
    def check_achievements(self, user_id, translation_count):
        """Check and award achievements based on progress"""
        achievements = self.get_achievements()
        newly_earned = []
        
        for ach in achievements:
            ach_id, name, desc, icon, requirement, points = ach
            
            if translation_count >= requirement:
                if self.award_achievement(user_id, ach_id):
                    newly_earned.append((name, desc, icon, points))
        
        return newly_earned
    
    def get_daily_goal(self, user_id):
        """Get today's goal"""
        from datetime import date
        today = date.today()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM daily_goals 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.execute('''
                INSERT INTO daily_goals (user_id, date) 
                VALUES (?, ?)
            ''', (user_id, today))
            conn.commit()
            cursor.execute('''
                SELECT * FROM daily_goals 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
            result = cursor.fetchone()
        
        conn.close()
        
        return {
            'target': result[3],
            'completed': result[4],
            'progress': (result[4] / result[3]) * 100 if result[3] > 0 else 0
        }
    
    def update_daily_goal(self, user_id):
        """Increment daily goal progress"""
        from datetime import date
        today = date.today()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE daily_goals 
            SET completed_translations = completed_translations + 1 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        conn.commit()
        conn.close()
    
    def get_app_setting(self, key, default=None):
        """Get app-wide setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_value FROM app_settings WHERE setting_key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else default
    
    def set_app_setting(self, key, value):
        """Set app-wide setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO app_settings (setting_key, setting_value) 
            VALUES (?, ?)
        ''', (key, value))
        
        conn.commit()
        conn.close()