import threading
from realtime_detection import DrownDetectionSystem
import time

def run_camera(camera_id, lora_port):
    detector = DrownDetectionSystem(camera_id=camera_id, lora_port=lora_port)
    detector.run()

def main():
    # Kamera ve LoRa port ayarları
    cameras = [
        {"id": 0, "port": "COM3"},  # Ana havuz kamerası
        {"id": 1, "port": "COM4"},  # Çocuk havuzu kamerası
        {"id": 2, "port": "COM5"},  # Derin havuz kamerası
        {"id": 3, "port": "COM6"}   # Yüzme havuzu kamerası
    ]
    
    # Her kamera için ayrı thread başlat
    threads = []
    for camera in cameras:
        thread = threading.Thread(
            target=run_camera,
            args=(camera["id"], camera["port"]),
            daemon=True
        )
        threads.append(thread)
        thread.start()
        print(f"Kamera {camera['id']} başlatıldı - Port: {camera['port']}")
        time.sleep(2)  # Kameralar arası başlatma gecikmesi
    
    try:
        # Ana thread'i canlı tut
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram sonlandırılıyor...")
        # Thread'lerin kapanmasını bekle
        for thread in threads:
            thread.join(timeout=1)

if __name__ == "__main__":
    main()
