import os
import time
import ctypes
import ctypes.wintypes
import threading
from datetime import datetime

_user32 = ctypes.windll.user32
_gdi32 = ctypes.windll.gdi32


def _capture_screen_to_bmp(path):
    w = _user32.GetSystemMetrics(0)
    h = _user32.GetSystemMetrics(1)
    hdc_screen = _user32.GetDC(0)
    hdc_mem = _gdi32.CreateCompatibleDC(hdc_screen)
    hbm = _gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
    _gdi32.SelectObject(hdc_mem, hbm)
    _gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, 0x00CC0020)
    bmi = ctypes.create_string_buffer(40)
    ctypes.memmove(bmi, ctypes.c_uint(40), 4)
    ctypes.memmove(bmi[4:], ctypes.c_uint(1), 4)
    ctypes.memmove(bmi[8:], ctypes.c_uint(24), 4)
    ctypes.memmove(bmi[12:], ctypes.c_uint(0), 4)
    ctypes.memmove(bmi[16:], ctypes.c_uint(0), 4)
    ctypes.memmove(bmi[20:], ctypes.c_uint(0), 4)
    ctypes.memmove(bmi[24:], ctypes.c_uint(0), 4)
    ctypes.memmove(bmi[24:], ctypes.c_uint(0), 4)
    buf_size = w * h * 3 + 54
    buf = ctypes.create_string_buffer(buf_size)
    written = ctypes.c_uint(0)
    _gdi32.GetDIBits(hdc_mem, hbm, 0, h, buf, bmi, 0)
    _gdi32.DeleteObject(hbm)
    _gdi32.DeleteDC(hdc_mem)
    _user32.ReleaseDC(0, hdc_screen)
    with open(path, 'wb') as f:
        f.write(b'BM')
        f.write((buf_size + 14).to_bytes(4, 'little'))
        f.write(b'\x00\x00\x00\x00\x36\x00\x00\x00')
        f.write(bytes(buf))
    return path


class ScreenshotEngine:
    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'output', 'screenshots')
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.running = False
        self.thread = None

    def capture_once(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(self.output_dir, f"screenshot_{ts}.bmp")
        try:
            _capture_screen_to_bmp(path)
            return path
        except Exception:
            return None

    def _loop(self, interval):
        while self.running:
            self.capture_once()
            time.sleep(interval)

    def start_auto(self, interval=5):
        if self.running:
            return False
        self.running = True
        self.thread = threading.Thread(target=self._loop, args=(interval,), daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
