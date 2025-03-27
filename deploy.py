import os
import time
import subprocess

# List of all files to copy
files_to_upload = ["NFC_PN532.py", "OLED_TEST.py", "PN532.py", "SSD1306.py"]

# Load the main.py template
with open("main_template.py", "r") as f:
    template = f.read()

for device_id in range(16, 57):  # Deploying to devices 16 to 56
    print(f"Deploying to device {device_id}...")

    # Replace placeholder with actual device_id
    main_py = template.replace("{{DEVICE_ID}}", str(device_id))

    # Save a temporary main.py file
    with open("main.py", "w") as f:
        f.write(main_py)

    # Copy main.py
    subprocess.run(["mpremote", "connect", "auto", "cp", "main.py", ":main.py"])

    # Copy other scripts
    for file in files_to_upload:
        subprocess.run(["mpremote", "connect", "auto", "cp", file, f":{file}"])

    print(f"Device {device_id} uploaded. Unplug and connect the next Pico.")
    input("Press Enter when ready for the next device...")  # Wait for user

print("Deployment complete for all devices!")
