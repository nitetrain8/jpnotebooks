import lxml.etree
from .lv_parse import lv_parse
import os
from .logger import log1, log2

def _parse_calfactors(fp):
    with open(fp, 'rb') as f:
        e = lxml.etree.parse(f).getroot()
    return lv_parse(e)    

def _cfnamefix(n):
    if n == "HarvestDelay(s)":
        return "Harvest Wait Time"
    if "MFC" in n:
        return -1
    return n

def update_calfactors_v2_v3(custf, newf, outd):
    cf = custf["cal factors"]
    nf = newf["cal factors"]
    cl = _parse_calfactors(cf)
    nl = _parse_calfactors(nf)

    # "Harvest" and "MFC Cal X" are the only factors
    # that should potentially be missing
    # note all values are type `LVType` here!
    for nv in nl:
        key = _cfnamefix(nv.name)
        if key == -1:
            continue
        cv = cl.get(key)
        if cv is None:
            if key != "Harvest Wait Time":
                log1("KEY NOT FOUND!!! %r"% key)
            continue
        if nv.name == "HarvestDelay(s)":
            nv.val = cv.val
            log1("Updating %s -> %s" % (nv.name, nv.val))
        else:
            for nv2 in nv:
                cv2 = cv[nv2.name]
                nv2.val = cv2.val
                log1("Updating: %25s -> %8s"%("'%s.%s'"%(nv.name, nv2.name), nv2.val))
        log1("-----------------------------------------------------")
        
    outf = os.path.join(outd, "Cal Factors.cfg")
    with open(outf, 'w') as f:
        f.write(nl.toxml())