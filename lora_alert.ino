#include <LoRa.h>
#include <SPI.h>

// LoRa pin tanımlamaları
#define SS_PIN 10
#define RST_PIN 9
#define DIO0_PIN 2
#define BUZZER_PIN 8
#define LED_PIN 7

// Durum değişkenleri
bool alarmActive = false;
unsigned long lastAlarmTime = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Pin modlarını ayarla
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // LoRa başlatma
  LoRa.setPins(SS_PIN, RST_PIN, DIO0_PIN);
  
  // LoRa frekans ve güç ayarları
  if (!LoRa.begin(915E6)) {
    Serial.println("LoRa başlatılamadı!");
    while (1) {
      digitalWrite(LED_PIN, HIGH);
      delay(300);
      digitalWrite(LED_PIN, LOW);
      delay(300);
    }
  }

  // LoRa ayarlarını optimize et
  LoRa.setSpreadingFactor(12);    // Daha uzun menzil için
  LoRa.setSignalBandwidth(125E3); // Bant genişliği
  LoRa.setCodingRate4(8);         // Hata düzeltme
  LoRa.setTxPower(20);            // Maksimum güç (20dBm)
  
  Serial.println("LoRa Sistemi Hazır!");
}

void loop() {
  // Raspberry Pi'den gelen verileri dinle
  if (Serial.available()) {
    String message = Serial.readStringUntil('\n');
    sendLoRaMessage(message);
    handleAlarm(true);
  }

  // LoRa mesajlarını dinle (diğer nodlardan gelen)
  receiveLoRaMessage();
  
  // Alarm durumunu kontrol et
  updateAlarm();
}

void sendLoRaMessage(String message) {
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();
  
  // Gönderim onayı
  Serial.println("Mesaj gönderildi: " + message);
}

void receiveLoRaMessage() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }
    Serial.println("Alınan: " + incoming);
  }
}

void handleAlarm(bool activate) {
  alarmActive = activate;
  lastAlarmTime = millis();
}

void updateAlarm() {
  if (alarmActive) {
    // Alarm sesi ve ışık paterni
    if ((millis() - lastAlarmTime) < 10000) { // 10 saniyelik alarm
      digitalWrite(LED_PIN, HIGH);
      tone(BUZZER_PIN, 1000, 500);
      delay(500);
      digitalWrite(LED_PIN, LOW);
      noTone(BUZZER_PIN);
      delay(500);
    } else {
      alarmActive = false;
      digitalWrite(LED_PIN, LOW);
      noTone(BUZZER_PIN);
    }
  }
}
