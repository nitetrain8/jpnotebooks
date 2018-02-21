# v2 -> v3 alarms update script
from collections import OrderedDict
import os
from .logger import log1, log2

def _parse_alm_file2(f):
    h = f.readline().lower()
    h = tuple(s.strip() for s in h.split(","))
    h2_1 = ("name", "audable", "ignore")
    h2_2 = ("name", "audible", "ignore")
    if h == h2_1 or h == h2_2:  
        v = 2
    elif h == ("name", "notify", "audible"):
        v = 3
    else:
        raise ValueError("Couldn't determine version: %s"%(repr(h)))
    alms = OrderedDict()
    for line in f:
        alm, a,b = line.strip().split(",")
        if v == 2:
            a,b = b,a
            a = "1" if a == "0" else "0"
        alms[alm] = a,b
    return alms
        
def _parse_alm_file(fp):
    with open(fp, 'r') as f:
        return _parse_alm_file2(f)
    
def _alm_reconcile(alm, c,o,n):
    nv = n[alm]
    try:
        cv = c[alm]
        ov = o[alm]
        if cv != ov:
            if cv != nv:
                log1("Updating : %31s: %s -> %r"%(repr(alm), nv, cv))
            else:
                log1("Updated  : %31s"%repr(alm))
            return cv
        else:
            #print("Default: %r: %r"%(alm, n[alm]))
            return nv
    except KeyError:
        return nv
    
    
def _update_alms(custf, oldf, newf, outf):
    c = _parse_alm_file(custf)
    o = _parse_alm_file(oldf)
    n = _parse_alm_file(newf)
    
    with open(outf, 'w') as f:
        f.write("Name, Notify, Audible\n")
        log1("                                              N    A        N    A")
        for alm in n:
            no,a = _alm_reconcile(alm,c,o,n)
            f.write("%s,%s,%s\n"%(alm,no,a))
        
def update_alarms_v2_v3(suffix, custf, oldf, newf, outd):
    name, name2 = suffix
    if name:
        name = "alarms %s"%name
    else:
        name = "alarms"
    name = name.lower()
    if name2:
        name2 = "alarms %s"%name2
    else:
        name2 = "alarms"
    name2 = name2.lower()
    cf = custf[name]
    of = oldf[name2]
    nf = newf[name2]
    log2("Scanning %r"%name.title())
    outf = os.path.join(outd, name.title()+".alm")
    _update_alms(cf, of, nf, outf)


def _lines(fp):
    with open(fp, 'r') as f:
        return f.read().splitlines()


def compare_alarms(suffix, custf, oldf, newf, change_only=False):
    name, name2 = suffix
    if name:
        name = "alarms %s"%name
    else:
        name = "alarms"
    name = name.lower()
    if name2:
        name2 = "alarms %s"%name2
    else:
        name2 = "alarms"
    name2 = name2.lower()
    cf = custf[name]
    of = oldf[name2]
    nf = newf[name2]
    log2("Scanning %r"%name.title())
    _cmp_alm(cf, of, nf, change_only)


def _almrpr(a):
    return "N:%d A:%d"%tuple(map(int, a))

def _cmp_alm(custf, oldf, newf, change_only):
    c = _parse_alm_file(custf)
    o = _parse_alm_file(oldf)
    n = _parse_alm_file(newf)
    log1("                                            Contents              |  Matches  | Restore")
    log1("Alarm                           Cust File | Old File  | New File  | CDI  PBS  | Action")
    for alm in n:
        nv = n[alm]
        cv = c.get(alm, None)
        ov = o.get(alm, None)
        if cv is None or ov is None:
            cs = os = ""
            ns = _almrpr(nv)
            m = " New "
        elif nv == ov and ov == cv:
            if change_only:
                continue
            else:
                cs = os = ns = ""
                m = "No Change"
        elif nv != ov and ov == cv:
            cs = ""
            os = _almrpr(ov)
            ns = _almrpr(nv)
            m  = "N    N"
        elif nv == ov and ov != cv:
            cs = _almrpr(cv)
            os = ""
            ns = _almrpr(nv)
            m  = "N    Y"
        elif nv == cv and ov != cv:
            cs = _almrpr(cv)
            os = ""
            ns = _almrpr(nv)
            m  = "Y    N"
        elif nv != cv and cv != ov:
            cs = _almrpr(cv)
            os = _almrpr(ov)
            ns = _almrpr(nv)
            m  = "N    N"
        else:
            cs = _almrpr(cv)
            os = _almrpr(ov)
            ns = _almrpr(nv)
            m  = "???"
        log1("%-30s: %-10s| %-10s| %-10s|%-10s | "%(alm, cs, os, ns, m))

    for alm in c:
        if alm not in n:
            cv = c.get(alm)
            ov = o.get(alm)
            cs = _almrpr(cv)
            os = _almrpr(ov) if ov else ""
            if cv == ov:
                cs = ""
            ns = ""
            m = "DNE"
            log1("%-30s: %-10s| %-10s| %-10s|%-10s | "%(alm, cs, os, ns, m))
