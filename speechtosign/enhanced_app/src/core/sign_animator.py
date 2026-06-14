import os
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import time
from threading import Thread
import tkinter as tk
from tkinter import Label, Canvas

class SignAnimator:
    def __init__(self, image_path="assets/sign_images"):
        """Initialize the sign language animator"""
        self.image_path = image_path
        self.current_animation = None
        self.is_animating = False
        self.animation_speed = 0.5  # seconds per gesture
        self.image_cache = {}
        self.load_images()
    
    def load_images(self):
        """Load all sign language images into memory"""
        if not os.path.exists(self.image_path):
            print(f"Warning: Image path {self.image_path} does not exist")
            return
        
        print("Loading sign language images...")
        for filename in os.listdir(self.image_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                letter = filename.split('.')[0].upper()
                img_path = os.path.join(self.image_path, filename)
                try:
                    img = Image.open(img_path)
                    self.image_cache[letter] = img
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        print(f"Loaded {len(self.image_cache)} sign language images")
    
    def get_sign_image(self, character, size=(400, 400)):
        """Get sign language image for a character"""
        char = character.upper()
        
        # Handle special characters
        if char == ' ':
            return self.create_blank_image(size)
        elif not char.isalnum():
            return self.create_blank_image(size, text=char)
        
        # Get image from cache
        if char in self.image_cache:
            img = self.image_cache[char].copy()
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
        else:
            return self.create_placeholder_image(size, char)
    
    def create_blank_image(self, size=(400, 400), text=""):
        """Create a blank image for spaces"""
        img = Image.new('RGB', size, color='white')
        if text:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            draw.text((x, y), text, fill='black', font=font)
        
        return img
    
    def create_placeholder_image(self, size=(400, 400), char="?"):
        """Create placeholder for missing characters"""
        img = Image.new('RGB', size, color='#f0f0f0')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 80)
            small_font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        text = char
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2 - 40
        draw.text((x, y), text, fill='#999999', font=font)
        
        msg = "Not Available"
        bbox = draw.textbbox((0, 0), msg, font=small_font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        y = size[1] // 2 + 40
        draw.text((x, y), msg, fill='#cccccc', font=small_font)
        
        return img
    
    def apply_transition_effect(self, img1, img2, progress):
        """Create smooth transition between two images"""
        return Image.blend(img1, img2, progress)
    
    def animate_text(self, text, display_callback, speed=None):
        """Animate text character by character"""
        if speed is None:
            speed = self.animation_speed
        
        self.is_animating = True
        text = ' '.join(text.split())
        
        if not text:
            self.is_animating = False
            return
        
        for i, char in enumerate(text):
            if not self.is_animating:
                break
            
            # Show the sign image
            current_img = self.get_sign_image(char)
            display_callback(current_img, char, i + 1, len(text))
            time.sleep(speed)
            
            # Show white gap after every letter
            blank = self.create_blank_image()
            display_callback(blank, char, i + 1, len(text))
            time.sleep(0.2)
        
        self.is_animating = False
    
    
    def stop_animation(self):
        """Stop current animation"""
        self.is_animating = False
    
    def set_animation_speed(self, speed):
        """Set animation speed (seconds per character)"""
        self.animation_speed = max(0.1, min(2.0, speed))
    
    def get_available_characters(self):
        """Get list of available characters"""
        return sorted(list(self.image_cache.keys()))
    
    def preprocess_text(self, text):
        """Preprocess text for animation"""
        text = text.upper()
        text = ' '.join(text.split())
        return text


class AnimatedSignDisplay:
    """Widget for displaying animated sign language - Fixed version"""
    
    def __init__(self, parent, animator, width=400, height=400):
        self.parent = parent
        self.animator = animator
        self.width = width
        self.height = height
        self.photo_refs = []  # Keep references to prevent garbage collection
        
        # Create canvas
        self.canvas = Canvas(
            parent,
            width=width,
            height=height,
            bg='white',
            highlightthickness=2,
            highlightbackground='#1f538d'
        )
        
        # Info label
        self.info_label = Label(
            parent,
            text="Ready to translate",
            font=("Segoe UI", 12),
            fg='#64748b',
            bg='white'
        )
        
        # Progress label
        self.progress_label = Label(
            parent,
            text="",
            font=("Segoe UI", 10),
            fg='#64748b',
            bg='white'
        )
    
    def pack(self, **kwargs):
        """Pack the display widgets"""
        self.info_label.pack(pady=(10, 5))
        self.canvas.pack(**kwargs)
        self.progress_label.pack(pady=(5, 10))
    
    def display_image(self, pil_image, current_char, current_pos, total_chars):
        """Display an image - called from animation thread"""
        self.parent.after_idle(
            self._do_update,
            pil_image.copy(),
            current_char,
            current_pos,
            total_chars
        )
    
    def _do_update(self, pil_image, current_char, current_pos, total_chars):
        """Actually update the display - runs in main thread"""
        try:
            # Check if canvas still exists before updating
            if not self.canvas.winfo_exists():
                return
                
            if pil_image.size != (self.width, self.height):
                pil_image = pil_image.resize(
                    (self.width, self.height),
                    Image.Resampling.LANCZOS
                )
            
            photo = ImageTk.PhotoImage(pil_image)
            self.photo_refs.append(photo)
            if len(self.photo_refs) > 5:
                self.photo_refs.pop(0)
            
            self.canvas.delete("all")
            self.canvas.create_image(
                self.width // 2,
                self.height // 2,
                image=photo,
                anchor='center'
            )
            
            char_display = current_char if current_char != ' ' else 'SPACE'
            self.info_label.config(text=f"Current: {char_display}")
            self.progress_label.config(text=f"Progress: {current_pos}/{total_chars}")
            
            self.canvas.update_idletasks()
            self.canvas.update()
            
        except Exception:
            # Silently ignore errors when widget is destroyed (page switched)
            pass
    
    def clear(self):
        """Clear the display"""
        self.parent.after_idle(self._do_clear)
    
    def _do_clear(self):
        """Actually clear - runs in main thread"""
        self.canvas.delete("all")
        self.info_label.config(text="Ready to translate")
        self.progress_label.config(text="")
        self.photo_refs.clear()
    
    def show_message(self, message):
        """Show a text message"""
        self.parent.after_idle(self._do_show_message, message)
    
    def _do_show_message(self, message):
        """Actually show message - runs in main thread"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=message,
            font=("Segoe UI", 16),
            fill='#64748b',
            width=self.width - 40,
            anchor='center'
        )
        self.info_label.config(text="")
        self.progress_label.config(text="")


class AnimationController:
    """Controller for managing animations in separate thread"""
    
    def __init__(self, animator, display_widget):
        self.animator = animator
        self.display = display_widget
        self.current_thread = None
    
    def start_animation(self, text, speed=None):
        """Start animation in separate thread"""
        self.stop_animation()
        
        text = self.animator.preprocess_text(text)
        
        if not text:
            self.display.show_message("No text to animate")
            return
        
        self.current_thread = Thread(
            target=self.animator.animate_text,
            args=(text, self.display.display_image, speed),
            daemon=True
        )
        self.current_thread.start()
    
    def stop_animation(self):
        """Stop current animation"""
        self.animator.stop_animation()
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=1.0)
    
    def is_running(self):
        """Check if animation is currently running"""
        return self.animator.is_animating
    
    def set_speed(self, speed):
        """Set animation speed"""
        self.animator.set_animation_speed(speed)