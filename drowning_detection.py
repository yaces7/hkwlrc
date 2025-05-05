import cv2
import numpy as np
from tensorflow.keras.models import load_model
import time

class DrowningDetector:
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.classes = ['normal_swimming', 'drowning']
        
    def preprocess_frame(self, frame):
        # Görüntüyü modele uygun boyuta getir
        processed = cv2.resize(frame, (224, 224))
        processed = processed / 255.0
        return np.expand_dims(processed, axis=0)
    
    def detect(self, frame):
        processed_frame = self.preprocess_frame(frame)
        prediction = self.model.predict(processed_frame)
        class_idx = np.argmax(prediction[0])
        confidence = prediction[0][class_idx]
        return self.classes[class_idx], confidence

class VideoProcessor:
    def __init__(self, camera_source=0):
        self.cap = cv2.VideoCapture(camera_source)
        self.detector = DrowningDetector('drowning_model.h5')
        
    def process_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Boğulma tespiti yap
            status, confidence = self.detector.detect(frame)
            
            # Sadece boğulma durumunu kontrol et
            if status == 'drowning' and confidence > 0.75:
                return status
                
            time.sleep(0.1)
            
    def __del__(self):
        self.cap.release()
