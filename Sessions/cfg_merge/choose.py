import datetime, os
from .defaults import *

class SelectCancel(Exception):
    pass

def select(l, prompt):
    print()
    print(prompt)
    for i, d in enumerate(l):
        print("%-3d: %s"%(i,d))
    while True:
        i = input("Enter selection (or 'q' to quit): ")
        if i == 'q':
            raise SelectCancel
        try:
            n = int(i)
            s = l[n]
        except Exception:
            print("%r is not a valid selection."%i)
            continue
        return s

def _ref_choose_version(defaults):
    l = os.listdir(defaults)
    l.sort()
    return select(l, "Select version number")

def _sort_types(s):
    """ Sort 'Mag' before 'Air' bioreactors """
    s = s.lower()
    parts = s.split()
    am = parts[0]
    if am not in ("mag", "air"):
        return (2, am, 0, 0)
    sz = parts[1]
    date = parts[-1]
    if am.startswith("mag"):
        i = 0
    elif am.startswith("air"):
        i = 1
    return (i, am, int(sz), date)    

def _ref_choose_config(defaults, version):
    fp = os.path.join(defaults, version)
    return select(sorted(os.listdir(fp), key=_sort_types), "Select Bioreactor Type")

def choose_reference(version=None, bioconf=None, defaults=def_defaults):
    """
    version : name of version folder
    bioconf    : bioreactor config folder in version folder
    defaults: filepath to default configs directory
    """
    if version is None:
        version = _ref_choose_version(defaults)
    if version is None:
        return
    if bioconf is None:
        bioconf = _ref_choose_config(defaults, version)
    if bioconf is None:
        return
    return os.path.join(defaults, version, bioconf)
    
def get_files(fp):
    return {os.path.splitext(f.lower())[0]: os.path.join(fp,f) for f in os.listdir(fp)}

def _sort_customer(s):
    sn, date = s.lower().split()
    return (datetime.datetime.strptime(date, "%y%m%d"),sn)
    
def choose_customer(sn=None, backups=def_backups):
    if sn is None:
        sn = select(sorted(os.listdir(backups), key=_sort_customer), "Select Backup Folder:")
    return os.path.join(backups, sn)