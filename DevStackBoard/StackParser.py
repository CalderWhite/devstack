import json
import re
from bs4 import BeautifulSoup as soup

class PositionSummary(object):
    """Stores the information about the required skills for a job posting, as well as meta data for that job."""
    def __init__(self,title,company,location,stacks):
        self.title = title
        if title != None:
            self.title = self.title.upper()
        self.company = company
        if company != None:
            self.company = self.company.upper()
        self.location = location
        if location != None:
            self.location = self.location.upper()
        self.stacks = stacks
        # convert all stacks to upper
        for i in range(len(stacks)):
            for j in range(len(stacks[i])):
                self.stacks[i][j] = self.stacks[i][j].upper()
    
    def combine_stacks(self):
        # convert this for firebase
        combined_stack = {}
        for stack in self.stacks:
            for skill in stack:
               combined_stack[skill] = True
        return combined_stack
    
    def to_dict(self):
        
        return {
            "title" : self.title,
            "company" : self.company,
            "location" : self.location,
            "stack" : self.combine_stacks()
        }
class SkillSummary(object):
    """Stores information about a skill required for tech. Being the companies that use it."""
    def __init__(self,name,*args):
        self.name = name.upper()
        self.companies = {}
        if len(args) > 0:
            self.companies = args[0]
        self.total = 0
        if len(args) > 1:
            self.total = args[1]
    
    def add_total(self,n):
        self.total += n
    
    def increment_company(self,company):
        comapny = company.upper()
        if company not in self.companies:
            self.companies[company] = 0
        self.companies[company] += 1
        self.add_total(1)
    
    def to_dict(self):
        return {
            "name" : self.name,
            "companies" : self.companies,
            "total" : self.total,
            "totalCompanies" : len(self.companies)
        }

class StackParser(object):
    def __init__(self):
        self.DELIMITER_RULE = r'[\-\,]'
        # the largest distance between two delimiters (characterized by DELIMITER_RULE)
        # for it considered to indicated a list
        self.MAX_DELIMITER_DISTANCE = 3
        # the minimum amount of items in a dev stack list
        self.MIN_LIST_LENGTH = 3
        # a set of regex rules to filter out stacks that aren't actually stacks
        self.excludes = [
            r'([0-9]+|[0-9]+\,) employees [0-9]+ agents'
        ]
        # characters that will be removed from stack items
        self.BAD_CHARACTERS = list("(){}[]\n\t")
        
        self.REPLACES = [
            (r'<br/>',"\n"),
            (r'( and\/or | and | or |[\,\/])',","), # include stacks that are delimited by and, or, etc.
            (r'[,]+',", "),
            (r'\\x[a-z0-9]{2}',""), # remove character escapes
            (r'^https?:\/\/.*[\r\n]*',''), # remove urls
            (re.compile('(etc\.|e\.g\.|jobs|careers)',re.IGNORECASE),'')
        ]
    def replace_terms(self,s):
        for i in self.REPLACES:
            s = re.sub(i[0],i[1],s)
        return s
    
    def cleanse_item(self,s):
        # remove all HTML
        s = soup(s,"html.parser").get_text()
        for c in self.BAD_CHARACTERS:
            s = s.replace(c,"")
        return s

    def find_stacks(self,text):
        text = self.cleanse_item(str(text.encode('ascii','ignore')))
        text = self.replace_terms(text).split(" ")
        
        prevAdded = False
        commas = []
        
        indicies = []
        
        for w in range(len(text)):
            if text[w].find(",") > -1:
                indicies.append(w)
                text[w] = text[w].replace(",","")
                
        
        prev = -self.MAX_DELIMITER_DISTANCE
        prev_added = False
        
        for i in indicies:
            if i - prev < self.MAX_DELIMITER_DISTANCE:
                if not prev_added:
                    commas.append([])
                    # the first item of a list shouldn't be added, since it is still far away from other commas.
                    # but once we figure out that the string of comma delimited words _is_ a list, 
                    # we add the first item.
                    prev_text = text[indicies[indicies.index(i)-1]]
                    if prev_text == "":continue
                    commas[-1].append(prev_text)
                if text[i] == "":continue
                commas[-1].append(text[i])
                prev_added = True
            else:
                prev_added = False
            prev = i
        
        for i in range(len(commas)-1,-1,-1):
            if len(commas[i]) < self.MIN_LIST_LENGTH:
                commas.pop(i)
            else:
                # remove based on exclude regex filters
                for rule in self.excludes:
                    if re.search(rule," ".join(commas[i])):
                        commas.pop(i)
                        break
        return commas
