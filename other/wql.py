import requests
import json
import datetime
import functools
from urllib.parse import urlencode

class Api():
    verbose = True
    _api_cache_ = {}
    def __init__(self, key):
        self.key = key
        self.sess = requests.Session()
        self.base = "https://www.warcraftlogs.com/v1"
        self.zones_ = None
        
    @property
    def zones(self):
        if self.zones_ is None:
            raw = self.request("/zones")
            self.zones_ = Zones(self, raw)
        return self.zones_
        
    def request(self, path, **kw):
        kw['api_key'] = self.key
        qs = make_query(**kw)
        p2 = path + qs
        url = self.base + p2
        if url in self._api_cache_:
            return self._api_cache_[url]
        if self.verbose:
            print("Requesting %r"%p2)
        r = self.sess.get(url)
        r.raise_for_status()
        raw = json.loads(r.content.decode())
        self._api_cache_[url] = raw
        return raw
    
    def clear_cache(self):
        self._api_cache_.clear()
        
    def parses(self, character, server, region="US"):
        path = "/parses/character/%s/%s/%s" % (character, server, region)
        raw = self.request(path)
        # flatten specs list
        return raw
    
    def reports(self, guildname, servername, region="US"):
        path = "/reports/guild/%s/%s/%s"%(guildname, servername, region)
        raw = self.request(path)
        return Reports(self, raw)
    
    def fights(self, code):
        path = "/report/fights/%s"%code
        raw = self.request(path)
        return Fights(self, raw, code)
    
    def events(self, id, start, end, **kw):
        path = "/report/events/%s"%id
        raw = self.request(path, start=start, end=end, **kw)
        return mk_struct(raw)

# class struct():
#     def __init__(self, fields):
#         self._fields_ = []
#         for k, v in fields:
#             setattr(self, k, v)
#             self._fields_.append(k)
            
#     def get(self, key, default=None):
#         try:
#             return getattr(self, key)
#         except KeyError:
#             return default
        
#     def __getattr__(self, key):
#         try:
#             return object.__getattr__(self, key)
#         except AttributeError:
#             return None
        
#     def __getitem__(self, key):
#         return getattr(self, key)
            
#     def __repr__(self):
#         return "<struct: %s>" % (", ".join("%s=%s"%(k,getattr(self, k)) for k in self._fields_))
    
class Struct2(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value
        
    def __hash__(self):
        return id(self)
        
# def Struct3(name, fields):
#     argstr = ", ".join("%s=None"%f for f in fields)
#     comma = ", " if argstr else ""
#     attrl = "        ".join("self.%s=%s\n"%f for f in fields)
#     src = """
# class %s():
#     def __init__(self%s%s):
#         %s
# """ % (name, comma, argstr, attrl)
            
def mk_struct(ob):
    if isinstance(ob, list):
        return [mk_struct(ob) for ob in list]
    fields = []
    for k, v in ob.items():
        if isinstance(v, dict):
            v = mk_struct(v)
        elif isinstance(v, list):
            v = mk_list(v)
        fields.append((k,v))
    return Struct2(fields)
        
            
def mk_list(l):
    rv = []
    for ob in l:
        if isinstance(ob, list):
            v = mk_list(ob)
        elif isinstance(ob, dict):
            v = mk_struct(ob)
        else:
            v = ob
        rv.append(v)
    return rv
            

def _ts2dt(t):
    return datetime.datetime.fromtimestamp(t/1000)

def _erepr(s, *a):
    if a:
        s2 = ": " + ", ".join("%r"%r for r in a)
    else:
        s2 = ""
    return "<%s%s>"%(s.__class__.__name__, s2)

def make_query(**kw):
    return "?" + urlencode(kw)

class Encounter():
    def __init__(self, api, d):
        self.api = api
        self.name = d['name']
        self.id = d['id']
        
    def __str__(self):
        return _erepr(self, self.id, self.name)

class Zone():
    def __init__(self, api, d):
        self.api = api
        self.name = d['name']
        self.id = d['id']
        self.encounters = [Encounter(api, e) for e in d.get('encounters', ())]
        
    def __str__(self):
        return _erepr(self, self.id, self.name)
    
    def __eq__(self, other):
        if isinstance(other, Zone):
            return self.id == other.id and self.name == other.name
        elif isinstance(other, int):
            return self.id == other
        elif isinstance(other, str):
            return self.name == other
        else:
            return NotImplemented

class Zones():
    def __init__(self, api, d):
        self.api = api
        self.id2z = {}
        self.n2z = {}
        self._raw = d
        d.append({
            'id': -1,
            'name': "Unknown Zone"
        })
        for c in d:
            z = Zone(api, c)
            self.id2z[z.id] = z
            self.n2z[z.name] = z
            
    def __getitem__(self, key):
        try:
            return self.id2z[key]
        except KeyError:
            pass
        try:
            return self.n2z[key]
        except KeyError:
            pass
        raise KeyError(key)
            

class ParseResult():
    def __init__(self, api, l):
        self.api = api
        self.parses = [Parse(self.api, d) for d in l]
        
class Parse():
    def __init__(self, api, d):
        self.api = api
        self.d = d
    def __getattr__(self, key):
        return self.d[key]
    
    
def mk_finder(box, *args):
    ast = ", ".join("%s=None" % a for a in args)
    if not args:
        ast = "self"
    else:
        ast = "self, " + ast
        
    cs = "        if %s is not None and %s != ob.%s: continue\n"
    continues = "".join(cs%(a, a, a) for a in args)
    src = """
def find(%s):
    rv = []
    for ob in self.%s:
%s
        rv.append(ob)
    return self._from_list(rv)
    """ % (ast, box, continues)
    ns = {}
    exec(src, ns, ns)
    return ns['find']


class Fight():
    def __init__(self, api, report_id, d, friendlies=(), enemies=()):
        self.friendlies = friendlies or Friendlies(api)
        self.enemies = enemies or Enemies(api)
        self.report_id = report_id
        self.api = api
        self.id = d['id']
        self.start_time = d['start_time']
        self.end_time = d['end_time']
        self.boss = d['boss']
        self.size = d['size']
        self.difficulty = d['difficulty']
        self.kill = d['kill']
        self.partial = d['partial']
        self.bossPercentage = d['bossPercentage']
        self.fightPercentage = d['fightPercentage']
        self.lastPhaseForPercentageDisplay = d['lastPhaseForPercentageDisplay']
        self.name = d['name']
        
    def actor(self, id):
        try:
            return self.friendlies[id]
        except KeyError:
            pass
        try:
            return self.enemies[id]
        except KeyError:
            pass
        raise KeyError("%r not found"%id)
        
    def __str__(self):
        return _erepr(self, self.id, self.name)
    
    def events(self, fs, **other):
        start = self.start_time
        rv = []
        while True:
            events = self.api.events(self.report_id, start, self.end_time, filter=fs, **other)
            start = events.nextPageTimestamp
            rv.extend(events.events)
            if start is None or start > f.end_time:
                break
        return rv
    
class Friendly():
    
    PLAYER_TYPES = {
        "Shaman",
        "Mage",
        "Warlock",
        "Druid",
        "DeathKnight",
        "Rogue",
        "Warrior",
        "DemonHunter",
        "Hunter",
        "Monk",
        "Paladin",
        "Priest"
    }
    
    
    def __init__(self, api, d):
        self.api = api
        self.name = d['name']
        self.id = d['id']
        self.type = d['type']
        self.petOwner = d.get('petOwner')  # pets only
        
        # fights is a list of dicts of "id": id for some reason
        self.fights = {f['id'] for f in d['fights']}
        
    def is_pet(self):
        return self.type == 'pet'
    
    def is_player(self):
        return self.type in self.PLAYER_TYPES
        
    def was_present(self, fid):
        return fid in self.fights
    
    def __repr__(self):
        return _erepr(self, self.id, self.name, self.type)
        

class Friendlies():
    def __init__(self, api, d=None):
        self.api = api
        if d is not None:
            self.friendlies = [Friendly(api, f) for f in d]
        else:
            self.friendlies = []
        self._mkdcts()
        
    def _mkdcts(self):
        self.n2f = {f.name: f for f in self.friendlies}
        self.id2f = {f.id: f for f in self.friendlies}
    
    def __getitem__(self, key):
        try:
            return self.n2f[key]
        except KeyError:
            pass
        try:
            return self.id2f[key]
        except KeyError:
            pass
        raise KeyError("%r not found"%key)
        
    def _from_list(self, l):
        cls = self.__class__
        self2 = cls(self.api)
        self2.friendlies = l
        self2._mkdcts()
        return self2

    def players(self):
        return self._from_list([f for f in self.friendlies if f.is_player()])
    
    def were_present(self, fid):
        rv = []
        for f in self:
            if f.was_present(fid):
                rv.append(f)
        return self._from_list(rv)
        
    def __iter__(self):
        return iter(self.friendlies)
    
    find = mk_finder("friendlies", "id", "name", "type")

    
class Fights():
    def __init__(self, api, d=None, report_id=None):
        self.report_id = report_id
        self.api = api
        if d is not None:
            self._raw = d
            self.title = d['title']
            self.owner = d['owner']
            self.start = _ts2dt(d['start'])
            self.end = _ts2dt(d['end'])
            self.zone = api.zones[d['zone']]
            
            lff = []  # list for friends
            lff.extend(d['friendlies'])
            lff.extend(d['friendlyPets'])
            self.friendlies = Friendlies(api, lff)
            
            lfe = []  # list for enemies
            lfe.extend(d['enemies'])
            lfe.extend(d['enemyPets'])
            self.enemies = Enemies(api, lfe)
            
            self.fights = [Fight(api, report_id, f) for f in d['fights'] if f['boss']]  # exclude trash
            for f in self.fights:
                f.friendlies = self.friendlies.were_present(f.id)
                f.enemies = self.enemies.were_present(f.id)
            
    def __iter__(self):
        return iter(self.fights)

    def index(self, i):
        return self.fights[i]
            
    def _from_list(self, l):
        cls = self.__class__
        self2 = cls(self.api, None, self.report_id)
        self2.title = self.title
        self2.owner = self.owner
        self2.start = self.start
        self2.end = self.end
        self2.zone = self.zone
        self2.friendlies = self.friendlies
        self2.fights = l
        return self2
    
    find = mk_finder("fights", "id", "boss", "size", "difficulty", "kill", "name")
    
    def __getitem__(self, key):
        for r in self.fights:
            if r.id == key or r.name == key or r.owner == key:
                return r
        raise KeyError("%r not found"%key)
        
    
class Reports():
    def __init__(self, api, d=None):
        self.api = api
        if d is not None:
            self.reports = [ReportMetadata(api, r) for r in d]
            
    def __iter__(self):
        return iter(self.reports)
        
    def sort(self, key=None, reverse=False):
        self.reports.sort(key=key, reverse=reverse)
            
    def _from_list(self, l):
        cls = self.__class__
        self2 = cls(self.api)
        self2.reports = l
        return self2
        
    def find_owner(self, o):
        return self._from_list([r for r in self.reports if r.owner == o])
    
    def find_id(self, i):
        return self._from_list([r for r in self.reports if r.id == i])
    
    def find_title(self, t):
        return self._from_list([r for r in self.reports if r.title == t])
    
    def find_zone(self, z):
        return self._from_list([r for r in self.reports if r.zone == z])
    
    def find(self, title=None, owner=None, id=None, zone=None, func=None):
        rv = []
        for r in self.reports:
            if title is not None and title != r.title: continue
            if owner is not None and owner != r.owner: continue
            if id is not None and id != r.id: continue
            if zone is not None and zone != r.zone: continue
            if func is not None and not func(r): continue
            rv.append(r)
        return self._from_list(rv)

    def find2(self, cb):
        return self._from_list([r for r in self.reports if cb(r)])
                
        
    def __getitem__(self, key):
        for r in self.reports:
            if r.id == key or r.name == key or r.owner == key:
                return r
        raise KeyError("%r not found"%key)
        
    def index(self, i):
        return self.reports[i]
        
    def __repr__(self):
        return "<Reports: %r>" % self.reports
        
    __str__ = __repr__

class ReportMetadata():
    def __init__(self, api, d):
        self.api = api
        self.end = _ts2dt(d['end'])
        self.id = d['id']
        self.owner = d['owner']
        self.start = _ts2dt(d['start'])
        self.title = d['title']
        self.zone = api.zones[d['zone']]
        
    def fights(self):
        return self.api.fights(self.id)
        
    def __str__(self):
        return _erepr(self, self.title, self.zone.name, self.owner)
    __repr__ = __str__
    
class Enemy():
    def __init__(self, api, d):
        self.api = api
        self.name = d['name']
        self.id = d['id']
        self.type = d['type']
        self.petOwner = d.get('petOwner')  # pets only
        
        # fights is a list of dicts of "id": id for some reason
        self.fights = {f['id'] for f in d['fights']}
        
    def is_pet(self):
        return self.type == 'pet'
    
    def is_player(self):
        return False
        
    def was_present(self, fid):
        return fid in self.fights

    ispet = is_pet
    isplayer = is_player
    waspresent = was_present
    
    def __repr__(self):
        return _erepr(self, self.id, self.name, self.type)
        

class Enemies():
    def __init__(self, api, d=None):
        self.api = api
        if d is not None:
            self.enemies = [Enemy(api, f) for f in d]
        else:
            self.enemies = []
        self._mkdcts()
        
    def _mkdcts(self):
        self.n2f = {f.name: f for f in self.enemies}
        self.id2f = {f.id: f for f in self.enemies}
    
    def __getitem__(self, key):
        try:
            return self.n2f[key]
        except KeyError:
            pass
        try:
            return self.id2f[key]
        except KeyError:
            pass
        raise KeyError("%r not found"%key)
        
    def _from_list(self, l):
        cls = self.__class__
        self2 = cls(self.api)
        self2.enemies = l
        self2._mkdcts()
        return self2
    
    def were_present(self, fid):
        rv = []
        for f in self:
            if f.was_present(fid):
                rv.append(f)
        return self._from_list(rv)
        
    def __iter__(self):
        return iter(self.enemies)
    
    find = mk_finder("enemies", "id", "name", "type")

def events_near(events, ev, before, after):
    rv = []
    b = ev.timestamp - before
    a = ev.timestamp + after
    for e in events:
        if e.timestamp >= b:
            if e.timestamp <= a:
                rv.append(e)
            else:
                break
    return rv

