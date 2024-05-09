import board
import libraries.light as light

i2c = board.I2C()
TSL2591 = light.TSL2591(i2c)