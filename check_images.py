import os
from PIL import Image

def check_images():
    base_dir = 'dataset'
    categories = ['normal_swimming', 'drowning']
    
    for category in categories:
        print(f"\n{category} klasoru kontrol ediliyor...")
        path = os.path.join(base_dir, category)
        
        if not os.path.exists(path):
            print(f"{path} klasoru bulunamadi!")
            continue
            
        files = os.listdir(path)
        print(f"Toplam dosya sayisi: {len(files)}")
        
        for file in files:
            file_path = os.path.join(path, file)
            try:
                # Resmi acmayi dene
                with Image.open(file_path) as img:
                    # Resim boyutlarini kontrol et
                    width, height = img.size
                    print(f"{file}: {width}x{height} - OK")
            except Exception as e:
                print(f"{file}: HATA - {str(e)}")

if __name__ == "__main__":
    check_images() 