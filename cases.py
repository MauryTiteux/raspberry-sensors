from datetime import datetime
from devices.dht11 import DHT11
from devices.tsl2591 import TSL2591

opening_hours = {
    'summer': [6, 23],
    'winter': [7, 20]
}

def getSolarBlindStatus(previous_lux: int):
    date = datetime.now()
    current_season = 'summer' if date.month > 3 and date.month < 10 else 'winter'
    current_opening_hours = opening_hours[current_season]

    humidity = DHT11.humidity
    temperature = DHT11.temperature
    lux = int(TSL2591.lux)

    if (date.hour <= current_opening_hours[0] or date.hour >= current_opening_hours[1]):
        return 'close'
    
    if (temperature > 25):
        if (humidity < 70):
            return 'close'
        else:
            if (lux > 80000 and lux > previous_lux * 0.1):
                return 'close'
            else:
                return 'open'

    if (temperature < 15):
        return 'open'

    if (humidity > 70):
        if (lux > 80000 and lux > previous_lux * 0.1):
            return 'close'
        else:
            return 'open'

    return 'open'
