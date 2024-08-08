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
from tools.db import db

def get_values(temperature, humidity, lux):
    return '{0}C {1}% {2} lx'.format(temperature, humidity, lux)

WATCHER_INTERVAL = 10
LUX_CACHE_INTERVAL = 600
CHAR_PER_LINE = 16

humidity = DHT11.humidity
temperature = DHT11.temperature
lux = int(TSL2591.lux)

ten_minutes_ago_lux = lux
ten_minutes_ago_lux_seconds = LUX_CACHE_INTERVAL

seconds = WATCHER_INTERVAL
message = get_values(temperature, humidity, lux)

def print_on_lcd(message):
    char_missing_first_line = CHAR_PER_LINE - len(message)

    if (char_missing_first_line != 0):
        message += ' ' * char_missing_first_line

    LCD.putstr(message)
    LCD.putstr(str(seconds) + 's - ' + datetime.strftime(datetime.now(), '%H:%M:%S'))

# Log lorsqu'une nouvelle session est lancée / le script démarre
status = None

data = (
    temperature,
    humidity,
    lux,
    status,
    'on',
    get_values(temperature, humidity, lux),
    'Nouvelle session démarrée'
)

cursor = db.cursor()

cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
db.commit()

cursor.close()

while True:
    LCD.clear()

    try:
        if (get_button_state() == 0):
            humidity = DHT11.humidity
            temperature = DHT11.temperature
            lux = int(TSL2591.lux)

            message = get_values(temperature, humidity, lux)

            seconds = WATCHER_INTERVAL

        if (seconds == 1):
            humidity = DHT11.humidity
            temperature = DHT11.temperature
            lux = int(TSL2591.lux)

            message = get_values(temperature, humidity, lux)

            seconds = WATCHER_INTERVAL
        else:        
            seconds = seconds - 1

        KY029.set_green()

        if (ten_minutes_ago_lux_seconds == 1):
            cursor = db.cursor()

            cursor.execute(f'UPDATE settings SET previous_lux = {str(lux)} WHERE id = 1')
            db.commit()

            cursor.close()

            ten_minutes_ago_lux_seconds = LUX_CACHE_INTERVAL
        else:
            ten_minutes_ago_lux_seconds = ten_minutes_ago_lux_seconds - 1

        # On récupère le log précedent 
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 1")
        previous_log = cursor.fetchone()
        db.commit()
        cursor.close()

        # On récupère les settings
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM settings")
        settings = cursor.fetchone()
        db.commit()
        cursor.close()

        if (settings['resume_at']):
            if (settings['resume_at'].timestamp() > datetime.now().timestamp()):
                status = settings['custom_solar_blind_status']
            else:
                cursor = db.cursor()

                cursor.execute(f'UPDATE settings SET resume_at = NULL, SET custom_solar_blind_status = NULL WHERE id = 1')
                db.commit()

                cursor.close()

                status = getSolarBlindStatus(settings, temperature, humidity, lux)
        else:
            status = getSolarBlindStatus(settings, temperature, humidity, lux)

        # On log au changement de statut
        if (previous_log['solar_blind_status'] != status):
            data = (
                temperature,
                humidity,
                lux,
                status,
                'on',
                get_values(temperature, humidity, lux)
            )

            cursor = db.cursor()
            cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message) VALUES (%s, %s, %s, %s, %s, %s)", data)
            db.commit()
            cursor.close()

            for second in range(5):
                KY009.set_off()
                LCD.clear()

                time.sleep(0.5)

                humidity = DHT11.humidity
                temperature = DHT11.temperature
                lux = int(TSL2591.lux)

                message = get_values(temperature, humidity, lux)
                print_on_lcd(message)

                if (status == 'on'):
                    KY009.set_yellow()
                else: 
                    KY009.set_blue()

                time.sleep(0.5)
                LCD.clear()

    except RuntimeError as e:
        KY029.set_red()

        seconds = 1
        message = 'Sensor errors'
        
        data = (
            temperature,
            humidity,
            lux,
            status,
            'on',
            get_values(temperature, humidity, lux),
            '❌ {0}'.format(e.args[0] if e.args[0] else message)
        )

        cursor = db.cursor()
        cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
        db.commit()
        cursor.close()

    print_on_lcd(message)
    time.sleep(1)
