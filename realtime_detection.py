import cv2
import numpy as np
from tensorflow.keras.models import load_model
import serial
import time

class DrownDetectionSystem:
    def __init__(self, camera_id=0, lora_port='COM3'):  # Windows için COM portu
        self.camera_id = camera_id
        self.model = load_model('drowning_model.h5')
        self.cap = cv2.VideoCapture(camera_id)
        
        # LoRa iletişimi için seri port
        try:
            self.serial_port = serial.Serial(
                port=lora_port,
                baudrate=9600,
                timeout=1
            )
            print(f"LoRa bağlantısı başarılı: {lora_port}")
        except Exception as e:
            print(f"LoRa bağlantı hatası: {e}")
            self.serial_port = None

        # Tespit parametreleri
        self.detection_threshold = 0.65  # Daha hassas tespit için eşik değeri düşürüldü
        self.frame_buffer = []
        self.buffer_size = 5   # Buffer boyutu düşürüldü - daha hızlı tepki için
        self.alert_count = 0
        self.alert_threshold = 3  # Daha hızlı alarm için düşürüldü
        self.last_alert_time = 0
        self.alert_cooldown = 10  # 10 saniye bekleme süresi

    def preprocess_frame(self, frame):
        processed = cv2.resize(frame, (224, 224))
        processed = processed / 255.0
        processed = np.expand_dims(processed, axis=0)
        return processed

    def detect_drowning(self, frame):
        processed_frame = self.preprocess_frame(frame)
        prediction = self.model.predict(processed_frame, verbose=0)
        
        is_drowning = prediction[0][1] > self.detection_threshold
        confidence = float(prediction[0][1])
        
        return is_drowning, confidence

    def send_alert(self):
        current_time = time.time()
        if current_time - self.last_alert_time < self.alert_cooldown:
            return

        if self.serial_port:
            # Format: ALERT,CAMERA_ID,STATUS,CONFIDENCE
            alert_message = f"ALERT,{self.camera_id},DROWNING,HIGH\n"
            try:
                self.serial_port.write(alert_message.encode())
                print(f"ALARM: Kamera {self.camera_id} - Boğulma Tespit Edildi!")
                self.last_alert_time = current_time
            except Exception as e:
                print(f"LoRa gönderme hatası: {e}")

    def draw_detection(self, frame, is_drowning, confidence):
        height, width = frame.shape[:2]
        
        if is_drowning:
            # Kırmızı çerçeve
            cv2.rectangle(frame, (10, 10), (width-10, height-10), (0, 0, 255), 3)
            
            # Uyarı metni
            text = f"BOĞULMA TESPİT EDİLDİ! (%{confidence*100:.1f})"
            cv2.putText(frame, text, (20, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            # Kamera ID'si
            camera_text = f"Kamera ID: {self.camera_id}"
            cv2.putText(frame, camera_text, (20, height-30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            # Normal durum metni
            text = f"Normal Yüzme (%{confidence*100:.1f})"
            cv2.putText(frame, text, (20, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Kamera ID'si
            camera_text = f"Kamera ID: {self.camera_id}"
            cv2.putText(frame, camera_text, (20, height-30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def run(self):
        print(f"Kamera {self.camera_id} başlatılıyor...")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Kamera görüntüsü alınamıyor!")
                break

            # Boğulma tespiti
            is_drowning, confidence = self.detect_drowning(frame)
            
            # Frame buffer güncelleme
            self.frame_buffer.append(is_drowning)
            if len(self.frame_buffer) > self.buffer_size:
                self.frame_buffer.pop(0)
            
            # Alarm kontrolü
            drowning_frames = sum(self.frame_buffer)
            if drowning_frames >= self.alert_threshold:
                self.send_alert()
            
            # Görsel çıktı
            window_name = f'Havuz Kamera {self.camera_id}'
            cv2.imshow(window_name, frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        if self.serial_port:
            self.serial_port.close()

def main():
    # Test için kamera ID'si ve port
    detector = DrownDetectionSystem(camera_id=0, lora_port='COM3')
    detector.run()

if __name__ == "__main__":
    main() 