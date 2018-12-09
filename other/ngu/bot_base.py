import itertools
from utils import *
from coords import *

import weakref

class SimpleItem():
    def __init__(self, parent, label, x, y):
        if parent is None:
            self._parent = None
        else:
            self._parent = weakref.ref(parent)
        self.label = label
        self.x = x
        self.y = y
        self.items = {}
        
    @property
    def parent(self):
        if self._parent is None:
            p = self
        else:
            p = self._parent()
            if p is None:
                p = self
        return p
    
    def hover_mouse(self):
        x, y = translate_coord2(self.x, self.y)
        mouse_move(x, y)
    
    def click(self):
        x, y = translate_coord2(self.x, self.y)
        left_click(x, y)
        
    def add_item(self, label, item):
        if label in self.items:
            raise ValueError("Item '%s' already exists in '%s'"%(label, self.get_full_name()))
        self.items[label] = item
            
    def get_full_name(self):
        name = self.label
        p = self
        while True:
            if p is None or p.parent is p:
                break
            p = p.parent
            name = p.label + "." + name
        return name
    
    def lookup(self, key):
        parts = key.split(".")
        item = self
        for p in parts:
            item = item.items.get(p)
            if item is None:
                raise KeyError(key)
        return item
    
    def click_sequence(self, *tags, st=0.2):
        it = self
        for t in tags:
            it = it.lookup(t)
            it.click()
            sleep(st)
    
    get = __getitem__ = lookup  # alias

class BasicButton(SimpleItem):
    pass

class SimpleMenu(SimpleItem):
        
    def add_button(self, label, x, y):
        btn = BasicButton(self, label, x, y)
        self.add_item(label, btn)
        return btn
        
    def add_menu(self, label, x, y):
        menu = SimpleMenu(self, label, x, y)
        self.add_item(label, menu)
        return menu
        
    def add_menu_with_buttons(self, label, x, y, buttons):
        menu = SimpleMenu(self, label, x, y)
        self.add_item(label, menu)
        for b, (x,y) in buttons:
            menu.add_button(b, x, y)
        return menu



class TrainingInfo():
    def __init__(self, start_time=None):
        start_time = start_time or time()
        self.level = ""
#         self.eps = eps
        self.start_time = start_time
        self.current_level_time = start_time
        self.thresholds = [
            ('idle', 0),
            ('regular', 5000),
            ('strong', 10000),
            ('parry', 15000),
            ('piercing', 20000),
            ('ultimate', 25000)
        ]
        self.idx = -1
        
    def training_done(self):
        return self.level == "ultimate" and time() - self.current_level_time > 300  # wild guess
        
    def time_to_cap(self):
        total = sum(t[1] for t in self.thresholds)
        time_req = total / 50
        elapsed = time() - self.start_time
        return time_req - elapsed
        
    def can_train_next(self):
        if self.idx == len(self.thresholds) - 1:
            return ""
        elapsed = time() - self.current_level_time - 1
        levels = elapsed * 50 
        lvl, thresh = self.thresholds[self.idx + 1]
        if levels > thresh:
            return lvl
        return ""
    
    def energy_capped_for_current(self):
        # Todo: calculate current energy & required cap energy
        return True  
                
    def advance(self):
        if self.idx == len(self.thresholds) - 1:
            return
        self.idx += 1
        self.current_level_time = time()
        self.level = self.thresholds[self.idx][0]

class Game(SimpleMenu):
    def __init__(self, stats):
        super().__init__(None, "Game", 0, 0)
        self.current_menu = ""
        self.stats = stats
        self.training = TrainingInfo()
        self.start_time = time()
        self.current_adventure = ""
        
    def run(self, start_time=None):
        self.start_time = start_time or time()
        
        # new game actions
        # TODO: intelligently calculate whether we actually have
        # enough energy to cap training, rather than this hardcoded wait
        wait(2)  # let energy build
        self.train()
        wait(2)  # let attack build
        self.nuke()
        wait(3)  # let nuke kill the bosses
        self.adventure()
        
        actions = self.train, self.adventure, self.spend_idle_energy, self.spend_idle_magic, self.nuke
        action_queue = itertools.cycle(actions)
        
        while True:
            if right_click_down():
                return  # abort
            if self.training.time_to_cap() <= 0:
                break
            next(action_queue)()
            sleep(0.1)
        self.rebirth()
            
    def rebirth(self):
        rb = self.lookup('rebirth')
        rb.click()
        wait(0.1)
        rb.lookup('rebirth').click()
        wait(0.1)
        rb.lookup('yes').click()        
        wait(0.1)
        
    def spend_idle_magic(self):
        best_spell = "tack"
        self.click_sequence("blood_magic", best_spell + "_plus")
            
    def spend_idle_energy(self):
        if not self.training.energy_capped_for_current():
            self.click_sequence("basic_training", self.training.level + "_cap")
        else:
            # use energy on best ROI for total dps
            self.click_sequence("augmentation", "safety_scissors_plus")
            
    def nuke(self):
        self.click_sequence("fight_boss", "nuke")
        
    def select_best_idle_adventure(self):
        return 'forest'
        
    def adventure(self):
        adv = self.select_best_idle_adventure()
#         if adv != self.current_adventure:
        self.click_sequence("adventure", "adventure_zones", adv, st=1)
            
        
    def begin(self):
        #self.click_sequence("rebirth", "rebirth.rebirth", "rebirth.yes")
        self.start_time = time()
        
    def current_time(self):
        return time() - self.start_time
    
    def train(self):
        lvl = self.training.can_train_next()
        if lvl:
            send_key('r')
            sleep(0.1)
            self.click_sequence("basic_training", lvl + "_cap")
            self.training.advance()
        

def init_game(game):
    FB = {l:c for l,c in FEATURE_BUTTONS}
    for lbl, buttons in SIMPLE_MENUS:
        x, y = FB[lbl]
        game.add_menu_with_buttons(lbl, x, y, buttons)

    # adventure
    x, y = FB['adventure']
    adv = game.add_menu('adventure', x, y)
    x, y = ADVENTURE_ZONE_MENU
    az = adv.add_menu('adventure_zones', x, y)
    for b, (x,y) in ADVENTURE_ZONES:
        az.add_button(b, x, y)
        
# game = Game(stats)
# init_game(game)

import math

GAME_INIT = 0
GAME_REBIRTH = 1
GAME_GAIN = 2
GAME_PENDING = 3
GAME_QUIT = 4
GAME_PRE_REBIRTH = 5

class Game2(Game):
    
    def __init__(self, *args):
        super().__init__(*args)
        init_game(self)
        self.state = GAME_REBIRTH
    
    def calc_current_energy(self):
        return self.calc_current_resource('energy')
    
    def calc_current_magic(self):
        return self.calc_current_resource('magic')
    
    def calc_rps(self, res):
        resource = self.stats[res]
        bars = resource['bars'] * resource['equip_bars_modifier']
        speed = resource['base_speed'] * resource['equip_speed_modifier']
        ticks = math.ceil(50 / speed)
        return math.floor(50 / ticks * bars)
    
    def calc_cap(self, res):
        return self.stats[res]['cap'] * self.stats[res]['equip_cap_modifier']
        
    def calc_current_resource(self, res):
        rps = self.calc_rps(res)
        r = rps * (time() - self.start_time - 1)
        return min(r, self.stats[res]['cap'] * self.stats[res]['equip_cap_modifier'])
    
    def energy_capped(self):
        return self.calc_current_energy() >= self.calc_cap('energy')
    
    def magic_capped(self):
        return self.calc_current_magic() >= self.calc_cap('magic')
    
    def wait_for_energy_nointerrupt(self, energy):
        while self.calc_current_energy() < energy:
            wait(0.1)
            
    def spend_magic_if_not_capped(self):
        if not self.magic_capped():
            self.spend_idle_magic()
            
    def run(self):
        self.state = GAME_REBIRTH
        self.resume()
    
    def resume(self):
        
        # each action below should actually be abstracted to class `Action` 
        # and held in an action queue, to improve responsiveness
        
        while True:
            if self.state == GAME_REBIRTH:
                print("Rebirthing")
                self.rebirth()
                self.state = GAME_INIT
                
            elif self.state == GAME_INIT:
                self.start_time = time()
                self.training = TrainingInfo()
                print("Waiting for initial energy")
                self.wait_for_energy_nointerrupt(500)
                self.train()
                print("Waiting to build base attack levels")
                wait(2)  # let attack build
                print("Nuking bosses")
                self.nuke()
                wait(3)  # let nuke kill the bosses
                print("Going for an adventure")
                self.adventure()
                self.state = GAME_GAIN
            
            elif self.state == GAME_GAIN:
                self.train()
                self.spend_magic_if_not_capped()
                self.adventure()
                if int(time()) % 10 == 0:
                    self.click_sequence('fight_boss', 'fight')
                if not self.energy_capped():
                    energy_time = (self.calc_cap('energy') - self.calc_current_energy()) / self.calc_rps('energy')
                    print("\rWaiting for energy cap. Est: %s"%hms(energy_time), end="")
                    self.spend_idle_energy()
                else:
                    print()
                    self.state = GAME_PENDING
                
            elif self.state == GAME_PENDING:
                self.train()
                self.spend_idle_energy()
                self.spend_magic_if_not_capped()
                
                if int(time()) % 60 == 0:
                    self.click_sequence('fight_boss', 'fight')
                self.click_sequence("basic_training")  # XXX debug only, to view status
                td = self.training.training_done()
                if td and time() - self.start_time > 60 * 60:
                    self.state = GAME_PRE_REBIRTH
                    print()
                elif not td:
                    training_time = self.training.time_to_cap() + 300
                    print("\rWaiting for training to complete. Est: %s"%hms(training_time), end="")
                else:
                    print("\rWaiting for 1 hr rebirth timer                 ", end="")
                    
            elif self.state == GAME_PRE_REBIRTH:
                # spend money on danger scissors
                print("Spending money on danger scissors")
                self.click_sequence("augmentation")
                send_key('r')
                wait(0.1)
                aug = self.lookup('augmentation')
                aug.click()
                dsp = aug.lookup('danger_scissors_plus')
                # 3 clicks, to be safe
                dsp.click()
                dsp.click()
                dsp.click()
                wait(20)
                print("Nuking bosses")
                self.nuke()
                now = time()
                print("Waiting 20 seconds to kill straggler boss")
                while time() - now < 20:
                    self.click_sequence('fight_boss', 'fight')
                    wait(0.1)
                self.state = GAME_REBIRTH
                r
            wait(0.1)
            if right_click_down():
                break
            #print(self.state)
                    
                    