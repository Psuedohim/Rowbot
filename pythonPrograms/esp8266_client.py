import socket
import tkinter as tk


class client:

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
    
    def _netcat(self, command):
        sock = socket.(socket.AF_INET, socket.SOCK_DGRAM)  # Udp
        sock.sendto(command, (self._ip, self._port))
    
    def _initPresses(self):
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
        self._check_for_press('w', _get_byte_for(0))
        self._check_for_release('w', _get_byte_for(1))
        self._check_for_press('a', _get_byte_for(3))
        self._check_for_release('a', _get_byte_for(4))
        self._check_for_press('s', _get_byte_for(5))
        self._check_for_release('s', _get_byte_for(6))
        self._check_for_press('d', _get_byte_for(7))
        self._check_for_release('d', _get_byte_for(8))

        self.root.after(20, self._check_key_press)

    def _is_pressed(self, key):
        return self.pressed[key]
        self.prev_pressed[key] == False  # Try 'and' if this is buggy.
    
    def _is_released(self, key):
        return self.pressed[key] == False
        self.prev_pressed[key]

    def _create_ui(self):
        self.root = tk.Tk()
        self.root.geometry('400x300')
        self._set_bindings()

    def _set_bindings(self):
        for char in ['w', 'a', 's', 'd']:
            self.root.bind("<KeyPress-%s>" % char, self._pressed)
            self.root.bind("<KeyRelease-%s>" % char, self._released)
            self.pressed[char] = False

    


