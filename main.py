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
    spi_instance = create_SPI()
    try:
        args = data.split(",")
    except:
        click.error("Can't do that mate")
    resp = spi_instance.xfer2(
        [0x20, 0x00, int(args[0]), int(args[1]), int(args[2]), int(args[3])]
    )
    click.echo(f"FPGA status = {resp[1]}")


@cli1.command()
def get_byte():
    spi_instance = create_SPI()
    resp = spi_instance.xfer2([0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
    click.echo(f"Bytes returned = {resp}")


@cli1.command()
# @click.option("--get", help="Command to send")
def led_off():
    """Send a command to turn the LED off over SPI"""
    spi_instance = create_SPI()
    spi_instance.xfer2([0x10])


cli = click.CommandCollection(sources=[cli1])
if __name__ == "__main__":
    cli()
