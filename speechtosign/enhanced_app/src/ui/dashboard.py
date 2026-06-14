import customtkinter as ctk
from tkinter import messagebox
import sys
import os
from datetime import datetime
from threading import Thread
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.database_manager import DatabaseManager
from src.core.sign_animator import SignAnimator, AnimatedSignDisplay, AnimationController
from src.core.speech_handler import SpeechHandler
from src.utils import config

class Dashboard(ctk.CTk):
    def __init__(self, user_id, username, login_window):
        super().__init__()
        
        self.user_id = user_id
        self.username = username
        self.login_window = login_window
        
        # Initialize components
        self.db = DatabaseManager(config.DATABASE_PATH)
        self.animator = SignAnimator(config.SIGN_IMAGES_PATH)
        self.speech_handler = SpeechHandler()
        
        # Session tracking
        self.session_id = self.db.create_session(user_id)
        self.translation_count = 0
        self.session_start = datetime.now()
        
        # Configure window
        self.title("Voice to Sign Language Translator")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        
        # Set theme
        ctk.set_appearance_mode("light")
        
        # Current view
        self.current_view = None
        
        # Create UI
        self.create_ui()
        
        # Center window
        self.center_window()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show translator view by default
        self.show_translator()
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create main dashboard UI"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Content area
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=config.BACKGROUND_COLOR
        )
        self.content_frame.pack(side="right", fill="both", expand=True)
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ctk.CTkFrame(
            self.main_container,
            width=250,
            fg_color=config.PRIMARY_COLOR
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.pack(pady=30, padx=20)
        
        ctk.CTkLabel(
            title_frame,
            text="🤟",
            font=(config.FONT_FAMILY, 40)
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Voice to Sign",
            font=(config.FONT_FAMILY, 18, "bold"),
            text_color="white"
        ).pack()
        
        # User info
        user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        user_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.username}",
            font=(config.FONT_FAMILY, 14),
            text_color="white"
        ).pack(anchor="w")
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=15, pady=20)
        
        self.nav_buttons = {}
        
        buttons_config = [
            ("🎙️ Translator", self.show_translator),
            ("📜 History", self.show_history),
            ("⭐ Favorites", self.show_favorites),
            ("📊 Statistics", self.show_statistics),
            ("⚙️ Settings", self.show_settings),
        ]
        
        for text, command in buttons_config:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                height=45,
                font=(config.FONT_FAMILY, 14),
                fg_color="transparent",
                text_color="white",
                hover_color=config.SECONDARY_COLOR,
                anchor="w",
                corner_radius=10
            )
            btn.pack(fill="x", pady=5)
            self.nav_buttons[text] = btn
        
        # Logout button at bottom
        ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            command=self.logout,
            height=40,
            font=(config.FONT_FAMILY, 14),
            fg_color=config.ERROR_COLOR,
            hover_color="#dc2626",
            corner_radius=10
        ).pack(side="bottom", pady=20, padx=15, fill="x")
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def highlight_nav_button(self, button_text):
        """Highlight active navigation button"""
        for text, btn in self.nav_buttons.items():
            if text == button_text:
                btn.configure(fg_color=config.SECONDARY_COLOR)
            else:
                btn.configure(fg_color="transparent")
    
    def show_translator(self):
        """Show translator interface"""
        self.clear_content()
        self.highlight_nav_button("🎙️ Translator")
        self.current_view = "translator"
        
        # Create translator view
        TranslatorView(self.content_frame, self)
    
    def show_history(self):
        """Show translation history"""
        self.clear_content()
        self.highlight_nav_button("📜 History")
        self.current_view = "history"
        
        # Create history view
        HistoryView(self.content_frame, self)
    
    def show_favorites(self):
        """Show favorites"""
        self.clear_content()
        self.highlight_nav_button("⭐ Favorites")
        self.current_view = "favorites"
        
        # Create favorites view
        FavoritesView(self.content_frame, self)
    
    def show_statistics(self):
        """Show statistics"""
        self.clear_content()
        self.highlight_nav_button("📊 Statistics")
        self.current_view = "statistics"
        
        # Create statistics view
        StatisticsView(self.content_frame, self)
    
    def show_settings(self):
        """Show settings"""
        self.clear_content()
        self.highlight_nav_button("⚙️ Settings")
        self.current_view = "settings"
        
        # Create settings view
        SettingsView(self.content_frame, self)
    
    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Close session
            self.db.close_session(self.session_id, self.translation_count)
            
            # Show login window
            self.destroy()
            self.login_window.deiconify()
            self.login_window.username_entry.delete(0, 'end')
            self.login_window.password_entry.delete(0, 'end')
    
    def on_closing(self):
        """Handle window close"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.db.close_session(self.session_id, self.translation_count)
            self.destroy()
            self.login_window.destroy()


class TranslatorView:
    """Translator interface view - FIXED VERSION"""
    
    def __init__(self, parent, dashboard):
        self.parent = parent
        self.dashboard = dashboard
        self.animator = dashboard.animator
        self.speech_handler = dashboard.speech_handler
        
        self.is_recording = False
        self.is_animating = False
        self.animation_start_time = None
        
        # Store references
        self.sign_display = None
        self.animation_controller = None
        
        self.create_ui()
    
    def create_ui(self):
        """Create translator interface"""
        import tkinter as tk
        
        # Main container
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        ctk.CTkLabel(
            main,
            text="🎙️ Voice to Sign Language Translator",
            font=(config.FONT_FAMILY, 28, "bold"),
            text_color=config.PRIMARY_COLOR
        ).pack(pady=(0, 20))
        
        # Content area with two columns
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        # Left column - Controls
        left_col = ctk.CTkFrame(content, fg_color="white", corner_radius=15)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Input section
        input_section = ctk.CTkFrame(left_col, fg_color="transparent")
        input_section.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            input_section,
            text="Enter Text or Use Voice",
            font=(config.FONT_FAMILY, 18, "bold"),
            text_color=config.TEXT_COLOR
        ).pack(anchor="w", pady=(0, 10))
        
        # Text input
        self.text_input = ctk.CTkTextbox(
            input_section,
            height=100,
            font=(config.FONT_FAMILY, 14)
        )
        self.text_input.pack(fill="x", pady=(0, 15))
        
        # Voice recording section
        voice_frame = ctk.CTkFrame(input_section, fg_color=config.BACKGROUND_COLOR, corner_radius=10)
        voice_frame.pack(fill="x", pady=(0, 15))
        
        self.voice_status = ctk.CTkLabel(
            voice_frame,
            text="🎤 Ready to record",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_LIGHT
        )
        self.voice_status.pack(pady=10)
        
        # Control buttons
        button_frame = ctk.CTkFrame(input_section, fg_color="transparent")
        button_frame.pack(fill="x")
        
        self.record_btn = ctk.CTkButton(
            button_frame,
            text="🎤 Start Recording",
            command=self.toggle_recording,
            height=45,
            font=(config.FONT_FAMILY, 14, "bold"),
            fg_color=config.SECONDARY_COLOR,
            hover_color="#0d9488"
        )
        self.record_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.translate_btn = ctk.CTkButton(
            button_frame,
            text="▶️ Translate",
            command=self.start_translation,
            height=45,
            font=(config.FONT_FAMILY, 14, "bold"),
            fg_color=config.PRIMARY_COLOR,
            hover_color="#1e40af"
        )
        self.translate_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Animation controls
        controls_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            controls_frame,
            text="Animation Speed",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR
        ).pack(anchor="w")
        
        self.speed_slider = ctk.CTkSlider(
            controls_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19,
            command=self.update_speed
        )
        self.speed_slider.set(0.5)
        self.speed_slider.pack(fill="x", pady=5)
        
        self.speed_label = ctk.CTkLabel(
            controls_frame,
            text="Speed: 0.5s per letter",
            font=(config.FONT_FAMILY, 10),
            text_color=config.TEXT_LIGHT
        )
        self.speed_label.pack(anchor="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)
        
        self.stop_btn = ctk.CTkButton(
            action_frame,
            text="⏹️ Stop",
            command=self.stop_animation,
            height=40,
            font=(config.FONT_FAMILY, 13),
            fg_color=config.ERROR_COLOR,
            state="disabled"
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.save_btn = ctk.CTkButton(
            action_frame,
            text="⭐ Save to Favorites",
            command=self.save_to_favorites,
            height=40,
            font=(config.FONT_FAMILY, 13),
            fg_color=config.WARNING_COLOR
        )
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Right column - Animation display
        right_col = ctk.CTkFrame(content, fg_color="white", corner_radius=15)
        right_col.pack(side="right", fill="both", expand=True)
        
        # Title
        title_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        title_frame.pack(pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="Sign Language Animation",
            font=(config.FONT_FAMILY, 18, "bold"),
            text_color=config.PRIMARY_COLOR
        ).pack()
        
        # IMPORTANT: Create regular tkinter frame for canvas
        # CustomTkinter doesn't play well with Canvas widgets
        canvas_outer = ctk.CTkFrame(right_col, fg_color="white")
        canvas_outer.pack(expand=True, padx=20, pady=20)
        
        # Use REGULAR tkinter Frame inside
        tk_frame = tk.Frame(canvas_outer, bg="white")
        tk_frame.pack()
        
        # Create display in regular tkinter frame
        self.sign_display = AnimatedSignDisplay(tk_frame, self.animator, 400, 400)
        self.sign_display.pack()
        
        # Initialize controller
        self.animation_controller = AnimationController(self.animator, self.sign_display)
        
        # Force update to ensure frame is ready
        self.parent.update_idletasks()
    
    def toggle_recording(self):
        """Toggle voice recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start voice recording"""
        self.is_recording = True
        self.record_btn.configure(text="⏹️ Stop Recording", fg_color=config.ERROR_COLOR)
        self.voice_status.configure(text="🔴 Recording... Speak now!")
        
        def record_thread():
            success, text = self.speech_handler.listen_once(timeout=10, phrase_time_limit=20)
            self.parent.after(0, lambda: self.after_recording(success, text))
        
        Thread(target=record_thread, daemon=True).start()
    
    def stop_recording(self):
        """Stop voice recording"""
        self.is_recording = False
        self.record_btn.configure(text="🎤 Start Recording", fg_color=config.SECONDARY_COLOR)
        self.voice_status.configure(text="🎤 Ready to record")
        self.speech_handler.stop_listening()
    
    def after_recording(self, success, text):
        """Handle recording result"""
        self.is_recording = False
        self.record_btn.configure(text="🎤 Start Recording", fg_color=config.SECONDARY_COLOR)
        
        if success:
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", text)
            self.voice_status.configure(text=f"✅ Recognized: {text}")
        else:
            self.voice_status.configure(text=f"❌ {text}")
    
    def start_translation(self):
        """Start translation animation"""
        text = self.text_input.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showwarning("No Input", "Please enter text or use voice recording")
            return
        
        if self.is_animating:
            messagebox.showinfo("Animation Running", "Please wait for current animation to finish")
            return
        
        # Update UI
        self.is_animating = True
        self.translate_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.animation_start_time = time.time()
        
        # Start animation
        speed = self.speed_slider.get()
        
        def run_and_complete():
            self.animation_controller.start_animation(text, speed)
            
            # Wait for completion
            while self.animation_controller.is_running():
                time.sleep(0.1)
            
            # Update UI in main thread
            self.parent.after(0, self.animation_complete, text)
        
        Thread(target=run_and_complete, daemon=True).start()
    
    def animation_complete(self, text):
        """Called when animation finishes"""
        self.is_animating = False
        self.translate_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # Save to history
        duration = time.time() - self.animation_start_time
        self.dashboard.db.add_translation(
            self.dashboard.user_id,
            text,
            text.upper(),
            duration
        )
        self.dashboard.translation_count += 1
    
    def stop_animation(self):
        """Stop current animation"""
        self.animation_controller.stop_animation()
        self.is_animating = False
        self.translate_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
    
    def update_speed(self, value):
        """Update animation speed"""
        self.speed_label.configure(text=f"Speed: {value:.1f}s per letter")
        if self.animation_controller:
            self.animation_controller.set_speed(value)
    
    def save_to_favorites(self):
        """Save current text to favorites"""
        text = self.text_input.get("1.0", "end-1c").strip()
        
        if not text:
            messagebox.showwarning("No Text", "Please enter text to save")
            return
        
        success = self.dashboard.db.add_favorite(self.dashboard.user_id, text)
        
        if success:
            messagebox.showinfo("Success", "Added to favorites!")
        else:
            messagebox.showerror("Error", "Failed to add to favorites")

# Placeholder views for other sections
class HistoryView:
    def __init__(self, parent, dashboard):
        self.parent = parent
        self.dashboard = dashboard
        self.create_ui()
    
    def create_ui(self):
        main = ctk.CTkFrame(self.parent, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(
            main,
            text="📜 Translation History",
            font=(config.FONT_FAMILY, 28, "bold"),
            text_color=config.PRIMARY_COLOR
        ).pack(pady=(0, 20))
        
        # History list will be implemented next
        content = ctk.CTkFrame(main, fg_color="white", corner_radius=15)
        content.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            content,
            text="History view - Coming in next step",
            font=(config.FONT_FAMILY, 16)
        ).pack(expand=True)


class FavoritesView:
    def __init__(self, parent, dashboard):
        ctk.CTkLabel(
            parent,
            text="⭐ Favorites - Coming soon",
            font=(config.FONT_FAMILY, 20)
        ).pack(expand=True)


class StatisticsView:
    def __init__(self, parent, dashboard):
        ctk.CTkLabel(
            parent,
            text="📊 Statistics - Coming soon",
            font=(config.FONT_FAMILY, 20)
        ).pack(expand=True)


class SettingsView:
    def __init__(self, parent, dashboard):
        ctk.CTkLabel(
            parent,
            text="⚙️ Settings - Coming soon",
            font=(config.FONT_FAMILY, 20)
        ).pack(expand=True)