import Firebase
from DevStackBoard import StackParser
from DevStackBoard.Scrapers import *


def get_all_jobs():
    
    jobs = []
    # first do batches
    s = HackerRankJobsAPI("software")
    try:
        jobs.extend(s.get_jobs())
    except Exception as ex:
        template = "HackerRankJobsAPI failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
    
    s = GithubJobsAPI("software")
    try:
        jobs.extend(s.get_jobs())
    except Exception as ex:
        template = "GithubJobsAPI failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
    
    s = StackOverflowJobsAPI("software")
    try:
        jobs.extend(s.get_jobs())
    except Exception as ex:
        template = "StackOverflowJobsAPI failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
    
    # then do generators
    
    gets = [
        Manulife("software"),
        SpaceX("software")
    ]
    for i in range(len(gets)):
        try:
            gets[i].load_jobs()
        except Exception as ex:
            template = "{1} failed. {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args,type(gets[i]))
    
    i = 0
    while len(gets) > 0:
        job = "nothing"
        try:
            job = gets[i].next_job()
        except Exception as ex:
            template = "{1} failed. {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args,type(gets[i]))
        if job == None:
            gets.pop(i)
        elif job != "nothing":
            jobs.append(job)
        
        i = (i+1) % len(gets)

def main():
    f = Firebase.Firebase("DEVSTACK_FIREBASE")
    get_all_jobs()

if __name__ == '__main__':
    main()