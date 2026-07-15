import psutil
import time

previous_devices = set()


def check_usb_devices():

    global previous_devices

    current_devices = set()

    for part in psutil.disk_partitions():

        if "removable" in part.opts.lower():
            current_devices.add(part.device)

    inserted = current_devices - previous_devices
    removed = previous_devices - current_devices

    previous_devices = current_devices

    return inserted, removed