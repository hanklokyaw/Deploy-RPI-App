'''
Tech Stack: Micropython, Raspberry Pi Pico, PN532 NFC/RFID,
            NFC-PN532 Lib at https://github.com/Carglglz/NFC_PN532_SPI
Raspberry Pi PICO 2020 was connected with PN532 NFC/RFID Module as below
PIN
--------------+-------------------------------
PN532 MODULE  |   RPI Pico Side
--------------+-------------------------------
col     LBL      PIN    GPIO    RP2 Fxn
----------------------------------------------
ORN     SCK       9       6     spi0 sck
YEL     MISO      6       4     spi0 rx
GRN     MOSI      10      7     spi0 tx
BLU     SS        7       5     spi0 cs(n)
VLT     VCC       40            VBUS (5v)
GRY     GND       38            GND
WHT
BLK
-----------------------------------------------
Code reference: https://github.com/Carglglz/NFC_PN532_SPI
Library used: https://github.com/Carglglz/NFC_PN532_SPI/blob/master/NFC_PN532.py
Library file was saved in the same direcotory as pn532.py
Author rt@mps.in 2022/07/12
'''

import NFC_PN532 as nfc
from machine import Pin, SPI
import time

# SPI
spi_dev = SPI(0, baudrate=1000, polarity=0, phase=0, sck=Pin(6), mosi=Pin(7), miso=Pin(4))
cs = Pin(5, Pin.OUT)
cs.on()

# SENSOR INIT
pn532 = nfc.PN532(spi_dev, cs)
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()


def read_nfc_with_duration(dev, tmot):
    """Accepts a device and a timeout in milliseconds.
    Starts counting the total duration the tag is presented,
    stops if the tag is removed or a different tag is presented.

    Returns the tag ID and the duration for each continuous tag.
    """
    last_tag = None
    start_time = None

    while True:
        uid = dev.read_passive_target(timeout=tmot)

        if uid is not None:
            # Format UID into a string
            numbers = [i for i in uid]
            current_tag = '{}-{}-{}-{}'.format(*numbers)
            # print(f'Current tag detected: {current_tag}')

            # If a new tag is presented
            if current_tag != last_tag:
                # If there was a previous tag, stop timing and print duration
                if last_tag is not None and start_time is not None:
                    duration = time.time() - start_time
                    print(f"Tag {last_tag} duration: {duration:.2f} seconds")
                    return last_tag, duration  # Return previous tag's info

                # Start timing for the new tag
                last_tag = current_tag
                start_time = time.time()
                # print(f"Started timing for tag: {last_tag}")

        else:
            # No tag detected, check if we need to end timing
            if last_tag is not None and start_time is not None:
                duration = time.time() - start_time
                print(f"Tag {last_tag} duration: {duration:.2f} seconds")
                return last_tag, duration  # Return last tag's info

            # If no tag was previously detected, keep waiting
            last_tag = None
            start_time = None
            # print("No tag present")

        # Short delay before the next read attempt
        time.sleep(0.1)  # Adjust for responsiveness


def read_tag(dev, tmot):
    while True:
        uid = dev.read_passive_target(timeout=tmot)

        if uid is not None:
            # Format UID into a string
            numbers = [i for i in uid]
            current_tag = '{}-{}-{}-{}'.format(*numbers)
            return current_tag
        else:
            return None


