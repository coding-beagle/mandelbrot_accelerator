import spidev
import click
from fixedpoint import FixedPoint
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image


def create_SPI() -> spidev.SpiDev:
    spi = spidev.SpiDev()

    spi.open(0, 0)

    spi.max_speed_hz = 2**21

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
    q12_52_raw = "".join(
        [str(hex(i)).split("0x")[-1] if i != 0 else "00" for i in resp[2:]]
    )

    str_number = "0x" + q12_52_raw

    click.echo(f"Bytes returned = {resp}")
    click.echo(f"Number bytes to binary = {q12_52_raw}")
    click.echo(
        f"Decoded Q12.52 fixed-point number = {float(FixedPoint(str_number, signed=1, m=12,n=52))}"
    )


def q12_52_bytes_to_float(bytes_input):
    q12_52_raw = "".join(
        [str(hex(i)).split("0x")[-1] if i != 0 else "00" for i in bytes_input]
    )

    return float(FixedPoint("0x" + q12_52_raw, signed=1, m=12, n=52))


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
    q12_52_raw = "".join(
        [str(hex(i)).split("0x")[-1] if i != 0 else "00" for i in resp[2:]]
    )

    str_number = "0x" + q12_52_raw

    click.echo(f"Bytes returned = {resp}")
    click.echo(f"Number bytes to binary = {q12_52_raw}")
    click.echo(
        f"Decoded Q12.52 fixed-point number = {float(FixedPoint(str_number, signed=1, m=12,n=52))}"
    )


@cli1.command()
@click.argument("data")
def get_iter_count(data):
    """
    Send an x,y coordinate bit integers to the FPGA to store in its registers
    This handles the appropriate bit padding required on the FPGA side.

    Then it sends a message to query whether or not those coordinates are part of
    the mandelbrot set
    """
    spi_instance = create_SPI()

    get_iteration_count_helper(spi_instance, data)


def get_iteration_count_helper(spi_instance, data):

    try:
        args = data.split(",")
    except:
        click.error("Can't do that mate")

    x, y = int(args[0]), int(args[1])

    # click.echo(f"Splitting {x},{y}")

    # x = x << 4
    # y = y << 4

    byte_1 = (int(x) & 0xFF00) >> 8
    byte_2 = int(x) & 0x00FF

    byte_3 = (int(y) & 0xFF00) >> 8
    byte_4 = int(y) & 0x00FF

    # click.echo(f"X Bytes for debug {byte_1},{byte_2}")
    # click.echo(f"Y Bytes for debug {byte_3},{byte_4}")

    resp = [0, 0, 0, 0, 0, 0]
    # while resp[1] != 170:
    resp = spi_instance.xfer2([0x20, 0x00, byte_1, byte_2, byte_3, byte_4])
    # if resp[1] != 170:
    # click.echo("Wrong message from FPGA, retrying!")
    # pass

    # click.echo(f"FPGA status = {resp[1]}, fetching resulting calculation")

    resp_2 = [0, 0, 0, 0, 0, 0, 0, 0]
    # while resp_2[1] != 170:
    resp_2 = spi_instance.xfer2(
        [0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    )
    # if resp_2[1] != 170:
    # pass
    # click.echo("Wrong message from FPGA, retrying!")

    # click.echo(f"FPGA status = {resp_2[1]}")
    # click.echo(f"Resultant bits = {[bin(i) for i in resp_2[2:]]}")
    return resp_2[-1]


@cli1.command()
def draw_mandelbrot():
    spi_instance = create_SPI()
    image_data = np.zeros((512, 1024, 3), dtype=np.uint8)

    try:
        for x in range(1024):
            for y in range(512):
                iteration_count = min(
                    get_iteration_count_helper(spi_instance, f"{x},{y}"), 255
                )
                image_data[y, x] = [iteration_count, 0, 0]
            click.echo(f"Finished column {x} / 1024")
    except KeyboardInterrupt:
        click.echo("Process interrupted. Saving the current image...")

    # Convert the image data to an Image object
    img = Image.fromarray(image_data, "RGB")

    # Save the image to a file
    img.save("mandelbrot.png")

    click.echo("Mandelbrot image saved as mandelbrot.png")


@cli1.command()
@click.argument("data")
@click.argument("register")
def set_value(data, register):
    if not (register in ["0", "1", "2", "3"]):
        click.error(
            "Wrong register entered! 0,1,2,3 for stepXVal, stepYVal, topLeftX, topLeftY"
        )

    spi_instance = create_SPI()

    click.echo(f"Setting data to {float(data)}")

    number = FixedPoint(float(data), signed=1, m=12, n=52, str_base=16)

    # Convert the FixedPoint number to bytes

    click.echo(f"number bytes = {hex(number)}")

    number_hex = hex(number).split("0x")[-1]

    args = [number_hex[i : i + 2] for i in range(0, len(number_hex), 2)]
    hex_args = [number_hex[i : i + 2] for i in range(0, len(number_hex), 2)]

    click.echo(f"Hex args = {hex_args}")

    # Send the command over SPI
    # resp = spi_instance.xfer2(args)

    # click.echo(f"FPGA Status {resp[1]}")


@cli1.command()
@click.argument("register")
def get_value(register):
    if not (register in ["0", "1", "2", "3"]):
        click.error(
            "Wrong register entered! 0,1,2,3 for stepXVal, stepYVal, topLeftX, topLeftY"
        )

    spi_instance = create_SPI()

    args = [0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    resp = spi_instance.xfer2(args)

    click.echo(f"FPGA Status {resp[1]}")
    value = q12_52_bytes_to_float(resp[2:])
    click.echo(f"Returned value = {value}")


@cli1.command()
# @click.option("--get", help="Command to send")
def led_off():
    """Send a command to turn the LED off over SPI"""
    spi_instance = create_SPI()
    spi_instance.xfer2([0x10])


cli = click.CommandCollection(sources=[cli1])
if __name__ == "__main__":
    cli()
