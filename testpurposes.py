import time
t = time.localtime()

name = "Alice"
age = 25

current_time = time.strftime("%H:%M:%S", t) 
stempelstatus="Eingestempelt"

def lcdanzeige():
    scroll_msg = f"{stempelstatus} um {current_time}"
    print(scroll_msg)

lcdanzeige()

f_string = f"Mein Name ist {name} und ich bin {age} Jahre alt."
print(f_string)