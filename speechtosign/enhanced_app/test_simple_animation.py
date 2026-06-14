import tkinter as tk
from PIL import Image, ImageTk
import os

root = tk.Tk()
root.title("Test Animation")

canvas = tk.Canvas(root, width=400, height=400, bg='white')
canvas.pack(pady=20)

label = tk.Label(root, text="Testing...")
label.pack()

# Load and display an image
img_path = "assets/sign_images/a.jpg"
if os.path.exists(img_path):
    img = Image.open(img_path)
    img = img.resize((400, 400))
    photo = ImageTk.PhotoImage(img)
    
    # Keep reference!
    canvas.image = photo
    
    canvas.create_image(200, 200, image=photo)
    label.config(text="Image loaded successfully!")
else:
    label.config(text=f"Image not found: {img_path}")

root.mainloop()