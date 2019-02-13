
# coding: utf-8

# In[29]:


import re

_test_data_raw = """*+Background:+*
Agitation refers to the mixing of vessel contents using a vertical wheel impeller. 

*+URS3646+* 
* *+URS3646.1:+* The system will control agitation using automatic and manual control, and be able to turn agitation off. 
** Point 1
** Point 2
* *+URS3646.2:+* Automatic control will use speed as a set point to control PV. 
* *+URS3646.3:+* Manual control will provide a constant controller output regardless of PV. 
* *+URS3646.4:+* The system will use appropriate constraints to coerce outputs within appropriate operating limits. 
* *+URS3646.5:+* The system will detect agitation speed PV based on actual agitation speed as detected by a hardware sensor.
* *+URS3646.6:+* The system will report agitation speed PV in units of revolutions per minute (RPM)
* *+URS3646.7:+* The system will provide a standard UI allowing an operator access to system controls
* *+URS3646.8:+* The system will attempt to detect and recover from failures or abnormal operation. 

*+FRS3646+* Agitation Control [URS3646]
* Note: All system variables in the following items will be located under the category "Agitation" unless specified otherwise. 
* *FRS3646.1:* Controller output will be determined by whether the bioreactor is configured as an AirDrive or MagDrive system. [URS3646.1]
** *FRS3646.1.1:* (AirDrive) The controller will output a Main Gas flow rate request. Ref FRS3654. [URS3646.1]
** *FRS3646.1.2:* (MagDrive) the controller will output motor duty as a percentage of full scale. [URS3646.1]
** Note: For both configurations, output modules will be used as necessary to translate requests into electronic signals. 
* *FRS3646.2:* Agitation speed (a.k.a "RPM") will be detected based on a hardware sensor and used as the Process Value (PV). [URS3646.5]
** *FRS3646.2.1:* RPM detection will use a Hall Effect sensor to detect the passing of sensor magnets on the mixing impeller. [URS3646.5]
** *FRS3646.2.2:* The time between magnets passing will be used to infer the agitation speed based on the number of magnets. [URS3646.6]
** *FRS3646.2.3:* The number of magnets on the impeller will be configurable via System Variable "Number of Magnets". [URS3646.5]
** *FRS3646.2.4:* The number of intervals to average will be configurable via System Variable "Samples to Average". [URS3646.5]
** *FRS3646.2.5:* A measured PV will be coerced to 0 if the raw value is less than System Variable "Minimum (RPM)". [URS3646.6]
** Note: the magnets on the impeller will be assumed to be evenly spaced. 
* *FRS3646.3:* HMI [URS3646.7]
** *FRS3646.3.1:* Users will be able to select one of three modes: Auto, Manual, or Off. [URS3646.7]
** *FRS3646.3.2:* The current PV, SP, and mode will be displayed to the user with appropriate units. [URS3646.7]
** *FRS3646.3.3:* Interlock or broken status will be displayed to the user. [URS3646.7]
* *FRS3646.4:* Auto Mode Control [URS3646.2]
** Note: Tuning is beyond the scope of this FRS. Understanding of a PID controller is required to understand PID requirements. 
** *FRS3646.4.1:* Users will be able to select a Set Point (SP) as an RPM target. [URS3646.2]
** *FRS3646.4.2:* A standard PID controller will be used to seek SP based on the current PV. [URS3646.2]
** *FRS3646.4.3:* The PID Controller will use the following System Variables for standard PID input parameters, under the Agitation category: [URS3646.2]
*** *FRS3646.4.3.1:* (MagDrive) P-Gain: "P Gain (%/RPM)" [URS3646.2]
*** *FRS3646.4.3.2:* (AirDrive) P-Gain: "P Gain (LPM/RPM)" [URS3646.2]
*** *FRS3646.4.3.3:* I-Time: "I Time (min)" [URS3646.2]
*** *FRS3646.4.3.4:* D-Time: "D Time (min)" [URS3646.2]
*** *FRS3646.4.3.5:* α: "Alpha" [URS3646.2]
*** *FRS3646.4.3.6:* β: "Beta" [URS3646.2]
*** *FRS3646.4.3.7:* γ: "Gamma" [URS3646.2]
*** *FRS3646.4.3.8:* Linearity: "Linearity" [URS3646.2]
** *FRS3646.4.4:* (AirDrive) Output will not be greater than System Variable "Gas Auto Max (LPM)". [URS3646.2]
** *FRS3646.4.5:* (AirDrive) Output will not be less than System Variable "Gas Auto Min (LPM)" [URS3646.2]
** *FRS3646.4.6:* (AirDrive) When PV is 0, the controller will not output more than System Variable "Gas Auto Max Startup (LPM)", unless this would violate the "Gas Auto Max (LPM)" or "Gas Auto Min (LPM)" settings. [URS3646.2]
** *FRS3646.4.7:* (MagDrive) Output will not be greater than System Variable "Power Auto Max (%)". [URS3646.2]
** *FRS3646.4.8:* (MagDrive) Output will not be less than System Variable "Power Auto Min (%)". [URS3646.2]
** *FRS3646.4.9:* (MagDrive) When PV is 0, the controller will not output more than System Variable "Auto Max Startup (%)", unless this would violate the "Power Auto Max (%)" or "Power Auto Min (%)" settings. [URS3646.2]
** *FRS3646.4.10:* Pulse and Lookup Modes [URS3646.2]
*** *FRS3646.4.10.1:* The controller will automatically transition from Auto Mode to Pulse Mode when the following conditions are met: [URS3646.2]
**** *FRS3646.4.10.1.1:* Output is nonzero [URS3646.2]
**** *FRS3646.4.10..2:* PV has been 0 for longer than the time specified by System Variable "Pulse Mode Timeout". [URS3646.8]
**** *FRS3646.4.10.1.3:* PV has been 0 for less than the time specified by System Variable "Lookup Mode Timeout". [URS3646.2]
*** *FRS3646.4.10.2:* While in pulse mode, output will alternate between zero and maximum allowed output every few seconds. [URS3646.2]
*** *FRS3646.4.10.3:* The controller will automatically transition from Pulse Mode or Auto Mode to Lookup Mode when the following conditions are met: [URS3646.8]
**** *FRS3646.4.10.3.1:* Output is nonzero [URS3646.8]
**** *FRS3646.4.10.3.2:* PV has been 0 for longer than the time specified by System Variable "Lookup Mode Timeout". [URS3646.8]
*** *FRS3646.4.10.4:* (AirDrive) While in lookup mode, the system will output as SP * (System Variable "Lookup Factor (LPM/RPM)"). [URS3646.8]
*** *FRS3646.4.10.5:* (MagDrive) While in lookup mode, the system will output as SP * (System Variable "Lookup Factor (%/RPM)"). [URS3646.8]
*** Note: If lookup timeout is equal or less than the pulse timeout, then the system will never enter pulse mode. 
* *FRS3646.5:* Manual Mode Control [URS3646.3]
** *FRS3646.5.1:* (AirDrive) Users will be able to select a gas flow rate in LPM as a target. [URS3646.3]
** *FRS3646.5.2:* (MagDrive) Users will be able to select a power output in % as a target. [URS3646.3]
** *FRS3646.5.3:* The system will output the user's request when not limited by interlocks, settings, or other specified circumstances. [URS3646.3]
** *FRS3646.5.4:* (AirDrive) Output will not be greater than System Variable "Gas Manual Max (LPM)". [URS3646.4]
** *FRS3646.5.5:* (MagDrive) Output will not be greater than System Variable "Power Manual Max (%)". [URS3646.5]
* *FRS3646.6:* Off Mode Control [URS3646.4]
** *FRS3646.6.1:* (AirDrive) The controller will output no Main Gas request. [URS3646.4,URS3646.6]
** *FRS3646.6.2:* (MagDrive) The controller will output no power request. [URS3646.4, URS3646.5]
** *+FRS3646.7.1+* I'm a test item

*+SDS3646+*
* *+SDS3646.1:+* I'm an item [FRS3646.6.2]
* *+SDS3646.2:+* I'm another item [FRS3646.7.1]"""

class Requirement():
    """ Mostly POD class designed 
    """
    def __init__(self, typ, num="", obs=False, refs=(), text="", _notag=False):
        self.type = typ
        self.num = num
        self.obs = obs
        self.refs = set(refs)
        self.text = text
        if _notag:
            self.tag = ""
        else:
            self.tag = typ + num
        
        self.parents = set()
        self.children = set()
        
    def __hash__(self):
        """ Used when adding to the `parents` or `children` 
        sets of a different Requirement item, to guarantee
        non-uniqueness of two requirements with identical
        tags.
        """
        return hash(self.tag)
    
    def childify(self):
        """ Entry point """
        return self._childify([])
        
    def _childify(self, path):
        """ 
        Yield each possible combinations of lists
        of self and all descendents.
        
        If there are circles in the graph, this 
        function will throw a recursion error. 
        """
        path.append(self)
        if not self.children:
            yield path
        else:
            for child in self.children:
                yield from child._childify(path.copy())
                
    def __repr__(self):
        return ("%s('%s%s')"%(self.__class__.__name__, self.type, self.num))
                
    def memfree(self):
        """ Free all references. 
        Needed to eliminate circular dependencies between parents and children. 
        """
        for c in self.children:
            c.memfree()
        self.children.clear()
        self.parents.clear()

def partial_sort(rows, idx=0, key=lambda x: x):
    """ Inner function to perform sequential sorting of
    a list of lists. 
    
    If index is 0, just sort normally. Otherwise, 
    sort the list in blocks such that each block is
    a sequence of rows where the value index - 1 is
    the same for all. 
    
    E.g. in the below diagram, if idx = 1, then
    a block of size 3 is identified by consecutive
    values of "1" found at idx - 1 = 0 in the list:
    
        [1, 2, 1]  <- block start
        [1, 3, 1]     
        [1, 4, 1]  <- block end
        [4, 5, 6]
        [5, 6, 7]
         ^
         check values in this column
    
    Note that `key` is called with only the one item
    from the list that is being used for the sort, not 
    the whole row. 
    """
    if idx == 0:
        return rows.sort(key=lambda row: key(row[idx]))
    
    i = start = 0
    nrows = len(rows)
    refidx = idx - 1
    while i < nrows:
        val = first_val = rows[i][refidx]
        i += 1
        while val == first_val and i < nrows:
            val = rows[i][refidx]
            i += 1
        rows[start: i - 1] = sorted(rows[start:i - 1], key=lambda row: key(row[idx]))
        start = i - 1

_req_types = [
    'URS',
    'FRS',
    'SDS',
    'IQ',
    'OQ',
    'PQ'
]

def _make_regex_ctx(_types):
    """ Create regex specific to the given list of traceable tags """
    item = "(%s)([\d\.]+)" % "|".join(_types)
    match = re.compile(item).match
    line_item_match = re.compile(r"^\>?[\*]*\s*(-*)[\+\*]+(?:%s)\:?[\+\*]*\:?\s*(.*?)(-*)\s*$" % item).match
    ref_find = re.compile(item).findall
    return item, match, line_item_match, ref_find

def _setparent(child, parent):
    """ Helper """
    child.parents.add(parent)
    parent.children.add(child)

_numfix_sub = re.compile(r"\.{2,}").sub
def _numfix(s):
    """ "3..4...5" -> "3.4.5" """
    return _numfix_sub(".", s)

class RequirementExtracter():
    _EMPTY_LINE = 0
    _RAW_LINE   = 1
    _REQ_RESULT = 2
    
    def __init__(self, types=_req_types):
        self._types = types
        self._req_item, self._req_match, self._item_match, self._ref_find = _make_regex_ctx(types)
        self._bracket_find = re.compile(r"(.*?)\[(.*)\](.*)").findall
        
    def _extract_refs(self, lines):
        """ Extract all references from the given line and return 
        a list of references and the line with references removed. 
        
        References must be of the form "[<tag><nums>]", where <tag> is 
        a tag that exactly matches one of the items from the `_types`
        list, and <nums> is a dotted-numbered item such as 123.1.10.5.
        The number of dotted numbers can be arbitrary. 
        
        This code fixes multiply-dotted items e.g. "3..1...4" to fix 
        any typos. Anyone who inputs multiple dots on purpose probably
        deserves to be shot. 
        """
        refs = []; text = []
        if isinstance(lines, str): 
            lines = lines.split()
        for line in lines:
            for before, bracket, after in self._bracket_find(line):
                text.append(before)
                text.append(after)
                for typ, num in self._ref_find(bracket):
                    num = _numfix(num)
                    refs.append((typ, num))
        return refs, ''.join(text)
    
    def _get_result_for_line(self, line):
        """ Scan a line of text and return the type of line. 
        Caller determines course of action based on the line type 
        and current program state. 
        """
        if not line or line.isspace():
            return self._EMPTY_LINE, None, None, None, True

        m = self._item_match(line)
        if m is None: 
            return self._RAW_LINE, "", "", line.strip(), False
        
        # if any idiot uses multiple dashes for dash1 and dash2 and somehow
        # does it in a way to pass this check, they can deal with the fallout
        
        dash1, type, num, text, dash2 = m.groups()
        cancel = dash1 == dash2 and dash1 != ""
        return self._REQ_RESULT, type, num, text, cancel
    
    def _current_finish(self, current, current_text, reqs, data):
        """ Compile the stored state for the current item and add
        it to the `reqs` and `data` structures. 
        """
        if current is None:
            return
        refs, text = self._extract_refs(current_text)
        refs = set("".join(r) for r in refs)
        current.text = text
        current.refs = refs
        reqs[current.tag] = current
        data[current.type].append(current)

    def _current_append(self, current, current_text, text):
        if current is None:
            return
        current_text.append(text)
        
    def _create_empties(self):
        """
        Create and pre-populate empty containers for a new run. 
        This function creates an dummy empty parent to act as
        a parent for the first item in the _types list, which
        simplifies other algorithms in this class. 
        
        This trick doesn't work for children, because the dummy child would
        always get pulled in by req.childify(). The dummy parent
        does not appear because it is not added to either top-level
        data structure. Note that this approach is incompatible with
        the original Requirement class design which used a WeakSet
        to contain parents, because this dummy parent would go out
        of scope here and become lost, leading to difficult to diagnose
        errors. 
        """
        reqs = {}
        data = {}
        empty_parents = {}  # typ -> empty parent Requirement
        empty_children = {} # typ -> empty child Requirement
        parent = Requirement("dummy_parent")

        for typ in self._types:
            r = Requirement(typ, _notag=True)
            _setparent(r, parent)
            data[typ] = [r]
            reqs['EMPTY_' + typ] = r
            empty_parents[typ] = parent
            parent = r

        for i in range(len(self._types) - 1):
            empty_children[self._types[i]] = data[self._types[i + 1]][0]
            
        return reqs, data, empty_parents, empty_children

    def _extract_frs_lines(self, lines, reqs, data):
        """ Extract the items from the list of lines, and place
        the resulting items into the reqs and data maps. 
        
        Scan line by line and store the state of the current item.
        If a new line matches an FRS item, finish compiling the previous item
        and create a new one. If it does not, add the text to the current list of
        text lines belonging to the previous item. 
        
        When the function starts, current and current_text are set to None, causing
        both helper functions `_current_finish()` and `_current_append()` to no-op 
        until the first requirement line is found. 
        """
        
        i = 0
        ll = len(lines)
        current = None
        current_text = None
        while i < ll:
            line = lines[i]
            result, type, num, text, cancel = self._get_result_for_line(line)
            if result == self._REQ_RESULT:
                self._current_finish(current, current_text, reqs, data)
                current = Requirement(type, num, cancel, (), "")
                current_text = [text]
            elif result == self._RAW_LINE:
                self._current_append(current, current_text, text)
            i += 1
        self._current_finish(current, current_text, reqs, data)
        
    def _finish_set_parents(self, reqs, empty_parents):
        """
        Finish pass #1: Set parents based on references tagged in each individual item. 
        If no parent is found, add on the empty parent so that eventual calls to 
        req.childify() will auto-include empty cells for the parent. 
        
        This function doesn't skip the first item in the _types list, because a dummy
        parent is included in the empty_parents list. 
        """
        for req in reqs.values():
            if not req.refs:
                _setparent(req, empty_parents[req.type])
            for ref in req.refs:
                parent = reqs.get(ref)
                if parent is None:
                    raise ValueError("Can't find item: '%s'"%ref)
                _setparent(req, parent)
                
    def _finish_set_empty_children(self, reqs, empty_children):
        """
        Finish pass #2: add empty children to any items that don't have 
        children, so that the eventual calls to req.childify() will 
        auto-include empty cells for the child. 
        
        Skip if the item's type is the last item in the types list,
        since the last item shouldn't have children. 
        """
        last_item = self._types[-1]
        for req in reqs.values():
            if not req.children and req.type != last_item:
                req.children.add(empty_children[req.type])
                
    def _do_childify(self, reqs):
        """ Get the list of requirement traces by calling
        `req.childify()` on each item in the list of requirements
        whose type is the first item in the types list. 
        
        Since items without direct parents have empty parents added,
        this will result in a list of all items. 
        
        This function uses `reqs` as input and checking each tag
        instead of using `data[self._types[0]]` mostly because 
        this is (was) the only existing use of the latter data 
        structure, making it a candidate for removal in a later
        release if the developer is so inclined...
        """
        rows = []
        t0 = self._types[0]
        for it in reqs.values():
            if it.type == t0:
                rows.extend(it.childify())
        return rows

    def _multisort_req_list(self, rows):
        """ Perform a stable sequential sort on the list of 
        rows to turn it into a human-readable hierarchy. 
        
        E.g. sort by types[0] THEN types[1] ... 
        
        The sort key is a lambda that turns the dotted-number
        stored in the requirement object into a list of integers
        that can be compared lexigraphically. 
        
        "3.4.5" -> (3, 4, 5)
        
        This is needed because comparing the strings lexigraphically
        results in e.g. "3.10" is less than "3.2". 
        """
        if not rows:
            return
        key = lambda s: [int(n or 0) for n in s.num.split(".")]
        for i in range(len(self._types)):
            partial_sort(rows, i, key=key)
            
    def _stringify_rows(self, rows):
        ret = []
        for row in rows:
            ret.append([r.tag for r in row])
        return ret
    
    def _extract_finish(self, reqs, data, empty_parents, empty_children):
        """ Common code required to finish the extraction process regardless
        of entry point. 
        
        Delegate all work to appropriate sub functions where necessary. 
        """
        self._finish_set_parents(reqs, empty_parents)
        self._finish_set_empty_children(reqs, empty_children)
        listified = self._do_childify(reqs)
        self._multisort_req_list(listified)
        
        # release references to allow GC to collect all objects
        # once `reqs` and `data` go out of scope. 
        for v in reqs.values():
            v.memfree()
        
        return self._stringify_rows(listified)
        
    def extract_text(self, text):
        """ Extract all reference items from a single continguous block of 
        text. Assumes text is properly formatted.
        """
        return self.extract_lines(text.splitlines())
        
    def extract_lines(self, lines):
        """ Extract all reference items from a list of properly-formatted
        lines. 
        """
        reqs, data, empty_parents, empty_children = self._create_empties()
        self._extract_frs_lines(lines, reqs, data)
        return self._extract_finish(reqs, data, empty_parents, empty_children)
        
    def extract_all(self, issues):
        reqs, data, empty_parents, empty_children = self._create_empties()
        for iss in issues:
            lines = iss.description.splitlines()
            self._extract_frs_lines(lines, reqs, data)
        return self._extract_finish(reqs, data, empty_parents, empty_children)


if __name__ == '__main__':
    for row in RequirementExtracter(_req_types).extract_text(_test_data_raw):
        print(repr(row))
