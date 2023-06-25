import sys
import threading
import time
from typing import Optional


class Spinner:
    """Simple implementation of a spinner"""

    def __init__(self):
        self.spinner_flag: bool = True
        self.thread: Optional[threading.Thread] = None

    def spinner(self, spin_delay: float = 0.12):
        while self.spinner_flag:
            for char in "|/-\\":
                sys.stdout.write("\r" + char)
                sys.stdout.flush()
                time.sleep(spin_delay)
        sys.stdout.write("\r")

    def stop(self):
        self.spinner_flag = False
        self.thread.join()

    def start(self):
        self.spinner_flag = True
        self.thread = threading.Thread(target=self.spinner)
        self.thread.start()
