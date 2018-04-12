import Scrapers
import sys

# Unit tests

def Manulife():
    s = Scrapers.Manulife("software")
    s.get_jobs(max_items=1)
def HackerRankJobsAPI():
    s = Scrapers.HackerRankJobsAPI("software")
    s.get_jobs(max_items=1)

TESTS = {
    "Manulife" : Manulife,
    "HackerRankJobsAPI" : HackerRankJobsAPI
}



def main(args):
    TESTS[args[0]]()

if __name__ == '__main__':
    main(sys.argv[1:])