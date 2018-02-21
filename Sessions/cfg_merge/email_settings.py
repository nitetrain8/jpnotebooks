from collections import OrderedDict
import os
from .logger import log1

def _parse_emails(fp):
    with open(fp, 'r') as f:
        lines = f.read().splitlines()
    emails = OrderedDict()
    for l in lines:
        # There's exactly 1 line in this file that doesn't obey
        # "key,value" format (uses "header1,header2,header3" even though
        # there's only 2 columns for each alarm thing.........)
        key, val = l.split(",",1)
        emails[key] = val
    return emails

def _emailnamefix(n):
    new_keys = ('EnableSSL','Snooze (min)','NI 9476 Error','24 Vdc Mezz Fuse',
                '24 Vdc MFC Fuse','24 Vdc Main Fuse','24 Vdc sbRIO Fuse','12 Vdc Atom Fuse',
                '12 Vdc Mezz Fuse','12 Vdc Mntr Fuse','24 Vdc Fill Pump Fuse','24 Vdc User1 Fuse',
                '24 Vdc Ind DO Fuse','24 Vdc User2 Fuse','24 Vdc User3 Fuse','12 Vdc User2 Fuse',
                '12 Vdc User3 Fuse','Comb Plate Popped','12 Vdc User1 Fuse','Restarted Recipe')
    if n in new_keys or n == "Name":
        return -1
    return n

def update_email_alerts_v2_v3(custf, oldf, newf, outd):
    cf = custf['email alerts settings']
    of = oldf['email alerts settings']
    nf = newf['email alerts settings']

    cl = _parse_emails(cf)
    ol = _parse_emails(of)
    nl = _parse_emails(nf)
    
    for key in nl:
        key2 = _emailnamefix(key)
        if key2 == -1:
            continue
        cv = cl[key2]
        ov = ol[key2]
        nv = nl[key]
        if cv != ov:
            nl[key] = cv
            log1("Updating %20s: %20s -> %s" %(key, nv, cv))
    
    outf = os.path.join(outd, "Email Alerts Settings.xml")
    with open(outf, 'w') as f:
        f.write("\n".join("%s,%s"%(k,nl[k]) for k in nl))


def _eparse(fp):
    with open(fp, 'r') as f:
        t = f.read()
    d = OrderedDict()
    t=t.splitlines()
    for l in t:
        a,b = l.split(",", 1)
        d[a] = b
    return d

def compare_emails(custf, oldf, newf, change_only=False):
    cf = custf['email alerts settings']
    of = oldf['email alerts settings']
    nf = newf['email alerts settings']

    cl = _parse_emails(cf)
    ol = _parse_emails(of)
    nl = _parse_emails(nf)

    log1("%-47s              Contents              |  Matches  | Restore"%"")
    log1("%-47s  Cust File | Old File  | New File  | CDI  PBS  | Action"%("Setting"))
    for alm in nl:
        nv = nl[alm]
        cv = cl.get(alm, None)
        ov = ol.get(alm, None)
        if cv is None or ov is None:
            cs = os = ""
            ns = nv
            m = " New "
        elif nv == ov and ov == cv:
            if change_only:
                continue
            else:
                cs = os = ns = ""
                m = "No Change"
        elif nv != ov and ov == cv:
            cs = ""
            os = ov
            ns = nv
            m  = "N    N"
        elif nv == ov and ov != cv:
            cs = cv
            os = ""
            ns = nv
            m  = "N    Y"
        elif nv == cv and ov != cv:
            cs = cv
            os = ""
            ns = nv
            m  = "Y    N"
        elif nv != cv and cv != ov:
            cs = cv
            os = ov
            ns = nv
            m  = "N    N"
        else:
            cs = cv
            os = ov
            ns = nv
            m  = "???"
        log1("%-30s: %-10s| %-10s| %-10s|%-10s | "%(alm, cs, os, ns, m))

    for alm in cl:
        if alm not in nl:
            cv = cl.get(alm)
            ov = ol.get(alm)
            cs = (cv)
            os = (ov)
            if cv == ov:
                cs = ""
            ns = ""
            m = "DNE"
            log1("%-30s: %-10s| %-10s| %-10s|%-10s | "%(alm, cs, os, ns, m))

