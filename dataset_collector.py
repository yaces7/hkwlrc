import cv2
import os
from datetime import datetime
import time

class DatasetCollector:
    def __init__(self):
        self.categories = ['normal_swimming', 'drowning']
        self.base_dir = 'dataset'
        self.setup_directories()
        
    def setup_directories(self):
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
        for category in self.categories:
            category_path = os.path.join(self.base_dir, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
    
    def collect_images(self, category, source=0):
        cap = cv2.VideoCapture(source)
        save_path = os.path.join(self.base_dir, category)
        
        if not cap.isOpened():
            print("Kamera veya video dosyası açılamadı!")
            return 0
        
        # Video FPS'ini 1'e düşürüyoruz (her saniye 1 kare)
        cap.set(cv2.CAP_PROP_FPS, 1)
        
        frame_count = 0
        frame_delay = 1.0  # Her kare için 1 saniye bekleme
        
        while True:
            start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                break
            
            display = frame.copy()
            cv2.putText(display, f"Kategori: {category}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display, "Space: Kaydet, Q: Çıkış", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Veri Toplama', display)
            
            # Her kare için 1 saniye bekleme
            key = cv2.waitKey(1000) & 0xFF  # 1000ms = 1 saniye
            
            if key == ord('q'):
                break
            elif key == ord(' '):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{category}_{timestamp}.jpg"
                filepath = os.path.join(save_path, filename)
                
                cv2.imwrite(filepath, frame)
                frame_count += 1
                print(f"Kaydedildi: {filename}")
                
                time.sleep(1.0)  # Kayıt sonrası bekleme
            
            # Her kare için ek bekleme
            time.sleep(1.0)  # Tam 1 saniye bekleme
        
        cap.release()
        cv2.destroyAllWindows()
        return frame_count

if __name__ == "__main__":
    collector = DatasetCollector()
    
    try:
        while True:
            print("\nVeri Seti Toplayıcı")
            print("------------------")
            print("Kategoriler:")
            for i, category in enumerate(collector.categories, 1):
                print(f"{i}. {category}")
            print("0. Çıkış")
            
            choice = input("\nKategori seçin (0-2): ")
            if choice == "0":
                break
                
            try:
                category_idx = int(choice) - 1
                if 0 <= category_idx < len(collector.categories):
                    source = input("Video kaynağı (Enter=webcam, dosya yolu): ")
                    source = 0 if source == "" else source
                    
                    count = collector.collect_images(
                        collector.categories[category_idx], 
                        source
                    )
                    print(f"\n{count} görüntü kaydedildi.")
                else:
                    print("Geçersiz seçim!")
            except ValueError:
                print("Geçersiz giriş!")
    except KeyboardInterrupt:
        print("\nProgram sonlandırılıyor...")
    finally:
        cv2.destroyAllWindows() 