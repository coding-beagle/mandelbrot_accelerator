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
    resp = spi_instance.xfer2([0x20, 0x00, 0x00])
    click.echo(f"FPGA response = {resp[1]}")


@cli1.command()
@click.argument("data")
def set_byte(data):
    """Send two 16 bit integers to the FPGA to store in it's registers"""
    spi_instance = create_SPI()
    try:
        args = data.split(",")
    except:
        click.error("Can't do that mate")

    byte_1 = (int(args[0]) & 0xFF) >> 8
    byte_2 = int(args[0]) & 0x0F

    byte_3 = (int(args[1]) & 0xFF) >> 8
    byte_4 = int(args[1]) & 0x0F

    click.echo(f"Spliting {args[0]} into {byte_1} and {byte_2}")
    click.echo(f"Spliting {args[1]} into {byte_3} and {byte_4}")

    resp = spi_instance.xfer2([0x20, 0x00, byte_1, byte_2, byte_3, byte_4])
    click.echo(f"FPGA status = {resp[1]}")


@cli1.command()
def get_byte():
    """Return the two 16 bit integers from the FPGA"""
    spi_instance = create_SPI()
    resp = spi_instance.xfer2([0x40, 0x00, 0x00, 0x00, 0x00])
    int1 = (resp[1] << 8 & 0xF0) | (resp[0] & 0x0F)
    int2 = (resp[3] << 8 & 0xF0) | (resp[2] & 0x0F)
    click.echo(f"Bytes returned = {resp}")
    click.echo(f"Decoded ints = {int1} and {int2}")


@cli1.command()
# @click.option("--get", help="Command to send")
def led_off():
    """Send a command to turn the LED off over SPI"""
    spi_instance = create_SPI()
    spi_instance.xfer2([0x10])


cli = click.CommandCollection(sources=[cli1])
if __name__ == "__main__":
    cli()
