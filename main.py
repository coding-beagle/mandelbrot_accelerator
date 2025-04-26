import spidev
import click


def create_SPI() -> spidev.SpiDev:
    spi = spidev.SpiDev()

    spi.open(0, 0)

    spi.max_speed_hz = 2**20

    spi.mode = 0b01

    return spi


@click.group()
def cli1():
    pass


@cli1.command()
# @click.option("--get", help="Command to send")
def led_on():
    """Send a command to turn the LED on over SPI"""
    spi_instance = create_SPI()
    spi_instance.xfer2(0x20)


@cli1.command()
# @click.option("--get", help="Command to send")
def led_off():
    """Send a command to turn the LED off over SPI"""
    spi_instance = create_SPI()
    spi_instance.xfer2(0x10)


cli = click.CommandCollection(sources=[cli1])
if __name__ == "__main__":
    cli()
