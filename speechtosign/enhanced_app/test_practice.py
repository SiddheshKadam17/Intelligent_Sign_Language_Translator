with open("professional_app_fixed.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add debug to create_ui
old = """    def create_ui(self):
        # Header
        ctk.CTkLabel("""

new = """    def create_ui(self):
        print("CREATING PRACTICE UI!")
        # Header
        ctk.CTkLabel("""

content = content.replace(old, new)

with open("professional_app_fixed.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Added debug")
