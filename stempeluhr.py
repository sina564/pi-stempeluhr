#!/usr/bin/python3
# -*- coding: utf-8 -*-

#importieren der benoetigten Bibliotheken
import RPi.GPIO as GPIO
import time
import MFRC522
import signal
t = time.localtime()

continue_reading = True #rfid anschmeissen

# Funktion zum 0.5 sek buzzern
def buzz():
    buzzer_pin = 12                         #buzzer_pin wird definiert
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buzzer_pin, GPIO.OUT)
    GPIO.output(buzzer_pin, GPIO.HIGH)      #Gebe Geraeusch aus fuer 0.5 sek
    time.sleep(0.5)                    
    GPIO.output(buzzer_pin, GPIO.LOW)       #Stoppe Geraeuschausgabe
    GPIO.cleanup()

# Funktion um cleanup Funktionen durchzuführen wenn das Script mit ctrl+c abgebrochen wird.
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read) #signt hook

MIFAREReader = MFRC522.MFRC522() # Erstelle ein Objekt aus der Klasse MFRC522

# Welcome message
print("Wilkommen bei der Stempeluhr.")
print("Druecke Ctrl-C zum abbrechen.")

# Diese Schleife Sucht dauerhaft nach Chips oder Karten. Wenn eine nah ist bezieht er die Uhrzeit und gibt sie aus.
while continue_reading:
    
    # Sucht Karte
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Wenn Karte gefunden
    if status == MIFAREReader.MI_OK:
        current_time = time.strftime("%H:%M:%S", t) #zieht sich die aktuelle zeit
        print("Karte gelesen, eingestempelt um:", current_time) #gibt uhrzeit des lesens des chips aus
        continue_reading = False
        GPIO.cleanup()
        print("Einen erfolgreichen Arbeitstag!")