from sikuli import Region, getBundleFolder
import os
try:
    __file__
except NameError:
    _base = os.path.dirname(getBundleFolder())
else:
    _base = os.path.dirname(__file__)

def _Image(s):
    return os.path.join(_base, s)


LOGIN_SCREEN_FULL     = Region(229,199,335,234)
LOGIN_SCREEN_FULL_IMG = _Image("LOGIN_SCREEN_FULL_IMG.png")
WELCOME_SCREEN        = Region(75,33,631,562)
WELCOME_SCREEN_IMG    = _Image("WELCOME_SCREEN_IMG.png")

KB_SCREEN_EMPTY       = Region(26,213,737,386)
KB_SCREEN_EMPTY_IMG   = _Image("KB_SCREEN_EMPTY_IMG.png")

KB_SCREEN_ENTER       = Region(649,444,103,46)

ACCOUNT_BUTTON        = Region(688,3,94,43)
ACCOUNT_MENU_MANAGE   = Region(681,49,86,43)
ACCOUNT_MENU_LOGOUT   = Region(680,96,86,39)

LOGIN_FIELD_NAME      = Region(318,259,149,20)
LOGIN_FIELD_PW        = Region(319,299,145,21)
LOGIN_FIELD_LOGIN     = Region(309,331,76,41)


MANAGE_MENU           = Region(338,43,127,49)

MANAGE_MENU_IMG       = _Image("MANAGE_MENU_IMG.png")
MANAGE_MENU_USERNAME  = Region(180,112,107,18)
KB_0 = Region(502,348,44,39)
KB_1 = Region(55,350,40,37)
KB_2 = Region(102,347,45,40)
KB_3 = Region(153,348,45,38)
KB_4 = Region(202,347,48,40)
KB_5 = Region(255,349,42,39)
KB_6 = Region(304,347,46,42)
KB_7 = Region(353,347,44,41)
KB_8 = Region(404,347,44,44)
KB_9 = Region(453,348,43,38)
KB_A = Region(103,445,46,48)
KB_B = Region(327,498,43,40)
KB_C = Region(227,495,49,47)
KB_D = Region(202,446,51,47)
KB_E = Region(177,394,46,49)
KB_F = Region(255,445,47,44)
KB_G = Region(302,444,53,53)
KB_H = Region(356,448,41,42)
KB_I = Region(427,396,48,44)
KB_J = Region(406,447,42,43)
KB_K = Region(455,446,46,44)
KB_L = Region(505,447,48,43)
KB_M = Region(428,496,44,42)
KB_N = Region(376,495,48,51)
KB_O = Region(478,395,49,48)
KB_P = Region(529,395,43,47)
KB_Q = Region(74,394,52,50)
KB_R = Region(227,396,46,46)
KB_S = Region(154,446,47,44)
KB_T = Region(277,396,47,44)
KB_U = Region(377,396,48,47)
KB_V = Region(276,493,46,48)
KB_W = Region(126,395,50,49)
KB_X = Region(177,495,47,47)
KB_Y = Region(327,396,47,48)
KB_Z = Region(127,493,46,47)
KEYBOARD_REGIONS = {
    "a": KB_A,
    "b": KB_B,
    "c": KB_C,
    "d": KB_D,
    "e": KB_E,
    "f": KB_F,
    "g": KB_G,
    "h": KB_H,
    "i": KB_I,
    "j": KB_J,
    "k": KB_K,
    "l": KB_L,
    "m": KB_M,
    "n": KB_N,
    "o": KB_O,
    "p": KB_P,
    "q": KB_Q,
    "r": KB_R,
    "s": KB_S,
    "t": KB_T,
    "u": KB_U,
    "v": KB_V,
    "w": KB_W,
    "x": KB_X,
    "y": KB_Y,
    "z": KB_Z,
    "A": KB_A,
    "B": KB_B,
    "C": KB_C,
    "D": KB_D,
    "E": KB_E,
    "F": KB_F,
    "G": KB_G,
    "H": KB_H,
    "I": KB_I,
    "J": KB_J,
    "K": KB_K,
    "L": KB_L,
    "M": KB_M,
    "N": KB_N,
    "O": KB_O,
    "P": KB_P,
    "Q": KB_Q,
    "R": KB_R,
    "S": KB_S,
    "T": KB_T,
    "U": KB_U,
    "V": KB_V,
    "W": KB_W,
    "X": KB_X,
    "Y": KB_Y,
    "Z": KB_Z,
    "0": KB_0,
    "1": KB_1,
    "2": KB_2,
    "3": KB_3,
    "4": KB_4,
    "5": KB_5,
    "6": KB_6,
    "7": KB_7,
    "8": KB_8,
    "9": KB_9,
}