import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

def check_dataset():
    if not os.path.exists('dataset'):
        raise FileNotFoundError("Dataset klasoru bulunamadi!")
        
    categories = ['normal_swimming', 'drowning']
    total_images = 0
    
    for category in categories:
        path = os.path.join('dataset', category)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{category} klasoru bulunamadi!")
        files = [f for f in os.listdir(path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        num_images = len(files)
        if num_images == 0:
            raise ValueError(f"{category} klasorunde hic goruntu yok!")
        print(f"{category}: {num_images} goruntu")
        total_images += num_images
    
    print(f"\nToplam: {total_images} goruntu")
    return total_images > 0

def create_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D(2, 2),
        
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(2, activation='softmax')
    ])
    
    return model

def train_model():
    try:
        print("Veri seti kontrol ediliyor...")
        check_dataset()
        
        print("\nVeri artirma ayarlari yapiliyor...")
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            validation_split=0.2
        )
        
        batch_size = 16
        img_size = 224
        
        print("Veri yukleniyor...")
        train_generator = train_datagen.flow_from_directory(
            'dataset',
            target_size=(img_size, img_size),
            batch_size=batch_size,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        validation_generator = train_datagen.flow_from_directory(
            'dataset',
            target_size=(img_size, img_size),
            batch_size=batch_size,
            class_mode='categorical',
            subset='validation',
            shuffle=True
        )
        
        print("\nModel olusturuluyor...")
        model = create_model()
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("\nModel egitimi basliyor...")
        history = model.fit(
            train_generator,
            epochs=20,
            validation_data=validation_generator,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ]
        )
        
        print("\nModel kaydediliyor...")
        model.save('drowning_model.h5')
        
        print("\nEgitim grafikleri ciziliyor...")
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Egitim Dogrulugu')
        plt.plot(history.history['val_accuracy'], label='Dogrulama Dogrulugu')
        plt.title('Model Dogrulugu')
        plt.xlabel('Epoch')
        plt.ylabel('Dogruluk')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Egitim Kaybi')
        plt.plot(history.history['val_loss'], label='Dogrulama Kaybi')
        plt.title('Model Kaybi')
        plt.xlabel('Epoch')
        plt.ylabel('Kayip')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('training_history.png')
        plt.show()
        
        print("\nEgitim tamamlandi!")
        
    except Exception as e:
        print(f"\nHata olustu: {str(e)}")
        return

if __name__ == "__main__":
    print("Program baslatiliyor...")
    train_model() 