import ctypes
from ctypes import wintypes as wt
from ctypes import sizeof
from time import sleep, time
import string
import pytesseract
from PIL import Image
import PIL
from PIL.ImageGrab import grab as screenshot

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002 
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_VIRTUALDESK = 0x4000

ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)
LONG = ctypes.c_long

# These depend on whether UNICODE is defined
LPCTSTR = wt.LPCSTR  # LPCWSTR or LPCSTR
LPTSTR = wt.LPSTR  # LPWSTR or LPSTR

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', wt.WORD),
        ('wScan', wt.WORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwextraInfo", ULONG_PTR)
    ]
    
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', LONG),
        ('dy', LONG),
        ('mouseData', wt.DWORD),
        ('dwFlags', wt.DWORD),
        ('time', wt.DWORD),
        ('dwExtraInfo', ULONG_PTR),
    ]
    
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ('uMsg', wt.DWORD),
        ('wParamL', wt.WORD),
        ('wParamH', wt.WORD)
    ]
    

class InptUnion(ctypes.Union):
    _fields_ = [
        ('mi', MOUSEINPUT),
        ('ki', KEYBDINPUT),
        ('hi', HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ('type', wt.DWORD),
        ('ip', InptUnion)
    ]
    
PINPUT = ctypes.POINTER(INPUT)

KEYEVENTF_KEYUP = 0x0002

def make_kb_input(keycode, scan_code=0, flags=0):
    ip = INPUT()
    ip.type = INPUT_KEYBOARD
    
    ki = KEYBDINPUT()
    ki.wVk = keycode
    ki.wScan = scan_code
    ki.dwFlags = flags
    
    ip.ip.ki = ki
    return ip    

KEYCODES = {}
for i in range(10):
    KEYCODES[str(i)] = 0x30 + i
    
for i, key in enumerate(string.ascii_lowercase):
    KEYCODES[key] = 0x41 + i

# Raw exported windows API functions

user32 = ctypes.windll.user32
k32 = ctypes.windll.kernel32

_SendInput = user32.SendInput
_SendInput.argtypes = [wt.UINT, PINPUT, ctypes.c_int]
_SendInput.restype = wt.UINT

def SendInput(*args):
    res = _SendInput(*args)
    if not res:
        raise OSError(k32.GetLastError())
    return res

FindWindow = user32.FindWindowA
FindWindow.argtypes = [LPCTSTR, LPCTSTR]
FindWindow.restype = wt.HWND

CloseHandle = k32.CloseHandle
CloseHandle.argtypes = [wt.HANDLE]
CloseHandle.restype = wt.BOOL

EnumWindows = user32.EnumWindows
EnumWindows.argtypes = [WNDENUMPROC, wt.LPARAM]
EnumWindows.restype = wt.BOOL

GetWindowText = user32.GetWindowTextA
GetWindowText.argtypes = [wt.HWND, LPTSTR, ctypes.c_int]
GetWindowText.restype = ctypes.c_int

SetActiveWindow = user32.SetActiveWindow
SetActiveWindow.argtypes = [wt.HWND]
SetActiveWindow.restype = wt.HWND

SetForegroundWindow = user32.SetForegroundWindow
SetForegroundWindow.argtypes = [wt.HWND]
SetForegroundWindow.restype = wt.BOOL

GetLastError = k32.GetLastError
GetLastError.argtypes = []
GetLastError.restype = ctypes.c_int

def make_mouse_move(x,y):
    return _mouse_event(x, y, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK)

def make_mouse_left_click(dwFlags):
    return _mouse_event(0, 0, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | dwFlags)

import win32api, math
SCREEN_X = win32api.GetSystemMetrics(78)
SCREEN_Y = win32api.GetSystemMetrics(79)

def norm(x, y):
    return math.ceil(x / (SCREEN_X) * 65535), math.ceil(y / (SCREEN_Y) * 65536)

def denorm(x,y):
    return math.floor((x / 65535) * SCREEN_X), math.floor((y / 65536) * SCREEN_Y)

def _mouse_event(x, y, flags):
    x = int(x)
    y = int(y)
    ip = INPUT()
    ip.type = INPUT_MOUSE
    mi = MOUSEINPUT()
    mi.dx = x
    mi.dy = y
    mi.mouseData = mi.time = 0
    mi.dwFlags = flags
    ip.ip.mi = mi
    return ip

def drag(x1, y1, x2, y2, delay=0.01):
    ip1 = _mouse_event(x1, y1, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN)
    ip2 = _mouse_event(x2, y2, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_MOVE)
    ip3 = _mouse_event(0, 0, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_LEFTUP)
    rv = 0
    rv += send_inputs(ip1)
    sleep(delay)
    rv += send_inputs(ip2)
    sleep(delay)
    rv += send_inputs(ip3)
    sleep(delay)
    return rv
    
def left_click(x,y):
    
    ip1 = _mouse_event(x, y, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN)
    
    ip2 = _mouse_event(0, 0, MOUSEEVENTF_LEFTUP)
    
    sz = ctypes.sizeof(ip1)
    arr = (INPUT * 2)(ip1, ip2)
    rv = SendInput(2, arr, sz)
    return rv
    
def _depr_left_click(x,y):
    ip1 = INPUT()
    ip1.type = INPUT_MOUSE
    
    x = int(x)
    y = int(y)
    
    mi = MOUSEINPUT()
    mi.dx = x
    mi.dy = y
    mi.mouseData = mi.time = 0
    mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN
    ip1.ip.mi = mi
    
    ip2 = INPUT()
    ip2.type = INPUT_MOUSE
    
    mi = MOUSEINPUT()
    mi.dx = 0
    mi.dy = 0
    mi.mouseData = mi.time = 0
    mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_LEFTUP
    ip2.ip.mi = mi
    
    sz = ctypes.sizeof(ip1)
    arr = (INPUT * 2)(ip1, ip2)
    rv = SendInput(2, arr, sz)
    return rv

def send_keyboard_input(keycode, scan_code=0):
    ip1 = make_kb_input(keycode, scan_code, 0)
    ip2 = make_kb_input(keycode, scan_code, KEYEVENTF_KEYUP)
    return send_inputs(ip1, ip2)

def send_key(key):
    vk = KEYCODES[key]
    send_keyboard_input(vk, 0)

def mouse_move(x,y):
    ip = make_mouse_move(x,y)
    return SendInput(1, PINPUT(ip), ctypes.sizeof(ip))
    
def mouse_click():
    ip2 = make_mouse_left_click(MOUSEEVENTF_LEFTDOWN)
    ip3 = make_mouse_left_click(MOUSEEVENTF_LEFTUP)
    send_inputs(ip2, ip3)

def send_inputs(*ips):
    sz = ctypes.sizeof(ips[0])
    array = (INPUT * len(ips))(*ips)
    return SendInput(len(ips), array, sz)

def get_pos(normalize=True):
    x, y = win32api.GetCursorPos()
    if normalize:
        x, y = norm(x, y)
    return x,y

def clickfind():
    down = False
    while True:
        try:
            sleep(0.01)
            print("\r    (%d, %d),"%get_pos(), end="")
            if win32api.GetKeyState(0xC0) & 0x8000:
                if not down:
                    print()
                    down = True
            else:
                down = False
        except:
            break
            

def right_click_down():
    return win32api.GetKeyState(0x02) & 0x8000

def wait(s):
    end = time() + s
    while True:
        left = end - time()
        if left > 0:
            sleep(min(left, 0.1))
        else:
            break


# If screen resolution affects these (it probably does), then I need a 3 point calibration to 
# scale all coordinates...

OFFSET_X = 0
OFFSET_Y = 0
REF_X = 8450
REF_Y = 20607

def get_offset():
    global OFFSET_X, OFFSET_Y
    while True:
        if right_click_down():
            x,y = get_pos()
            OFFSET_X = x - REF_X
            OFFSET_Y = y - REF_Y
            break
    sleep(0.01)
    
def translate_coord(x,y):
    return x + OFFSET_X, y + OFFSET_Y

cpu1 = {
    'basic_training': (8407, 20753),
    'blood_magic': (8429, 38010),
    'idle_cap': (23109, 27597)
}

def get_pos_by_click():
    down = False
    while True:
        if right_click_down() and not down:
            down = True
        elif not right_click_down() and down:
            return get_pos()
        wait(0.1)

SCALE_Y = 1
SCALE_X = 1
OX = 0
OY = 0
X1 = 0
Y1 = 0
        
def get_scales():
    global SCALE_Y, SCALE_X, OX, OY, X1, Y1
    x2, y2 = get_pos_by_click()
    x4, y4 = get_pos_by_click()
    x6, y6 = get_pos_by_click()
    X1, Y1 = cpu1['basic_training']
    x3, y3 = cpu1['blood_magic']
    x5, y5 = cpu1['idle_cap']
    SCALE_Y = (y4 - y2) / (y3 - Y1)
    SCALE_X = (x6 - x2) / (x5 - X1)
    OX = x2 - X1
    OY = y2 - Y1
    
def translate_coord2(x, y):
    return math.floor(X1 + (x-X1) * SCALE_X + OX), math.floor(Y1 + (y-Y1) * SCALE_Y + OY)
    
def hms(s):
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return "%02d:%02d:%02d"%(h, m, s)

def find_btn_coords(features):
    coords = []
    for f in features:
        print("(%r, "%f, end="")
        while True:
            if right_click_down():
                if not down:
                    down = True
                    p = get_pos()
                    coords.append(p)
                    print("(%d, %d)),"%p)
                    break
            else:
                down = False
            sleep(0.1)
                
def find_bbox_coords(features):
    down = False
    for f in features:
        print("(%r, "%f, end="")
        while True:
            if right_click_down():
                if not down:
                    down = True
                    top, left = get_pos(False)
            else:
                if down:
                    down = False
                    bottom, right = get_pos(False)
                    print("(%d, %d, %d, %d)),"%(top, left, bottom, right))
                    break
            sleep(0.1)