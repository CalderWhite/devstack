import json
import re

class StackParser(object):
    def __init__(self,excludes):
        self.DELIMITER_RULE = r'[\-\,]'
        # the largest distance between two delimiters (characterized by DELIMITER_RULE)
        # for it considered to indicated a list
        self.MAX_DELIMITER_DISTANCE = 20
        # the minimum amount of items in a dev stack list
        self.MIN_LIST_LENGTH = 3
        # a set of regex rules to filter out stacks that aren't actually stacks
        self.excludes = excludes

    def find_stacks(self,text):
        prev = -self.MAX_DELIMITER_DISTANCE - 1
        prevAdded = False
        commas = []
        for match in re.finditer(self.DELIMITER_RULE,text):
            # we only care about the first, since we're only matching one character
            current_index = match.span()[0]
            
            # if they are close together, act on them
            if current_index - prev < self.MAX_DELIMITER_DISTANCE:
                
                if not prevAdded:
                    commas.append([])
                    prev_index = prev
                    s = ""
                    while prev_index > 0 and text[prev_index] != " ":
                        s = text[prev_index] + s
                        prev_index -= 1
                    commas[-1].append(s)
                # if we aren't at the end of the string, to avoid an IndexError
                current_index -= 1
                s = ""
                while current_index > 0 and text[current_index] != " ":
                    s = text[current_index] + s
                    current_index -= 1
                commas[-1].append(s)
                prevAdded = True
            else:
                prevAdded = False
            prev = current_index
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

def main():
    r = open('dist.json')
    j = json.loads(r.read())
    s = StackParser([
        r'([0-9]+|[0-9]+\,) employees [0-9]+ agents'
    ])
    for job in j["c3-iot"]:
        stacks = s.find_stacks(job["description"])
        print(stacks)

if __name__ == '__main__':
    main()