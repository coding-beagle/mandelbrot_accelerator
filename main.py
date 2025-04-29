import spidev
import click


def create_SPI() -> spidev.SpiDev:
    spi = spidev.SpiDev()

    spi.open(0, 0)

    spi.max_speed_hz = 2**20 + 2**15

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
    """Send two 16 bit integers to the FPGA to store in its registers"""
    spi_instance = create_SPI()
    try:
        args = data.split(",")
    except:
        click.error("Can't do that mate")

    byte_1 = (int(args[0]) & 0xFF00) >> 8
    byte_2 = int(args[0]) & 0x00FF

    byte_3 = (int(args[1]) & 0xFF00) >> 8
    byte_4 = int(args[1]) & 0x00FF

    click.echo(f"Spliting {args[0]} into {byte_1} and {byte_2}")
    click.echo(f"Spliting {args[1]} into {byte_3} and {byte_4}")

    resp = [0, 0, 0, 0, 0, 0]
    while resp[1] != 170:
        resp = spi_instance.xfer2([0x20, 0x00, byte_1, byte_2, byte_3, byte_4])
        if resp[1] != 170:
            click.echo("Wrong message from FPGA, retrying!")
    click.echo(f"FPGA status = {resp[1]}")


@cli1.command()
@click.argument("data")
def set_coords(data):
    """
    Send an x,y coordinate bit integers to the FPGA to store in its registers
    This handles the appropriate bit padding required on the FPGA side.
    """
    spi_instance = create_SPI()
    try:
        args = data.split(",")
    except:
        click.error("Can't do that mate")

    x, y = int(args[0]), int(args[1])

    click.echo(f"Splitting {x},{y}")

    # x = x << 4
    # y = y << 4

    byte_1 = (int(x) & 0xFF00) >> 8
    byte_2 = int(x) & 0x00FF

    byte_3 = (int(y) & 0xFF00) >> 8
    byte_4 = int(y) & 0x00FF

    click.echo(f"X Bytes for debug {byte_1},{byte_2}")
    click.echo(f"Y Bytes for debug {byte_3},{byte_4}")

    resp = [0, 0, 0, 0, 0, 0]
    while resp[1] != 170:
        resp = spi_instance.xfer2([0x20, 0x00, byte_1, byte_2, byte_3, byte_4])
        if resp[1] != 170:
            click.echo("Wrong message from FPGA, retrying!")

    click.echo(f"FPGA status = {resp[1]}")


@cli1.command()
def get_byte():
    """Return the two 16 bit integers from the FPGA"""
    spi_instance = create_SPI()
    resp = [0, 0, 0, 0, 0, 0]
    while resp[1] != 170:
        resp = spi_instance.xfer2([0x40, 0x00, 0x00, 0x00, 0x00, 0x00])
        if resp[1] != 170:
            click.echo("Wrong message from FPGA, retrying!")
    int1 = (resp[2] << 8 & 0xFF00) | (resp[3] & 0x00FF)
    int2 = (resp[4] << 8 & 0xFF00) | (resp[5] & 0x00FF)
    click.echo(f"Bytes returned = {resp}")
    click.echo(f"Decoded ints = {int1} and {int2}")


@cli1.command()
def get_complex_x():
    """Return the complex representation of the x screen space coordinate"""
    spi_instance = create_SPI()
    resp = [0, 0, 0, 0, 0, 0]
    while resp[1] != 170:
        resp = spi_instance.xfer2(
            [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        )
        if resp[1] != 170:
            click.echo("Wrong message from FPGA, retrying!")

    # Combine the bytes into a 64-bit integer
    q12_52_raw = "".join([hex(i) for i in resp[2:9]])
    # for i in range(2, 9):
    # q12_52_raw += hex(resp[i]).strip("0x")

    # Check if the number is negative (sign bit is set)
    # if q12_52_raw & (1 << 63):
    #     q12_52_raw -= 1 << 64

    # Convert from Q12.52 fixed-point to floating-point
    # q12_52_float = q12_52_raw / (2**52)

    # resp_bytes = ""

    # for i in range(8):
    #     resp_bytes += str(bin(resp[2:][i])).strip("0b")

    click.echo(f"Bytes returned = {resp}")
    # click.echo(f"Number bytes to hex = {[hex(i) for i in resp[2:]]}")
    click.echo(f"Number bytes to binary = {q12_52_raw}")
    # click.echo(f"Decoded Q12.52 fixed-point number = {q12_52_float}")


@cli1.command()
def get_complex_y():
    """Return the complex representation of the y screen space coordinate"""
    spi_instance = create_SPI()
    resp = [0, 0, 0, 0, 0, 0]
    while resp[1] != 170:
        resp = spi_instance.xfer2(
            [0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        )
        if resp[1] != 170:
            click.echo("Wrong message from FPGA, retrying!")

    # Combine the bytes into a 64-bit integer
    q12_52_raw = 0
    for i in range(2, 9):
        q12_52_raw = (q12_52_raw << 8) | resp[i]

    # Check if the number is negative (sign bit is set)
    if q12_52_raw & (1 << 63):
        q12_52_raw -= 1 << 64

    # Convert from Q12.52 fixed-point to floating-point
    q12_52_float = q12_52_raw / (2**52)

    click.echo(f"Bytes returned = {resp}")
    click.echo(f"Decoded Q12.52 fixed-point number = {q12_52_float}")


@cli1.command()
# @click.option("--get", help="Command to send")
def led_off():
    """Send a command to turn the LED off over SPI"""
    spi_instance = create_SPI()
    spi_instance.xfer2([0x10])


cli = click.CommandCollection(sources=[cli1])
if __name__ == "__main__":
    cli()
