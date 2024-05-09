# led RGB

from gpiozero import LED

# Déclaration des LEDs sur leurs broches GPIO correspondantes
led_rouge = LED(13)
led_vert = LED(19)
led_bleue = LED(26)

def set_blue():
    led_rouge.off()
    led_vert.on()
    led_bleue.on()

def set_yellow():
    led_rouge.on()
    led_vert.on()
    led_bleue.off()


# while True:
#     set_blue()
#     time.sleep(1)  # Mode d'attente pendant 3 secondes
#     set_yellow()
#     time.sleep(1)