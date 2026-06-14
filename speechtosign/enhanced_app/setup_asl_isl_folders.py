"""
Setup ASL and ISL separate folders
===================================
This script:
1. Creates assets/asl_sign_images/ folder with your ASL backup
2. Creates assets/isl_sign_images/ folder with your new ISL images
3. Both sets remain available to switch between
"""

import os
import shutil

# Paths
BASE = r"D:\Voice-to-Sign-language-Translator\speechtosign\enhanced_app\assets"
ASL_BACKUP = os.path.join(BASE, "sign_images_ASL_BACKUP")
ISL_CURRENT = os.path.join(BASE, "sign_images")
ASL_FOLDER = os.path.join(BASE, "asl_sign_images")
ISL_FOLDER = os.path.join(BASE, "isl_sign_images")

print("="*50)
print("  Setting up ASL + ISL folders")
print("="*50)

# Step 1: Copy ASL backup to asl_sign_images
if os.path.exists(ASL_BACKUP):
    if not os.path.exists(ASL_FOLDER):
        print(f"\nCreating ASL folder from backup...")
        shutil.copytree(ASL_BACKUP, ASL_FOLDER)
        print(f"✅ ASL folder ready: assets/asl_sign_images/")
    else:
        print(f"✅ ASL folder already exists")
else:
    print(f"❌ ASL backup not found at: {ASL_BACKUP}")
    print("   Make sure you ran setup_isl_dataset.py first")

# Step 2: Copy current ISL images to isl_sign_images
if os.path.exists(ISL_CURRENT):
    if not os.path.exists(ISL_FOLDER):
        print(f"\nCreating ISL folder...")
        shutil.copytree(ISL_CURRENT, ISL_FOLDER)
        print(f"✅ ISL folder ready: assets/isl_sign_images/")
    else:
        print(f"✅ ISL folder already exists")
else:
    print(f"❌ Current sign_images not found")

print("\n" + "="*50)
print("✅ DONE! Both datasets ready:")
print(f"   ASL: assets/asl_sign_images/ (26 images)")
print(f"   ISL: assets/isl_sign_images/ (26 images)")
print("\nNow run your app:")
print("   python professional_app_COMPLETE.py")
print("="*50)