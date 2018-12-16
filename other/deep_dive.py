# coding: utf-8

import os
import clipboard
import csv

dld = "C:/users/administrator/downloads"
dld = os.path.normpath(dld)

def gfp(fn):
    return os.path.join(dld, fn)

def ofp():
    with open(gfp("Warcraft Logs - Combat Analysis for Warcraft.csv"), 'r', encoding="utf-8-sig") as f:
     return f.read()
     
def get():
    lines = pfp()
    header = lines[0]
    hidx = {h:i for i, h in enumerate(header)}
    plines = lines[1:]
    out = []
    def vals(p): return p[hidx["Name"]], p[hidx["DPS"]]
    for p in plines:
        out.append("    %-15s %s"%vals(p))
    s = "\n".join(out)
    clipboard.copy(s)
       
def pfp():
    s = ofp()
    return list(csv.reader(s.splitlines()))
    
def get():
    lines = pfp()
    header = lines[0]
    hidx = {h:i for i, h in enumerate(header)}
    plines = lines[1:]
    out = []
    def vals(p): return p[hidx["Name"]], p[hidx["Amount"]].split("%")[-1]
    for p in plines:
        out.append("    %-15s %s"%vals(p))
    s = "\n".join(out)
    clipboard.copy(s)
      