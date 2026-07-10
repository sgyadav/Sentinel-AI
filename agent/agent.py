import time

from monitor import get_system_info
from sender import send_system_info

while True:

    info = get_system_info()

    print(info)

    send_system_info(info)

    time.sleep(5)