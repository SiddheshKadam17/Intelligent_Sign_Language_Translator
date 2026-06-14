"""
ULTIMATE PROFESSIONAL VOICE TO SIGN LANGUAGE TRANSLATOR
Part 1 of 5: Core Setup & Imports

Features Included:
- Multi-theme support (Blue, Green, Purple, Orange)
- Smooth dark/light mode transitions
- Toast notifications
- Loading animations
- Achievement system
- Daily goals tracking
- Settings manager
- Advanced UI/UX
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import sys
import os
import re
from threading import Thread
import time
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import json

# Add to path
sys.path.append('src')
from src.core.sign_animator import SignAnimator, AnimatedSignDisplay
from src.core.speech_handler import SpeechHandler
from src.core.database_manager import DatabaseManager
from src.core.settings_manager import SettingsManager
from src.utils import config
from src.utils.theme_manager import ThemeManager, ToastNotification, LoadingOverlay








class ProfessionalSignLanguageApp(ctk.CTk):
    """
    Ultimate Professional Voice to Sign Language Translator

    Features:
    - Multi-theme support with smooth transitions
    - Dark/Light mode with animations
    - Achievement system with badges
    - Daily goals and progress tracking
    - Toast notifications
    - Loading overlays
    - Advanced statistics with charts
    - Export functionality (GIF, PDF)
    - Keyboard shortcuts
    - Auto-save functionality
    - Practice/Quiz mode
    """

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("SignTalk Pro - Ultimate Sign Language Translator")
        self.geometry("1500x900")
        self.minsize(1200, 700)

        # Initialize managers
        self.db = DatabaseManager(config.DATABASE_PATH)
        self.settings_manager = SettingsManager()
        self.current_sign_mode = "ISL"     # ASL or ISL

        # App state
        self.current_user = None
        self.session_id = None
        self.current_theme_mode = "light"
        self.current_color_scheme = "blue"
        self.theme_colors = {
            'primary': '#1f538d',
            'secondary': '#14b8a6',
            'surface': '#1e293b',
            'background': '#0f172a',
            'text': '#f8fafc',
            'text_secondary': '#94a3b8',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444'
        }

        # Keyboard shortcuts
        self.bind_shortcuts()

        # Show splash screen then login
        self.show_splash_screen()

    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Control-t>', lambda e: self.show_translator() if self.current_user else None)
        self.bind('<Control-h>', lambda e: self.show_history() if self.current_user else None)
        self.bind('<Control-f>', lambda e: self.show_favorites() if self.current_user else None)
        # Statistics removed
        self.bind('<Control-d>', lambda e: self.toggle_theme() if self.current_user else None)
        self.bind('<Control-q>', lambda e: self.logout() if self.current_user else None)

    def show_splash_screen(self):
        """Show splash screen with loading animation"""
        splash = ctk.CTkFrame(self, fg_color=("#1f538d", "#0f172a"))
        splash.place(relx=0, rely=0, relwidth=1, relheight=1)

        container = ctk.CTkFrame(splash, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor='center')

        # Logo
        ctk.CTkLabel(
            container, text="🤟",
            font=("Segoe UI", 120)
        ).pack(pady=20)

        # Title
        ctk.CTkLabel(
            container, text="SignTalk Pro",
            font=("Segoe UI", 48, "bold"),
            text_color="white"
        ).pack()

        ctk.CTkLabel(
            container, text="Ultimate Professional Edition",
            font=("Segoe UI", 20),
            text_color="white"
        ).pack(pady=10)

        # Progress bar
        progress = ctk.CTkProgressBar(container, width=400)
        progress.pack(pady=30)
        progress.set(0)

        # Loading text
        loading_label = ctk.CTkLabel(
            container, text="Initializing...",
            font=("Segoe UI", 14),
            text_color="white"
        )
        loading_label.pack()

        # Animate loading
        def animate_loading(step=0):
            if step <= 100:
                progress.set(step / 100)

                texts = [
                    "Initializing...",
                    "Loading components...",
                    "Setting up database...",
                    "Loading animations...",
                    "Preparing interface...",
                    "Almost ready..."
                ]
                loading_label.configure(text=texts[min(step // 20, len(texts) - 1)])

                self.after(30, lambda: animate_loading(step + 2))
            else:
                splash.destroy()
                self.show_login()

        animate_loading()

    def show_login(self):
        """Show enhanced login window"""
        LoginWindow(self, self.db, self.on_login_success)

    def on_login_success(self, user_id, username):
        """Called after successful login"""
        self.current_user = {"id": user_id, "name": username}
        self.session_id = self.db.create_session(user_id)

        # Load user preferences
        prefs = self.settings_manager.get_user_preferences(user_id)
        self.current_theme_mode = prefs['theme']
        self.current_color_scheme = prefs['color_scheme']

        # Apply theme
        self.apply_theme(self.current_theme_mode, self.current_color_scheme)

        # Show loading
        loading = LoadingOverlay(self, "Loading your workspace...")

        def load_app():
            time.sleep(1)  # Simulate loading
            self.after(0, lambda: [loading.hide(), self.create_main_app()])

        Thread(target=load_app, daemon=True).start()

    def apply_theme(self, mode, scheme):
        """Apply theme with smooth transition"""
        self.current_theme_mode = mode
        self.current_color_scheme = scheme

        # Set CustomTkinter appearance mode
        ctk.set_appearance_mode(mode)

        # Get theme colors
        self.theme_colors = ThemeManager.get_theme(mode, scheme)

        # Apply to config
        ThemeManager.apply_theme_to_config(mode, scheme)

        # Update user preference
        if self.current_user:
            self.settings_manager.update_preference(
                self.current_user['id'], 'theme', mode
            )
            self.settings_manager.update_preference(
                self.current_user['id'], 'color_scheme', scheme
            )

    def toggle_theme(self):
        """Toggle between light and dark mode with animation"""
        new_mode = "dark" if self.current_theme_mode == "light" else "light"
        self.apply_theme(new_mode, self.current_color_scheme)

        # Show notification
        ToastNotification.show(
            self,
            f"🌙 Switched to {new_mode.title()} Mode",
            type='info'
        )

        # Refresh current view
        if hasattr(self, 'content_area'):
            # Re-create current view to apply new theme
            current_view = getattr(self, '_current_view', 'translator')
            getattr(self, f'show_{current_view}')()

    def create_main_app(self):
        """Create main application interface"""
        # Initialize components
        self.animator = SignAnimator("assets/sign_images")
        self.speech_handler = SpeechHandler()

        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Create sidebar
        self.create_enhanced_sidebar()

        # Content area
        self.content_area = ctk.CTkFrame(
            self.main_container,
            fg_color=self.theme_colors['background']
        )
        self.content_area.pack(side="right", fill="both", expand=True)

        # Show translator by default
        self.show_translator()

        # Check achievements
        self.check_and_show_achievements()

        # Show daily goal
        self.show_daily_goal_notification()




    def create_enhanced_sidebar(self):
        """Create enhanced sidebar with glassmorphism"""
        sidebar = ctk.CTkFrame(
            self.main_container,
            width=280,
            fg_color=self.theme_colors['primary'],
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo section with animation
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=30)

        ctk.CTkLabel(logo_frame, text="🤟", font=("Segoe UI", 60)).pack()
        ctk.CTkLabel(
            logo_frame, text="SignTalk Pro",
            font=("Segoe UI", 22, "bold"),
            text_color="white"
        ).pack()
        ctk.CTkLabel(
            logo_frame, text="Ultimate Edition",
            font=("Segoe UI", 12),
            text_color="white"
        ).pack()

        # User info card
        user_card = ctk.CTkFrame(
            sidebar,
            fg_color=(self.theme_colors['accent'], self.theme_colors['surface']),
            corner_radius=15
        )
        user_card.pack(fill="x", padx=15, pady=15)

        user_info = ctk.CTkFrame(user_card, fg_color="transparent")
        user_info.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            user_info, text="👤",
            font=("Segoe UI", 30)
        ).pack(side="left", padx=(0, 10))

        user_text = ctk.CTkFrame(user_info, fg_color="transparent")
        user_text.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            user_text, text=self.current_user['name'],
            font=("Segoe UI", 14, "bold"),
            text_color="white",
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            user_text, text="Premium Member",
            font=("Segoe UI", 11),
            text_color="white",
            anchor="w"
        ).pack(fill="x")

        # Streak counter
        streak_frame = ctk.CTkFrame(sidebar, fg_color="#f59e0b", corner_radius=10)
        streak_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            streak_frame, 
            text="🔥 3 Day Streak!",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        ).pack(pady=10)
        
        # Daily goal progress
        goal = self.settings_manager.get_daily_goal(self.current_user['id'])

        goal_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        goal_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            goal_frame, text=f"📅 Daily Goal: {goal['completed']}/{goal['target']}",
            font=("Segoe UI", 12),
            text_color="white"
        ).pack(fill="x")

        progress_bar = ctk.CTkProgressBar(
            goal_frame,
            progress_color=self.theme_colors['success']
        )
        progress_bar.pack(fill="x", pady=5)
        progress_bar.set(goal['progress'] / 100)

        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=15, pady=20)

        self.nav_buttons = {}
        nav_items = [
            ("🎙️ Translator", self.show_translator, "Ctrl+T"),
            ("📜 History", self.show_history, "Ctrl+H"),
            ("⭐ Favorites", self.show_favorites, "Ctrl+F"),
            ("🏆 Achievements", self.show_achievements, ""),
            ("🎯 Practice", self.show_practice, ""),
            ("⚙️ Settings", self.show_settings, ""),
            ("👤 Profile", self.show_profile, "")
        ]

        for text, command, shortcut in nav_items:
            btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=3)

            btn = ctk.CTkButton(
                btn_frame, text=text,
                command=command,
                height=45,
                font=("Segoe UI", 14, "bold"),
                fg_color="transparent",
                text_color="white",
                hover_color=self.theme_colors['secondary'],
                anchor="w",
                corner_radius=10
            )
            btn.pack(side="left", fill="x", expand=True)
            self.nav_buttons[text] = btn

            if shortcut:
                ctk.CTkLabel(
                    btn_frame, text=shortcut,
                    font=("Segoe UI", 9),
                    text_color="white"
                ).pack(side="right", padx=5)

        # Theme selector
        theme_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            theme_frame, text="Color Theme",
            font=("Segoe UI", 11),
            text_color="white"
        ).pack(anchor="w")

        theme_buttons = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_buttons.pack(fill="x", pady=5)

        colors = {
            'blue': '#3b82f6',
            'green': '#10b981',
            'purple': '#a78bfa',
            'orange': '#fb923c'
        }

        for scheme, color in colors.items():
            btn = ctk.CTkButton(
                theme_buttons, text="",
                width=30, height=30,
                fg_color=color,
                hover_color=color,
                corner_radius=15,
                command=lambda s=scheme: self.change_color_scheme(s)
            )
            btn.pack(side="left", padx=2)

        # Dark mode toggle
        ctk.CTkButton(
            sidebar, text="🌙 Toggle Theme (Ctrl+D)",
            command=self.toggle_theme,
            height=45,
            font=("Segoe UI", 13),
            fg_color=(self.theme_colors['accent'], self.theme_colors['surface']),
            hover_color=self.theme_colors['secondary'],
            corner_radius=10
        ).pack(side="bottom", fill="x", padx=15, pady=(0, 10))

        # Logout button
        ctk.CTkButton(
            sidebar, text="🚪 Logout (Ctrl+Q)",
            command=self.logout,
            height=45,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.theme_colors['error'],
            hover_color="#dc2626",
            corner_radius=10
        ).pack(side="bottom", fill="x", padx=15, pady=(0, 10))

    def change_color_scheme(self, scheme):
        """Change color scheme"""
        self.apply_theme(self.current_theme_mode, scheme)
        ToastNotification.show(
            self,
            f"🎨 Applied {scheme.title()} Theme",
            type='success'
        )

    def clear_content(self):
        """Clear content area with fade animation"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def highlight_nav(self, text):
        """Highlight active navigation button"""
        for btn_text, btn in self.nav_buttons.items():
            if btn_text == text:
                btn.configure(fg_color=self.theme_colors['secondary'])
            else:
                btn.configure(fg_color="transparent")

    def check_and_show_achievements(self):
        """Check and show newly earned achievements"""
        stats = self.db.get_user_stats(self.current_user['id'])
        newly_earned = self.settings_manager.check_achievements(
            self.current_user['id'],
            stats['total_translations']
        )

        for achievement in newly_earned:
            name, desc, icon, points = achievement
            self.show_achievement_popup(name, desc, icon, points)

    def show_achievement_popup(self, name, desc, icon, points):
        """Show achievement earned popup"""
        popup = ctk.CTkToplevel(self)
        popup.title("Achievement Unlocked!")
        popup.geometry("400x300")
        popup.resizable(False, False)

        # Center window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 150
        popup.geometry(f"400x300+{x}+{y}")

        container = ctk.CTkFrame(popup, fg_color=self.theme_colors['primary'])
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            container, text="🎉",
            font=("Segoe UI", 80)
        ).pack(pady=20)

        ctk.CTkLabel(
            container, text="Achievement Unlocked!",
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        ).pack()

        ctk.CTkLabel(
            container, text=f"{icon} {name}",
            font=("Segoe UI", 24, "bold"),
            text_color="white"
        ).pack(pady=10)

        ctk.CTkLabel(
            container, text=desc,
            font=("Segoe UI", 14),
            text_color="white"
        ).pack()

        ctk.CTkLabel(
            container, text=f"+{points} points",
            font=("Segoe UI", 16, "bold"),
            text_color=self.theme_colors['warning']
        ).pack(pady=10)

        ctk.CTkButton(
            container, text="Awesome!",
            command=popup.destroy,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color=self.theme_colors['success']
        ).pack(pady=20)

    def show_daily_goal_notification(self):
        """Show daily goal notification"""
        goal = self.settings_manager.get_daily_goal(self.current_user['id'])

        if goal['completed'] == 0:
            ToastNotification.show(
                self,
                f"🎯 Today's Goal: Complete {goal['target']} translations",
                duration=4000,
                type='info'
            )

    def logout(self):
        """Logout with confirmation"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.db.close_session(self.session_id, 0)
            self.main_container.destroy()

            # Show goodbye message
            ToastNotification.show(
                self,
                "👋 Goodbye! See you soon!",
                type='success'
            )

            self.after(1000, self.show_login)



    # View navigation methods
    def show_translator(self):
        self.clear_content()
        self._current_view = 'translator'
        self.highlight_nav("🎙️ Translator")
        EnhancedTranslatorView(self.content_area, self)

    def show_history(self):
        self.clear_content()
        self._current_view = 'history'
        self.highlight_nav("📜 History")
        EnhancedHistoryView(self.content_area, self)

    def show_favorites(self):
        self.clear_content()
        self._current_view = 'favorites'
        self.highlight_nav("⭐ Favorites")
        EnhancedFavoritesView(self.content_area, self)


    def show_achievements(self):
        self.clear_content()
        self._current_view = 'achievements'
        self.highlight_nav("🏆 Achievements")
        AchievementsView(self.content_area, self)

    def show_practice(self):
        self.clear_content()
        self._current_view = 'practice'
        self.highlight_nav("🎯 Practice")
        PracticeView(self.content_area, self)

    def show_settings(self):
        self.clear_content()
        self._current_view = 'settings'
        self.highlight_nav("⚙️ Settings")
        EnhancedSettingsView(self.content_area, self)

    def show_profile(self):
        self.clear_content()
        self._current_view = 'profile'
        self.highlight_nav("👤 Profile")
        EnhancedProfileView(self.content_area, self)


# Login Window with enhanced design
class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent, db, callback):
        super().__init__(parent)
        self.db = db
        self.callback = callback

        self.title("SignTalk Pro - Login")
        self.geometry("550x700")
        self.resizable(False, False)

        self.create_ui()
        self.center_window()
        self.grab_set()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 275
        y = (self.winfo_screenheight() // 2) - 350
        self.geometry(f"550x700+{x}+{y}")

    def create_ui(self):
        # Gradient header
        header = ctk.CTkFrame(self, fg_color="#1f538d", corner_radius=0, height=200)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="🤟", font=("Segoe UI", 80)).pack(pady=20)
        ctk.CTkLabel(header, text="SignTalk Pro", font=("Segoe UI", 32, "bold"), 
                    text_color="white").pack()
        ctk.CTkLabel(header, text="Ultimate Professional Edition", font=("Segoe UI", 14),
                    text_color="white").pack(pady=(5, 20))

        # Form
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=50, pady=40)

        ctk.CTkLabel(form, text="Welcome Back!", font=("Segoe UI", 24, "bold")).pack(pady=(0, 30))

        ctk.CTkLabel(form, text="Username", font=("Segoe UI", 13), anchor="w").pack(fill="x", pady=(0, 5))
        self.username = ctk.CTkEntry(form, height=45, font=("Segoe UI", 14), 
                                     placeholder_text="Enter your username")
        self.username.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(form, text="Password", font=("Segoe UI", 13), anchor="w").pack(fill="x", pady=(0, 5))
        self.password = ctk.CTkEntry(form, height=45, show="●", font=("Segoe UI", 14),
                                     placeholder_text="Enter your password")
        self.password.pack(fill="x", pady=(0, 30))

        ctk.CTkButton(form, text="Login", command=self.login, height=50,
                     font=("Segoe UI", 16, "bold"), fg_color="#1f538d",
                     hover_color="#14b8a6").pack(fill="x", pady=(0, 15))

        ctk.CTkButton(form, text="Create New Account", command=self.show_signup, height=45,
                     font=("Segoe UI", 14), fg_color="transparent", border_width=2,
                     border_color="#1f538d", text_color="#1f538d").pack(fill="x")

        self.password.bind('<Return>', lambda e: self.login())

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get()

        if not user or not pwd:
            messagebox.showerror("Error", "Please fill all fields")
            return

        success, uid, name = self.db.authenticate_user(user, pwd)

        if success:
            self.destroy()
            self.callback(uid, name or user)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_signup(self):
        SignupWindow(self, self.db)


class SignupWindow(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        self.title("Create Account")
        self.geometry("550x750")
        self.create_ui()
        self.center_window()
        self.transient(parent)
        self.grab_set()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 275
        y = (self.winfo_screenheight() // 2) - 375
        self.geometry(f"550x750+{x}+{y}")

    def create_ui(self):
        header = ctk.CTkFrame(self, fg_color="#14b8a6", corner_radius=0, height=150)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Create Account", font=("Segoe UI", 28, "bold"),
                    text_color="white").pack(expand=True)

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=50, pady=30)

        fields = [("Full Name", False), ("Username", False), ("Email", False),
                 ("Password", True), ("Confirm Password", True)]

        self.entries = {}
        for label, is_pwd in fields:
            ctk.CTkLabel(form, text=label, font=("Segoe UI", 12), anchor="w").pack(fill="x", pady=(0, 5))
            entry = ctk.CTkEntry(form, height=40, show="●" if is_pwd else "", font=("Segoe UI", 14))
            entry.pack(fill="x", pady=(0, 15))
            self.entries[label] = entry

        ctk.CTkButton(form, text="Create Account", command=self.signup, height=50,
                     font=("Segoe UI", 16, "bold"), fg_color="#14b8a6").pack(fill="x", pady=(20, 0))

    def signup(self):
        name = self.entries["Full Name"].get().strip()
        user = self.entries["Username"].get().strip()
        email = self.entries["Email"].get().strip()
        pwd = self.entries["Password"].get()
        confirm = self.entries["Confirm Password"].get()

        if not all([name, user, email, pwd, confirm]):
            messagebox.showerror("Error", "Fill all fields")
            return

        if pwd != confirm:
            messagebox.showerror("Error", "Passwords don't match")
            return

        if len(pwd) < 6:
            messagebox.showerror("Error", "Password too short")
            return

        success, result = self.db.create_user(user, email, pwd, name)

        if success:
            messagebox.showinfo("Success", "Account created! Login now.")
            self.destroy()
        else:
            messagebox.showerror("Error", str(result))


# Enhanced Translator View
class EnhancedTranslatorView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        self.app = app
        self.is_animating = False
        self.create_ui()

    def create_ui(self):
        # Title with gradient
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(title_frame, text="🎙️ Voice to Sign Language Translator",
                    font=("Segoe UI", 32, "bold"),
                    text_color=self.app.theme_colors['primary']).pack(side="left")
        
        # Controls frame (right side)
        controls_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        controls_frame.pack(side="right")

        # ASL / ISL toggle button
        sign_btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        sign_btn_frame.pack(side="left", padx=8)

        ctk.CTkLabel(
            sign_btn_frame, text="Sign Style:",
            font=("Segoe UI", 11), text_color="gray"
        ).pack()

        self.sign_label = ctk.CTkButton(
            sign_btn_frame,
            text=f"🤟 {self.app.current_sign_mode}  ⇄",
            command=self.toggle_sign_mode,
            width=130, height=38,
            font=("Segoe UI", 13, "bold"),
            fg_color="#f59e0b",
            hover_color="#d97706",
            text_color="white",
            corner_radius=10
        )
        self.sign_label.pack()


        # Quick stats
        stats_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        stats_frame.pack(side="right")

        stats = self.app.db.get_user_stats(self.app.current_user['id'])
        ctk.CTkLabel(stats_frame, text=f"📊 {stats['total_translations']} translations",
                    font=("Segoe UI", 12), text_color=self.app.theme_colors['text_secondary']).pack(side="left", padx=10)

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True)

        # Left panel
        left = ctk.CTkFrame(content, width=480, fg_color=self.app.theme_colors['surface'], 
                           corner_radius=20)
        left.pack(side="left", fill="y", padx=(0, 20))
        left.pack_propagate(False)

        # Input section
        input_section = ctk.CTkFrame(left, fg_color="transparent")
        input_section.pack(fill="x", padx=25, pady=25)

        ctk.CTkLabel(input_section, text="📝 Enter Text or Use Voice",
                    font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(0, 15))

        self.text_input = ctk.CTkTextbox(input_section, height=120, font=("Segoe UI", 14),
                                         border_width=2, border_color=self.app.theme_colors['primary'])
        self.text_input.pack(fill="x")

        # Voice section
        voice_section = ctk.CTkFrame(left, fg_color=self.app.theme_colors['background'], corner_radius=15)
        voice_section.pack(fill="x", padx=25, pady=20)

        voice_header = ctk.CTkFrame(voice_section, fg_color="transparent")
        voice_header.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(voice_header, text="🎤", font=("Segoe UI", 28)).pack(side="left")
        ctk.CTkLabel(voice_header, text="Voice Input", font=("Segoe UI", 15, "bold")).pack(side="left", padx=10)

        self.voice_status = ctk.CTkLabel(voice_section, text="Ready to record",
                                         font=("Segoe UI", 12), text_color=self.app.theme_colors['text_secondary'])
        self.voice_status.pack(pady=(0, 15))

        # Action buttons
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=15)

        self.record_btn = ctk.CTkButton(btn_frame, text="🎤 Record Voice", command=self.record,
                                       height=55, font=("Segoe UI", 15, "bold"),
                                       fg_color=self.app.theme_colors['secondary'],
                                       hover_color=self.app.theme_colors['accent'])
        self.record_btn.pack(fill="x", pady=(0, 12))

        self.translate_btn = ctk.CTkButton(btn_frame, text="▶️ Start Translation", command=self.translate,
                                          height=55, font=("Segoe UI", 15, "bold"),
                                          fg_color=self.app.theme_colors['primary'])
        self.translate_btn.pack(fill="x")

        # Speed control
        speed_section = ctk.CTkFrame(left, fg_color="transparent")
        speed_section.pack(fill="x", padx=25, pady=20)

        speed_header = ctk.CTkFrame(speed_section, fg_color="transparent")
        speed_header.pack(fill="x")

        ctk.CTkLabel(speed_header, text="⚡ Animation Speed", font=("Segoe UI", 13, "bold"),
                    anchor="w").pack(side="left")

        self.speed_label = ctk.CTkLabel(speed_header, text="1.0s", font=("Segoe UI", 12, "bold"),
                                       text_color=self.app.theme_colors['primary'])
        self.speed_label.pack(side="right")

        self.speed_slider = ctk.CTkSlider(speed_section, from_=0.3, to=2.5, command=self.update_speed,
                                         button_color=self.app.theme_colors['primary'],
                                         button_hover_color=self.app.theme_colors['secondary'])
        self.speed_slider.set(1.0)
        self.speed_slider.pack(fill="x", pady=8)

        # Control buttons
        control_frame = ctk.CTkFrame(left, fg_color="transparent")
        control_frame.pack(fill="x", padx=25, pady=15)

        self.stop_btn = ctk.CTkButton(control_frame, text="⏹️ Stop", command=self.stop, height=45,
                                     fg_color=self.app.theme_colors['error'], state="disabled")
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(control_frame, text="⭐", command=self.save_fav, height=45, width=45,
                     fg_color=self.app.theme_colors['warning']).pack(side="left", padx=3)

        ctk.CTkButton(control_frame, text="💾", command=self.export, height=45, width=45,
                     fg_color="#6b7280").pack(side="left", padx=3)

        # GIF Export button (NEW!)
        ctk.CTkButton(control_frame, text="📥 GIF", command=self.export_as_gif, 
                     height=45, width=80,
                     fg_color="#8b5cf6", hover_color="#7c3aed",
                     font=("Segoe UI", 12, "bold")).pack(side="left", padx=3)

        # Right panel - Display
        right = ctk.CTkFrame(content, fg_color=self.app.theme_colors['surface'], corner_radius=20)
        right.pack(side="right", fill="both", expand=True)

        import tkinter as tk
        self.display_frame = tk.Frame(right, bg=self.app.theme_colors['surface'])
        self.display_frame.pack(fill="both", expand=True, padx=25, pady=25)

        self.display = AnimatedSignDisplay(self.display_frame, self.app.animator)
        self.display.pack()

    def record(self):
        self.record_btn.configure(state="disabled", text="⏺️ Recording...")
        self.voice_status.configure(text="🔴 Listening... Speak now!")

        def rec():
            success, text = self.app.speech_handler.listen_once()
            self.after(0, lambda: self.after_rec(success, text))
        Thread(target=rec, daemon=True).start()

    def after_rec(self, success, text):
        self.record_btn.configure(state="normal", text="🎤 Record Voice")
        if success:
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", text)
            self.voice_status.configure(text=f"✅ Recognized: {text}")
            ToastNotification.show(self.app, f"✅ Recognized: {text}", type='success')
        else:
            self.voice_status.configure(text=f"❌ {text}")
            ToastNotification.show(self.app, f"❌ {text}", type='error')

    def translate(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            ToastNotification.show(self.app, "⚠️ Please enter text first", type='warning')
            return

        # Save for GIF export
        self.last_text = text

        self.translate_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        start = time.time()
        # Create animation controller if not exists
        if not hasattr(self, 'anim_controller'):
            from src.core.sign_animator import AnimationController
            self.anim_controller = AnimationController(self.app.animator, self.display)
        
        # Start the animation
        self.anim_controller.start_animation(text)

        def check():
            if not hasattr(self, "anim_controller") or not self.anim_controller.is_running():
                duration = time.time() - start
                self.app.db.add_translation(self.app.current_user["id"], text, text.upper(), duration)
                self.app.settings_manager.update_daily_goal(self.app.current_user['id'])
                self.translate_btn.configure(state="normal")
                self.stop_btn.configure(state="disabled")
                ToastNotification.show(self.app, "✅ Translation complete!", type='success')

                # Check achievements
                self.app.check_and_show_achievements()
            else:
                self.after(100, check)
        self.after(100, check)

    
    def toggle_sign_mode(self):
        """Toggle between ASL and ISL sign images"""
        import os
        from src.core.sign_animator import SignAnimator

        asl_folder = os.path.join("assets", "asl_sign_images")
        isl_folder = os.path.join("assets", "isl_sign_images")

        # Stop any running animation first
        if hasattr(self, 'anim_controller'):
            try:
                self.anim_controller.stop_animation()
            except:
                pass

        # Determine target folder
        if self.app.current_sign_mode == "ISL":
            target_folder = asl_folder
            new_mode = "ASL"
        else:
            target_folder = isl_folder
            new_mode = "ISL"

        if not os.path.exists(target_folder):
            print(f"Folder not found: {target_folder}")
            return

        # IMPORTANT: Recreate the entire animator with the new folder
        self.app.animator = SignAnimator(target_folder)
        
        # Recreate the animation controller with the new animator
        if hasattr(self, 'anim_controller'):
            del self.anim_controller
        from src.core.sign_animator import AnimationController
        self.anim_controller = AnimationController(self.app.animator, self.display)

        # Update UI
        self.app.current_sign_mode = new_mode
        self.sign_label.configure(text=f"🤟 {new_mode}  ⇄")
        print(f"Switched to {new_mode} from {target_folder}")

    

    def create_display(self):
        """Recreate the sign display widget"""
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        import tkinter as tk
        self.display = AnimatedSignDisplay(self.display_frame, self.app.animator)
        self.display.pack(fill="both", expand=True)

    

    def export_as_gif(self):
        """Export the last translation as an animated GIF"""
        if not hasattr(self, 'last_text') or not self.last_text:
            messagebox.showinfo("No Translation", "Please translate something first!")
            return
        
        try:
            from PIL import Image
            import os
            from datetime import datetime
            
            text = self.last_text.upper()
            all_frames = []
            frame_duration = 500
            
            # Get image path from animator
            img_folder = self.app.animator.image_path
            
            previous_char = None  # ✅ NEW LINE
            
            for char in text:
                if char == ' ':
                    blank = Image.new('RGB', (400, 400), color='white')
                    all_frames.append(blank)
                    previous_char = None  # ✅ NEW LINE
                elif char.isalpha():
                    # ✅ NEW BLOCK - Handle repeated letters
                    if previous_char == char:
                        blank = Image.new('RGB', (400, 400), color='white')
                        all_frames.append(blank)
                    
                    img_path = os.path.join(img_folder, f"{char.lower()}.jpg")
                    if os.path.exists(img_path):
                        img = Image.open(img_path).convert('RGB').resize((400, 400))
                        all_frames.append(img)
                    
                    previous_char = char  # ✅ NEW LINE
            
            if not all_frames:
                messagebox.showerror("Error", "No frames to export!")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = self.app.current_sign_mode
            output_dir = "exports"
            os.makedirs(output_dir, exist_ok=True)
            safe_text = ''.join(c for c in text[:10] if c.isalnum())
            output_file = os.path.join(output_dir, f"{mode}_{safe_text}_{timestamp}.gif")
            
            all_frames[0].save(
                output_file,
                save_all=True,
                append_images=all_frames[1:],
                duration=frame_duration,
                loop=0,
                optimize=True
            )
            
            messagebox.showinfo(
                "Export Successful! 🎉",
                f"GIF saved to:\n{os.path.abspath(output_file)}\n\nShare it on WhatsApp, Instagram!"
            )
            
            import subprocess
            subprocess.Popen(f'explorer /select,"{os.path.abspath(output_file)}"')
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export GIF:\n{str(e)}")
            print(f"GIF export error: {e}")


    def stop(self):
        if hasattr(self, 'anim_controller'):
            self.anim_controller.stop_animation()
        self.translate_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def update_speed(self, val):
        self.speed_label.configure(text=f"{val:.1f}s")
        self.anim_controller.set_speed(val)

    def save_fav(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if text:
            self.app.db.add_favorite(self.app.current_user["id"], text)
            ToastNotification.show(self.app, "⭐ Added to favorites!", type='success')

    def export(self):
        """Export translation as GIF (old method - use export_as_gif for better results)"""
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            ToastNotification.show(self.app, "⚠️ Enter text first", type='warning')
            return

        filename = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")],
                                                initialfile=f"sign_{text.replace(' ', '_')}.gif")
        if filename:
            try:
                from PIL import Image
                import os
                frames = []
                
                # Get image path from animator
                img_folder = self.app.animator.image_path
                
                previous_letter = None  # ✅ ADD THIS LINE BEFORE THE LOOP
                
                for letter in text.upper():  # ✅ FIXED INDENTATION
                    if letter == ' ':
                        blank = Image.new('RGB', (400, 400), color='white')
                        frames.append(blank)
                        previous_letter = None  # ✅ RESET ON SPACE
                    elif letter.isalpha():
                        # ✅ CHECK FOR REPEATED LETTER
                        if previous_letter == letter:
                            blank = Image.new('RGB', (400, 400), color='white')
                            frames.append(blank)
                        
                        img_path = os.path.join(img_folder, f"{letter.lower()}.jpg")
                        if os.path.exists(img_path):
                            img = Image.open(img_path).convert('RGB').resize((400, 400))
                            frames.append(img)
                        
                        previous_letter = letter  # ✅ TRACK THE LETTER
                
                if frames:
                    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=500, loop=0, optimize=True)
                    ToastNotification.show(self.app, f"💾 Saved: {filename}", type='success')
                else:
                    ToastNotification.show(self.app, "❌ No frames to export", type='error')
            except Exception as e:
                ToastNotification.show(self.app, f"❌ Export failed: {e}", type='error')
                print(f"Export error: {e}")




# Enhanced History View  
class EnhancedHistoryView(ctk.CTkScrollableFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        self.app = app

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(title_frame, text="📜 Translation History",
                    font=("Segoe UI", 32, "bold"),
                    text_color=self.app.theme_colors['primary']).pack(side="left")

        search_bar = ctk.CTkFrame(self, fg_color=self.app.theme_colors['surface'], corner_radius=15)
        search_bar.pack(fill="x", pady=(0, 20))

        self.search_entry = ctk.CTkEntry(search_bar, placeholder_text="🔍 Search history...",
                                         height=45, font=("Segoe UI", 14))
        self.search_entry.pack(fill="x", padx=20, pady=15)
        self.search_entry.bind('<KeyRelease>', self.search_history)

        self.history_container = ctk.CTkFrame(self, fg_color="transparent")
        self.history_container.pack(fill="both", expand=True)

        self.load_history()

    def load_history(self):
        for widget in self.history_container.winfo_children():
            widget.destroy()

        history = self.app.db.get_user_history(self.app.current_user["id"], 50)

        if not history:
            ctk.CTkLabel(self.history_container, text="No history yet! Start translating.",
                        font=("Segoe UI", 16), text_color=self.app.theme_colors['text_secondary']).pack(pady=50)
        else:
            for item in history:
                self.create_history_card(item)

    def create_history_card(self, item):
        hid, inp, out, date, dur = item

        card = ctk.CTkFrame(self.history_container, fg_color=self.app.theme_colors['surface'], 
                           corner_radius=15)
        card.pack(fill="x", pady=8)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=18)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left, text=inp, font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(left, text=f"📅 {date} | ⏱️ {dur:.1f}s", font=("Segoe UI", 11),
                    text_color=self.app.theme_colors['text_secondary'], anchor="w").pack(fill="x", pady=(5, 0))

        ctk.CTkButton(content, text="🗑️", width=40, height=35,
                     fg_color=self.app.theme_colors['error'],
                     command=lambda: self.delete_item(hid, card)).pack(side="right")

    def delete_item(self, hid, card):
        self.app.db.delete_history_item(hid)
        card.destroy()
        ToastNotification.show(self.app, "🗑️ Deleted from history", type='info')

    def search_history(self, event):
        query = self.search_entry.get().strip()
        if query:
            results = self.app.db.search_history(self.app.current_user["id"], query)
            for widget in self.history_container.winfo_children():
                widget.destroy()
            for item in results:
                self.create_history_card(item)
        else:
            self.load_history()


# Enhanced Favorites View
class EnhancedFavoritesView(ctk.CTkScrollableFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        self.app = app

        ctk.CTkLabel(self, text="⭐ Favorite Phrases", font=("Segoe UI", 32, "bold"),
                    text_color=self.app.theme_colors['primary']).pack(pady=(0, 25))

        favs = self.app.db.get_favorites(self.app.current_user["id"])

        if not favs:
            ctk.CTkLabel(self, text="No favorites yet! Add some from translator.",
                        font=("Segoe UI", 16), text_color=self.app.theme_colors['text_secondary']).pack(pady=50)
        else:
            for fid, phrase, date in favs:
                self.create_fav_card(fid, phrase, date)

    def create_fav_card(self, fid, phrase, date):
        card = ctk.CTkFrame(self, fg_color=self.app.theme_colors['surface'], corner_radius=15)
        card.pack(fill="x", pady=8)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=18)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left, text=phrase, font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(left, text=f"Added: {date}", font=("Segoe UI", 11),
                    text_color=self.app.theme_colors['text_secondary'], anchor="w").pack(fill="x", pady=(5, 0))

        ctk.CTkButton(content, text="🗑️", width=40, height=35,
                     fg_color=self.app.theme_colors['error'],
                     command=lambda: self.delete(fid, card)).pack(side="right")

    def delete(self, fid, card):
        self.app.db.remove_favorite(fid)
        card.destroy()
        ToastNotification.show(self.app, "🗑️ Removed from favorites", type='info')




class AchievementsView(ctk.CTkScrollableFrame):
    """Achievements view with unique badges"""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        self.app = app
        
        # Header
        ctk.CTkLabel(self, text="🏆 Achievements", font=("Arial Bold", 32)).pack(pady=20)
        
        # Hardcoded unique achievements (no duplicates)
        achievements = [
            {"name": "First Steps", "desc": "Complete your first translation", "icon": "🎯", "points": 10, "unlocked": True},
            {"name": "Getting Started", "desc": "Complete 10 translations", "icon": "💫", "points": 20, "unlocked": True},
            {"name": "Dedicated Learner", "desc": "Complete 50 translations", "icon": "📚", "points": 50, "unlocked": False},
            {"name": "Sign Master", "desc": "Complete 100 translations", "icon": "🏆", "points": 100, "unlocked": False},
            {"name": "Speed Demon", "desc": "Complete 5 translations in a day", "icon": "⚡", "points": 30, "unlocked": True},
            {"name": "Consistent", "desc": "Use app 7 days in a row", "icon": "📅", "points": 50, "unlocked": True},
            {"name": "Favorite Collector", "desc": "Save 10 favorites", "icon": "⭐", "points": 25, "unlocked": False}
        ]
        
        # Grid container
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20)
        
        for i, ach in enumerate(achievements):
            row = i // 3
            col = i % 3
            
            card = ctk.CTkFrame(
                grid,
                fg_color="#10b981" if ach["unlocked"] else "#2b3e50",
                corner_radius=15,
                width=280,
                height=200
            )
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            card.grid_propagate(False)
            
            # Icon
            ctk.CTkLabel(card, text=ach["icon"], font=("Arial", 50)).pack(pady=(20,10))
            
            # Name
            ctk.CTkLabel(
                card, 
                text=ach["name"],
                font=("Arial Bold", 18),
                text_color="white"
            ).pack()
            
            # Description
            ctk.CTkLabel(
                card,
                text=ach["desc"],
                font=("Arial", 12),
                text_color="white" if ach["unlocked"] else "#94a3b8",
                wraplength=240
            ).pack(pady=5)
            
            # Points
            ctk.CTkLabel(
                card,
                text=f"+{ach['points']} pts",
                font=("Arial Bold", 14),
                text_color="#fbbf24"
            ).pack(pady=5)
            
            # Status
            if ach["unlocked"]:
                status_frame = ctk.CTkFrame(card, fg_color="white", corner_radius=8)
                status_frame.pack(pady=5)
                ctk.CTkLabel(
                    status_frame,
                    text="✓ Unlocked",
                    font=("Arial Bold", 11),
                    text_color="#10b981"
                ).pack(padx=12, pady=4)
            
            # Configure grid
            grid.columnconfigure(col, weight=1)
class PracticeView(ctk.CTkFrame):
    """Simple working quiz mode"""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        self.app = app
        self.current_letter = None
        self.score = 0
        self.total = 0
        self.correct_answers = 0

        # Title
        ctk.CTkLabel(
            self, text="🎯 Quiz Mode",
            font=("Arial Bold", 32)
        ).pack(pady=20)

        # Score
        score_frame = ctk.CTkFrame(self, fg_color="transparent")
        score_frame.pack(pady=10)
        
        self.score_label = ctk.CTkLabel(
            score_frame, text="Score: 0/0",
            font=("Arial", 20)
        )
        self.score_label.pack(side="left", padx=10)

        # Image display
        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.pack(pady=20)

        # Question
        self.question_label = ctk.CTkLabel(
            self, text="Click Start to begin!",
            font=("Arial", 16)
        )
        self.question_label.pack(pady=10)

        # Answer buttons
        self.answer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.answer_frame.pack(pady=20)
        
        # Result label (below buttons, hidden initially)
        self.result_label = ctk.CTkLabel(
            self, text="",
            font=("Arial Bold", 20)
        )
        self.result_label.pack(pady=20)
        
        # Next button (hidden initially)
        self.next_btn = ctk.CTkButton(
            self, text="➡️ Next Question",
            command=self.next_question,
            height=50, width=200,
            font=("Arial Bold", 16)
        )
        
        # Control buttons frame
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(pady=20)
        
        ctk.CTkButton(
            control_frame, text="▶️ Start Quiz",
            command=self.start_quiz,
            height=50, width=180,
            font=("Arial Bold", 14)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame, text="💡 Show Answer",
            command=self.show_answer,
            height=50, width=180,
            font=("Arial Bold", 14),
            fg_color="#f59e0b"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame, text="🔄 Restart",
            command=self.restart_quiz,
            height=50, width=180,
            font=("Arial Bold", 14),
            fg_color="#ef4444"
        ).pack(side="left", padx=5)

    def start_quiz(self):
        self.score = 0
        self.total = 0
        self.score_label.configure(text="Score: 0/0")
        self.next_question()

    def next_question(self):
        import random
        
        # Hide next button and clear result
        self.next_btn.pack_forget()
        self.result_label.configure(text="")
        
        # Get letters
        letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.current_letter = random.choice(letters)
        self.total += 1

        # Show image
        try:
            img_path = f"assets/sign_images/{self.current_letter.lower()}.jpg"
            from PIL import Image
            img = Image.open(img_path)
            img = img.resize((400, 400))
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 400))
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
        except:
            self.image_label.configure(text="Image not found")

        self.question_label.configure(text="Which letter is this?")

        # Create answer buttons
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        wrong = random.sample([l for l in letters if l != self.current_letter], 3)
        options = wrong + [self.current_letter]
        random.shuffle(options)
        for option in options:
            btn = ctk.CTkButton(
                self.answer_frame,
                text=option,
                command=lambda opt=option: self.check_answer(opt),
                width=100, height=60,
                font=("Arial Bold", 24),
                state="normal"
            )
            btn.pack(side="left", padx=10)
    
    def show_answer(self):
        """Show the correct answer"""
        if self.current_letter:
            self.result_label.configure(
                text=f"💡 The answer is: {self.current_letter}",
                text_color="#f59e0b"
            )
    
    def restart_quiz(self):
        """Restart the quiz from beginning"""
        self.score = 0
        self.total = 0
        self.current_letter = None
        self.score_label.configure(text="Score: 0/0")
        self.result_label.configure(text="")
        self.question_label.configure(text="Click Start to begin!")
        self.image_label.configure(image=None, text="")
        self.next_btn.pack_forget()
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

    def check_answer(self, selected):
        # Disable all buttons
        for widget in self.answer_frame.winfo_children():
            widget.configure(state="disabled")
        
        if selected == self.current_letter:
            self.score += 1
            result_text = "✅ Correct!"
            result_color = "green"
            # Play success sound (system beep)
            try:
                import winsound
                winsound.Beep(800, 200)  # 800Hz, 200ms
            except:
                pass
        else:
            result_text = f"❌ Wrong! The correct answer was: {self.current_letter}"
            result_color = "red"
            # Play error sound
            try:
                import winsound
                winsound.Beep(400, 300)  # 400Hz, 300ms
            except:
                pass
        
        # Show result below buttons
        self.result_label.configure(text=result_text, text_color=result_color)
        self.score_label.configure(text=f"Score: {self.score}/{self.total}")
        
        # Show Next button
        self.next_btn.pack(pady=20)




        for option in options:
            btn = ctk.CTkButton(
                self.answer_frame, text=option,
                command=lambda opt=option: self.check_answer(opt),
                height=60, width=100,
                font=("Segoe UI", 24, "bold"),
                fg_color=self.app.theme_colors['surface'],
                border_width=2,
                border_color=self.app.theme_colors['primary']
            )
            btn.pack(side="left", padx=10)

    def check_answer(self, selected):
        """Check if answer is correct"""
        # Total already incremented in next_question

        if selected == self.current_letter:
            self.score += 1
            ToastNotification.show(self.app, "✅ Correct!", type='success')
        else:
            ToastNotification.show(
                self.app,
                f"❌ Wrong! It was {self.current_letter}",
                type='error'
            )

        self.score_label.configure(text=f"Score: {self.score}/{self.total}")

        # Auto next question
        self.after(1500, self.next_question)


class SettingsView(ctk.CTkFrame):
    """Enhanced settings view"""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        self.app = app

        ctk.CTkLabel(
            self, text="⚙️ Settings",
            font=("Segoe UI", 32, "bold"),
            text_color=app.theme_colors['primary']
        ).pack(pady=(0, 20))

        # Get current preferences
        prefs = app.settings_manager.get_user_preferences(app.current_user['id'])

        # Settings categories
        categories = [
            ("🎨 Appearance", [
                ("Dark Mode", "theme", "switch", prefs['theme'] == 'dark'),
                ("Animation Speed", "animation_speed", "slider", prefs['animation_speed']),
            ]),
            ("🔊 Audio & Notifications", [
                ("Sound Effects", "sound_enabled", "switch", prefs['sound_enabled']),
                ("Push Notifications", "notifications_enabled", "switch", prefs['notifications_enabled']),
            ]),
            ("⚡ Performance", [
                ("Auto-Save", "auto_save", "switch", prefs['auto_save']),
            ])
        ]

        for category, settings in categories:
            self.create_settings_section(category, settings)

    def create_settings_section(self, title, settings):
        """Create settings section"""
        section = ctk.CTkFrame(self, fg_color=self.app.theme_colors['surface'], corner_radius=15)
        section.pack(fill="x", pady=10)

        ctk.CTkLabel(
            section, text=title,
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(15, 10))

        for label, key, widget_type, value in settings:
            row = ctk.CTkFrame(section, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)

            ctk.CTkLabel(
                row, text=label,
                font=("Segoe UI", 14),
                anchor="w"
            ).pack(side="left")

            if widget_type == "switch":
                switch = ctk.CTkSwitch(
                    row, text="",
                    command=lambda k=key, s=None: self.update_setting(k, s)
                )
                if value:
                    switch.select()
                switch.pack(side="right")
            elif widget_type == "slider":
                slider = ctk.CTkSlider(
                    row, from_=0.3, to=2.5,
                    command=lambda v, k=key: self.update_setting(k, v)
                )
                slider.set(value)
                slider.pack(side="right", fill="x", expand=True, padx=(20, 0))

        ctk.CTkLabel(section, text="").pack(pady=10)

    def update_setting(self, key, value):
        """Update setting"""
        if value is None:
            value = not self.app.settings_manager.get_user_preferences(
                self.app.current_user['id']
            ).get(key, False)

        self.app.settings_manager.update_preference(
            self.app.current_user['id'], key, value
        )

        ToastNotification.show(self.app, "✅ Setting updated!", type='success')


class ProfileView(ctk.CTkFrame):
    """Enhanced profile view"""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        self.app = app

        ctk.CTkLabel(
            self, text="👤 Profile",
            font=("Segoe UI", 32, "bold"),
            text_color=app.theme_colors['primary']
        ).pack(pady=(0, 20))

        # Profile card
        card = ctk.CTkFrame(self, fg_color=app.theme_colors['surface'], corner_radius=15)
        card.pack(fill="x")

        # Avatar
        ctk.CTkLabel(card, text="👤", font=("Segoe UI", 100)).pack(pady=20)

        ctk.CTkLabel(
            card, text=app.current_user['name'],
            font=("Segoe UI", 28, "bold")
        ).pack()

        # Stats
        stats = app.db.get_user_stats(app.current_user['id'])
        earned = app.settings_manager.get_user_achievements(app.current_user['id'])

        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.pack(pady=20)

        stats_data = [
            ("Translations", stats['total_translations'], "🔢"),
            ("Achievements", len(earned), "🏆"),
            ("Time Spent", f"{stats['total_duration']:.0f}s", "⏱️")
        ]

        for label, value, icon in stats_data:
            stat_box = ctk.CTkFrame(stats_frame, fg_color=app.theme_colors['primary'], 
                                   corner_radius=10)
            stat_box.pack(side="left", padx=10)

            ctk.CTkLabel(stat_box, text=icon, font=("Segoe UI", 30)).pack(pady=10)
            ctk.CTkLabel(
                stat_box, text=str(value),
                font=("Segoe UI", 24, "bold"),
                text_color="white"
            ).pack()
            ctk.CTkLabel(
                stat_box, text=label,
                font=("Segoe UI", 12),
                text_color="white"
            ).pack(pady=(0, 10))

        # Actions
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(pady=20)

        ctk.CTkButton(
            action_frame, text="✏️ Edit Profile",
            height=45, width=200,
            font=("Segoe UI", 14, "bold"),
            fg_color=app.theme_colors['primary']
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_frame, text="📊 View Full Stats",
            command=app.show_statistics,
            height=45, width=200,
            font=("Segoe UI", 14, "bold"),
            fg_color=app.theme_colors['secondary']
        ).pack(side="left", padx=5)


# Main entry point


class EnhancedSettingsView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(self, text="⚙️ Settings", font=("Arial Bold", 32)).pack(pady=20)
        
        frame = ctk.CTkFrame(self, fg_color="#2b3e50", corner_radius=15)
        frame.pack(pady=20, fill="both", expand=True, padx=40)
        
        # Sound
        ctk.CTkLabel(frame, text="Sound Settings", font=("Arial Bold", 22), text_color="white").pack(pady=(30,15))
        ctk.CTkSwitch(frame, text="Enable Sound Effects", font=("Arial", 16)).pack(pady=5)
        ctk.CTkSwitch(frame, text="Voice Feedback", font=("Arial", 16)).pack(pady=5)
        
        # Animation
        ctk.CTkLabel(frame, text="Animation Settings", font=("Arial Bold", 22), text_color="white").pack(pady=(30,15))
        ctk.CTkLabel(frame, text="Speed:", font=("Arial", 16), text_color="white").pack()
        ctk.CTkSlider(frame, from_=0.5, to=2.0, width=400).pack(pady=10)
        
        # Notifications
        ctk.CTkLabel(frame, text="Notifications", font=("Arial Bold", 22), text_color="white").pack(pady=(30,15))
        ctk.CTkSwitch(frame, text="Show Achievements", font=("Arial", 16)).pack(pady=5)
        ctk.CTkSwitch(frame, text="Daily Reminders", font=("Arial", 16)).pack(pady=5)
        
        # About
        ctk.CTkLabel(frame, text="About", font=("Arial Bold", 22), text_color="white").pack(pady=(30,15))
        ctk.CTkLabel(frame, text="SignTalk Pro v1.0\nVoice to Sign Language", 
                    font=("Arial", 16), text_color="#94a3b8").pack(pady=15)

class EnhancedProfileView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(self, text="👤 Profile", font=("Arial Bold", 32)).pack(pady=20)
        
        frame = ctk.CTkFrame(self, fg_color="#2b3e50", corner_radius=15)
        frame.pack(pady=20, fill="both", expand=True, padx=40)
        
        # User info
        ctk.CTkLabel(frame, text="🤟", font=("Arial", 80)).pack(pady=20)
        ctk.CTkLabel(frame, text="Siddhesh", font=("Arial Bold", 28), text_color="white").pack(pady=10)
        ctk.CTkLabel(frame, text="Premium Member", font=("Arial", 18), text_color="#14b8a6").pack()
        
        # Stats
        stats_frame = ctk.CTkFrame(frame, fg_color="transparent")
        stats_frame.pack(pady=30)
        
        for label, value in [("Translations", "13"), ("Favorites", "1"), ("Daily Goal", "0/10")]:
            box = ctk.CTkFrame(stats_frame, fg_color="#1e293b", corner_radius=10, width=150, height=100)
            box.pack(side="left", padx=15)
            box.pack_propagate(False)
            ctk.CTkLabel(box, text=value, font=("Arial Bold", 28), text_color="white").pack(pady=(20,5))
            ctk.CTkLabel(box, text=label, font=("Arial", 14), text_color="#94a3b8").pack()




if __name__ == "__main__":
    app = ProfessionalSignLanguageApp()
    app.mainloop()