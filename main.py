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
    # Log lorsqu'une nouvelle session est lancée / le script démarre
    data = (
        DHT11.temperature,
        DHT11.humidity,
        int(TSL2591.lux),
        None,
        'on',
        get_values(),
        'Nouvelle session démarrée'
    )

    cursor = db.cursor()

    cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
    db.commit()

    cursor.close()
except:
    print('error 1')
 
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
            try:
                cursor = db.cursor()

                cursor.execute(f'UPDATE settings SET previous_lux = {str(TSL2591.lux)} WHERE id = 1')
                db.commit()

                cursor.close()
            except:
                print('error 2')

            ten_minutes_ago_lux_seconds = LUX_CACHE_INTERVAL
        else:
            ten_minutes_ago_lux_seconds = ten_minutes_ago_lux_seconds - 1

        char_missing_first_line = CHAR_PER_LINE - len(message)

        if (char_missing_first_line != 0):
            message += ' ' * char_missing_first_line

        LCD.putstr(message)
        LCD.putstr(str(seconds) + 's - ' + datetime.strftime(datetime.now(), '%H:%M:%S'))

        # On récupère le log précedent 
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM logs ORDER BY created_at DESC LIMIT 0,1")
        previous_log = cursor.fetchone()

        cursor.close()

        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute("SELECT * FROM settings")
            settings = cursor.fetchone()

            cursor.close()

            if (settings['resume_at']):
                if (settings['resume_at'].microsecond > datetime.now().microsecond):
                    status = settings['custom_solar_blind_status']
                else:
                    cursor = db.cursor()

                    cursor.execute(f'UPDATE settings SET resume_at = NULL WHERE id = 1')
                    db.commit()

                    cursor.close()

                    status = getSolarBlindStatus(settings)
            else:
                status = getSolarBlindStatus(settings)

            if (status == 'on'):
                KY009.set_yellow()
            else:
                KY009.set_blue()

            # On log au changement de statut
            if (previous_log['solar_blind_status'] != status):
                data = (
                    DHT11.temperature,
                    DHT11.humidity,
                    int(TSL2591.lux),
                    status,
                    'on',
                    get_values(),
                    'Hello'
                )

                try:
                    cursor = db.cursor()

                    cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
                    db.commit()

                    cursor.close()
                except:
                    print('error 3')


        except Exception as e:
            # On log lorsqu'il y a une erreur mais que le script tourne toujours
            data = {
                DHT11.temperature,
                DHT11.humidity,
                int(TSL2591.lux),
                previous_log['solar_blind_status'],
                'on',
                get_values(),
                'Error'
            }

            try:
                # Log lorsqu'une nouvelle session est lancée / le script démarre
                data = (
                    DHT11.temperature,
                    DHT11.humidity,
                    int(TSL2591.lux),
                    None,
                    'on',
                    get_values(),
                    'Nouvelle session démarrée'
                )

                cursor = db.cursor()

                cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
                db.commit()

                cursor.close()
            except:
                print('error 4')

            KY029.set_red()

        time.sleep(1)
except:
    # On log lorsqu'il y a une erreur mais que le script s'arrête
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM logs ORDER BY created_at DESC LIMIT 0,1")
    previous_log = cursor.fetchone()

    cursor.close()

    data = {
        DHT11.temperature,
        DHT11.humidity,
        int(TSL2591.lux),
        previous_log['solar_blind_status'],
        'off',
        get_values(),
        'Fatal error'
    }

    cursor = db.cursor()

    cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)

    db.commit()
    cursor.close()

    KY029.set_red()
