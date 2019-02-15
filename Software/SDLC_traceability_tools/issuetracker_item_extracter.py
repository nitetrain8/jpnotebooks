
import re

class Requirement():
    """ Mostly POD class designed 
    """
    def __init__(self, typ, num="", obs=False, refs=(), text="", _notag=False):
        self.type = typ
        self.num = num
        self.obs = obs
        self.refs = set(refs)
        self.text = text
        self._tag = typ + num
        if _notag:
            self.tag = ""
        else:
            self.tag = self._tag
        
        self.parents = set()
        self.children = set()
        
    def __hash__(self):
        """ Used when adding to the `parents` or `children` 
        sets of a different Requirement item, to guarantee
        non-uniqueness of two requirements with identical
        tags.
        """
        return hash(self.tag)
    
    def __eq__(self, other):
        if not isinstance(other, Requirement):
            return NotImplemented
        return self._tag == other._tag
    
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
        return ("%s('%s', '%s', _notag=%s)"%(self.__class__.__name__, self.type, self.num, str(self.tag=="")))
                
    def memfree(self):
        """ Free all references. 
        Needed to eliminate circular dependencies between parents and children. 
        """
        for c in self.children:
            c.memfree()
        self.children.clear()
        self.parents.clear()

def _partial_sort(data, start, end, key, idx):
    data[start:end] = sorted(data[start:end], key=lambda row: key(row[idx]))
     
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
    if idx == 0 or len(rows) < 2:
        return rows.sort(key=lambda row: key(row[idx]))
    
    i = start = 0
    nrows = len(rows)
    refidx = idx - 1
    first_val = rows[0][refidx]
    while True:
        i += 1
        if i >= nrows:
            _partial_sort(rows, start, i, key, idx)
            break
        val = rows[i][refidx]
        if val != first_val:
            _partial_sort(rows, start, i, key, idx)
            start = i
            first_val = rows[i][refidx]

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
    item = r"(%s)([\d\.]+)" % "|".join(_types)
    match = re.compile(item).match
    line_item_match = re.compile(r"^\>?[\*]*\s*(-*)[\+\*]+(?:%s)\:?[\+\*]*\:?\s*(.*?)(-*)\s*$" % item).match
    ref_find = re.compile(item).findall
    return item, match, line_item_match, ref_find

def _setparent(child, parent):
    """ Helper """
    if child is None or parent is None:
        return
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
    
    def __init__(self, types=tuple(_req_types)):
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
        if current.tag in refs:
            raise ValueError("Duplicate tag found: '%s'"%current.tag)
        reqs[current.tag] = current
        data[current.type].append(current)

    def _current_append(self, current, current_text, text):
        if current is None:
            return
        current_text.append(text)
        
    def _create_empties(self):
        """
        Create and pre-populate empty containers for a new run. 
        This function creates a dummy empty parent to act as
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

        # build lists of parents and children in multiple passes to simplify
        # the algorithm

        parents = []
        children = []
        for typ in self._types:
            rp = Requirement(typ, _notag=True)
            rc = Requirement(typ, _notag=True)
            parents.append(rp)
            children.append(rc)

        ll = len(self._types) - 1
        for i, typ in enumerate(self._types):
            data[typ] = [parents[i], children[i]]

            # These get special key names so they can be 
            # easily accessed later
            key = "EMPTY_PARENT_" + typ
            key2 = "EMPTY_CHILD_" + typ
            reqs[key] = parents[i]
            reqs[key2] = children[i]

            parents[i].text = key
            children[i].text = key2

            # assign parent ref
            if i < ll:
                parents[i + 1].refs = {key}
                children[i + 1].refs = {key2}
                
                # empty child map
                empty_children[typ] = children[i + 1]  

            # empty parent map
            if i > 0:
                empty_parents[typ] = parents[i - 1]

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
        t0 = self._types[0]
        for req in reqs.values():
            if not req.refs and req.type != t0:
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
        that can be compared lexicographically. 
        
        "3.4.5" -> (3, 4, 5)
        
        This is needed because comparing the strings lexicographically
        results in e.g. "3.10" is less than "3.2". 
        """
        if not rows:
            return

        # This key is a somewhat hacky way of ensuring that empty cells 
        # [""] are sorted to the bottom of the list. 
        key = lambda s: [int(n or 0) for n in s.num.split(".")] if s.num else [9999999999999]
        for i in range(len(self._types)):
            partial_sort(rows, i, key=key)
            
    def _stringify_rows(self, rows):
        """ Turn rows of requirement items into rows of strings. 
        Filter out blank rows by verifying that each row has at 
        least one non-empty string. 
        """
        ret = []
        for row in rows:
            r = [r.tag for r in row]
            if any(r):
                ret.append(r)
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
    from _itie_test_data_raw import _test_data_raw
    for row in RequirementExtracter(_req_types).extract_text(_test_data_raw):
        print(repr(row))
