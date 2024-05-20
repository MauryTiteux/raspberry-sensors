from libraries.i2c_lcd import I2cLcd
from devices.dht11 import DHT11
from devices.tsl2591 import TSL2591 
from devices.lcd_1602 import LCD
from devices.button import get_button_state
import devices.ky_029 as KY029
import devices.ky_009 as KY009
import time
from datetime import datetime
from cases import getSolarBlindStatus
import cases

def get_values():
    try:
        return '{0}C {1}% {2} lx'.format(DHT11.temperature, DHT11.humidity, int(TSL2591.lux))
    except:
        return 'sensors_error'

WATCHER_INTERVAL = 10
LUX_CACHE_INTERVAL = 600
CHAR_PER_LINE = 16

ten_minutes_ago_lux = int(TSL2591.lux)
ten_minutes_ago_lux_seconds = LUX_CACHE_INTERVAL

seconds = WATCHER_INTERVAL
message = get_values()

try:
    while True:
        LCD.clear()
        KY029.set_green()

        if (get_button_state() == 0):
            message = get_values()
            
            if (message == 'sensors_error'):
                seconds = seconds
            else:
                seconds = WATCHER_INTERVAL

        if (seconds == 1):
            message = get_values()

            if (message == 'sensors_error'):
                seconds = 1
            else:
                seconds = WATCHER_INTERVAL
        else:        
            seconds = seconds - 1

        if (ten_minutes_ago_lux_seconds == 1):
            ten_minutes_ago_lux = int(TSL2591.lux)
            ten_minutes_ago_lux_seconds = LUX_CACHE_INTERVAL
        else:
            ten_minutes_ago_lux_seconds = ten_minutes_ago_lux_seconds - 1

        char_missing_first_line = CHAR_PER_LINE - len(message)

        if (char_missing_first_line != 0):
            message += ' ' * char_missing_first_line

        LCD.putstr(message)
        LCD.putstr(str(seconds) + 's - ' + datetime.strftime(datetime.now(), '%H:%M:%S'))

        try:
            status = getSolarBlindStatus(ten_minutes_ago_lux)

            if (status == 'open'):
                KY009.set_yellow()
            else:
                KY009.set_blue()
        except:
            KY029.set_red()

        time.sleep(1)
except:
    KY029.set_red()
