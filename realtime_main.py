from drowning_detection import VideoProcessor
from serial_communication import LoRaCommunicator
import time

def main():
    video_processor = VideoProcessor()
    lora_comm = LoRaCommunicator()
    
    try:
        while True:
            # Video işleme ve tespit
            status = video_processor.process_video()
            
            # Tehlike durumu tespit edilirse
            if status:
                # LoRa üzerinden uyarı gönder
                lora_comm.send_alert(status)
                print(f"Tehlike tespit edildi: {status}")
                time.sleep(5)  # Sürekli uyarı göndermemek için bekle
                
    except KeyboardInterrupt:
        print("Program sonlandırılıyor...")
    finally:
        lora_comm.close()

if __name__ == "__main__":
    main()
