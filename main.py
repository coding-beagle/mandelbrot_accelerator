import spidev

spi = spidev.SpiDev()

spi.open(0, 0)

spi.max_speed_hz = 2 ** 20

spi.mode = 0b01


send_data = [int(input("Enter byte to send: ").strip())]
print(str(send_data))
print(spi.xfer2(send_data))
