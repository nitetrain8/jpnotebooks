import os

from .lv_parse import lv_parse
import lxml.etree
from .logger import log1

def _parse_sysvars(fp):
    with open(fp, 'rb') as f:
        e = lxml.etree.parse(f).getroot()
    return lv_parse(e)

def _namefix(g,n):
    """ Some names got updated, normalized, etc in v2->v3 """
    if g == "Temperature":
        if n == "Mismatch Thresh (C)":
            return "Max Delta (C)"
    elif g == "pH":
        if n == "Rate Fail Delta PV":
            return "Fail Rate (pH/min)"
        elif n == "Rate Fail Delta Time (s)":
            # new SysVar, old used 1 min hardcoded
            return -1
        elif n == "Mismatch Thresh":
            return "Max Delta"
    elif g == "DO":
        if n == "Mismatch Thresh (DO%)":
            return "Max Delta"
    elif g == "Safety":
        if n == "Max Temp (C)":
            return "Main Temp Max (C)"
    # exclude PID parameters
    for p in "P Gain", "I Time", "D Time", "Alpha", "Gamma", "Beta", "Linearity":
        if p in n:
            return -2
    return n

def update_sysvars_v2_v3(fn, custf, oldf, newf, outd):
    outf = os.path.join(outd, "system variables%s.sys"%(" " + fn if fn else ""))
    cf = custf['system variables%s'%(" " + fn if fn else "")]
    of = oldf['system variables']
    nf = newf['system variables']
    cf = _parse_sysvars(cf)
    of = _parse_sysvars(of)
    nf = _parse_sysvars(nf)
    
    for group in nf:
        cg = cf.lookup(group.name)
        og = of.lookup(group.name)
        for val in group:
            v2n = _namefix(group.name, val.name)
            if v2n == -1:  # changed functionality etc, so we should skip
                # log1("Skipping '%s.%s'"%(group.name, val.name))
                continue
            gv = "'%s.%s'"%(group.name, val.name)
            try:
                cv = cg.lookup(v2n)
                ov = og.lookup(v2n)
                if cv.val != ov.val:
                    log1("Updating : %42s: %r -> %r"%(gv, val.val, cv.val))
                    val.val = cv.val
            except KeyError:
                log1("Not Found: %42s"%(gv))
                
    with open(outf, 'w') as f:
        f.write(nf.toxml())

def update_sysvars_v2_v3_2(fn, custf, oldf, newf, outd):
    outf = os.path.join(outd, "system variables%s.sys"%(" " + fn if fn else ""))
    cf = custf['system variables%s'%(" " + fn if fn else "")]
    of = oldf['system variables']
    nf = newf['system variables']
    cf = _parse_sysvars(cf)
    of = _parse_sysvars(of)
    nf = _parse_sysvars(nf)
    
    for group in nf:
        cg = cf.lookup(group.name)
        og = of.lookup(group.name)
        for val in group:
            v2n = _namefix(group.name, val.name)
            gv = "'%s.%s'"%(group.name, val.name)
            if isinstance(v2n, int):  # changed functionality etc, so we should skip
                if v2n == -1:
                    log1("%42s %s"%(gv, "New Function"))
                elif v2n == -2:
                    log1("%42s %s"%(gv, "PID Tuning Changed"))
                # log1("Skipping '%s.%s'"%(group.name, val.name))
                continue
            try:
                log1("%42s %s %s %s" % (gv, og.lookup(v2n).val, cg.lookup(v2n).val, val.val))
            except KeyError:
                log1("Not Found: %42s"%(gv))
                
    with open(outf, 'w') as f:
        f.write(nf.toxml())

def compare_sysvars(fn, custf, oldf, newf, change_only=False):
    cf = custf['system variables%s'%(" " + fn if fn else "")]
    of = oldf['system variables']
    nf = newf['system variables']
    cf = _parse_sysvars(cf)
    of = _parse_sysvars(of)
    nf = _parse_sysvars(nf)
    log1("%-42s              Contents              |  Matches  | Restore"%"")
    log1("%-42s  Cust File | Old File  | New File  | CDI  PBS  | Action"%"Group.Variable")
    for group in nf:
        cg = cf.lookup(group.name)
        og = of.lookup(group.name)
        for val in group:
            v2n = _namefix(group.name, val.name)
            gn = "'%s.%s'"%(group.name, val.name)
            cs = os = ns = m = None
            if isinstance(v2n, int):  # changed functionality etc, so we should skip
                if v2n == -1:
                    cs = os = ns = ""
                    m = "New"
                elif v2n == -2:
                    cs = os = ns = ""
                    m = "PID"
            else:
                try:
                    cv = cg.lookup(v2n)
                    ov = og.lookup(v2n)
                    nv = val
                except KeyError:
                    cs = os = ns = ""
                    m = "Not Found"
                else:
                    if nv.val == ov.val and ov.val == cv.val:
                        if change_only:
                            continue
                        else:
                            cs = os = ns = ""
                            m = "No Change"
                    elif nv.val != ov.val and ov.val == cv.val:
                        cs = ""
                        os = ov.tostr()
                        ns = nv.tostr()
                        m  = "N    N"
                    elif nv.val == ov.val and ov.val != cv.val:
                        cs = cv.tostr()
                        os = ""
                        ns = nv.tostr()
                        m  = "N    Y"
                    elif nv.val == cv.val and ov.val != cv.val:
                        cs = cv.tostr()
                        os = ""
                        ns = nv.tostr()
                        m  = "Y    N"
                    elif nv.val != cv.val and cv.val != ov.val:
                        cs = cv.tostr()
                        os = ov.tostr()
                        ns = nv.tostr()
                        m  = "N    N"
                    else:
                        cs = cv.tostr()
                        os = ov.tostr()
                        ns = nv.tostr()
                        m  = "???"
            assert None not in (cs, os, ns, m)
            log1("%-42s: %-10s| %-10s| %-10s|%-10s | "%(gn, cs, os, ns, m))
            