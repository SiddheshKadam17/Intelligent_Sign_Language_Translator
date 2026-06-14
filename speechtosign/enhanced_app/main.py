import customtkinter as ctk
import sys
import os

# Get absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

sys.path.append('src')
from src.ui.login_window import LoginWindow

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()