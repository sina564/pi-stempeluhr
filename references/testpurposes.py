import time
t = time.localtime()

current_time = time.strftime("%H:%M:%S", t) 
stempelstatus="Eingestempelt"

def lcdanzeige():
    scroll_msg = f"{stempelstatus} um {current_time}"
    print(scroll_msg)

lcdanzeige()