import sys
import json

# local imports
import Scrapers
import StackParser


# Unit tests

def Manulife():
    s = Scrapers.Manulife("software")
    s.get_jobs(max_items=1)
def HackerRankJobsAPI():
    s = Scrapers.HackerRankJobsAPI("software")
    s.get_jobs(max_items=1)
class StackParserTests(object):
    class BadParsing(Exception):
        pass
    def __init__(self):
        self.test_data = json.loads(open("testData.json").read())["StackParser"]
        self.parser = StackParser.StackParser()
    def run_tests(self):
        self.check_stack_finding()
    def check_stack_finding(self):
        """Checks that the doc parsing algorithm is finding stacks correctly"""
        for i in self.test_data["finding"]:
            output = self.parser.find_stacks(i[0])
            if [", ".join(i) for i in output] != i[1]:
                print([", ".join(i) for i in output],i[1])
                raise StackParserTests.BadParsing("Stack Parsing algorithm not working.")
def runStackParser():
    s = StackParserTests()
    s.run_tests()

TESTS = {
    "Manulife" : Manulife,
    "HackerRankJobsAPI" : HackerRankJobsAPI,
    "StackParser" : runStackParser
}



def main(args):
    TESTS[args[0]]()

if __name__ == '__main__':
    main(sys.argv[1:])