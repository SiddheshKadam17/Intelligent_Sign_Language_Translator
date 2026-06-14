"""
ISL Dataset Setup Script - EXACT FIT FOR YOUR DATASET
======================================================
Your structure:
D:\Voice-to-Sign-language-Translator\speechtosign\Indian\
    A\  (70-80 images)
    B\  (70-80 images)
    ...
    Z\  (70-80 images)

This script will:
1. Go into each letter folder (A, B, C... Z)
2. Pick ONE good image from the middle
3. Resize it to 400x400
4. Save as a.jpg, b.jpg... to your app's sign_images folder
5. Backup your old ASL images first
"""

import os
import shutil
from PIL import Image

# =====================================================
# YOUR EXACT PATHS (no need to change these!)
# =====================================================
ISL_SOURCE = r"D:\Voice-to-Sign-language-Translator\speechtosign\Indian"
APP_SIGNS  = r"D:\Voice-to-Sign-language-Translator\speechtosign\enhanced_app\assets\sign_images"
ASL_BACKUP = r"D:\Voice-to-Sign-language-Translator\speechtosign\enhanced_app\assets\sign_images_ASL_BACKUP"
# =====================================================

def pick_middle_image(folder_path):
    """Pick one image from the middle of the folder (best quality usually)"""
    all_files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
    ])
    if not all_files:
        return None
    # Pick from middle (avoid first/last which can be blurry)
    middle_index = len(all_files) // 2
    return os.path.join(folder_path, all_files[middle_index])


def copy_and_resize(source_path, output_path):
    """Copy image, convert to RGB, resize to 400x400, save as JPG"""
    try:
        img = Image.open(source_path)
        img = img.convert('RGB')
        img = img.resize((400, 400), Image.Resampling.LANCZOS)
        img.save(output_path, 'JPEG', quality=95)
        return True
    except Exception as e:
        print(f"    Warning: {e}")
        try:
            shutil.copy2(source_path, output_path)
            return True
        except:
            return False


def main():
    print("=" * 55)
    print("   ISL DATASET SETUP - SignTalk Pro")
    print("=" * 55)

    # Check source folder
    if not os.path.exists(ISL_SOURCE):
        print(f"\nERROR: Source folder not found:\n   {ISL_SOURCE}")
        return
    print(f"\nFound ISL dataset at:\n   {ISL_SOURCE}")

    # Backup old ASL images
    if os.path.exists(APP_SIGNS) and not os.path.exists(ASL_BACKUP):
        print(f"\nBacking up your ASL images to:\n   {ASL_BACKUP}")
        shutil.copytree(APP_SIGNS, ASL_BACKUP)
        print("Backup done! (You can restore anytime)")
    elif os.path.exists(ASL_BACKUP):
        print(f"\nASL backup already exists - skipping backup")

    # Create output folder
    os.makedirs(APP_SIGNS, exist_ok=True)

    # Process each letter A-Z
    print(f"\nProcessing letters A-Z...")
    print("-" * 40)

    success = []
    failed  = []

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        letter_folder = os.path.join(ISL_SOURCE, letter)
        output_file   = os.path.join(APP_SIGNS, f"{letter.lower()}.jpg")

        if not os.path.exists(letter_folder):
            print(f"  MISSING  {letter} -> Folder not found!")
            failed.append(letter)
            continue

        images = [f for f in os.listdir(letter_folder)
                  if f.lower().endswith(('.jpg','.jpeg','.png','.bmp'))]

        if not images:
            print(f"  EMPTY    {letter} -> No images in folder!")
            failed.append(letter)
            continue

        source_img = pick_middle_image(letter_folder)

        if copy_and_resize(source_img, output_file):
            print(f"  OK  {letter} -> {letter.lower()}.jpg  (picked 1 from {len(images)} images)")
            success.append(letter)
        else:
            print(f"  FAIL     {letter} -> Could not copy!")
            failed.append(letter)

    # Summary
    print("\n" + "=" * 55)
    print(f"SUCCESS : {len(success)}/26  ->  {', '.join(success)}")
    if failed:
        print(f"FAILED  : {', '.join(failed)}")
    print("=" * 55)

    if len(success) == 26:
        print("\nALL 26 ISL SIGNS READY!")
        print("\nNow run your app:")
        print("  python professional_app_COMPLETE.py")
        print("\nYour app now uses ISL signs instead of ASL!")
        print(f"(Old ASL backup saved at: {ASL_BACKUP})")
    else:
        print(f"\nWARNING: {26-len(success)} letters missing.")
        print(f"Add them manually to: {APP_SIGNS}")


if __name__ == "__main__":
    main()