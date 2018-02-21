try:
    from .matchers import *
except ImportError:
    from matchers import *


# States
def _make_stuff(nname, mapname, *args):
    g = globals()
    enst = list(enumerate(args))
    for i, s in enst:
        g[s] = i
    g[nname] = 3
    g[mapname] = {s:n for s,n in enst}

_make_stuff("N_INPUTS", "INPUT2NAME", "IN_NONE", "IN_HEADER", "IN_FRS", "IN_LINE")

class BackupIterator():
    def __init__(self, it):
        self.it = list(it)
        self.i = 0
        self.m = len(it)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.i >= self.m:
            raise StopIteration
        else:
            rv = self.it[self.i]
            self.i += 1
            return rv

    def backup(self):
        self.i -= 1
        if self.i < 0:
            self.i = 0

    def peek(self):
        return self.it[self.i]


class _IssueParserSM():
    def __init__(self):
        self.lines_iter = BackupIterator(())
        self.hist = []

    def parse(self, text):
        self.lines_iter = BackupIterator(text.splitlines())
        self.hist = []

    def next(self):
        try:
            return self.lines_iter.next()
        except StopIteration:
            return None

    def backup(self):
        self.lines_iter.backup()

    def read_section(self):
        lines = []
        while True:
            l = self.next()
            if l is None:
                break
            if toplevel_match(l):
                self.backup()
                break
            m = header_match(l)
            if m:
                _, _, f, _, suffix = m.groups()
                if frs_match(f):
                    if suffix:
                        l = f + ": " + suffix
                    else:
                        l = f
            self.hist.append(("IN_LINE", l))
            lines.append(l)
        return "\n".join(lines)

    def read_inner(self):
        section = "Description"
        while True:
            l = self.next()
            if l is None:
                break
            m = toplevel_match(l)
            if m and is_toplevel(m):
                ind, pre, header, post, suffix = m.groups()
                if suffix is not None:
                    section = header + ": " + suffix
                else:
                    section = header
                self.hist.append(("IN_HEADER", l))
            else:
                self.backup()
            yield section, self.read_section()

    def read(self):
        rv = DictList()
        for s, t in self.read_inner():
            rv.add(s,t)
        return rv

class DictList():
    def __init__(self):
        self.vl = []
        self.kl = []
        self.d = {}
        self.warnings = 0

    def add(self, k, v):
        if k in self.d:
            print("Duplicate Key Warning (%r)"%k)
            self.warnings += 1
        self.kl.append(k)
        self.vl.append(v)
        self.d[k] = v

    def __getitem__(self, k):
        try:
            return self.d[k]
        except KeyError:
            pass
        try:
            return self.vl[k]
        except (IndexError, TypeError):
            pass
        raise KeyError(k)

    def __setitem__(self, k, v):
        self.add(k,v)

    def __delitem__(self, k):
        v = self.d[k]
        del self.d[k]
        i = self.vl.index(v)
        del self.kl[i]
        del self.vl[i]

    append = add

    def insert(self, k, i, v):
        self.kl.insert(i, k)
        self.vl.insert(i, v)
        self.d[k] = v

    def __iter__(self):
        for k,v in zip(self.kl, self.vl):
            yield k,v

    def __repr__(self):
        return "DictList(%s)"%(", ".join("(%r, %s"%(k,_reprify(v)) for k,v in self.d.items()))

    def __contains__(self, key):
        return key in self.d

def _reprify(o):
    if isinstance(o, dict):
        return "{...}"
    elif isinstance(o, list):
        return "[...]"
    elif isinstance(o, tuple):
        return "(...)"
    else:
        return repr(o)

class IssuesExtractor():
    def __init__(self, issues=None):
        self.issues = issues or []
        
    def extract(self, section):
        sections = self._extract_all()
        got = []
        for iss, sec in sections:
            if section in sec:
                got.append((iss, sec[section]))
        return got
        
    def _extract_all(self):
        all_sections = []
        p = _IssueParserSM()
        for i in self.issues:
            p.parse(i.description or "")
            sections = p.read()
            if sections.warnings:
                print("Got %d warning(s) while parsing issue #%d\n"%(sections.warnings, i.id))
            all_sections.append((i, sections))
        return all_sections