import re

class Reference():
    """ Mostly POD class designed to hold data related to a requirement
    or test item. 
    """
    def __init__(self, typ, num="", obs=False, refs=(), text="", priority="", milestone="", *, _notag=False):
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
        self.priority = priority
        self.milestone = milestone
        
        self.parents = set()
        self.children = set()
        
    def copy(self):
        new = self.__class__(self.type, self.num, self.obs, self.refs, self.text)
        new.tag = self.tag
        new.parents = self.parents.copy()
        new.children = self.children.copy()
        return new

    def equals(self, other):
        return self.type == other.type and \
                self.num == other.num and \
                self.obs == other.obs and \
                self.text == other.text

    def merged(self, other):
        new = self.copy()
        new.refs.update(other.refs)
        new.parents.update(other.parents)
        new.children.update(other.children)
        return new

    # __hash__ and __eq__ needed for dict storage and 
    # sorting functionality
        
    def __hash__(self):
        """ Used when adding to the `parents` or `children` 
        sets of a different Requirement item, to guarantee
        non-uniqueness of two requirements with identical
        tags.
        """
        return hash(self._tag)
    
    def __eq__(self, other):
        if not isinstance(other, Reference):
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
    data[start:end] = sorted(data[start:end], key=key)
     
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
        [1, 3, 5]     
        [1, 4, 3]  <- block end
        [4, 5, 6]
        [5, 6, 7]
         ^
         check values in this column
    
    Note that `key` is called with only the one item
    from the list that is being used for the sort, not 
    the whole row. 
    """
    thekey = lambda row: key(row[idx])
    
    if idx == 0 or len(rows) < 2:
        return rows.sort(key=thekey)
    
    i = start = 0
    nrows = len(rows)
    refidx = idx - 1
    first_val = rows[0][refidx]
    while True:
        i += 1
        if i >= nrows:
            _partial_sort(rows, start, i, thekey, idx)
            break
        val = rows[i][refidx]
        if val != first_val:
            _partial_sort(rows, start, i, thekey, idx)
            start = i
            first_val = rows[i][refidx]

_req_types = [
    'URS',
    'FRS',
    'SDS',
]

_test_types = [
    'UNIT',
    'USER',
    'BETA'
]


__item_template = r"(%s)([\d\.]+)"

def create_item_matcher(types):
    return re.compile(__item_template % "|".join(types)).match

def _make_regex_ctx(_types):
    """ Create regex specific to the given list of traceable tags """
    item = __item_template % "|".join(_types)
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


class IssuetrackerParser():
    """ For parsing requirements from issuetracker
    """
    
    _EMPTY_LINE = 0
    _RAW_LINE   = 1
    _REQ_RESULT = 2
    
    def __init__(self, types=tuple(_req_types + _test_types)):
        self._req_item, self._req_match, self._item_match, self._ref_find = _make_regex_ctx(types)

        # 1) match anything that isn't left bracket, 
        # 2) ignore left bracket
        # 3) capture everything until right bracket,
        # 4) then right bracket
        # 5) then capture everything until left bracket
        
        # The first group captures nothing after the first set of brackets
        # in a string, but this is fine. 
        self._bracket_find = re.compile(r"([^\[]*)\[([^\]]*)\]([^\[]*)").findall
        self._types = types
        
    def get_types(self):
        return self._types

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
            results = self._bracket_find(line)

            # If no results are found, don't forget to add the line back
            # as text! Otherwise, the line would be missing from output.
            # If results, the whole line will be captured 
            # correctly by the regex. 

            if not results:
                text.append(line)
            else:
                for before, bracket, after in results:
                    text.append(before)
                    typnums = self._ref_find(bracket)

                    # False positive? Add the bracketed text back. 
                    if not typnums:
                        text.append("[")
                        text.append(bracket)
                        text.append("]")
                    else:
                        for typ, num in typnums:
                            num = _numfix(num)
                            refs.append((typ, num))

                    text.append(after)

            text.append("\n")

        # In all code paths above, the last element in the list
        # is a superfluous newline. 
        if text:
            text.pop()

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
        
        dash1, typ, num, text, dash2 = m.groups()
        cancel = dash1 == dash2 and dash1 != ""
        return self._REQ_RESULT, typ, num, text, cancel
    
    def _current_finish(self, current, current_text, reqs, iss):
        """ Compile the stored state for the current item and add
        it to the `reqs` and `data` structures. 
        """
        if current is None:
            return
        refs, text = self._extract_refs(current_text)
        refs = set("".join(r) for r in refs)
        current.text = text
        current.refs = refs
        current.priority = iss.priority.name
        current.milestone = iss.sprint_milestone.name
        reqs.append(current)

    def _current_append(self, current, current_text, text):
        if current is None:
            return
        current_text.append(text)
        
    def _extract_frs_lines(self, lines, reqs, iss=None):
        """ Extract the items from the list of lines, and place
        the resulting items into the reqs and data maps. 
        
        Scan line by line and store the state of the current item.
        If a new line matches a req item, finish compiling the previous item
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
            result, typ, num, text, cancel = self._get_result_for_line(line)
            if result == self._REQ_RESULT:
                self._current_finish(current, current_text, reqs, iss)
                current = Reference(typ, num, cancel, (), "")
                current_text = [text]
            elif result == self._RAW_LINE:
                self._current_append(current, current_text, text)
            elif result == self._EMPTY_LINE:
                self._current_finish(current, current_text, reqs, iss)
                current = current_text = None
            i += 1
        self._current_finish(current, current_text, reqs, iss)
        
    def parse_into(self, reqs, text, iss=None):
        if isinstance(text, str):
            text = text.splitlines()
        self._extract_frs_lines(text, reqs, iss)
        
    def parse_text(self, text, iss=None):
        reqs = []
        self.parse_into(reqs, text, iss)
        return reqs

    def parse(self, iss):
        return self.parse_text(iss.description, iss)
    
    def parse_all(self, issues):
        reqs = []
        for iss in issues:
            new = self.parse(iss)
            reqs.extend(new)
        return reqs
        
        
class RequirementExtracter():
    
    def __init__(self, req_types=tuple(_req_types), test_types=tuple(_test_types)):
        self._req_types = req_types
        self._test_types = test_types
        
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
        empty_parents = {}  # typ -> empty parent Requirement
        empty_children = {} # typ -> empty child Requirement

        # build lists of parents and children in multiple passes to simplify
        # the algorithm

        types = self._req_types + ['TEST']

        parents = []
        children = []
        for typ in types:
            rp = Reference(typ, _notag=True)
            rc = Reference(typ, _notag=True)
            parents.append(rp)
            children.append(rc)

        ll = len(types) - 1
        for i, typ in enumerate(types):
            # These get special key names so they can be 
            # easily removed later
            key = 'EMPTY_PARENT_' + typ
            key2 = 'EMPTY_CHILD_' + typ
            reqs[key] = parents[i]
            reqs[key2] = children[i]

            parents[i].text = key
            children[i].text = key2

            # These conditional blocks can be combined later.
            # I left them separate here for logical clarity

            # assign parent
            if i < ll:
                parents[i + 1].refs = {key}
                children[i + 1].refs = {key2}

            # empty parent map
            if i > 0:
                empty_parents[typ] = parents[i - 1]

            # empty child map
            if i < ll:
                empty_children[typ] = children[i + 1]  

        # all test types have the same dummy parent
        for typ in self._test_types:
            empty_parents[typ] = parents[-2]

        return reqs, empty_parents, empty_children


    def _finish_set_parents(self, reqs, empty_parents):
        """
        Finish pass #1: Set parents based on references tagged in each individual item. 
        If no parent is found, add on the empty parent so that eventual calls to 
        req.childify() will auto-include empty cells for the parent. 
        """
        t0 = self._req_types[0]
        for req in reqs.values():
            if not req.refs and req.type != t0:
                _setparent(req, empty_parents[req.type])
            for ref in req.refs:
                parent = reqs.get(ref)
                if parent is None:
                    raise ValueError("Can't find item '%s' referenced by '%s'"%(ref, req.tag))

                # This is some fancy code that adds blank intermediates
                # between references that are not sequential. For example,
                # for _req_types = [URS, FRS, SDS]:
                # 
                # if req.type == SDS and parent.type == URSS, create
                # blank intermediate FRS
                # 
                # if req.type == BUG and parent.type == URS, create
                # blank FRS and SDS.
                # 
                # If types are sequential (common case), the loop is a noop.
                # Note that because the req.type value is only checked
                # against the contents of the _req_types list, 
                # any arbitrary reference type not contained 
                # within that list will work properly. 
                # 
                # Also note that if req.type is earlier in the list
                # than the parent, then weird stuff happens. 

                ii = self._req_types.index(parent.type)
                for i in range(ii+1, len(self._req_types)):
                    typ = self._req_types[i]
                    if typ == req.type:
                        break
                    p = Reference(typ, _notag=True)
                    _setparent(p, parent)
                    parent = p
                _setparent(req, parent)
                
    def _finish_set_empty_children(self, reqs, empty_children):
        """
        Finish pass #2: add empty children to any items that don't have 
        children, so that the eventual calls to req.childify() will 
        auto-include empty cells for the child. 
        
        Skip if the item's type is the last item in the types list,
        since the last item shouldn't have children. 
        """
        for req in reqs.values():
            if not req.children and req.type != 'TEST':
                req.children.add(empty_children[req.type])
                
    def _fixify_tests(self, reqs):
        tt = set(self._test_types)
        for k, r in reqs.items():
            if r.type in tt:
                r = r.copy()
                r.type = "TEST"
                reqs[k] = r
                
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
        t0 = self._req_types[0]
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
        key = lambda s: [int(n or 0) if s.num else 1<<31 for n in s.num.split(".") ]
        for i in range(len(self._req_types)):
            partial_sort(rows, i, key=key)
            
    def _stringify_rows(self, rows):
        """ Turn rows of requirement items into rows of strings. 
        Filter out blank rows by verifying that each row has at 
        least one non-empty string. 
        """
        ret = [self._req_types + ["Validation"]]
        for row in rows:
            r = [r.tag for r in row]
            if any(r):
                ret.append(r)
        return ret
    
    def _extract_finish(self, reqs, empty_parents, empty_children):
        """ Common code required to finish the extraction process regardless
        of entry point. 
        
        Delegate all work to appropriate sub functions where necessary. 
        """
        self._fixify_tests(reqs)
        self._finish_set_parents(reqs, empty_parents)
        self._finish_set_empty_children(reqs, empty_children)
        listified = self._do_childify(reqs)
        self._multisort_req_list(listified)
        
        # release references to allow GC to collect all objects
        # once `reqs` and `data` go out of scope. 
        for v in reqs.values():
            v.memfree()
        
        return self._stringify_rows(listified)
        
    def extract(self, lreqs):
        reqs = {}
        for r in lreqs:
            if r.obs:
                continue  # skip obsolete issues
            other = reqs.get(r.tag)
            if other is not None and not r.equals(other):
                raise ValueError("Ambiguous duplicate requirement for '%s':\n'%s'\n'%s'"%(r.tag, r.text, other.text))
            reqs[r.tag] = r
        r, p, c = self._create_empties()
        reqs.update(r)
        return self._extract_finish(reqs, p, c)
    

def rowify_issues(types, issues):
    parser = IssuetrackerParser(types)
    reqs = parser.parse_all(issues)
    rex = RequirementExtracter(types)
    rows = rex.extract(reqs)
    return rows

def rowify_text(types, text):
    parser = IssuetrackerParser(types)
    reqs = parser.parse_text(text)
    rex = RequirementExtracter(types)
    rows = rex.extract(reqs)
    return rows