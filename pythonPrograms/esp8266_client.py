import socket
import tkinter as tk


class Client:

    def __init__(self, ip, port="80"):  # Default port is 80.
        self._ip = ip
        self._port = port
        self.pressed = {}
        self.prev_pressed = {}
        self._init_presses()
        self._create_ui()

    def _netcat(self, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Udp
        sock.sendto(command, (self._ip, self._port))

    def _init_presses(self):
        """Set key press' default state: false."""
        self.pressed["w"] = False
        self.pressed["a"] = False
        self.pressed["s"] = False
        self.pressed["d"] = False
        self.prev_pressed["w"] = False
        self.prev_pressed["a"] = False
        self.prev_pressed["s"] = False
        self.prev_pressed["d"] = False

    def start(self):
        self._check_key_press()
        self.root.mainloop()

    def _check_for_press(self, key, command):
        if self._is_pressed(key):
            self.prev_pressed[key] = True
            self._netcat(command)

    def _get_byte_for(self, int):
        """Return byte for passed integer."""
        return int.to_bytes(1, byteorder='big')

    def _check_for_release(self, key, command):
        if self._is_released(key):
            self.prev_pressed[key] = False
            self._netcat(command)

    def _check_key_press(self):
        # self._check_for_press('w', self._get_byte_for(0))
        # self._check_for_release('w', self._get_byte_for(1))
        # self._check_for_press('a', self._get_byte_for(3))
        # self._check_for_release('a', self._get_byte_for(4))
        # self._check_for_press('s', self._get_byte_for(5))
        # self._check_for_release('s', self._get_byte_for(6))
        # self._check_for_press('d', self._get_byte_for(7))
        # self._check_for_release('d', self._get_byte_for(8))
        self._check_for_press("w", b"\x01")
        self._check_for_release("w", b"\x02")
        self._check_for_press("s", b"\x03")
        self._check_for_release("s", b"\x04")
        self._check_for_press("d", b"\x05")
        self._check_for_release("d", b"\x06")
        self._check_for_press("a", b"\x07")
        self._check_for_release("a", b"\x08")

        self.root.after(20, self._check_key_press)

    def _is_pressed(self, key):
        # Try 'and' if this is buggy.
        return self.pressed[key] and self.prev_pressed[key] == False

    def _is_released(self, key):
        # Same as function above.
        return self.pressed[key] == False and self.prev_pressed[key]

    def _create_ui(self):
        self.root = tk.Tk()
        self.root.geometry('400x300')
        self._set_bindings()

    def _set_bindings(self):
        for char in ['w', 'a', 's', 'd']:
            self.root.bind("<KeyPress-%s>" % char, self._pressed)
            self.root.bind("<KeyRelease-%s>" % char, self._released)
            self.pressed[char] = False

    def _pressed(self, event):
        self.pressed[event.char] = True

    def _released(self, event):
        self.pressed[event.char] = False


# Testing
ip = "192.168.4.1"
port = 80

client = Client(ip, port)
client.start()
