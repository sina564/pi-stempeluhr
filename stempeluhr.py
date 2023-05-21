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

#0.5 sek buzzer
def buzz():
    buzzer_pin = 12                         #buzzer_pin wird definiert
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buzzer_pin, GPIO.OUT)
    GPIO.output(buzzer_pin, GPIO.HIGH)      #Gebe Geraeusch aus fuer 0.5 sek
    time.sleep(0.5)                    
    GPIO.output(buzzer_pin, GPIO.LOW)       #Stoppe Geraeuschausgabe
    GPIO.cleanup()

#chip uid return
def gib_uid():
    (status, uid) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        return uid
    else:
        return None

def arbeitsstart():
    global start_time, stempelstatus, current_time
    buzz() 
    current_time = time.strftime("%H:%M", t)
    start_time = time.time() #zur berechnung der arbeitszeit am ende
    print("Karte gelesen, eingestempelt um:", current_time)
    print("Einen erfolgreichen Arbeitstag!")
    stempelstatus="Eingestempelt"
    lcdanzeige()

def feierabend():
    global stempelstatus, end_time, current_time
    buzz()  
    current_time = time.strftime("%H:%M", t) 
    end_time = time.time() #fuer arbeitszeitberechnung
    print("Karte gelesen, ausgestempelt um:", current_time)
    print("Einen schönen Feierabend!")
    stempelstatus ="Ausgestempelt"
    arbeitszeitberechnen()
    lcdanzeige()

def arbeitszeitberechnen():
    global hours, minutes
    #falls vorhanden: arbeitszeit anzeigen 
    if start_time is not None:
        arbeitszeit = end_time - start_time #ergebnis in sekunden
        #umrechnen in std und min
        hours = arbeitszeit // 3600
        minutes = (arbeitszeit % 3600) // 60
        print(f"Arbeitszeit: {hours} Stunden und {minutes} Minuten")
    else:
        print("Fehler bei Zeitberechnung: kein Startwert vorhanden")

# Funktion zum abbrechen mit ctrl+c
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
signal.signal(signal.SIGINT, end_read)
              
def lcdanzeige():
    lcd.backlight = True
    if stempelstatus=="Ausgestempelt":
        scroll_msg = f"{stempelstatus} um {current_time}, Arbeitszeit: {hours} Stunden und {minutes} Minuten "
    elif stempelstatus=="Eingestempelt":
        scroll_msg = f"{stempelstatus} um {current_time}"
    else:
        print("Fehler bei der Statusanzeige: kein Status vorhanden")
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
        if chip_uid:
            if chip_uid in eingestempelte_chips: # AUSSTEMPELN
                eingestempelte_chips[chip_uid] = not eingestempelte_chips[chip_uid] 
                feierabend()
            else: # EINSTEMPELN
                eingestempelte_chips[chip_uid] = True
                arbeitsstart()
        else:
            # Fehler beim Lesen der Chip-UID
            print("Fehler beim Lesen der Chip-UID.")

#debug
print(eingestempelte_chips)