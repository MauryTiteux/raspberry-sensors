import RPi.GPIO as GPIO

Button = 16
GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_button_state():
    return GPIO.input(Button)
