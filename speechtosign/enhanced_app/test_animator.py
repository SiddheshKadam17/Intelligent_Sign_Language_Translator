import sys
sys.path.append('src')
from src.core.sign_animator import SignAnimator

# Initialize animator
animator = SignAnimator("assets/sign_images")

# Check what loaded
print(f"Loaded {len(animator.image_cache)} images")
print("Available characters:", animator.get_available_characters())

# Test getting an image
test_char = 'A'
img = animator.get_sign_image(test_char)
print(f"Got image for '{test_char}': {img.size}")

# Save test image to verify
img.save("test_output.png")
print("Saved test image as test_output.png")