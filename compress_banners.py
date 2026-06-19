import os
import glob
from PIL import Image

def compress_banners():
    banners_dir = 'banners'
    # Compress pngs to jpgs
    for file in glob.glob(os.path.join(banners_dir, '*.png')):
        img = Image.open(file).convert('RGB')
        # Create new filename with .jpg extension
        new_filename = file.rsplit('.', 1)[0] + '.jpg'
        # Save as optimized jpeg
        img.save(new_filename, 'JPEG', quality=75, optimize=True)
        print(f"Compressed {file} -> {new_filename}")
        
    # Update index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace references
    html = html.replace('/banners/image1.png', '/banners/image1.jpg')
    html = html.replace('/banners/imagem2.png', '/banners/imagem2.jpg')
    html = html.replace('/banners/imagem3.png', '/banners/imagem3.jpg')
    html = html.replace('/banners/imagem4.png', '/banners/imagem4.jpg')
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("index.html updated to use compressed banners.")

if __name__ == '__main__':
    compress_banners()
