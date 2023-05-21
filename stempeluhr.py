#!/usr/bin/python3
# -*- coding: utf-8 -*-

#importieren der benoetigten Bibliotheken
import RPi.GPIO as GPIO
import time
import datetime
import MFRC522
import signal
import board
import busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd

t = time.localtime()

eingestempelte_chips = {} #uids der eingestempelten chips sammeln
start_time = None

continue_reading = True #rfid anschmeissen
MIFAREReader = MFRC522.MFRC522() 

# Definiere LCD Zeilen und Spaltenanzahl.
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA) # Initialisierung I2C Bus fuer lcd
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows, 0x21)

def buzz(): #0.5 sek buzzer
    buzzer_pin = 12                         #buzzer_pin wird definiert
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buzzer_pin, GPIO.OUT)
    GPIO.output(buzzer_pin, GPIO.HIGH)      #Gebe Geraeusch aus fuer 0.5 sek
    time.sleep(0.5)                    
    GPIO.output(buzzer_pin, GPIO.LOW)       #Stoppe Geraeuschausgabe
    GPIO.cleanup()

def gib_uid(): #chip uid return
    (status, uid) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        return uid
    else:
        return None

def arbeitsstart(chip_uid):
    global start_time, stempelstatus, current_time
    buzz() 
    current_time = time.strftime("%H:%M", t)
    start_time = time.time() #zur berechnung der arbeitszeit am ende
    eingestempelte_chips[chip_uid] = (time.time(), True)  #startzeit + true für den Chip im dic speichern
    print(f"Chip {chip_uid} eingestempelt um: {current_time} Einen erfolgreichen Arbeitstag!")
    stempelstatus="Eingestempelt"
    lcdanzeige()

def feierabend(chip_uid):
    global stempelstatus,current_time
    buzz()  
    current_time = time.strftime("%H:%M", t) 
    end_time = time.time()  # für Arbeitszeitberechnung
    start_time = eingestempelte_chips.pop(chip_uid)[0]  # Startzeit für den Chip abrufen und Eintraege entfernen
    print(f"Chip {chip_uid} ausgestempelt um: {current_time}. Einen schönen Feierabend!")
    stempelstatus ="Ausgestempelt"
    arbeitszeitberechnen(chip_uid, end_time)
    lcdanzeige()

def arbeitszeitberechnen(chip_uid, end_time):
    global hours, minutes
    if chip_uid in eingestempelte_chips:
        start_time = eingestempelte_chips[chip_uid][0]  # Startzeit des Chips abrufen
        arbeitszeit = end_time - start_time  # Ergebnis in Sekunden
        # Umrechnen in Stunden und Minuten
        hours = arbeitszeit // 3600
        minutes = (arbeitszeit % 3600) // 60
        print(f"Arbeitszeit für Chip {chip_uid}: {hours} Stunden und {minutes} Minuten")
    else:
        print(f"Chip {chip_uid} ist nicht eingestempelt.")

def end_read(signal, frame): # Funktion zum Abbrechen mit CTRL+C
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
signal.signal(signal.SIGINT, end_read)
              
def lcdanzeige(): # Funktion für Ausgabe von Status und Zeit auf LCD
    lcd.backlight = True
    if stempelstatus=="Ausgestempelt":
        scroll_msg = f"{stempelstatus} um {end_time}, Arbeitszeit: {hours} Stunden und {minutes} Minuten"
    elif stempelstatus=="Eingestempelt":
        scroll_msg = f"{stempelstatus} um {start_time}"
    else:
        print("Fehler bei der Statusanzeige: kein Stempel-Status vorhanden.")
        scroll_msg = "Fehler"
    lcd.message = scroll_msg
    for i in range(len(scroll_msg)):
        time.sleep(0.5)
        lcd.move_right()
    for i in range(len(scroll_msg)):
        time.sleep(0.5)
        lcd.move_left()

print("Wilkommen bei der Stempeluhr der FIT GmbH.")
print("Druecke Ctrl-C zum abbrechen.")

# dauerhaftes suchen nach Karten
while continue_reading:
    
    # Sucht Karte
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Wenn Karte gefunden
    if status == MIFAREReader.MI_OK:
        chip_uid = gib_uid()
        if chip_uid: #wenn uid einen wert hat
            if chip_uid in eingestempelte_chips: 
                feierabend(chip_uid) # AUSSTEMPELN
            else: 
                arbeitsstart(chip_uid) # EINSTEMPELN
        else:
            print("Fehler beim Lesen der Chip-UID.")