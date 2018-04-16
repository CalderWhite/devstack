import json
import re

class PositionSummary(object):
    def __init__(self,title,company,location,stacks):
        self.title = title
        self.company = company
        self.location = location
        self.stacks = stacks
    
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
            (r'( and\/or | and | or |[\,\/])',","),
            (r'[,]+',", "),
            (r'\\x[a-z0-9]{2}',"")
        ]
    def replace_terms(self,s):
        for i in self.REPLACES:
            s = re.sub(i[0],i[1],s)
        return s
    
    def cleanse_item(self,s):
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
