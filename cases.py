from datetime import datetime

def getSolarBlindStatus(settings, temperature, humidity, lux):
    opening_hours = {
        'summer': [settings['summer_opening_hour'], settings['summer_closing_hour']],
        'winter': [settings['winter_opening_hour'], settings['winter_closing_hour']]
    }

    date = datetime.now()
    current_season = 'summer' if date.month > 3 and date.month < 10 else 'winter'
    current_opening_hours = opening_hours[current_season]
    
    if (date.hour <= current_opening_hours[0] or date.hour >= current_opening_hours[1]):
        return 'off'
    
    if (temperature > settings['temperature_max']):
        if (humidity < settings['humidity_max']):
            return 'off'
        else:
            if (lux > settings['lux'] and lux > settings['previous_lux'] * 0.1):
                return 'off'
            else:
                return 'on'

    if (temperature < settings['temperature_min']):
        return 'on'

    if (humidity > settings['humidity_max']):
        if (lux > settings['lux'] and lux > settings['previous_lux'] * 0.1):
            return 'off'
        else:
            return 'on'

    return 'on'
