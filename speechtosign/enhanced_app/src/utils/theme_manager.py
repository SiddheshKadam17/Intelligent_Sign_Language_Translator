class ThemeManager:
    """Manage app themes and color schemes"""
    
    # Color schemes
    THEMES = {
        'blue': {
            'light': {
                'primary': '#1f538d',
                'secondary': '#14b8a6',
                'background': '#f8fafc',
                'surface': '#ffffff',
                'text': '#0f172a',
                'text_secondary': '#64748b',
                'success': '#22c55e',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#3b82f6'
            },
            'dark': {
                'primary': '#3b82f6',
                'secondary': '#14b8a6',
                'background': '#0f172a',
                'surface': '#1e293b',
                'text': '#f1f5f9',
                'text_secondary': '#94a3b8',
                'success': '#22c55e',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#60a5fa'
            }
        },
        'green': {
            'light': {
                'primary': '#059669',
                'secondary': '#8b5cf6',
                'background': '#f0fdf4',
                'surface': '#ffffff',
                'text': '#064e3b',
                'text_secondary': '#6b7280',
                'success': '#10b981',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#34d399'
            },
            'dark': {
                'primary': '#10b981',
                'secondary': '#8b5cf6',
                'background': '#064e3b',
                'surface': '#065f46',
                'text': '#ecfdf5',
                'text_secondary': '#a7f3d0',
                'success': '#34d399',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#6ee7b7'
            }
        },
        'purple': {
            'light': {
                'primary': '#7c3aed',
                'secondary': '#ec4899',
                'background': '#faf5ff',
                'surface': '#ffffff',
                'text': '#581c87',
                'text_secondary': '#6b7280',
                'success': '#22c55e',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#a78bfa'
            },
            'dark': {
                'primary': '#a78bfa',
                'secondary': '#f472b6',
                'background': '#581c87',
                'surface': '#6b21a8',
                'text': '#faf5ff',
                'text_secondary': '#e9d5ff',
                'success': '#22c55e',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#c4b5fd'
            }
        },
        'orange': {
            'light': {
                'primary': '#ea580c',
                'secondary': '#06b6d4',
                'background': '#fff7ed',
                'surface': '#ffffff',
                'text': '#7c2d12',
                'text_secondary': '#6b7280',
                'success': '#22c55e',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#fb923c'
            },
            'dark': {
                'primary': '#fb923c',
                'secondary': '#22d3ee',
                'background': '#7c2d12',
                'surface': '#9a3412',
                'text': '#fff7ed',
                'text_secondary': '#fed7aa',
                'success': '#22c55e',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'accent': '#fdba74'
            }
        }
    }
    
    @staticmethod
    def get_theme(mode='light', scheme='blue'):
        """Get theme colors"""
        return ThemeManager.THEMES.get(scheme, ThemeManager.THEMES['blue']).get(mode, ThemeManager.THEMES['blue']['light'])
    
    @staticmethod
    def get_available_schemes():
        """Get list of available color schemes"""
        return list(ThemeManager.THEMES.keys())
    
    @staticmethod
    def apply_theme_to_config(mode='light', scheme='blue'):
        """Apply theme to config module"""
        theme = ThemeManager.get_theme(mode, scheme)
        
        # Update config module
        import src.utils.config as config
        config.PRIMARY_COLOR = theme['primary']
        config.SECONDARY_COLOR = theme['secondary']
        config.BACKGROUND_COLOR = theme['background']
        config.TEXT_COLOR = theme['text']
        config.TEXT_LIGHT = theme['text_secondary']
        config.SUCCESS_COLOR = theme['success']
        config.ERROR_COLOR = theme['error']
        config.WARNING_COLOR = theme['warning']
        
        return theme


class ToastNotification:
    """Toast notification system"""
    
    @staticmethod
    def show(parent, message, duration=3000, type='info'):
        """Show toast notification"""
        import customtkinter as ctk
        
        colors = {
            'success': '#22c55e',
            'error': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6'
        }
        
        toast = ctk.CTkFrame(parent, fg_color=colors.get(type, colors['info']), corner_radius=10)
        toast.place(relx=0.5, rely=0.1, anchor='n')
        
        ctk.CTkLabel(
            toast, text=message,
            font=("Segoe UI", 13, "bold"),
            text_color="white"
        ).pack(padx=20, pady=12)
        
        def hide():
            toast.destroy()
        
        parent.after(duration, hide)


class LoadingOverlay:
    """Loading overlay with spinner"""
    
    def __init__(self, parent, text="Loading..."):
        import customtkinter as ctk
        
        self.overlay = ctk.CTkFrame(parent, fg_color=("white", "#1e293b"))
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        container = ctk.CTkFrame(self.overlay, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Spinner (using label animation)
        self.spinner = ctk.CTkLabel(container, text="⏳", font=("Segoe UI", 60))
        self.spinner.pack()
        
        ctk.CTkLabel(
            container, text=text,
            font=("Segoe UI", 16)
        ).pack(pady=10)
        
        self.animate_spinner()
    
    def animate_spinner(self):
        """Animate spinner"""
        spinners = ["⏳", "⌛", "⏳", "⌛"]
        current = spinners[0]
        idx = 0
        
        def update():
            nonlocal idx
            if hasattr(self, 'spinner') and self.spinner.winfo_exists():
                self.spinner.configure(text=spinners[idx % len(spinners)])
                idx += 1
                self.overlay.after(500, update)
        
        update()
    
    def hide(self):
        """Hide loading overlay"""
        self.overlay.destroy()