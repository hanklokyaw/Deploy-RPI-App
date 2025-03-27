from machine import Pin, I2C
import SSD1306
import time

# Initialize I2C1 with GP10 and GP11 for OLED
i2c = I2C(1, scl=Pin(11), sda=Pin(10))
# test i2c address
print("I2C addresses:", i2c.scan())


# Initialize OLED display (128x32 resolution)
oled = SSD1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)


def display_message(title, content):
    """
    Displays a title on the first line and content on the second and third lines.
    If the content is too long for the second line, it continues on the third.

    Parameters:
    - title (str): The text for the first line.
    - content (str): The text for the second and possibly third line.
    """
    oled.fill(0)  # Clear display

    # Display the title on the first line
    oled.text(title, 0, 0)

    # Set parameters for display dimensions
    line_height = 10  # Each line height in pixels
    max_chars_per_line = 16  # Approximate max characters per line on 128x32 OLED

    # Display content on the second and third lines if needed
    if len(content) <= max_chars_per_line:
        # Content fits on the second line only
        oled.text(content, 0, line_height * 1)
    else:
        # Split content for the second and third lines
        second_line = content[:max_chars_per_line]
        third_line = content[max_chars_per_line:max_chars_per_line*2]

        # Display content on the second and third lines
        oled.text(second_line, 0, line_height * 1)
        oled.text(third_line, 0, line_height * 2)

    oled.show()  # Update the display




# # Test the display function
# title_message = "102256986"
# content_message = "ED-PRGEFAC-TI-16g-2.5"
# display_message(title_message, content_message)
# time.sleep(5)  # Keep the message on screen for 5 seconds


