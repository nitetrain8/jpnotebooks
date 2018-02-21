""" Regex match functions. Development from frs_granularize3. """

import re
subitem_match = re.compile(r"^(?:([#]+)\s*)").match
magic_match = re.compile(r"^@lm\:\<(.+)\>").match
header_match = re.compile(r"^(?:([\*\#]*) )?([\+\*]+)([^\*\+]+?)\:?([\+\*]+)\:?\s*(.+)?$").match
frs_match = re.compile(r"([FU]RS\d*)\.?([\d\.]+)?").match
num_escape_match = re.compile(r"^(\*{2})(\#+)").match
image_caption_match = re.compile(r"(Image \d+)").match

def toplevel_match(s):
    m = header_match(s)
    if m and not is_toplevel(m):
        return None
    return m

def is_toplevel(m):
    # m must be a match from header_match
    return m.group(1) is None