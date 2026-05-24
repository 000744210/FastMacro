import ctypes
import os
import sys
import queue
import random
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from ctypes import wintypes
except Exception:
    raise RuntimeError("This script is Windows-only.")

if os.name != "nt":
    raise RuntimeError("This script is Windows-only.")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


user32.SetWindowsHookExW.argtypes = (
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD
)
user32.SetWindowsHookExW.restype = ctypes.c_void_p

user32.CallNextHookEx.argtypes = (
    ctypes.c_void_p,
    ctypes.c_int,
    wintypes.WPARAM,
    wintypes.LPARAM
)
user32.CallNextHookEx.restype = wintypes.LPARAM

winmm = ctypes.windll.winmm

winmm.timeBeginPeriod.argtypes = (wintypes.UINT,)
winmm.timeBeginPeriod.restype = wintypes.UINT

winmm.timeEndPeriod.argtypes = (wintypes.UINT,)
winmm.timeEndPeriod.restype = wintypes.UINT

# ----------------------------------------------------------------------
# SendInput structures
# ----------------------------------------------------------------------
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MAPVK_VK_TO_VSC = 0

ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]

user32.SendInput.argtypes = (
    wintypes.UINT,
    ctypes.POINTER(INPUT),
    ctypes.c_int
)

user32.SendInput.restype = wintypes.UINT


# ----------------------------------------------------------------------
# Win32 constants
# ----------------------------------------------------------------------
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
HC_ACTION = 0

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C
WM_MOUSEHWHEEL = 0x020E

LLKHF_EXTENDED = 0x01
LLKHF_INJECTED = 0x10
LLKHF_ALTDOWN = 0x20
LLKHF_UP = 0x80

LLMHF_INJECTED = 0x00000001

MOUSEEVENTF_ABSOLUTE = 0x8000

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x01000

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

#For touchMask
TOUCH_MASK_NONE=          0x00000000 #Default
TOUCH_MASK_CONTACTAREA=   0x00000001
TOUCH_MASK_ORIENTATION=   0x00000002
TOUCH_MASK_PRESSURE=      0x00000004
TOUCH_MASK_ALL=           0x00000007

#For touchFlag
TOUCH_FLAG_NONE=          0x00000000

#For pointerType
PT_POINTER=               0x00000001#All
PT_TOUCH=                 0x00000002
PT_PEN=                   0x00000003
PT_MOUSE=                 0x00000004

#For pointerFlags
POINTER_FLAG_NONE=        0x00000000#Default
POINTER_FLAG_NEW=         0x00000001
POINTER_FLAG_INRANGE=     0x00000002
POINTER_FLAG_INCONTACT=   0x00000004
POINTER_FLAG_FIRSTBUTTON= 0x00000010
POINTER_FLAG_SECONDBUTTON=0x00000020
POINTER_FLAG_THIRDBUTTON= 0x00000040
POINTER_FLAG_FOURTHBUTTON=0x00000080
POINTER_FLAG_FIFTHBUTTON= 0x00000100
POINTER_FLAG_PRIMARY=     0x00002000
POINTER_FLAG_CONFIDENCE=  0x00004000
POINTER_FLAG_CANCELED=    0x00008000
POINTER_FLAG_DOWN=        0x00010000
POINTER_FLAG_UPDATE=      0x00020000
POINTER_FLAG_UP=          0x00040000
POINTER_FLAG_WHEEL=       0x00080000
POINTER_FLAG_HWHEEL=      0x00100000
POINTER_FLAG_CAPTURECHANGED=0x00200000





VK_NAMES = {
    # letters
    **{chr(c): c for c in range(ord("A"), ord("Z") + 1)},
    # digits
    **{str(d): 0x30 + d for d in range(10)},

    # common controls
    "Space": 0x20,
    "Enter": 0x0D,
    "Tab": 0x09,
    "BackSpace": 0x08,
    "Delete": 0x2E,
    "Escape": 0x1B,
    "Up": 0x26,
    "Down": 0x28,
    "Left": 0x25,
    "Right": 0x27,
    "Home": 0x24,
    "End": 0x23,
    "PgUp": 0x21,
    "PgDn": 0x22,
    "Insert": 0x2D,
    "LShift": 0xA0,
    "RShift": 0xA1,
    "LCtrl": 0xA2,
    "RCtrl": 0xA3,
    "LAlt": 0xA4,
    "RAlt": 0xA5,
    "LWin": 0x5B,
    "RWin": 0x5C,

    # punctuation / OEM keys
    ",": 0xBC,
    ".": 0xBE,
    "/": 0xBF,
    ";": 0xBA,
    "'": 0xDE,
    "[": 0xDB,
    "]": 0xDD,
    "\\": 0xDC,
    "-": 0xBD,
    "=": 0xBB,
    "`": 0xC0,

    # function keys
    **{f"F{i}": 0x6F + i for i in range(1, 13)},

    # numpad
    "Numpad0": 0x60,
    "Numpad1": 0x61,
    "Numpad2": 0x62,
    "Numpad3": 0x63,
    "Numpad4": 0x64,
    "Numpad5": 0x65,
    "Numpad6": 0x66,
    "Numpad7": 0x67,
    "Numpad8": 0x68,
    "Numpad9": 0x69,
    "NumpadDot": 0x6E,
    "NumpadDiv": 0x6F,
    "NumpadMult": 0x6A,
    "NumpadAdd": 0x6B,
    "NumpadSub": 0x6D,
    "NumpadEnter": 0x0D,

    # misc
    "PrintScreen": 0x2C,
    "ScrollLock": 0x91,
    "Pause": 0x13,
    "CapsLock": 0x14,
    "NumLock": 0x90,
}

VK_TO_NAME = {vk: name for name, vk in VK_NAMES.items()}

HOTKEY_NAMES = {f"F{i}" for i in range(1, 10)}

MOUSE_BUTTON_NAMES = {
    WM_LBUTTONDOWN: "LButton",
    WM_LBUTTONUP: "LButton",
    WM_RBUTTONDOWN: "RButton",
    WM_RBUTTONUP: "RButton",
    WM_MBUTTONDOWN: "MButton",
    WM_MBUTTONUP: "MButton",
    WM_XBUTTONDOWN: None,  # resolved from mouseData
    WM_XBUTTONUP: None,
}

# ----------------------------------------------------------------------
# Win32 structures
# ----------------------------------------------------------------------
class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


class POINTER_INFO(ctypes.Structure):
    _fields_=[("pointerType",ctypes.c_uint32),
              ("pointerId",ctypes.c_uint32),
              ("frameId",ctypes.c_uint32),
              ("pointerFlags",ctypes.c_int),
              ("sourceDevice",wintypes.HANDLE),
              ("hwndTarget",wintypes.HWND),
              ("ptPixelLocation",POINT),
              ("ptHimetricLocation",POINT),
              ("ptPixelLocationRaw",POINT),
              ("ptHimetricLocationRaw",POINT),
              ("dwTime",wintypes.DWORD),
              ("historyCount",ctypes.c_uint32),
              ("inputData",ctypes.c_int32),
              ("dwKeyStates",wintypes.DWORD),
              ("PerformanceCount",ctypes.c_uint64),
              ("ButtonChangeType",ctypes.c_int)
              ]


class POINTER_TOUCH_INFO(ctypes.Structure):
    _fields_=[("pointerInfo",POINTER_INFO),
              ("touchFlags",ctypes.c_int),
              ("touchMask",ctypes.c_int),
              ("rcContact", wintypes.RECT),
              ("rcContactRaw",wintypes.RECT),
              ("orientation", ctypes.c_uint32),
              ("pressure", ctypes.c_uint32)]



#Initialize Pointer and Touch info

pointerInfo=POINTER_INFO(pointerType=PT_TOUCH,
                         pointerId=0,
                         ptPixelLocation=POINT(950,540))

touchInfo=POINTER_TOUCH_INFO(pointerInfo=pointerInfo,
                             touchFlags=TOUCH_FLAG_NONE,
                             touchMask=TOUCH_MASK_ALL,
                             rcContact=wintypes.RECT(pointerInfo.ptPixelLocation.x-5,
                                  pointerInfo.ptPixelLocation.y-5,
                                  pointerInfo.ptPixelLocation.x+5,
                                  pointerInfo.ptPixelLocation.y+5),
                             orientation=90,
                             pressure=32000)




LowLevelKeyboardProc = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
LowLevelMouseProc = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# ----------------------------------------------------------------------
# Win32 helpers
# ----------------------------------------------------------------------

#def tick_count() -> int:
#    return int(kernel32.GetTickCount64())

_qpc_freq = ctypes.c_int64()
kernel32.QueryPerformanceFrequency(ctypes.byref(_qpc_freq))

def tick_count() -> float:
    val = ctypes.c_int64()
    kernel32.QueryPerformanceCounter(ctypes.byref(val))
    return val.value * 1000.0 / _qpc_freq.value  # ms as float

def set_cursor_pos(x: int, y: int) -> None:
    user32.SetCursorPos(int(x), int(y))



EXTENDED_KEYS = {
    0x21, # Page Up
    0x22, # Page Down
    0x23, # End
    0x24, # Home
    0x25, # Left
    0x26, # Up
    0x27, # Right
    0x28, # Down
    0x2D, # Insert
    0x2E, # Delete
    0x6F, # Numpad Divide
    0x90, # NumLock
    0xA3, # Right Ctrl
    0xA5, # Right Alt
}

def keybd_event(vk: int, key_up: bool = False) -> None:
    flags = 0

    if key_up:
        flags |= KEYEVENTF_KEYUP

    if vk in EXTENDED_KEYS:
        flags |= KEYEVENTF_EXTENDEDKEY

    scan = user32.MapVirtualKeyW(vk, 0)

    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki = KEYBDINPUT(
        wVk=vk,
        wScan=scan,
        dwFlags=flags,
        time=0,
        dwExtraInfo=None
    )

    user32.SendInput(
        1,
        ctypes.byref(inp),
        ctypes.sizeof(INPUT)
    )


def mouse_event(flags: int, dx: int = 0, dy: int = 0, data: int = 0) -> None:
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.union.mi = MOUSEINPUT(
        dx=dx,
        dy=dy,
        mouseData=data,
        dwFlags=flags,
        time=0,
        dwExtraInfo=None
    )

    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def touchDown(x, y, fingerRadius=9):
    touchInfo.pointerInfo.ptPixelLocation.x = x
    touchInfo.pointerInfo.ptPixelLocation.y = y
    touchInfo.rcContact.left = x - fingerRadius
    touchInfo.rcContact.right = x + fingerRadius
    touchInfo.rcContact.top = y - fingerRadius
    touchInfo.rcContact.bottom = y + fingerRadius

    if (ctypes.windll.user32.InitializeTouchInjection(1, 1) != 0):
        print("Initialized Touch Injection")

    touchInfo.pointerInfo.pointerFlags = (POINTER_FLAG_DOWN |
                                          POINTER_FLAG_INRANGE |
                                          POINTER_FLAG_INCONTACT)
    if (ctypes.windll.user32.InjectTouchInput(1, ctypes.byref(touchInfo)) == 0):
        print("Failed with Error: " + ctypes.FormatError())
    else:
        print("Touch Down Succeeded!")


def touchUp():
    touchInfo.pointerInfo.pointerFlags = POINTER_FLAG_UP
    if (ctypes.windll.user32.InjectTouchInput(1, ctypes.byref(touchInfo)) == 0):
        print("Failed with Error: " + ctypes.FormatError())
    else:
        print("Pull Up Succeeded!")


def touchMove(x, y, fingerRadius=4):
    touchInfo.pointerInfo.ptPixelLocation.x = x
    touchInfo.pointerInfo.ptPixelLocation.y = y
    touchInfo.rcContact.left = x - fingerRadius
    touchInfo.rcContact.right = x + fingerRadius
    touchInfo.rcContact.top = y - fingerRadius
    touchInfo.rcContact.bottom = y + fingerRadius

    touchInfo.pointerInfo.pointerFlags = (POINTER_FLAG_UPDATE |
                                          POINTER_FLAG_INRANGE |
                                          POINTER_FLAG_INCONTACT)
    if (ctypes.windll.user32.InjectTouchInput(1, ctypes.byref(touchInfo)) == 0):
        print("Failed with Error: " + ctypes.FormatError())
    else:
        print("Touch Move Succeeded!")
    
# This sleeps for the exact amount of seconds. Normal sleep can overshoot/undershoot the duration so we stop a bit early to busywait the last remaining 4ms.
def sleep_spin(duration_ms: float, stop_event=None) -> None:
    target = tick_count() + duration_ms
    coarse = duration_ms - 4
    if coarse > 0:
        time.sleep(coarse / 1000.0)
    while tick_count() < target:
        pass 
# ----------------------------------------------------------------------
# App
# ----------------------------------------------------------------------

# takes the current executable path and makes it so all mcr files open using it.
# This keeps the executable portable with the feature an installer would have.
def register_mcr_filetype():

    try:
        import winreg
        
        
        exe_path = os.path.abspath(sys.argv[0])
        if not exe_path[-3:] == "exe":
            return 0 # running in python mode. skip
        # .mcr -> FastMacroFile
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.mcr") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "FastMacroFile")

        # FastMacroFile description
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\FastMacroFile") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "FastMacro Macro File")

        # Open command
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\FastMacroFile\shell\open\command"
        ) as key:
            command = f'"{exe_path}" "%1"'
            winreg.SetValue(key, "", winreg.REG_SZ, command)

        print(".mcr association registered.")

    except Exception as e:
        print("Failed to register file type:", e)



# not a virus payload. Used to embed an app icon in the application.
appIcon = "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAMAAAAp4XiDAAAAQlBMVEUAAAAYIjcaJjcdKT0VITQTHjAQGiz09fjN2eKhtcRJvvd/h5MdpPxTlLkcg8pOYnYeZpkyQFIVQ2kXJjwUIDUOGitxQC95AAAAB3RSTlMAGUhcl9Df9+2+tgAAAgpJREFUeNqlltGSqyAQRNeouyAKDD3z/796ZyJriMbkWntSFD5w7J6iUsnXX+hu/Rtu3UG4DSPeMg6354QBzPjE0DXGyAY+MXZXDfCWM3Dlg6D0NeSbN4DNa97BUNio1Xr+L8CPmJEvMNThNyithB0JXBm73Sh5mrx3zv3s8AflmLJTAr9WQBt7hV4riJPyspjHiVKyoa2q4RJVwCfFRLFyqSpBNs4UBmPxfqtFv8eJzhQAnJYlBL/2qlfCWKaF5Ki0kGtHZ5qUdFAEOca4KN77xrCJymRkSKPIs/LzRJI83YmlVYym1u5K4lTJjbJh09eUQHcgiPPKFLFXAF6mbRKSSpkrsQjLIYUBrMUcdkosLEqjoBhJCe756vNsZIjslBKVadruPm3Bce0kB4WLQaQZz70Qa6e9YqBRvDwU63Si5PlRLEnLqVLs2xLuJHxSLtAolFIiqTCECzS3vFO88z4xWGwFz2XOYgu8voFZgCcFLhDI+0BeVedSmSPinHOMpejK8f7YKuScCzq7C7qRS6wHsh3NuhW1cjGvVZKzkOA92XIksagQ8/0DVVAi59wqwVtS8EGNoA+IyLlmRJMZuuFXGUXW0YgAJrKHdWIwAEFhhtgmqnwZg1xguCv9BYNv9df12uUbPV8KuTQN91Uwh68ZRj9+FkZt1dL1w/h9zjgOffd1oHvLn/64/QNKeoVd0OWtkAAAAABJRU5ErkJggg=="
class MacroRecorderApp:
    def __init__(self,opened_file) -> None:
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.title("Macro Recorder")
        self.root.geometry("320x296")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#0e0e17")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Map>", self._on_restore)
        self.root.iconphoto(False,tk.PhotoImage(data=appIcon))

        self.recording = False
        self.replaying = False
        self.loop_replay = False
        self.record_paused = False
        self.paused_at = 0
        self.paused_total = 0
        self.actions = []
        self.start_time = 0
        self.held_keys = set()
        self.recent_files = []
        self._replay_start_tick  = 0.0
        self._replay_loop_count  = 0
        self._replay_repeat_total = 1

        self.lock = threading.RLock()
        self.queue = queue.Queue()
        self.stop_replay_event = threading.Event()
        self.replay_mouse_thread = None

        self.hook_thread = None
        self.hook_thread_id = None
        self._kb_hook = None
        self._mouse_hook = None
        self._keyboard_proc_ref = LowLevelKeyboardProc(self._keyboard_proc)
        self._mouse_proc_ref = LowLevelMouseProc(self._mouse_proc)


        
        state = AppStateManager("FastMacro.ini")
        self.state = state
        self.recent_files = state.get_list("core","recent_files",fallback=[])
        self.loop_replay = state.get_int("core","loop_active",fallback=0)
        self.repeat_count = state.get("core","repeat_count",fallback="1")
        self.speed_index = state.get_int("core","speed_index",fallback=4) # 4 = x1 speed
        
        self.record_mouse_inputs = state.get_int("settings","record_mouse_inputs",fallback=1)
        self.record_keyboard_inputs = state.get_int("settings","record_keyboard_inputs",fallback=1)
        self.use_touch_api = state.get_int("settings","use_touch_api",fallback=0)
        self.minimize_on_run = state.get_int("settings","minimize_on_run", fallback=0)
        
        self._build_ui()
        
        self._start_hook_thread()
        self._schedule_queue_pump()
        self._schedule_refresh()
        
        if opened_file:
            self.actions = self.parse_file(opened_file)
            self._add_recent(opened_file)
        
        self.refresh_gui()
        self._refresh_recent_buttons()
    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        W         = 320
        H_IDLE    = 266
        H_COMPACT = 96
        self._W        = W
        self._H_IDLE   = H_IDLE
        self._H_COMPACT= H_COMPACT

        # -- Palette --------------------------------------------------
        BG      = "#0e0e17"
        SURF    = "#161622"
        SURF2   = "#1c1c2e"
        BORDER  = "#24243a"
        TEXT    = "#dde0ff"
        MUTED   = "#4a4a6a"
        MUTED2  = "#7070a0"
        C_REC   = "#ff4560"
        C_PLAY  = "#00e096"
        C_PAUSE = "#ffb300"
        C_UI    = "#4fa8ff"

        self._BG    = BG
        self._SURF  = SURF
        self._SURF2 = SURF2
        self._TEXT  = TEXT
        self._MUTED = MUTED
        self._MUTED2= MUTED2
        self._C_REC = C_REC
        self._C_PLAY= C_PLAY
        self._C_PAUSE = C_PAUSE



        # Recording filter state (referenced by Settings popup)
        self._moves_var = tk.IntVar(value=self.record_mouse_inputs)
        self._keys_var  = tk.IntVar(value=self.record_keyboard_inputs)

        # Behaviour settings
        self._minimize_on_run_var = tk.IntVar(value=self.minimize_on_run)
        self._use_touch_var = tk.IntVar(value=self.use_touch_api)
        
        def _on_settings_change(*args):
            self.state.set("settings","record_mouse_inputs",self._moves_var.get())
            self.state.set("settings","record_keyboard_inputs",self._keys_var.get())
            self.state.set("settings","use_touch_api",self._use_touch_var.get())
            self.state.set("settings","minimize_on_run",self._minimize_on_run_var.get())
            self.state.save()
        
        self._moves_var.trace_add("write", _on_settings_change)
        self._keys_var.trace_add("write", _on_settings_change)
        self._minimize_on_run_var.trace_add("write", _on_settings_change)
        self._use_touch_var.trace_add("write", _on_settings_change)
        
        
        self._touch_mode = False       # plain bool, safe to read from hook thread
        self._touch_is_down = False    # tracks whether a touch contact is active



        root = self.root
        root.configure(bg=BG)
        root.geometry(f"{W}x{H_IDLE}")

        # -------------------------------------------------------------
        # Status bar. Used as the title bar for the borderless mode.
        # -------------------------------------------------------------

        # Status bar
        self.status_bar = tk.Frame(root, bg=SURF2)
        self.status_bar.place(x=0, y=0, width=W, height=34)

        self._dot_canvas = tk.Canvas(
            self.status_bar,
            width=10,
            height=10,
            bg=SURF2,
            highlightthickness=0,
            bd=0
        )

        self._dot_canvas.place(x=11, y=11)

        self._dot_oval = self._dot_canvas.create_oval(
            1, 1, 9, 9,
            fill=MUTED,
            outline=""
        )
        self.status_label = tk.Label(
            self.status_bar, text="IDLE",
            bg=SURF2, fg=TEXT,
            font=("Segoe UI", 9, "bold"), anchor="w")
        self.status_label.place(x=26, y=0, width=180, height=34)

        self._timer_label = tk.Label(
            self.status_bar, text="",
            bg=SURF2, fg=MUTED2,
            font=("Consolas", 9), anchor="e")
        self._timer_label.place(x=140, y=0, width=106, height=34)

        # Progress bar - 2px strip at very bottom of status bar, replay only
        self._progress_canvas = tk.Canvas(
            self.status_bar, height=2, bg=SURF2, highlightthickness=0)
        self._progress_canvas.place(x=0, y=32, width=W, height=2)
        self._progress_bar = self._progress_canvas.create_rectangle(
            0, 0, 0, 2, fill=C_PLAY, outline="")

        # Stats row
        stats = tk.Frame(root, bg=BG)
        stats.place(x=0, y=34, width=W, height=32)

        tk.Label(stats, text="ACTIONS", bg=BG, fg=MUTED,
                 font=("Segoe UI", 6, "bold"), anchor="center").place(x=12, y=2, width=90, height=10)
        self.action_count = tk.Label(stats, text="0", bg=BG, fg=TEXT,
                                      font=("Consolas", 13, "bold"), anchor="center")
        
        self.action_count.place(x=12, y=14, width=90, height=16)

        tk.Label(stats, text="DURATION", bg=BG, fg=MUTED,
                 font=("Segoe UI", 6, "bold"), anchor="center").place(x=106, y=2, width=110, height=10)
        self._dur_label = tk.Label(stats, text="0.0 s", bg=BG, fg=TEXT,
                                    font=("Consolas", 13, "bold"), anchor="center")
        self._dur_label.place(x=106, y=14, width=110, height=16)

        # Loop counter - shown during replay only
        self._loop_hdr_label = tk.Label(stats, text="LOOP", bg=BG, fg=MUTED,
                                         font=("Segoe UI", 6, "bold"))
        self._loop_hdr_label.place(x=236, y=2, width=76, height=10)
        self._loop_count_label = tk.Label(stats, text="", bg=BG, fg=C_PLAY,
                                           font=("Consolas", 13, "bold"), anchor="center")
        self._loop_count_label.place(x=236, y=14, width=76, height=16)

        # Separator
        tk.Frame(root, bg=BORDER).place(x=0, y=66, width=W, height=1)

        # -------------------------------------------------------------
        # COMPACT FRAME  (replaces idle frame during record / replay)
        # -------------------------------------------------------------
        self._compact_frame = tk.Frame(root, bg=BG)

        # -- Recording compact row --
        self._compact_rec = tk.Frame(self._compact_frame, bg=BG)
        self._compact_rec.place(x=0, y=0, width=W, height=26)

        tk.Button(self._compact_rec, text="Stop  F2",
                  command=self.stop_or_stopreplay,
                  font=("Segoe UI", 8), bg=SURF, fg=TEXT,
                  relief="flat", bd=0, activebackground=SURF2,
                  activeforeground=TEXT, cursor="hand2"
                  ).place(x=8, y=0, width=148, height=26)

        self._compact_pause_btn = tk.Button(
            self._compact_rec, text="Pause  F8",
            command=self.toggle_pause_recording,
            font=("Segoe UI", 8), bg=SURF, fg=TEXT,
            relief="flat", bd=0, activebackground=SURF2,
            activeforeground=TEXT, cursor="hand2")
        self._compact_pause_btn.place(x=160, y=0, width=152, height=26)

        # -- Replaying compact row --
        self._compact_rep = tk.Frame(self._compact_frame, bg=BG)
        self._compact_rep.place(x=0, y=0, width=W, height=26)

        tk.Button(self._compact_rep, text="Stop  F4",
                  command=self.stop_replay,
                  font=("Segoe UI", 8), bg=SURF, fg=TEXT,
                  relief="flat", bd=0, activebackground=SURF2,
                  activeforeground=TEXT, cursor="hand2"
                  ).place(x=8, y=0, width=304, height=26)

        # -------------------------------------------------------------
        # IDLE FRAME  (full controls, hidden during record / replay)
        # -------------------------------------------------------------
        self._idle_frame = tk.Frame(root, bg=BG)

        IF = self._idle_frame   # shorthand

        def place_btn(parent, x, y, w, h, text, cmd, bg=SURF, fg=TEXT):
            b = tk.Button(parent, text=text, command=cmd,
                          font=("Segoe UI", 8), bg=bg, fg=fg,
                          relief="flat", bd=0,
                          activebackground=SURF2, activeforeground=TEXT,
                          cursor="hand2")
            b.place(x=x, y=y, width=w, height=h)
            return b

        def sep(parent, y):
            tk.Frame(parent, bg=BORDER).place(x=0, y=y, width=W, height=1)

        def slbl(parent, text, x, y, color=MUTED2):
            tk.Label(parent, text=text, bg=BG, fg=color,
                     font=("Segoe UI", 6, "bold")).place(x=x, y=y, width=90, height=10)

        # RECORDING
        slbl(IF, "RECORD", 0, 4, C_REC)

        place_btn(IF,   8, 16,  73, 24, "Record  F1", self.start_recording,
                  bg="#1a080e", fg=C_REC)
        place_btn(IF,  85, 16,  73, 24, "Stop  F2",   self.stop_or_stopreplay)
        place_btn(IF, 162, 16,  73, 24, "Pause  F8",  self.toggle_pause_recording)
        place_btn(IF, 239, 16,  73, 24, "Append  F9", self.start_append_recording)

        sep(IF, 44)

        #PLAYBACK 
        slbl(IF, "PLAYBACK", 0, 48, C_PLAY)

        # Play + Stop each take half the row 
        place_btn(IF,   8, 60, 148, 24, "Play  F3", self.start_replay,
                  bg="#001a10", fg=C_PLAY)
        place_btn(IF, 160, 60, 148, 24, "Stop  F4", self.stop_replay)

        # SPEED + LOOP row
        #slbl(IF, "SPEED", 8, 90)
        tk.Label(IF, text="SPEED", bg=BG, fg=MUTED2,
                     font=("Segoe UI", 6, "bold"),anchor="center").place(x=8, y=90, width=120, height=10)
        SPEEDS = [0.1,0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0,5.0,6.0,7.0,8.0,9.0,10.0,12.0,15.0,20.0,30.0,40.0,50.0,60.0,70.0,80.0,90.0,100.0]
        self._speeds    = SPEEDS
        self._speed_idx = self.speed_index

        def spd_dec():
            self._speed_idx = max(0, self._speed_idx - 1)
            _upd_spd()
        def spd_inc():
            self._speed_idx = min(len(SPEEDS) - 1, self._speed_idx + 1)
            _upd_spd()
        def _upd_spd():
            self.state.set("core","speed_index",self._speed_idx)
            self.state.save()
            self._spd_lbl.config(text=f"{SPEEDS[self._speed_idx]:g}×")
            

        place_btn(IF,  8, 102, 28, 22, "<", spd_dec, bg=SURF2, fg=MUTED2)
        self._spd_lbl = tk.Label(IF, text="1.0×", bg=SURF, fg=C_UI,
                                  font=("Consolas", 9, "bold"), anchor="center")
        self._spd_lbl.place(x=40, y=102, width=56, height=22)
        place_btn(IF, 100, 102, 28, 22, ">", spd_inc, bg=SURF2, fg=MUTED2)
        _upd_spd()
        # Loop - custom flat toggle button (no OS checkbox widget)
        self.loop_var = tk.IntVar(value=self.loop_replay) # loads from ini file
        self._loop_btn = tk.Button(IF, text="Loop", command=self._toggle_loop_btn,
                                    font=("Segoe UI", 8), bg=SURF2, fg=MUTED2,
                                    relief="flat", bd=0,
                                    activebackground=SURF, activeforeground=TEXT,
                                    cursor="hand2")
        self._loop_btn.place(x=140, y=102, width=52, height=22)
        
        # Repeat count - labelled properly; hidden when loop is active
        self._repeat_lbl = tk.Label(IF, text="REPEAT", bg=BG, fg=MUTED2,
                                     font=("Segoe UI", 6, "bold"))
        self._repeat_lbl.place(x=195, y=90, width=60, height=10)
        
        def _on_repeat_changed( *args):
            value = self._repeat_var.get()
            self.state.set("core","repeat_count",value)
            self.state.save()
            
        self._repeat_var = tk.StringVar(value=self.repeat_count)
        self._repeat_var.trace_add("write", _on_repeat_changed)
        self._repeat_entry = tk.Entry(IF, textvariable=self._repeat_var,
                                       bg=SURF, fg=TEXT, insertbackground=TEXT,
                                       relief="flat", font=("Consolas", 9),
                                       justify="center")
        self._repeat_entry.place(x=206, y=102, width=36, height=22)
        self._repeat_x_lbl = tk.Label(IF, text="×", bg=BG, fg=MUTED2,
                                       font=("Segoe UI", 8))
        self._repeat_x_lbl.place(x=246, y=104, width=12, height=16)
        
        sep(IF, 130)

        # ·· FILES ····················································
        # Save / Load share the row; Clear is muted (not red); Settings gone from here
        place_btn(IF,   8, 136, 100, 24, "Save  F6", self.save_to_file)
        place_btn(IF, 112, 136, 100, 24, "Load  F7", self.load_from_file)
        place_btn(IF, 216, 136,  96, 24, "Clear",    self.clear_recording,
                  bg=SURF2, fg=MUTED2)

        sep(IF, 166)

        # ·· RECENT ···················································
        tk.Label(IF, text="RECENT", bg=BG, fg=MUTED,
                 font=("Segoe UI", 6, "bold")).place(x=8, y=170, width=44, height=10)

        self._recent_btns = []
        for i in range(2):
            rb = tk.Button(IF, text="—",
                           command=lambda idx=i: self._load_recent(idx),
                           bg=BG, fg=MUTED2, relief="flat", bd=0,
                           font=("Segoe UI", 8), anchor="w",
                           activebackground=BG, activeforeground=TEXT,
                           cursor="hand2")
            rb.place(x=8 + i * 156, y=182, width=148, height=14)
            self._recent_btns.append(rb)

        # -- Initial layout -------------------------------------------
        self._idle_frame.place(x=0, y=68, width=W, height=H_IDLE - 68)

        # -- Window chrome buttons (right side of status bar) ---------
        # Layout from right: [×  26px] [4px] [–  26px] [4px] [...  24px] [4px]
        # Close
        self._close_btn = tk.Button(
            self.status_bar, text="×",
            command=self.on_close,
            font=("Segoe UI", 11), bg=SURF2, fg=MUTED2,
            relief="flat", bd=0,
            activebackground="#3a0a10", activeforeground="#ff4560",
            cursor="hand2")
        self._close_btn.place(x=W - 28, y=0, width=28, height=32)

        # Minimize
        self._min_btn = tk.Button(
            self.status_bar, text="–",
            command=self._minimize,
            font=("Segoe UI", 10), bg=SURF2, fg=MUTED2,
            relief="flat", bd=0,
            activebackground=SURF, activeforeground=TEXT,
            cursor="hand2")
        self._min_btn.place(x=W - 56, y=0, width=28, height=32)

        # Settings (sits left of minimize)
        self._settings_btn = tk.Button(
            self.status_bar, text="...",
            command=self._open_settings,
            font=("Segoe UI", 8), bg=SURF2, fg=MUTED2,
            relief="flat", bd=0,
            activebackground=SURF, activeforeground=TEXT,
            cursor="hand2")
        self._settings_btn.place(x=W - 82, y=5, width=22, height=20)

        # -- Drag to move (status bar is the window handle) -----------
        for widget in (self.status_bar, self.status_label,
                       self._dot_canvas, self._timer_label):
            widget.bind("<ButtonPress-1>",   self._drag_start)
            widget.bind("<B1-Motion>",        self._drag_motion)
            widget.bind("<ButtonRelease-1>",  self._drag_end)

        # -- Hotkeys --------------------------------------------------
        for key in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            root.bind_all(f"<{key}>", self._tk_hotkey_handler, add=True)
        
        self._sync_loop_btn()
        
    def _tk_hotkey_handler(self, event):
        # We keep actual hotkeys in the low-level keyboard hook.
        return "break"

    # -------------- hooks --------------
    def _start_hook_thread(self) -> None:
        self.hook_thread = threading.Thread(target=self._hook_thread_main, name="WinHooks", daemon=True)
        self.hook_thread.start()

    def _hook_thread_main(self) -> None:
        self.hook_thread_id = kernel32.GetCurrentThreadId()
        self._kb_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._keyboard_proc_ref, None, 0)
        self._mouse_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self._mouse_proc_ref, None, 0)
        if not self._kb_hook or not self._mouse_hook:
            self.queue.put(("error", "Failed to install global input hooks."))
            return

        msg = wintypes.MSG()
        while True:
            ret = user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
            if ret == 0:
                break
            if ret == -1:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self._kb_hook:
            user32.UnhookWindowsHookEx(self._kb_hook)
            self._kb_hook = None
        if self._mouse_hook:
            user32.UnhookWindowsHookEx(self._mouse_hook)
            self._mouse_hook = None
    def _keyboard_proc(self, nCode, wParam, lParam):
        if nCode == HC_ACTION:
            tick = tick_count()
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            injected = bool(kb.flags & LLKHF_INJECTED)
            is_up = wParam in (WM_KEYUP, WM_SYSKEYUP) or bool(kb.flags & LLKHF_UP)
            vk = int(kb.vkCode)
            name = VK_TO_NAME.get(vk)

            if injected:
                return user32.CallNextHookEx(self._kb_hook, nCode, wParam, lParam)

            if name in HOTKEY_NAMES:
                if not is_up:
                    self.queue.put(("hotkey", name,tick))
                return 1

            if name is not None:
                self.queue.put(("key", name, not is_up,tick))

        return user32.CallNextHookEx(self._kb_hook, nCode, wParam, lParam)
    def _mouse_proc(self, nCode, wParam, lParam):
       
        if nCode == HC_ACTION:
            tick = tick_count()
            ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            injected = bool(ms.flags & LLMHF_INJECTED)

            if injected:
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            if wParam in (
                WM_LBUTTONDOWN,
                WM_LBUTTONUP,
                WM_RBUTTONDOWN,
                WM_RBUTTONUP,
                WM_MBUTTONDOWN,
                WM_MBUTTONUP,
                WM_XBUTTONDOWN,
                WM_XBUTTONUP
            ):

                btn = None

                if wParam in (WM_LBUTTONDOWN, WM_LBUTTONUP):
                    btn = "LButton"

                elif wParam in (WM_RBUTTONDOWN, WM_RBUTTONUP):
                    btn = "RButton"

                elif wParam in (WM_MBUTTONDOWN, WM_MBUTTONUP):
                    btn = "MButton"

                elif wParam in (WM_XBUTTONDOWN, WM_XBUTTONUP):
                    xbtn = (ms.mouseData >> 16) & 0xFFFF
                    btn = "XButton1" if xbtn == 1 else "XButton2"

                if btn:
                    is_down = wParam in (
                        WM_LBUTTONDOWN,
                        WM_RBUTTONDOWN,
                        WM_MBUTTONDOWN,
                        WM_XBUTTONDOWN
                    )


                    self.queue.put((
                        "mouse",
                        btn,
                        is_down,
                        int(ms.pt.x),
                        int(ms.pt.y),
                        tick
                    ))
                    
                    if self._touch_mode and self.recording:
                        if is_down:
                            touchDown(int(ms.pt.x), int(ms.pt.y))
                            self._touch_is_down = True
                        else:
                            touchUp()
                            self._touch_is_down = False
                        return 1  # suppress the actual mouse click

            elif wParam in (WM_MOUSEWHEEL, WM_MOUSEHWHEEL):

                delta = ctypes.c_short(
                    (ms.mouseData >> 16) & 0xFFFF
                ).value

                if wParam == WM_MOUSEWHEEL:
                    direction = "WheelUp" if delta > 0 else "WheelDown"
                else:
                    direction = "WheelRight" if delta > 0 else "WheelLeft"

                self.queue.put((
                    "wheel",
                    direction,
                    int(ms.pt.x),
                    int(ms.pt.y),
                    tick
                ))

            elif wParam == WM_MOUSEMOVE:

                
                if self.recording:
                    self.queue.put((
                        "move",
                        int(ms.pt.x),
                        int(ms.pt.y),
                        tick
                    ))
                    
                    if self._touch_is_down:
                        touchMove(int(ms.pt.x),int(ms.pt.y))

        return user32.CallNextHookEx(
            None,
            nCode,
            wParam,
            lParam
        )

    # -------------- queue --------------
    def _schedule_queue_pump(self):
        self._pump_queue()
        self.root.after(50, self._schedule_queue_pump)

    def _pump_queue(self):
        while True:
            try:
                item = self.queue.get_nowait()
            except queue.Empty:
                break

            kind = item[0]
            if kind == "error":
                messagebox.showerror("Macro Recorder", item[1])
            elif kind == "hotkey":
                self._handle_hotkey(item[1])
            elif kind == "key":
                _, name, is_down,tick = item
                self.record_key(name, is_down,tick)
            elif kind == "mouse":
                _, btn, is_down, x, y,tick = item
                self.record_mouse(btn, is_down, x, y,tick)
            elif kind == "wheel":
                _, direction, x, y,tick = item
                self.record_wheel(direction, x, y,tick)
            elif kind == "move":
                _, x, y,tick = item
                self.record_move(x, y,tick)

    def _handle_hotkey(self, name: str) -> None:
        if name == "F1":
            self.start_recording()
        elif name == "F2":
            self.stop_recording()
        elif name == "F3":
            self.start_replay()
        elif name == "F4":
            self.stop_replay()
        elif name == "F5":
            self.toggle_loop()
        elif name == "F6":
            self.save_to_file()
        elif name == "F7":
            self.load_from_file()
        elif name == "F8":
            self.toggle_pause_recording()
        elif name == "F9":
            self.start_append_recording()

    # -------------- recording --------------
    def start_recording(self) -> None:
        with self.lock:
            if self.replaying:
                messagebox.showwarning("Macro Recorder", "Stop replay first (F4) before recording.")
                return
            if self.recording:
                return
            self.actions = []
            self.held_keys = set()
            self.record_paused = False
            self.paused_at = 0
            self.paused_total = 0
            self.start_time = tick_count()
            self.recording = True
        self.refresh_gui()
        if self._minimize_on_run_var.get():
            self._minimize()

    def start_append_recording(self) -> None:
        with self.lock:
            if self.replaying:
                messagebox.showwarning("Macro Recorder", "Stop replay first (F4) before recording.")
                return
            if self.recording:
                return
            last_t = self.actions[-1]["t"] if self.actions else 0
            self.held_keys = set()
            self.record_paused = False
            self.paused_at = 0
            self.paused_total = 0
            self.start_time = tick_count() - last_t
            self.recording = True
        self.refresh_gui()
        if self._minimize_on_run_var.get():
            self._minimize()

    def stop_recording(self) -> None:
        with self.lock:
            if not self.recording:
                return
            self.recording = False
            self.record_paused = False
            self.held_keys = set()
        self.refresh_gui()
        if self._minimize_on_run_var.get():
            self._restore_window()

    def clear_recording(self) -> None:
        with self.lock:
            if self.recording or self.replaying:
                return
            self.actions = []
        self.refresh_gui()

    def toggle_pause_recording(self) -> None:
        with self.lock:
            if not self.recording:
                return
            if not self.record_paused:
                self.record_paused = True
                self.paused_at = tick_count()
                self.held_keys = set()
            else:
                self.paused_total += tick_count() - self.paused_at
                self.paused_at = 0
                self.record_paused = False
        self.refresh_gui()

    def record_key(self, key: str, is_down: bool, tick: int) -> None:
        with self.lock:
            if not self.recording or self.replaying or self.record_paused:
                return
            if key in HOTKEY_NAMES:
                return
            # Respect the "Record Keys" toggle
            if hasattr(self, '_keys_var') and not self._keys_var.get():
                return
            t = tick - self.start_time - self.paused_total
            self.actions.append({"type": "key", "key": key, "down": is_down, "t": int(t)})

    def record_mouse(self, btn: str, is_down: bool, x: int, y: int, tick: int) -> None:
        with self.lock:
            if not self.recording or self.replaying or self.record_paused:
                return
            t = tick - self.start_time - self.paused_total
            self.actions.append({"type": "mouse", "btn": btn, "down": is_down, "x": int(x), "y": int(y), "t": int(t)})

    def record_wheel(self, direction: str, x: int, y: int, tick: int) -> None:
        with self.lock:
            if not self.recording or self.replaying or self.record_paused:
                return
            t = tick - self.start_time - self.paused_total
            self.actions.append({"type": "wheel", "dir": direction, "x": int(x), "y": int(y), "t": int(t)})

    def record_move(self, x: int, y: int, tick: int) -> None:
        with self.lock:
            if not self.recording or self.replaying or self.record_paused:
                return
            # Respect the "Record Moves" toggle
            if hasattr(self, '_moves_var') and not self._moves_var.get():
                return

            t = tick - self.start_time - self.paused_total

            if self.actions:
                last = self.actions[-1]

                if (
                    last.get("type") == "move"
                    and last.get("x") == int(x)
                    and last.get("y") == int(y)
                ):
                    return

            self.actions.append({
                "type": "move",
                "x": int(x),
                "y": int(y),
                "t": int(t)
            })

    # -------------- replay --------------
    def start_replay(self) -> None:
        with self.lock:
            if self.recording:
                messagebox.showwarning("Macro Recorder", "Stop recording first (F2) before replaying.")
                return
            if not self.actions:
                messagebox.showwarning("Macro Recorder", "Nothing recorded yet.")
                return
            if self.replaying:
                return
            self.replaying = True
            self._replay_start_tick = tick_count()
            self.stop_replay_event.clear()
            actions = list(self.actions)

        try:
            repeat = max(1, int(self._repeat_var.get()))
        except Exception:
            repeat = 1

        self._replay_loop_count   = 0
        self._replay_repeat_total = repeat
        self.refresh_gui()
        if self._minimize_on_run_var.get():
            self._minimize()

        randSeed = time.time_ns()
        self.replay_mouse_thread = threading.Thread(
            target=self._replay_worker,
            args=(actions, repeat),
            daemon=True
        )
        self.replay_mouse_thread.start()


    def _replay_worker(self, actions, repeat: int = 1):

        screen_w = user32.GetSystemMetrics(0) - 1
        screen_h = user32.GetSystemMetrics(1) - 1

        loop_count = 0

        try:
            while not self.stop_replay_event.is_set():
                # -- Speed multiplier --------------------------------
                # just incase speed is not defined for some reason. I can probably convert this to a normal index.
                speed = getattr(self, '_speeds', [1.0])[getattr(self, '_speed_idx', 3)]
                if speed <= 0:
                    speed = 1.0

                replay_start = tick_count()
                sleep_offset = 0
                resolved_sleeps = {}
                for idx, action in enumerate(actions):
                    if action.get("type") == "sleep":
                        if action.get("val") == "rand":
                            resolved_sleeps[idx] = random.randint(0, 30000)
                        else:
                            resolved_sleeps[idx] = int(action.get("val", 0))

                for idx, action in enumerate(actions):
                    if self.stop_replay_event.is_set():
                        break

                    elapsed = tick_count() - replay_start

                    if action.get("type") == "sleep": # sleep was a personal feature I needed. Can be removed. It just allows for randomness in playback to not look like a full robot.
                        delay = int(action.get("t", 0)) / speed + sleep_offset - elapsed
                        if delay > 0:
                            sleep_spin(delay)
                            if self.stop_replay_event.is_set():
                                break
                        dur = resolved_sleeps.get(idx, 0) / speed
                        if dur > 0:
                            sleep_spin(dur)
                            if self.stop_replay_event.is_set():
                                break
                        sleep_offset += dur
                        continue

                    delay = int(action.get("t", 0)) / speed + sleep_offset - elapsed
                    if delay > 0:
                        sleep_spin(delay)
                        if self.stop_replay_event.is_set():
                            break

                    if action["type"] == "key":
                        vk = VK_NAMES.get(action["key"])
                        if vk is None:
                            continue
                        keybd_event(vk, key_up=not action.get("down", False))

                    elif action["type"] == "mouse":
                        x = int(action.get("x", 0))
                        y = int(action.get("y", 0))
                        
                        if not self._touch_mode:
                            set_cursor_pos(x, y)
                        
                        btn = action.get("btn")
                        if btn == "LButton":
                            if self._touch_mode:
                                if action.get("down", False):
                                    self._touch_is_down = True
                                    touchDown(x,y)
                                    
                                else:
                                    self._touch_is_down = False
                                    touchUp()
                            else:   
                                mouse_event(MOUSEEVENTF_LEFTDOWN if action.get("down", False) else MOUSEEVENTF_LEFTUP)
                        elif btn == "RButton":
                            mouse_event(MOUSEEVENTF_RIGHTDOWN if action.get("down", False) else MOUSEEVENTF_RIGHTUP)
                        elif btn == "MButton":
                            mouse_event(MOUSEEVENTF_MIDDLEDOWN if action.get("down", False) else MOUSEEVENTF_MIDDLEUP)
                        elif btn == "XButton1":
                            mouse_event(MOUSEEVENTF_XDOWN if action.get("down", False) else MOUSEEVENTF_XUP, data=1)
                        elif btn == "XButton2":
                            mouse_event(MOUSEEVENTF_XDOWN if action.get("down", False) else MOUSEEVENTF_XUP, data=2)

                    elif action["type"] == "wheel":
                        x = int(action.get("x", 0))
                        y = int(action.get("y", 0))
                        set_cursor_pos(x, y)
                        direction = action.get("dir")
                        if direction == "WheelUp":
                            mouse_event(MOUSEEVENTF_WHEEL, data=120)
                        elif direction == "WheelDown":
                            mouse_event(MOUSEEVENTF_WHEEL, data=-120)
                        elif direction == "WheelRight":
                            mouse_event(MOUSEEVENTF_HWHEEL, data=120)
                        elif direction == "WheelLeft":
                            mouse_event(MOUSEEVENTF_HWHEEL, data=-120)

                    elif action["type"] == "move":
                        x = action["x"]
                        y = action["y"]
                        abs_x = int(x * 65535 / screen_w)
                        abs_y = int(y * 65535 / screen_h)
                        if self._touch_mode :
                            
                            if self._touch_is_down:
                                touchMove(x,y)
                        else:
                            inp = INPUT()
                            inp.type = INPUT_MOUSE
                            inp.union.mi = MOUSEINPUT(
                                dx=abs_x,
                                dy=abs_y,
                                mouseData=0,
                                dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                                time=0,
                                dwExtraInfo=None
                            )
                            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

                    if self.stop_replay_event.is_set():
                        break
                
                if self._touch_is_down:
                    self._touch_is_down = False
                    touchUp()
                    
                if self.stop_replay_event.is_set():
                    break

                loop_count += 1
                self._replay_loop_count = loop_count
                if not self.loop_replay and loop_count >= repeat:
                    break

        finally:
            self.root.after(0, self._finish_replay)

    def _finish_replay(self) -> None:
        with self.lock:
            self.replaying = False
        self.refresh_gui()
        if self._minimize_on_run_var.get():
            self._restore_window()

    def stop_replay(self) -> None:
        with self.lock:
            if not self.replaying:
                return
            self.stop_replay_event.set()
        self.refresh_gui()
        if self.replay_mouse_thread and self.replay_mouse_thread.is_alive():
            self.replay_mouse_thread.join(timeout=0.5)

    def stop_or_stopreplay(self) -> None:
        if self.recording:
            self.stop_recording()
        else:
            self.stop_replay()

    def toggle_loop(self) -> None:
        with self.lock:
            self.loop_replay = not self.loop_replay
            self.loop_var.set(1 if self.loop_replay else 0)
            self.state.set("core","loop_active",1 if self.loop_replay else 0)
            self.state.save()
        self._sync_loop_btn()
        self.refresh_gui()

    def _toggle_loop_btn(self) -> None:
        self.toggle_loop()

    def _sync_loop_btn(self) -> None:
        """Keep the custom loop button appearance in sync with loop_replay state."""
        if not hasattr(self, '_loop_btn'):
            return
        C_PLAY = self._C_PLAY
        if self.loop_replay:
            self._loop_btn.config(bg=C_PLAY, fg="#001a10",
                                   activebackground=C_PLAY, activeforeground="#001a10")
            # Hide repeat widgets if loop is active.
            self._repeat_lbl.place_forget()
            self._repeat_entry.place_forget()
            self._repeat_x_lbl.place_forget()
        else:
            self._loop_btn.config(bg=self._SURF2, fg=self._MUTED2,
                                   activebackground=self._SURF, activeforeground=self._TEXT)
            # Restore repeat widgets
            self._repeat_lbl.place(x=195, y=90, width=60, height=10)
            self._repeat_entry.place(x=206, y=102, width=36, height=22)
            self._repeat_x_lbl.place(x=246, y=104, width=12, height=16)

    # -------------- save/load --------------
    def save_to_file(self) -> None:
        with self.lock:
            if not self.actions:
                messagebox.showwarning("Macro Recorder", "Nothing to save.")
                return
            default_path = os.path.join(os.path.dirname(__file__), "recording.mcr")
            path = filedialog.asksaveasfilename(
                title="Save Recording",
                defaultextension=".mcr",
                initialdir=os.path.dirname(__file__),
                initialfile="recording.mcr",
                filetypes=[("Macro Files", "*.mcr")],
            )
            if not path:
                return
            lines = []
            prev_t = 0
            for a in self.actions:
                t = int(a.get('t', 0))
                delta = t - prev_t
                prev_t = t
                if a["type"] == "key":
                    lines.append(f"key\t{a['key']}\t{int(bool(a['down']))}\t{delta}\n")
                elif a["type"] == "mouse":
                    lines.append(f"mouse\t{a['btn']}\t{int(bool(a['down']))}\t{int(a['x'])}\t{int(a['y'])}\t{delta}\n")
                elif a["type"] == "wheel":
                    lines.append(f"wheel\t{a['dir']}\t{int(a['x'])}\t{int(a['y'])}\t{delta}\n")
                elif a["type"] == "sleep":
                    lines.append(f"sleep\t{a['val']}\t{delta}\n")
                elif a["type"] == "move":
                    lines.append(f"move\t{int(a['x'])}\t{int(a['y'])}\t{delta}\n")

            with open(path, "w", encoding="utf-8", newline="") as f:
                f.writelines(lines)
            self._add_recent(path)

    def parse_file(self,file):
        actions = []
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                for raw in f:
                    line = raw.rstrip("\r\n")
                    if not line:
                        continue
                    cols = line.split("\t")
                    t = cols[0]
                    if t == "key" and len(cols) >= 4:
                        actions.append({"type": "key", "key": cols[1], "down": cols[2] in ("1", "true", "True"), "t": int(float(cols[3]))})
                    elif t == "mouse" and len(cols) >= 6:
                        actions.append({"type": "mouse", "btn": cols[1], "down": cols[2] in ("1", "true", "True"), "x": int(float(cols[3])), "y": int(float(cols[4])), "t": int(float(cols[5]))})
                    elif t == "wheel" and len(cols) >= 5:
                        actions.append({"type": "wheel", "dir": cols[1], "x": int(float(cols[2])), "y": int(float(cols[3])), "t": int(float(cols[4]))})
                    elif t == "move" and len(cols) >= 4:
                        actions.append({
                            "type": "move",
                            "x": int(float(cols[1])),
                            "y": int(float(cols[2])),
                            "t": int(float(cols[3]))
                        })
                    elif t == "sleep" and len(cols) >= 2:
                        val = cols[1]
                        if val != "rand":
                            try:
                                val = int(float(val))
                            except Exception:
                                pass
                        actions.append({"type": "sleep", "val": val, "t": int(float(cols[2])) if len(cols) >= 3 else 0})
            # converts the milliseconds_after_the_previous_input to timestamps for the program to use instead. 
            abs_t = 0
            for a in actions:
                abs_t += a["t"]
                a["t"] = abs_t
            return actions
        except Exception as e:
            return [] # failed to parse. they get nothing
        return []

    def load_from_file(self) -> None:
        with self.lock:
            if self.recording or self.replaying:
                messagebox.showwarning("Macro Recorder", "Stop recording/replay before loading.")
                return
            path = filedialog.askopenfilename(
                title="Load Recording",
                initialdir=os.path.dirname(__file__),
                filetypes=[("Macro Files", "*.mcr")],
            )
            if not path:
                return
            actions = self.parse_file(path)
            
            self.actions = actions
        self._add_recent(path)
        self.refresh_gui()

    # -------------- window chrome --------------
    def _minimize(self) -> None:
        # temporarily disable borderless
        self.root.overrideredirect(False)

        # minimize to taskbar
        self.root.iconify()


    def _restore_window(self) -> None:
        """Restore the window from minimized state (used by Minimize on Run)."""
        if self.root.state() == "iconic":
            self.root.overrideredirect(False)
            self.root.deiconify()
            # _on_restore will re-apply overrideredirect after a short delay

    def _on_restore(self, event) -> None:
        # restore borderless only after restore
        if self.root.state() == "normal":
            self.root.after(
                10,
                lambda: self.root.overrideredirect(True)
            )

    def _drag_start(self, event) -> None:
        self._drag_off_x = event.x_root - self.root.winfo_x()
        self._drag_off_y = event.y_root - self.root.winfo_y()

    def _drag_motion(self, event) -> None:
        x = event.x_root - self._drag_off_x
        y = event.y_root - self._drag_off_y
        self.root.geometry(f"+{x}+{y}")

    def _drag_end(self, event) -> None:
        win_x = self.root.winfo_x()
        win_y = self.root.winfo_y()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()

        # Collect all monitors via EnumDisplayMonitors
        monitors = []
        def _monitor_cb(hmon, hdc, rect, data):
            r = rect.contents
            monitors.append((r.left, r.top, r.right, r.bottom))
            return 1
        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_ulong, ctypes.c_ulong,
            ctypes.POINTER(wintypes.RECT), ctypes.c_double)
        ctypes.windll.user32.EnumDisplayMonitors(
            None, None, MONITORENUMPROC(_monitor_cb), 0)

        if not monitors:
            # Fallback: primary screen only
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            monitors = [(0, 0, sw, sh)]

        # Minimum pixels that must remain visible on any monitor
        MARGIN = 60

        # Check if the window already has enough overlap with any monitor
        for ml, mt, mr, mb in monitors:
            overlap_x = max(0, min(win_x + win_w, mr) - max(win_x, ml))
            overlap_y = max(0, min(win_y + win_h, mb) - max(win_y, mt))
            if overlap_x >= MARGIN and overlap_y >= MARGIN:
                return  # fine where it is

        # Find the nearest monitor and snap to it
        def _dist(ml, mt, mr, mb):
            cx = win_x + win_w // 2
            cy = win_y + win_h // 2
            nx = max(ml, min(cx, mr))
            ny = max(mt, min(cy, mb))
            return (cx - nx) ** 2 + (cy - ny) ** 2

        ml, mt, mr, mb = min(monitors, key=lambda m: _dist(*m))

        snapped_x = max(ml, min(win_x, mr - MARGIN))
        snapped_y = max(mt, min(win_y, mb - MARGIN))

        self.root.geometry(f"+{snapped_x}+{snapped_y}")

    # -------------- settings popup --------------
    def _open_settings(self) -> None:
        if hasattr(self, '_settings_win') and self._settings_win.winfo_exists():
            self._settings_win.lift()
            return

        BG    = self._BG
        SURF  = self._SURF
        TEXT  = self._TEXT
        MUTED2= self._MUTED2

        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("220x160")
        win.resizable(False, False)
        win.configure(bg=BG)
        win.attributes("-topmost", True)
        win.iconphoto(False,tk.PhotoImage(data=appIcon))
        self._settings_win = win
        
        rx = self.root.winfo_x()
        ry = self.root.winfo_y()
        win.geometry(f"220x160+{rx + self._W + 4}+{ry}")

        tk.Label(win, text="RECORDING FILTERS", bg=BG, fg=MUTED2,
                 font=("Segoe UI", 6, "bold")).place(x=12, y=10, width=196, height=10)

        for i, (text, var) in enumerate([
            ("Record Mouse Movements", self._moves_var),
            ("Record Keyboard Input",  self._keys_var),
        ]):
            tk.Checkbutton(win, text=text, variable=var,
                           bg=BG, fg=TEXT, selectcolor=SURF,
                           activebackground=BG, activeforeground=TEXT,
                           font=("Segoe UI", 9), highlightthickness=0,
                           cursor="hand2").place(x=12, y=26 + i * 24, width=200, height=22)

        tk.Label(win, text="BEHAVIOUR", bg=BG, fg=MUTED2,
                 font=("Segoe UI", 6, "bold")).place(x=12, y=78, width=196, height=10)

        tk.Checkbutton(win, text="Minimize on Run", variable=self._minimize_on_run_var,
                       bg=BG, fg=TEXT, selectcolor=SURF,
                       activebackground=BG, activeforeground=TEXT,
                       font=("Segoe UI", 9), highlightthickness=0,
                       cursor="hand2").place(x=12, y=92, width=200, height=22)

        def _on_touch_toggle():
            self._touch_mode = bool(self._use_touch_var.get())
            if not self._touch_mode and self._touch_is_down:
                touchUp()
                self._touch_is_down = False

        tk.Checkbutton(win, text="Use Touchscreen as Click", variable=self._use_touch_var,
                       command=_on_touch_toggle,
                       bg=BG, fg=TEXT, selectcolor=SURF,
                       activebackground=BG, activeforeground=TEXT,
                       font=("Segoe UI", 9), highlightthickness=0,
                       cursor="hand2").place(x=12, y=116, width=200, height=22)

        tk.Button(win, text="Close", command=win.destroy,
                  font=("Segoe UI", 8), bg=SURF, fg=MUTED2,
                  relief="flat", bd=0,
                  activebackground=self._SURF2, activeforeground=TEXT,
                  cursor="hand2").place(x=12, y=138, width=56, height=18)

    # -------------- layout switching --------------
    def _update_layout(self) -> None:
        W = self._W
        if self.recording or self.replaying:
            self._idle_frame.place_forget()
            self._compact_frame.place(x=0, y=68, width=W, height=26)
            if self.recording:
                self._compact_rep.place_forget()
                self._compact_rec.place(x=0, y=0, width=W, height=26)
            else:
                self._compact_rec.place_forget()
                self._compact_rep.place(x=0, y=0, width=W, height=26)
            self.root.geometry(f"{W}x{self._H_COMPACT}")
            self._settings_btn.place_forget()
        else:
            self._compact_frame.place_forget()
            self._idle_frame.place(x=0, y=68, width=W, height=self._H_IDLE - 68)
            self.root.geometry(f"{W}x{self._H_IDLE}")
            self._settings_btn.place(x=self._W - 82, y=5, width=22, height=20)


    # -------------- gui refresh --------------
    def _schedule_refresh(self):
        self.refresh_gui()
        self.root.after(100, self._schedule_refresh)

    def refresh_gui(self) -> None:
        BG      = self._BG
        SURF2   = self._SURF2
        MUTED   = self._MUTED
        MUTED2  = self._MUTED2
        TEXT    = self._TEXT
        C_REC   = self._C_REC
        C_PLAY  = self._C_PLAY
        C_PAUSE = self._C_PAUSE

        with self.lock:
            count = len(self.actions)
            dur_ms = max((a.get("t", 0) for a in self.actions), default=0)

            if self.recording and self.record_paused:
                status_text = "  PAUSED"
                bar_bg      = "#1a1400" # yellow
                dot_color   = C_PAUSE
                lbl_fg      = C_PAUSE
                elapsed_ms  = self.paused_at - self.start_time - self.paused_total
            elif self.recording:
                status_text = "  RECORDING"
                bar_bg      = "#1a060b" # red
                dot_color   = C_REC
                lbl_fg      = C_REC
                elapsed_ms  = tick_count() - self.start_time - self.paused_total
            elif self.replaying:
                status_text = "  REPLAYING"
                bar_bg      = "#00160d" # green
                dot_color   = C_PLAY
                lbl_fg      = C_PLAY
                elapsed_ms  = tick_count() - self._replay_start_tick
            else:
                status_text = "  IDLE"
                bar_bg      = SURF2
                dot_color   = MUTED
                lbl_fg      = MUTED2
                elapsed_ms  = 0

        # -- Status bar ----------------------------------------------
        self.status_bar.config(bg=bar_bg)
        self.status_label.config(text=status_text, bg=bar_bg, fg=lbl_fg)
        self._timer_label.config(bg=bar_bg)
        self._min_btn.config(bg=bar_bg)
        self._close_btn.config(bg=bar_bg)
        self._dot_canvas.config(bg=bar_bg)
        self._dot_canvas.itemconfig(self._dot_oval, fill=dot_color)

        if self.recording or self.replaying:
            s = max(0.0, elapsed_ms / 1000.0)
            m = int(s // 60)
            self._timer_label.config(text=f"{m:02d}:{s % 60:04.1f}", fg=dot_color)
        else:
            self._timer_label.config(text="", fg=MUTED2)

        # -- Stats ---------------------------------------------------
        self.action_count.config(text=f"{count:,}")
        dur_s = dur_ms / 1000.0
        if dur_s >= 60:
            m2 = int(dur_s // 60)
            self._dur_label.config(text=f"{m2}:{dur_s % 60:04.1f}")
        else:
            self._dur_label.config(text=f"{dur_s:.1f} s")

        # -- Loop counter (right of stats row) ------------------------
        if self.replaying:
            lc = self._replay_loop_count
            if self.loop_replay:
                loop_text = f"{lc + 1}"
            else:
                total = self._replay_repeat_total
                loop_text = f"{lc + 1}/{total}" if total > 1 else ""
            self._loop_count_label.config(text=loop_text)
            if loop_text:
                self._loop_hdr_label.place(x=236, y=2, width=76, height=10)
                self._loop_count_label.place(x=236, y=14, width=76, height=16)
            else:
                self._loop_hdr_label.place_forget()
                self._loop_count_label.place_forget()
        else:
            self._loop_hdr_label.place_forget()
            self._loop_count_label.place_forget()

        # -- Progress bar ---------------------------------------------
        W = self._W
        if self.replaying and dur_ms > 0:
            # Adjust for playback speed: actual wall-clock duration per loop pass
            # todo: this can get out of sync. This should be tied to reset when the playback loop reset.
            speed = self._speeds[self._speed_idx]
            if speed <= 0:
                speed = 1.0
            actual_dur_ms = dur_ms / speed
            # Progress within current loop pass
            loop_elapsed = elapsed_ms % max(actual_dur_ms, 1) if actual_dur_ms > 0 else 0
            frac = min(1.0, max(0.0, loop_elapsed / actual_dur_ms))
            bar_w = int(frac * W)
            self._progress_canvas.config(bg=self._SURF2)
            self._progress_canvas.coords(self._progress_bar, 0, 0, bar_w, 2)
            self._progress_canvas.itemconfig(self._progress_bar, fill=self._C_PLAY)
        else:
            self._progress_canvas.coords(self._progress_bar, 0, 0, 0, 2)
            self._progress_canvas.config(bg=self.status_bar.cget("bg"))

        # -- Compact pause button -------------------------------------
        if self.record_paused:
            self._compact_pause_btn.config(text="Resume  F8", fg=C_PAUSE)
        else:
            self._compact_pause_btn.config(text="Pause  F8", fg=TEXT)

        # -- Loop button sync -----------------------------------------
        self._sync_loop_btn()

        # -- Window layout -------------------------------------------
        self._update_layout()

        self.root.title(f"Macro Recorder  ·  {count:,} actions")

    # -------------- recent files --------------
    def _add_recent(self, path: str) -> None:
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:2]
        self.state.set_list("core","recent_files",self.recent_files)
        self.state.save()
        self._refresh_recent_buttons()

    def _refresh_recent_buttons(self) -> None:
        for i, btn in enumerate(self._recent_btns):
            if i < len(self.recent_files):
                name = os.path.basename(self.recent_files[i])
                btn.config(text=f"  {name}", fg="#7070a0")
            else:
                btn.config(text="  -", fg="#4a4a6a")

    def _load_recent(self, idx: int) -> None:
        if idx >= len(self.recent_files):
            return
        path = self.recent_files[idx]
        if not os.path.exists(path):
            messagebox.showwarning("Macro Recorder", f"File not found:\n{path}")
            return
        with self.lock:
            if self.recording or self.replaying:
                messagebox.showwarning("Macro Recorder", "Stop recording/replay before loading.")
                return

            actions = self.parse_file(path)
            self.actions = actions
        self.refresh_gui()

    # -------------- close --------------
    def on_close(self) -> None:
        try:
            self.stop_replay_event.set()
        except Exception:
            pass
        try:
            if self.hook_thread_id:
                user32.PostThreadMessageW(self.hook_thread_id, 0x0012, 0, 0)  # WM_QUIT
        except Exception:
            pass
        self.root.after(50, self.root.destroy)

    def run(self) -> None:
        self.root.mainloop()


# --------- INI manager code ------------
# This should be in a new file but I want to keep this as a 1 file project for portability. 

import configparser
import os
from pathlib import Path
from typing import Any
import json
 
class AppStateManager:
    """
    Manages application state persistence using an INI file.
 
    Wraps Python's configparser with typed getters, auto-save on context
    exit, and safe defaults so missing keys never crash your app.
    """
 
    def __init__(self, filepath: str = "app_state.ini", auto_load: bool = True):
        """
        Args:
            filepath:  Path to the INI file (created if it doesn't exist).
            auto_load: If True, load existing state immediately on init.
        """
        self.filepath = Path(filepath)
        self._config = configparser.ConfigParser()
        if auto_load:
            self.load()
 
    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
 
    def load(self) -> bool:
        """
        Load state from disk.
 
        Returns:
            True if the file was found and read; False if it didn't exist yet.
        """
        if not self.filepath.exists():
            return False
        self._config.read(self.filepath, encoding="utf-8")
        return True
 
    def save(self) -> None:
        """Write current state to disk, creating parent directories as needed."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            self._config.write(f)
 
    def delete(self) -> bool:
        """
        Delete the INI file and reset in-memory state.
 
        Returns:
            True if the file was deleted; False if it didn't exist.
        """
        self._config = configparser.ConfigParser()
        if self.filepath.exists():
            os.remove(self.filepath)
            return True
        return False
 
    # ------------------------------------------------------------------
    # Context manager  (with AppStateManager(...) as state:)
    # ------------------------------------------------------------------
 
    def __enter__(self) -> "AppStateManager":
        return self
 
    def __exit__(self, *_) -> None:
        self.save()
 
    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
 
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Store a value under [section] / key.
        The value is coerced to a string (booleans become "true"/"false").
 
        Args:
            section: INI section name (created automatically if absent).
            key:     Option name within the section.
            value:   Any value — converted to str for storage.
        """
        if not self._config.has_section(section):
            self._config.add_section(section)
        # Normalise booleans so get_bool() can reliably round-trip them
        if isinstance(value, bool):
            self._config.set(section, key, "true" if value else "false")
        else:
            self._config.set(section, key, str(value))
 
    def set_list(self, section: str, key: str, value: list) -> None:
        self.set(section, key, json.dumps(value))

    def remove_key(self, section: str, key: str) -> bool:
        """Remove a single key. Returns True if it existed."""
        return self._config.has_option(section, key) and self._config.remove_option(section, key)
 
    def remove_section(self, section: str) -> bool:
        """Remove an entire section. Returns True if it existed."""
        return self._config.remove_section(section)
 
    # ------------------------------------------------------------------
    # Read — typed getters
    # ------------------------------------------------------------------
 
    def get(self, section: str, key: str, fallback: str = "") -> str:
        """Return a value as a string, or *fallback* if not found."""
        return self._config.get(section, key, fallback=fallback)
 
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Return a value as an int, or *fallback* if not found / not numeric."""
        try:
            return self._config.getint(section, key, fallback=fallback)
        except ValueError:
            return fallback
 
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Return a value as a float, or *fallback* if not found / not numeric."""
        try:
            return self._config.getfloat(section, key, fallback=fallback)
        except ValueError:
            return fallback
 
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """
        Return a value as a bool.
        Recognises: true/false, yes/no, on/off, 1/0 (case-insensitive).
        Returns *fallback* if key is absent or value is unrecognised.
        """
        try:
            return self._config.getboolean(section, key, fallback=fallback)
        except ValueError:
            return fallback

    def get_list(self, section: str, key: str, fallback: list = []) -> list:
        raw = self.get(section, key, fallback=None)
        if raw is None:
            return fallback
        try:
            result = json.loads(raw)
            return result if isinstance(result, list) else fallback
        except (json.JSONDecodeError, ValueError):
            return fallback 
    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------
 
    def has(self, section: str, key: str) -> bool:
        """Return True if [section] / key exists."""
        return self._config.has_option(section, key)
 
    def sections(self) -> list[str]:
        """Return a list of all section names."""
        return self._config.sections()
 
    def keys(self, section: str) -> list[str]:
        """Return all keys within a section (empty list if section missing)."""
        if not self._config.has_section(section):
            return []
        return list(self._config.options(section))
 
    def as_dict(self) -> dict[str, dict[str, str]]:
        """Return the entire state as a plain nested dict."""
        return {s: dict(self._config.items(s)) for s in self._config.sections()}
 
    def __repr__(self) -> str:
        return f"AppStateManager(filepath={str(self.filepath)!r}, sections={self.sections()})"
 
 













if __name__ == "__main__":
    os.system('color')
    print("Rename .py with .pyw to remove the console.\nAlternatively, Use the executable version at:\n"+"\033[91m"+"https://github.com/000744210/FastMacro"+"\033[0m")
    try:
        # Force Windows timer resolution to 1ms
        winmm.timeBeginPeriod(1)
        
        opened_file = None
        if len(sys.argv) > 1:
            opened_file = sys.argv[1]
        register_mcr_filetype()
        app = MacroRecorderApp(opened_file)
        app.run()
        
    finally:
        # Always restore system timer resolution on exit
        winmm.timeEndPeriod(1)