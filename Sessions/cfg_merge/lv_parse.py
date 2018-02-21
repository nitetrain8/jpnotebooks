import json
try:
    import lxml
    import lxml.etree as libxml
except ImportError:
    import xml.etree.ElementTree as libxml
from collections import OrderedDict

class LVType():
    def __init__(self, typ, name, val):
        self.type = typ
        self.name = name
        self._val = 0
        self.val = val

    @property
    def val(self):
        return self._val
    @val.setter
    def val(self, v):
        v = self._check(v)
        self._val = v

    def _check(self, v):
        return v
        
    def isiter(self):
        return hasattr(self, "__iter__")
        
    def dump(self, ind=0):
        s = ind*" "
        if self.type == "Cluster" or self.type == "Array":
            print(s+self.name+" "+self.type)
            for v in self.val:
                v.dump(ind+1)
        else:
            print(s+self.name + " " + self.type+" "+repr(self.val))

    def toxml(self):
        b = []
        self._toxml(b)
        return "\n".join(b)
    
    def _toxml(self, b):
        """ Write lines to buffer b"""
        raise NotImplementedError

    def _todict(self):
        return {self.name: self.val}

    def tojson(self, **kw):
        return json.dumps(self._todict(), **kw)

    def tostr(self):
        return str(self)


class LVSimpleType(LVType):
    def _todict(self):
        return self.val

    def _toxml(self, b):
        b.append("<%s>"%self.type)
        b.append("<Name>%s</Name>"%self.name)
        b.append("<Val>%s</Val>"%self.tostr())
        b.append("</%s>"%self.type)


class LVInt(LVSimpleType):
    def _check(self, v):
        return int(v)
    def tostr(self):
        return "%d" % self.val


class LVFloat(LVSimpleType):
    def _check(self, v):
        return float(v)
        
    def tostr(self):
        if self.val < 1:
            return "%.5e"%self.val
        else:
            return "%.5f" % self.val


class LVCluster(LVType):
    def __iter__(self):
        return iter(self.val)

    def _todict(self):
        return {v.name: v._todict() for v in self.val}

    def _toxml(self, b):
        b.append("<Cluster>")
        b.append("<Name>%s</Name>"%self.name)
        b.append("<NumElts>%d</NumElts>"%len(self.val))
        for v in self.val:
            v._toxml(b)
        b.append("</Cluster>")

    def lookup(self, key):
        for v in self.val:
            if v.name == key:
                return v
        raise KeyError(key)
            
    __getitem__ = lookup

    def get(self, key, default=None):
        try:
            return self.lookup(key)
        except KeyError:
            return default

class LVArray(LVType):
    def __iter__(self):
        return iter(self.val)

    def _toxml(self, b):
        b.append("<Array>")
        b.append("<Name>%s</Name>"%self.name)
        b.append("<Dimsize>%d</Dimsize>"%len(self.val))
        for v in self.val:
            v._toxml(b)
        b.append("</Array>")

    def _todict(self):
        return [v._todict() for v in self.val]

    def lookup(self, key):
        return self.val[key]

    def get(self, key, default=None):
        try:
            return self.lookup(key)
        except IndexError:
            return default

    __getitem__ = lookup


class LVChoice(LVType):
    def _todict(self):
        return self.val

    def _toxml(self, b):
        b.append("<%s>%s</%s>"%(self.type, self.val, self.type))


def _lv_parse_cluster(typ, e):
    name = e[0].text
    val = []
    for el in e[2:]:
        v = lv_parse(el)
        val.append(v)
    return LVCluster(typ, name, val)

def _lv_parse_float(typ, e):
    name = e[0].text
    val = float(e[1].text)
    return LVFloat(typ, name, val)

def _lv_parse_int(typ, e):
    name = e[0].text
    val = int(e[1].text)
    return LVInt(typ, name, val)

def _lv_parse_ew(typ, e):
    # this only occurs in OLD (1.3 and before)
    # config files, for bioreactor model. 
    return LVChoice(typ, e[0].text, list(e[1:-1]))

_skip = object()

_lv_parse_types = {
    'Cluster': _lv_parse_cluster,
    "DBL"    : _lv_parse_float,
    "SGL": _lv_parse_float,
    'U8': _lv_parse_int,
    'U16': _lv_parse_int,
    'U32': _lv_parse_int,
    'I8': _lv_parse_int,
    'I16': _lv_parse_int,
    'I32': _lv_parse_int,
    'EW': _lv_parse_ew,
}

def lv_parse(e):
    typ = e.tag
    func = _lv_parse_types[typ]
    if func is not _skip:
        return func(typ, e)


def _flatten(lv, sep, d, pre):
    if lv.isiter():
        for v in lv:
            if pre is None:
                n = v.name
            else:
                n = sep.join((pre, v.name))
            _flatten(v, sep, d, n)
    else:
        d[pre] = lv.tostr()


def flatten(lv, sep=".", pre=True):
    # recursively flatten a tree of LV types into a list
    # of only leaf nodes. 
    # hierarchy is represented by dotted names.
    # or, pass a different sep character instead of a dot.
    rv = OrderedDict()
    _flatten(lv, sep, rv, lv.name if pre else None)
    return rv

def lv_parse_string(s):
    return lv_parse(libxml.fromstring(s))

def lv_parse_file(f):
    return lv_parse(libxml.parse(f))

def dump(e, ind=0):
    inds = " "*ind
    print(inds+"<%s>"%e.tag)
    for el in e:
        if len(el):
            dump(el, ind+1)
        else:
            print(inds+"<%s>%s</%s>"%(el.tag, el.text, el.tag))
    print(inds+"</%s>"%e.tag)