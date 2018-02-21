from time import sleep
import org.sikuli.natives.OCR as OCR
import org.sikuli.script.TextRecognizer as TR
from sikuli import Settings
import string
import sys
import contextlib
import random


def rand(a,b):
    return a + random.random()*(b-a)

# hack the current path into sys.path
import sys, os
__file__ = os.path.dirname(getBundlePath())
sys.path.append(__file__)
from shell_regions import *

class BadError(Exception): pass



class Options():
    KB_WAIT_SLEEP = 0.3, 2
    WELCOME_WAIT  = 0.6, 2
    LOGIN_WAIT    = 0.3, 2
    OPEN_ACC_WAIT = 0.2, 1
    KB_WAIT_USER  = 0.1, 1
    KB_WAIT_PW    = 0.1, 1
    LOGOUT_WAIT   = 1.0, 3
    WAIT_STEPS = [
        "KB_WAIT_SLEEP",
        "WELCOME_WAIT",
        "LOGIN_WAIT",
        "OPEN_ACC_WAIT",
        "KB_WAIT_USER",
        "KB_WAIT_PW",
        "LOGOUT_WAIT",
    ]
    def __init__(self):
        for step in self.WAIT_STEPS:
            setattr(self, step, rand(*getattr(self, step)))

    def showops(self):
        for k in self.WAIT_STEPS:
            print("%s: %s" % (k, getattr(self, k)))


def startup():
    if LOGIN_SCREEN_FULL.exists(LOGIN_SCREEN_FULL_IMG):
        pass
    elif WELCOME_SCREEN.exists(WELCOME_SCREEN_IMG):
        logout()
        wait_for_login_screen()
    else:
        raise BadError("Unrecognized Starting Condition")

    Settings.OcrTextRead = True
    Settings.OcrLanguage = "eng" 

    # reset the TextRecognizer
    TR.reset()
    # instantiate it 
    TR.getInstance()

    wl = string.ascii_letters + string.digits
    OCR.setParameter("tessedit_char_whitelist", wl)

# wait_for actions

def wait_for_keyboard():
    #KB_SCREEN_EMPTY.wait(KB_SCREEN_EMPTY_IMG, 10)
    sleep(OPS.KB_WAIT_SLEEP)

def wait_for_welcome():
    #WELCOME_SCREEN.wait(WELCOME_SCREEN_IMG, 10)
    sleep(OPS.WELCOME_WAIT)

def wait_for_login_screen():
    #LOGIN_SCREEN_FULL.wait(LOGIN_SCREEN_FULL_IMG)
    sleep(OPS.LOGIN_WAIT)

# menu actions
def open_account_menu():
    ACCOUNT_BUTTON.click()

def open_manage():
    open_account_menu()
    sleep(OPS.OPEN_ACC_WAIT)
    ACCOUNT_MENU_MANAGE.click()
    MANAGE_MENU.wait(MANAGE_MENU_IMG)

# low level actions

@contextlib.contextmanager
def quick_click(t=0.3):
    mmd = Settings.MoveMouseDelay
    Settings.MoveMouseDelay = t
    try:
        yield
    finally:
        Settings.MoveMouseDelay = mmd

def typetext(s, t=0.1):
    for c in s:
        type(c)
        sleep(t)

def kb_text(s, t=0):
    with quick_click(t):
        for c in s:
            KEYBOARD_REGIONS[c].click()

def keyboard_enter():
    KB_SCREEN_ENTER.click()

# high level actions

def logout():
    open_account_menu()
    sleep(OPS.OPEN_ACC_WAIT)
    ACCOUNT_MENU_LOGOUT.click()
    sleep(OPS.LOGOUT_WAIT)

def login(user, pw):
    LOGIN_FIELD_NAME.click()
    wait_for_keyboard()
    kb_text(user, OPS.KB_WAIT_USER)
    keyboard_enter()
    wait_for_login_screen()
    LOGIN_FIELD_PW.click()
    wait_for_keyboard()
    kb_text(pw, OPS.KB_WAIT_PW)
    keyboard_enter()
    wait_for_login_screen()
    LOGIN_FIELD_LOGIN.click()
    wait_for_welcome()

def check_name(u):
    name = find_name()
    if isinstance(u, str):
        good = name == u
    elif isinstance(u, (list, tuple)):
        good = name in u
    if not good:
        print("NAME_MISMATCH:", u, name)
        lines = ['Found Mismatched Name!',
                 "Got '%s', Expected '%s'" % (u, name),
                 'Stop running?']
        s = "\n".join(lines)
        stop = popAsk(s)
        if stop:
            sys.exit(1)

def find_name():
    return MANAGE_MENU_USERNAME.text()

def rand_acc_btn():
    open_account_menu()
    sleep(OPS.OPEN_ACC_WAIT)
    i = random.randint(1,2)
    if i == 1:  # Manage
        print(usr, "MANAGE")
        ACCOUNT_MENU_MANAGE.click()
        MANAGE_MENU.wait(MANAGE_MENU_IMG)
    else:       # logout
        print(usr, "LOGOUT")
        ACCOUNT_MENU_LOGOUT.click()
        sleep(OPS.LOGOUT_WAIT)
    return i

def run_test(usr, pw, *exp):
    global OPS
    OPS = Options()
    OPS.showops()
    login(usr, pw)
    while True:
        screen = rand_acc_btn(usr)
        if screen == 1:
            check_name(exp or usr)
        else:
            break
    check_stop()

STOP = False
def hotkey_exit(ev):
   global STOP
   STOP = True

def check_stop():
    global STOP
    if STOP:
        sys.exit(0)

def main():
    startup()
    Settings.WaitScanRate = 2
    Env.addHotkey(Key.F1, KeyModifier.ALT, hotkey_exit)    
    
    # The pixelated font and grayscale causes
    # tesseract to confuse '1' and 'l' (one and L).
    # There is no way around this as they look 
    # very similar depending on font.
    
    while True:
        with quick_click(0):
            run_test('user1', '12345', 'user1', 'userl')
            #run_test('user1', '12345', 'user1', 'userl')
            run_test('pbstech', '727246')


if __name__ == '__main__':
    main()