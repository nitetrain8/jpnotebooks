from collections import OrderedDict
import os
from .logger import log1


def _parse_logger(fp):
    with open(fp, 'r') as f:
        f.readline()  # discard header
        lines = f.read().splitlines()
    log = OrderedDict()
    for line in lines:
        name, db, rec, grp = line.split("\t")
        log[name] = (db, rec, grp)
    return log

def _lfmt(v):
    d, r, _ = v
    return "%7s %9s"%(repr(d),repr(r))

def _skipname(n):
    for p in "Alpha", "Beta", "Gamma", "Linearity":
        if "Control%s"%p in n:
            return True
    if "CalMFC" in n:
        return True
    if "DOO2ControlMag" in n or "DOO2ControlAir" in n:
        return True
    return False

def update_logger_settings_v2_v3(fn, custf, oldf, newf, outd):
    outf = os.path.join(outd, "Logger Settings%s.sys"%(" " + fn if fn else ""))
    cf = custf["logger settings%s"%(" " + fn if fn else "")]
    of = oldf["logger settings"]
    nf = newf["logger settings"]
    cl = _parse_logger(cf)
    ol = _parse_logger(of)
    nl = _parse_logger(nf)
    for var in nl:
        if _skipname(var):
            continue
        if var in cl:
            cv = cl.pop(var)
            ov = ol.pop(var, None)
            if ov is None:
                log1("Missing! %35s: In ref but not in customer file"%var)
                continue
            nv = nl[var]
            if cv != ov:
                nl[var] = cv
                log1("Updating %35s: %15s -> %15s"%(var, _lfmt(nv), _lfmt(cv)))
        else:
            pass
            # Show list of old variables which did not get updated
            # print("Not found: %35s"%var)
    # old vars 
    for var in cl:
        cv = cl[var]
        ov = ol.get(var)
        if ov is None:
            continue
        if cv != ov:
            log1("Not Updated: %35s %s -> %s"%(var, _lfmt(ov), _lfmt(cv)))
        elif var not in nl:
            log1("Not Updated: %35s"%var)
        # print(var)
    # to file
    b = ["Data Name\tThreshold change to record\tRecord\tGroup"]
    for var in nl:
        db, rec, grp = nl[var]
        b.append("\t".join((var, db, rec, grp)))
    with open(outf, 'w') as f:
        f.write("\n".join(b))

def _lgv(l,v):
    va = l.get(v)
    if va is None:
        return None
    a,b, _ = va
    return "%.4f %s" % (float(a), b[0])

def compare_logger(fn, custf, oldf, newf, change_only=False):
    cf = custf["logger settings%s"%(" " + fn if fn else "")]
    of = oldf["logger settings"]
    nf = newf["logger settings"]
    cl = _parse_logger(cf)
    ol = _parse_logger(of)
    nl = _parse_logger(nf)

    log1("%-47s              Contents              |  Matches  | Restore"%"")
    log1("%-47s  Cust File | Old File  | New File  | CDI  PBS  | Action"%("Variable"))
    for var in nl:
        if var in cl:
            cv = _lgv(cl, var)
            ov = _lgv(ol, var)
            nv = _lgv(nl, var)
            if cv is None or ov is None:
                cs = os = ns = ""
                m = "Missing"
            elif nv == ov and ov == cv:
                if change_only:
                    continue
                else:
                    cs = os = ns = ""
                    m = "No Change"
            elif nv != ov and ov == cv:
                cs = ""
                os = str(ov)
                ns = str(nv)
                m  = "N    N"
            elif nv == ov and ov != cv:
                cs = str(cv)
                os = ""
                ns = str(nv)
                m  = "N    Y"
            elif nv == cv and ov != cv:
                cs = str(cv)
                os = ""
                ns = str(nv)
                m  = "Y    N"
            elif nv != cv and cv != ov:
                cs = str(cv)
                os = str(ov)
                ns = str(nv)
                m  = "N    N"
            else:
                cs = cv
                os = ov
                ns = nv
                m  = "???"
                assert None not in (cs, os, ns, m)
        else:
            cs = os = ns = ""
            m = "New"    
        log1("%-47s: %-10s| %-10s| %-10s|%-10s | "%(var, cs, os, ns, m))

    for var in cl:
        if var not in nl:
            cv = _lgv(cl, var)
            ov = _lgv(ol, var)
            cs = str(cv)
            os = str(ov)
            if cs == os:
                cs = ""
            ns = ""
            m  = "DNE"
            log1("%-47s: %-10s| %-10s| %-10s|%-10s | "%(var, cs, os, ns, m))
