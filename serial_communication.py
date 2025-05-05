import serial
import time

class LoRaCommunicator:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.serial = serial.Serial(port, baudrate)
        time.sleep(2)  # Arduino'nun başlaması için bekle
        
    def send_alert(self, alert_type):
        message = f"ALERT:{alert_type}"
        self.serial.write(message.encode())
        
    def close(self):
        self.serial.close()
