import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.database_manager import DatabaseManager
from src.utils import config

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.db = DatabaseManager(config.DATABASE_PATH)
        
        # Configure window
        self.title("Voice to Sign Language - Login")
        self.geometry(f"{800}x{600}")
        self.resizable(False, False)
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Center window on screen
        self.center_window()
        
        # Current user data
        self.current_user_id = None
        self.current_username = None
        
        # Create UI
        self.create_login_ui()
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_login_ui(self):
        """Create login interface"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Left side - Welcome message
        left_frame = ctk.CTkFrame(main_frame, fg_color=config.PRIMARY_COLOR, corner_radius=20)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        welcome_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        welcome_container.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            welcome_container,
            text="🤟",
            font=("Segoe UI", 80)
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            welcome_container,
            text="Voice to Sign",
            font=(config.FONT_FAMILY, 32, "bold"),
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            welcome_container,
            text="Language Translator",
            font=(config.FONT_FAMILY, 24),
            text_color="white"
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            welcome_container,
            text="Break communication barriers\nwith real-time translation",
            font=(config.FONT_FAMILY, 14),
            text_color="white",
            justify="center"
        ).pack()
        
        # Right side - Login form
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Form container
        form_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        ctk.CTkLabel(
            form_frame,
            text="Welcome Back!",
            font=(config.FONT_FAMILY, 28, "bold"),
            text_color=config.PRIMARY_COLOR
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            form_frame,
            text="Sign in to continue",
            font=(config.FONT_FAMILY, 14),
            text_color=config.TEXT_LIGHT
        ).pack(pady=(0, 30))
        
        # Username field
        ctk.CTkLabel(
            form_frame,
            text="Username",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your username",
            width=300,
            height=40,
            font=(config.FONT_FAMILY, 14)
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password field
        ctk.CTkLabel(
            form_frame,
            text="Password",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your password",
            width=300,
            height=40,
            show="●",
            font=(config.FONT_FAMILY, 14)
        )
        self.password_entry.pack(pady=(0, 30))
        
        # Login button
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="Sign In",
            command=self.handle_login,
            width=300,
            height=45,
            font=(config.FONT_FAMILY, 16, "bold"),
            fg_color=config.PRIMARY_COLOR,
            hover_color=config.SECONDARY_COLOR,
            corner_radius=10
        )
        self.login_btn.pack(pady=(0, 20))
        
        # Divider
        divider_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        divider_frame.pack(fill="x", pady=15)
        
        ctk.CTkFrame(divider_frame, height=1, fg_color=config.TEXT_LIGHT).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(divider_frame, text="OR", text_color=config.TEXT_LIGHT).pack(side="left")
        ctk.CTkFrame(divider_frame, height=1, fg_color=config.TEXT_LIGHT).pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Sign up link
        signup_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        signup_frame.pack()
        
        ctk.CTkLabel(
            signup_frame,
            text="Don't have an account? ",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_LIGHT
        ).pack(side="left")
        
        signup_btn = ctk.CTkButton(
            signup_frame,
            text="Sign Up",
            command=self.show_signup,
            width=60,
            height=25,
            font=(config.FONT_FAMILY, 12, "bold"),
            fg_color="transparent",
            text_color=config.PRIMARY_COLOR,
            hover_color=config.BACKGROUND_COLOR
        )
        signup_btn.pack(side="left")
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
    
    def show_signup(self):
        """Show signup window"""
        self.withdraw()  # Hide login window
        signup_window = SignUpWindow(self)
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validation
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Authenticate
        success, user_id, full_name = self.db.authenticate_user(username, password)
        
        if success:
            self.current_user_id = user_id
            self.current_username = full_name or username
            
            # Show success message
            messagebox.showinfo("Success", f"Welcome back, {self.current_username}!")
            
            # Open main application
            self.open_main_app()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, 'end')
    
    def open_main_app(self):
        """Open main application window"""
        from src.ui.dashboard import Dashboard
        self.withdraw()
        app = Dashboard(self.current_user_id, self.current_username, self)
        app.mainloop()


class SignUpWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.db = parent.db
        
        # Configure window
        self.title("Sign Up - Voice to Sign Language")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_signup_ui()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_signup_ui(self):
        """Create signup interface"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="Create Account",
            font=(config.FONT_FAMILY, 28, "bold"),
            text_color=config.PRIMARY_COLOR
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            main_frame,
            text="Join us to start translating",
            font=(config.FONT_FAMILY, 14),
            text_color=config.TEXT_LIGHT
        ).pack(pady=(0, 30))
        
        # Full Name
        ctk.CTkLabel(
            main_frame,
            text="Full Name",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.fullname_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter your full name",
            width=400,
            height=40,
            font=(config.FONT_FAMILY, 14)
        )
        self.fullname_entry.pack(pady=(0, 15))
        
        # Username
        ctk.CTkLabel(
            main_frame,
            text="Username",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Choose a username",
            width=400,
            height=40,
            font=(config.FONT_FAMILY, 14)
        )
        self.username_entry.pack(pady=(0, 15))
        
        # Email
        ctk.CTkLabel(
            main_frame,
            text="Email",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="your.email@example.com",
            width=400,
            height=40,
            font=(config.FONT_FAMILY, 14)
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Password
        ctk.CTkLabel(
            main_frame,
            text="Password",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Create a strong password",
            width=400,
            height=40,
            show="●",
            font=(config.FONT_FAMILY, 14)
        )
        self.password_entry.pack(pady=(0, 15))
        
        # Confirm Password
        ctk.CTkLabel(
            main_frame,
            text="Confirm Password",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Re-enter your password",
            width=400,
            height=40,
            show="●",
            font=(config.FONT_FAMILY, 14)
        )
        self.confirm_password_entry.pack(pady=(0, 30))
        
        # Sign up button
        ctk.CTkButton(
            main_frame,
            text="Create Account",
            command=self.handle_signup,
            width=400,
            height=45,
            font=(config.FONT_FAMILY, 16, "bold"),
            fg_color=config.PRIMARY_COLOR,
            hover_color=config.SECONDARY_COLOR,
            corner_radius=10
        ).pack(pady=(0, 15))
        
        # Back to login
        back_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        back_frame.pack()
        
        ctk.CTkLabel(
            back_frame,
            text="Already have an account? ",
            font=(config.FONT_FAMILY, 12),
            text_color=config.TEXT_LIGHT
        ).pack(side="left")
        
        ctk.CTkButton(
            back_frame,
            text="Sign In",
            command=self.back_to_login,
            width=60,
            height=25,
            font=(config.FONT_FAMILY, 12, "bold"),
            fg_color="transparent",
            text_color=config.PRIMARY_COLOR,
            hover_color=config.BACKGROUND_COLOR
        ).pack(side="left")
    
    def handle_signup(self):
        """Handle signup attempt"""
        full_name = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not all([full_name, username, email, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Create user
        success, result = self.db.create_user(username, email, password, full_name)
        
        if success:
            messagebox.showinfo("Success", "Account created successfully!\nPlease sign in.")
            self.back_to_login()
        else:
            messagebox.showerror("Error", f"Failed to create account: {result}")
    
    def back_to_login(self):
        """Return to login window"""
        self.destroy()
        self.parent.deiconify()