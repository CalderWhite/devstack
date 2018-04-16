from DevStackBoard import StackParser
from DevStackBoard.Scrapers import *

import Firebase
import time
from threading import Thread

def get_job(company):
    job = "nothing"
    try:
        job = company.next_job()
    except Exception as ex:
        template = "{1} failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args,type(gets[i]))
    
    return job

def get_all_jobs():
    
    jobs = []
    # first do batches
    s = HackerRankJobsAPI("software")
    try:
        jobs.extend(s.get_jobs())
    except Exception as ex:
        template = "HackerRankJobsAPI failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
    
    s = GithubJobsAPI("software")
    try:
        jobs.extend(s.get_jobs())
    except Exception as ex:
        template = "GithubJobsAPI failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
    
    s = StackOverflowJobsAPI("software")
    try:
        jobs.extend(s.get_jobs())
    except Exception as ex:
        template = "StackOverflowJobsAPI failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
    
    # then do generators
    gets = [
        Manulife("software"),
        SpaceX("software"),
        Facebook("software")
    ]
    total = 0
    for i in range(len(gets)):
        try:
            gets[i].load_jobs()
            total += len(gets[i].job_queue)
        except Exception as ex:
            template = "{2} failed. {0} occurred while initializing (ran .load_jobs). Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args,type(gets[i]))
            print(message)
    
    i = 0
    progress = 0
    while len(gets) > 0:
        def add_job(company,progress):
            job = get_job(company)
            if job == None:
                gets.pop(i)
            elif job != "nothing":
                jobs.append(job)
            print("Finished %s/%s [%s]" % (progress,total,type(company).__name__))
        t = Thread(target=add_job,args=(gets[i],progress,))
        t.start()
        #t.join() # this kills preformance... so I'm taking it out against good judgement
        # add a waiting period so we don't get a 429 from the servers,
        # but if there are more websites to rotate through, then wait for less time
        progress += 1
        try:
            time.sleep(0.25 / len(gets))
            i = (i+1) % len(gets)
        except ZeroDivisionError:
            break
    for i in range(len(jobs)):
        jobs[i] = jobs[i].to_dict()
    
    with open("dist.json",'w') as w:
        w.write(json.dumps(jobs,indent=4))

def main():
    f = Firebase.Firebase("DEVSTACK_FIREBASE")
    get_all_jobs()

if __name__ == '__main__':
    main()