#include <SPI.h>
#include <LoRa.h>
#include <LiquidCrystal_I2C.h>

// LCD ekran ayarları
LiquidCrystal_I2C lcd(0x27, 20, 4);  // 20x4 LCD ekran

// LoRa pin tanımlamaları
#define SS_PIN 10
#define RST_PIN 9
#define DIO0_PIN 2

// Alarm pin tanımlamaları
#define BUZZER_PIN 6
#define LED_PIN 7

void setup() {
  Serial.begin(9600);
  
  // Pin modlarını ayarla
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // LCD başlat
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print("Havuz Guvenlik");
  lcd.setCursor(0, 1);
  lcd.print("Sistemi Hazir");
  
  // LoRa başlat
  LoRa.setPins(SS_PIN, RST_PIN, DIO0_PIN);
  
  if (!LoRa.begin(433E6)) {  // 433MHz frekansı
    Serial.println("LoRa başlatılamadı!");
    lcd.clear();
    lcd.print("LoRa Hatasi!");
    while (1);
  }
  
  delay(2000);
  lcd.clear();
}

void activateAlarm(int camera_id) {
  // Alarm LED'ini yak
  digitalWrite(LED_PIN, HIGH);
  
  // Buzzer ile alarm çal
  for(int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, 1000);  // 1kHz
    delay(500);
    noTone(BUZZER_PIN);
    delay(200);
  }
  
  // LCD'ye uyarı mesajı
  lcd.clear();
  lcd.print("!!! DIKKAT !!!");
  lcd.setCursor(0, 1);
  lcd.print("Kamera-");
  lcd.print(camera_id);
  lcd.setCursor(0, 2);
  lcd.print("BOGULMA TEHLIKESI");
  lcd.setCursor(0, 3);
  lcd.print("HEMEN MUDAHALE ET!");
}

void deactivateAlarm() {
  digitalWrite(LED_PIN, LOW);
  noTone(BUZZER_PIN);
}

void processMessage(String message) {
  // Mesaj formatı: "ALERT,CAMERA_ID,STATUS,CONFIDENCE"
  int firstComma = message.indexOf(',');
  int secondComma = message.indexOf(',', firstComma + 1);
  int thirdComma = message.indexOf(',', secondComma + 1);
  
  if (firstComma == -1 || secondComma == -1) return;
  
  String command = message.substring(0, firstComma);
  String camera_id = message.substring(firstComma + 1, secondComma);
  String status = message.substring(secondComma + 1, thirdComma);
  
  if (command == "ALERT" && status == "DROWNING") {
    int camera_number = camera_id.toInt();
    activateAlarm(camera_number);
    
    // Serial monitöre bilgi yazdır
    Serial.print("Alarm: Kamera ");
    Serial.print(camera_number);
    Serial.println(" - Boğulma Tehlikesi!");
    
    delay(5000);  // 5 saniye alarm aktif
    deactivateAlarm();
    
    // LCD'yi normal duruma getir
    lcd.clear();
    lcd.print("Sistem Aktif");
    lcd.setCursor(0, 1);
    lcd.print("Izleniyor...");
  }
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String message = "";
    while (LoRa.available()) {
      message += (char)LoRa.read();
    }
    
    // RSSI değerini kontrol et
    Serial.print("RSSI: ");
    Serial.println(LoRa.packetRssi());
    
    // Mesajı işle
    processMessage(message);
  }
} 