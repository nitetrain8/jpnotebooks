from collections import OrderedDict
from .logger_settings import _parse_logger
import os
from .logger import log1, log2

def _parse_recipes(fp):
    with open(fp, 'r') as f:
        lines = f.read().splitlines()
        
    recipes = OrderedDict()
    it = iter(lines)
    while True:
        line = next(it, None)
        if line is None:break
        if line == "":continue
        if not line.startswith("Func"):
            raise ValueError("Malformed config file")
        _, name = line.split(" ",1)
        recipes[name] = rec = []
        while True:
            line = next(it, None)
            if not line: break
            rec.append(line)
    return recipes

def _rmatch(a,b):
    if len(a) != len(b):
        return False
    for l1, l2 in zip(a,b):
        if l1 != l2:
            return False
    return True

def update_recipes(custf, oldf, newf, outd):
    cf = custf['bioreactor recipes']
    of = oldf['bioreactor recipes']
    nf = newf['bioreactor recipes']
    
    cl = _parse_recipes(cf)
    ol = _parse_recipes(of)
    nl = _parse_recipes(nf)
    
    for r in cl:
        cv = cl[r]
        ov = ol.get(r)
        
        if ov and not _rmatch(cv,ov):
            log1("%-30s %r"%("Default Recipe Mismatch:",r))
        if r not in nl:
            nl[r] = cv
            log1("%-30s %r"%("Adding recipe to list:",r))
    
    # sanity check w/ list of logger settings
    log = _parse_logger(newf['logger settings'])
    for r in nl:
        for line in nl[r]:
            parts = line.split()
            if not parts:
                continue
            elif parts[0] == "Set":
                v = parts[1].strip("\"")
            elif parts[1] == "until":  # wait until step 
                v = parts[2].strip("\"")
            else:  # wait step
                continue
            if v not in log:
                    log1("%-30s %r -> %r"%("Bad Logger Variable!",r, v))

    outf = os.path.join(outd, "Bioreactor Recipes.cfg")
    with open(outf, 'w') as f:
        for r in nl:
            lines = nl[r]
            f.write("Func %s\n"%r)
            f.write("\n".join(lines))
            f.write("\n")
    