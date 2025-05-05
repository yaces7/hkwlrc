import cv2
import numpy as np
from tensorflow.keras.models import load_model
import time

def test_camera():
    try:
        # Model yukleme
        model = load_model('drowning_model.h5')
        print("Model basariyla yuklendi!")
    except:
        print("Model yuklenemedi! Once train_model.py calistirilmali.")
        return

    # Kamera baslat
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera acilamadi!")
        return
    
    print("\nKontroller:")
    print("C: Kamera degistir")
    print("Q: Cikis")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera goruntusu alinamiyor!")
            continue
            
        # Goruntuyu modele uygun hale getir
        processed = cv2.resize(frame, (224, 224))
        processed = processed / 255.0
        processed = np.expand_dims(processed, axis=0)
        
        # Tahmin yap
        prediction = model.predict(processed, verbose=0)
        class_idx = np.argmax(prediction[0])
        confidence = prediction[0][class_idx]
        
        # Sonucu ekrana yaz
        status = "Normal Yuzme" if class_idx == 0 else "BOGULMA!"
        color = (0, 255, 0) if class_idx == 0 else (0, 0, 255)
        
        # Bogulma tespiti ve kare cizimi
        if class_idx == 1 and confidence > 0.50:  # Hassasiyeti artirdik
            # Tum ekrani kirmizi cerceve icine al
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 3)
            
            # Buyuk uyari yazisi
            cv2.putText(frame, "BOGULMA TESPIT EDILDI!", (int(w/4), int(h/2)),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        
        # Durum bilgisini goster
        cv2.putText(frame, f"{status}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        cv2.putText(frame, f"Guven: {confidence:.2f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        # Goruntuyu goster
        cv2.imshow('Bogulma Tespit Sistemi', frame)
        
        # Tus kontrolu
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            cap.release()
            cap = cv2.VideoCapture(1 if cap.get(cv2.CAP_PROP_POS_FRAMES) == 0 else 0)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera() 