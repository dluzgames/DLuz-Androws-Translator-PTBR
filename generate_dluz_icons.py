from PIL import Image
import os
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

user_logo_path = r'C:\Users\dluzgg\.gemini\antigravity\brain\25c3e37f-f14d-4c68-b5c0-79c6bc5019c5\.user_uploaded\media_1787244840531.png'
scratch_dir = r'C:\Users\dluzgg\.gemini\antigravity\brain\25c3e37f-f14d-4c68-b5c0-79c6bc5019c5\scratch'

img = Image.open(user_logo_path).convert('RGBA')
print(f"Original Logo Size: {img.size}")

# 1. Generate multi-resolution ICO (256, 128, 64, 48, 32, 16)
ico_path = os.path.join(scratch_dir, 'dluz_logo.ico')
ico_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
img.save(ico_path, format='ICO', sizes=ico_sizes)
print(f"Saved ICO: {ico_path} ({os.path.getsize(ico_path)} bytes)")

# 2. Generate standard PNGs
png_256 = os.path.join(scratch_dir, 'dluz_logo_256.png')
img.resize((256, 256), Image.Resampling.LANCZOS).save(png_256)

png_64 = os.path.join(scratch_dir, 'dluz_logo_64.png')
img.resize((64, 64), Image.Resampling.LANCZOS).save(png_64)

png_32 = os.path.join(scratch_dir, 'dluz_logo_32.png')
img.resize((32, 32), Image.Resampling.LANCZOS).save(png_32)

print("DLuz icon assets generated successfully!")
