
from jpnotebooks.Software.SDLC_traceability_tools.issuetracker_item_extracter import Reference
from officelib.xllib import *

class UserTestsParser():
    def __init__(self):
        pass
    
    def _extract_excel_rows(self, file):
        xl = Excel()
        with screen_lock(xl):
            wb = xl.Workbooks.Open(file)
            ur = wb.Worksheets(1).UsedRange
            headers = ur.GetResize(1, ur.Columns.Count).Value2[0]
            data = ur.GetResize(ur.Rows.Count - 1, ur.Columns.Count).GetOffset(1, 0).Value2
            wb.Close(False)
        del xl
        return headers, data
    
    def parse_rows(self, headers, rows):
        hm = {h: i for i, h in enumerate(headers)}
        def gh(h, r):
            return r[hm[h]]
        reqs = []
        for row in rows:
            refs = gh("List Web FRS", row) or ""
            refs = refs.splitlines()
            tid = str(gh("ID_TEST", row))
            if tid.endswith(".0"):
                tid = tid[:-2]
            req = Reference("USR", tid, False, refs, gh("Test Name", row))
            reqs.append(req)
        return reqs
        
    def parse_excel(self, file):
        headers, data = self._extract_excel_rows(file)
        return self.parse_rows(headers, data)
        

