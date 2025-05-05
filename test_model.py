import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import os
import numpy as np

class ModelTester:
    def __init__(self):
        self.img_height = 224
        self.img_width = 224
        self.batch_size = 4  # Küçük veri seti için küçük batch size
        self.epochs = 5
        self.dataset_dir = "dataset/drowning"

    def prepare_data(self):
        # Veri artırma ve normalizasyon
        datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2  # %20'si test için
        )

        # Eğitim verisi
        self.train_generator = datagen.flow_from_directory(
            self.dataset_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='training'
        )

        # Test verisi
        self.validation_generator = datagen.flow_from_directory(
            self.dataset_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='validation'
        )

        print("\nSınıf dağılımı:")
        for class_name, class_index in self.train_generator.class_indices.items():
            class_count = len(os.listdir(os.path.join(self.dataset_dir, class_name)))
            print(f"{class_name}: {class_count} görüntü")

    def create_model(self):
        # MobileNetV2 temel model
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(self.img_height, self.img_width, 3)
        )
        
        # Transfer learning için base model'i dondur
        base_model.trainable = False

        # Model yapısını oluştur
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation='relu')(x)
        predictions = Dense(len(self.train_generator.class_indices), activation='softmax')(x)
        
        self.model = Model(inputs=base_model.input, outputs=predictions)
        
        # Model derleme
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

    def train_and_evaluate(self):
        # Model eğitimi
        print("\nModel eğitiliyor...")
        history = self.model.fit(
            self.train_generator,
            validation_data=self.validation_generator,
            epochs=self.epochs
        )

        # Model değerlendirme
        print("\nModel değerlendiriliyor...")
        evaluation = self.model.evaluate(self.validation_generator)
        print(f"\nTest doğruluğu: {evaluation[1]:.2f}")

        # Modeli kaydet
        self.model.save('drowning_model.h5')
        print("\nModel kaydedildi: drowning_model.h5")

    def test_single_image(self):
        """Tek bir görüntü üzerinde test yapar"""
        from tensorflow.keras.preprocessing import image
        
        print("\nTest görüntüsü seçin:")
        for i, class_name in enumerate(self.train_generator.class_indices.keys()):
            print(f"{i+1}. {class_name}")
        
        class_choice = int(input("Sınıf seçin (numara): ")) - 1
        class_name = list(self.train_generator.class_indices.keys())[class_choice]
        
        # Seçilen sınıftan rastgele bir görüntü al
        class_path = os.path.join(self.dataset_dir, class_name)
        image_name = np.random.choice(os.listdir(class_path))
        img_path = os.path.join(class_path, image_name)
        
        # Görüntüyü yükle ve işle
        img = image.load_img(img_path, target_size=(self.img_height, self.img_width))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.
        
        # Tahmin yap
        predictions = self.model.predict(img_array)
        predicted_class = list(self.train_generator.class_indices.keys())[np.argmax(predictions[0])]
        confidence = np.max(predictions[0])
        
        print(f"\nTest sonucu:")
        print(f"Gerçek sınıf: {class_name}")
        print(f"Tahmin edilen sınıf: {predicted_class}")
        print(f"Güven skoru: {confidence:.2f}")

def main():
    tester = ModelTester()
    
    print("Veri hazırlanıyor...")
    tester.prepare_data()
    
    print("\nModel oluşturuluyor...")
    tester.create_model()
    
    tester.train_and_evaluate()
    
    # Tek görüntü testi
    while True:
        test_again = input("\nBir görüntü test etmek ister misiniz? (e/h): ")
        if test_again.lower() != 'e':
            break
        tester.test_single_image()

if __name__ == "__main__":
    main() 