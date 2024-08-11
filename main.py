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

cursor = db.cursor(dictionary=True)
cursor.execute("SELECT * FROM settings")
settings = cursor.fetchone()
db.commit()
cursor.close()

seconds = WATCHER_INTERVAL
message = get_values(temperature, humidity, lux)
previous_resume_at = settings['resume_at']

timer_before_changing_status = 0

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

        # Récupération des events
        cursor = db.cursor(dictionary=True)
        cursor.execute(f'SELECT * FROM events WHERE {datetime.now().timestamp()} BETWEEN start_at AND end_at')
        event = cursor.fetchone()
        db.commit()
        cursor.close()

        # Récupération des récurrences
        cursor = db.cursor(dictionary=True)
        cursor.execute(f'SELECT * FROM days WHERE day = {datetime.today().weekday()} AND is_recurrent = 1')
        recurrent = cursor.fetchone()
        db.commit()
        cursor.close()

        if (settings['resume_at']):
            if (settings['resume_at'].timestamp() > datetime.now().timestamp()):
                timer_before_changing_status = 0
                status = settings['custom_solar_blind_status']

                if (previous_resume_at is None):
                    data = (
                        temperature,
                        humidity,
                        lux,
                        status,
                        'on',
                        get_values(temperature, humidity, lux),
                        'Mode manuel activé'
                    )

                    cursor = db.cursor()
                    cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
                    db.commit()
                    cursor.close()

                    previous_resume_at = settings['resume_at']
            else:
                cursor = db.cursor()
                cursor.execute(f'UPDATE settings SET resume_at = NULL, SET custom_solar_blind_status = NULL WHERE id = 1')
                db.commit()
                cursor.close()

                status = getSolarBlindStatus(settings, temperature, humidity, lux)
        # Si event programmé ou récurrent, on force le statut à off
        elif (event or recurrent):
            status = 'off'
            timer_before_changing_status = 0
        else:
            status = getSolarBlindStatus(settings, temperature, humidity, lux)

        if (previous_resume_at and settings['resume_at'] is None):
            data = (
                temperature,
                humidity,
                lux,
                status,
                'on',
                get_values(temperature, humidity, lux),
                'Mode manuel désactivé'
            )

            cursor = db.cursor()
            cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
            db.commit()
            cursor.close()

            previous_resume_at = None
        
        # Si le log précédent est un autre jour qu'aujourd'hui et qu'on a un event programmé, on log
        if (event and previous_log['created_at'].weekday() != datetime.today().weekday()):
            data = (
                temperature,
                humidity,
                lux,
                status,
                'on',
                get_values(temperature, humidity, lux),
                f"Évenement programmé du {datetime.strftime(event['start_at'], '%D %M %Y')} au {datetime.strftime(event['end_at'], '%D %M %Y')}"
            )

            cursor = db.cursor()
            cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
            db.commit()
            cursor.close()

        # Si le log précédent est un autre jour qu'aujourd'hui et qu'on a un event récurrent, on log
        if (recurrent and previous_log['created_at'].weekday() != datetime.today().weekday()):
            data = (
                temperature,
                humidity,
                lux,
                status,
                'on',
                get_values(temperature, humidity, lux),
                f"Ouverture décallée à {recurrent['start_at_hour']}h"
            )

            cursor = db.cursor()
            cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
            db.commit()
            cursor.close()

        # Si on a un décompte de 5 minutes et décompte les minutes seconde par seconde
        if (timer_before_changing_status > 0):
            timer_before_changing_status  = timer_before_changing_status - 1

        # On log au changement de statut et si au moins 5 minutes sont passées
        if (previous_log['solar_blind_status'] != status and timer_before_changing_status == 0):
            # On initialise le décompte de 5 minutes si en mode auto
            if (settings['resume_at'] is None and event is None and recurrent is None):
                timer_before_changing_status = 300

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

        if (status == 'on'):
            KY009.set_yellow()
        else: 
            KY009.set_blue()

        cursor = db.cursor()
        cursor.execute("INSERT INTO logs(temperature, humidity, lux, solar_blind_status, script_status, message, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
        db.commit()
        cursor.close()

    print_on_lcd(message)
    time.sleep(1)
