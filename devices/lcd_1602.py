from libraries.i2c_lcd import I2cLcd
 
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
I2C_BUS = 1

LCD = I2cLcd(I2C_BUS, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
