from OLED_TEST import display_message
import network
import socket
import time
import json
import urequests as requests
from machine import Pin, I2C, SPI
import SSD1306
from PN532 import read_tag, read_nfc_with_duration
import NFC_PN532 as nfc

###### FOR OLED ###########
# Initialize I2C1 with GP10 and GP11 for OLED
i2c = I2C(1, scl=Pin(11), sda=Pin(10))
# Initialize OLED display (128x32 resolution)
oled = SSD1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)
###########################

###### FOR NFC ############
# SPI
spi_dev = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(6), mosi=Pin(7), miso=Pin(4))
cs = Pin(5, Pin.OUT)
cs.on()
# SENSOR INIT
pn532 = nfc.PN532(spi_dev, cs)
ic, ver, rev, support = pn532.get_firmware_version()
print(f"Found PN532 with firmware version: {ver}.{rev}")
pn532.SAM_configuration()
###########################

# Reset Wi-Fi connection
def reset_wifi():
    wlan = network.WLAN(network.STA_IF)
    if wlan.active():
        wlan.active(False)
    wlan.active(True)
    print("Wi-Fi reset completed.")

# Reset socket connection
def reset_socket():
    try:
        sock = socket.socket()
        sock.close()
        print("Socket reset completed.")
    except Exception as e:
        print(f"Socket reset error: {e}")

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Reset Wi-Fi before connecting (optional, depending on your needs)
    reset_wifi()  # If you need to reset the Wi-Fi hardware, keep this line; otherwise, you can remove it.

    # Try connecting to the Wi-Fi
    while not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect(ssid, password)
        # Wait for 5 seconds and check again
        timeout = 0
        while not wlan.isconnected() and timeout < 5:
            time.sleep(1)
            timeout += 1
        if timeout >= 5:
            print("Still not connected. Retrying in 5 seconds...")
            time.sleep(5)  # Wait 5 seconds before retrying


####### DEVICE/STATION/OPERATION ID #########
device_id = 3
operator_id = "OPT001"
last_tag = "000"
tag_id = None

####### FOR WIFI ##########
# Update with your network details
# ssid = 'Seaside3-2.4'
# password = 'RollerCoaster95060!'
ssid = '165-Corp'
password = '4851Anato*'

display_message(f"Device ID: {device_id}","")
time.sleep(2)
reset_socket()  # Reset socket before starting
display_message("Connecting...", "")
connect_to_wifi(ssid, password)
display_message("Wi-Fi connected.", "")

# Prepare to create a socket
sock = socket.socket()
sock.bind(("", 8001))
sock.listen(1)

# SERVER_URL = "10.1.10.204"
SERVER_URL = "192.168.10.244"
SERVER_PORT = 5022
###########################


def get_so_item_info(cup_tag_id):
    """Fetch sales order ID by cup_tag_id from the server."""
    try:
        response = requests.get(f"http://{SERVER_URL}:5022/get_so_item/{cup_tag_id}")

        if response.status_code == 200:
            response_data = response.json()  # Parse the JSON response
            return response_data.get("sales_order_id", "Not Found"), response_data.get("item", "Not Found")
        else:
            print(f"Error fetching sales order info: {response.text}")
            return "No Sales Order.", "Contact QA."
    except Exception as e:
        return "No Sales Order.", "Contact QA."


def send_log(operator_id, tag_id, device_id, duration):
    """Send logs to the server."""
    t = time.localtime()  # Get local time as a struct_time
    timestamp = "{:02}-{:02}-{:04} {:02}:{:02}:{:02}".format(t[1], t[2], t[0], t[3], t[4], t[5])

    data = {
        "operator_tag_id": operator_id,
        "tag_id": tag_id,
        "device_id": device_id,
        "duration": duration,
        "timestamp": timestamp
    }

    request_body = json.dumps(data)
    request = "POST /add_log HTTP/1.1\r\n" \
              "Host: {}:{}\r\n" \
              "Content-Type: application/json\r\n" \
              "Content-Length: {}\r\n" \
              "\r\n" \
              "{}".format(SERVER_URL, SERVER_PORT, len(request_body), request_body)

    try:
        client_sock = socket.socket()
        client_sock.connect((SERVER_URL, SERVER_PORT))
        client_sock.send(request.encode())
        response = client_sock.recv(1024)
        # print(f"Log response: {response.decode()}")
        client_sock.close()
    except Exception as e:
        print(f"Failed to send log: {e}")


### MAIN FUNCTION V1.2 ###
display_message("Place the cup...", "")
while True:
    tag_id = read_tag(pn532, 500)
    duration = 0
    if last_tag != tag_id and tag_id is not None:
        try:
            display_message("Reading...", "")
            sales_order_id, item = get_so_item_info(tag_id)
            sales_order_id = str(sales_order_id)

            display_message("Logging...", "")
            send_log(operator_id, tag_id, device_id, duration)
            display_message(sales_order_id, item)
            # capture duration and send again
            tag_id, duration = read_nfc_with_duration(pn532, 500)
            send_log(operator_id, tag_id, device_id, duration)

            last_tag = tag_id
        except Exception as e:
            display_message("No Sales Order.", "")

    elif tag_id is None:
        display_message("Place the cup...", "")
        last_tag = "000"



