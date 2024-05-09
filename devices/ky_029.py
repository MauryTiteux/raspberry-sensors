# led bicolore

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

LED_ROUGE = 20
LED_VERTE = 21
GPIO.setup(LED_ROUGE, GPIO.OUT, initial= GPIO.LOW)
GPIO.setup(LED_VERTE, GPIO.OUT, initial= GPIO.LOW)

def set_red():
    GPIO.output(LED_ROUGE,GPIO.HIGH) #la Led s'allume
    GPIO.output(LED_VERTE,GPIO.LOW) #la LED commute

def set_green():
    GPIO.output(LED_ROUGE,GPIO.LOW) #la Led s'allume
    GPIO.output(LED_VERTE,GPIO.HIGH) #la LED commute
