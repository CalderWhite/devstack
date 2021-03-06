from DevStackBoard.StackParser import StackParser, PositionSummary, SkillSummary
from DevStackBoard.Scrapers import *

import Firebase
import time
from threading import Thread

total = 0

def save_jobs(filename, jobs):
    print("Converting jobs to json...")
    dist = []
    for i in range(len(jobs)):
        dist.append(jobs[i].to_dict())
    print("Saving snapshot...")
    json.dump(dist,open(filename,'w'),indent=4)

def save_skills(filename, skills):
    json.dump([i.to_dict() for i in skills],open("skills.json",'w'),indent=4)

def skill_orient(summaries):
    """Convert from having a list of position summaries with stacks, to having a list of stacks with companies that use them."""
    skills = {}
    for summary in summaries:
        for skill in summary.combine_stacks():
            if skill not in skills:
                skills[skill] = SkillSummary(skill)
            skills[skill].increment_company(summary.company)
    
    return [skills[i] for i in skills]

def delete_collection(coll_ref, batch_size, path):
    global total
    docs = coll_ref.limit(batch_size).get()
    deleted = 0

    for doc in docs:
        print(u'Deleting doc ({}) {}/{}'.format(total,path,doc.id))
        doc.reference.delete()
        deleted = deleted + 1
        total += 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size, path)


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
    
    s = HackerNewsWhoIsHiring("software")
    try:
        jobs.extend(s.get_jobs())
    except Exception as ex:
        template = "HackerNewsWhoIsHiring failed. {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
    
    # then do generators
    global gets
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
    save_jobs("jobs.json",jobs)
    return jobs
def parse_jobs(jobs):
    s = StackParser()
    position_summaries = []
    total = len(jobs)
    i = 0
    for job in jobs:
        position_summaries.append(PositionSummary(
            job.title,
            job.company,
            job.location,
            s.find_stacks(job.description)
        ))
        #print("%s/%s" % (i+1,total))
        i += 1
    return position_summaries

def reset_database(filename=None):
    """Flushes out the old data and adds the new. Set filename to a path if you want to parse a snapshot of jobs generated by get_all_jobs()."""
    f = Firebase.Firebase("credentials.json")
    
    if filename != None:
        jobs = [
            Job(
                i["company"],
                i["title"],
                i["description"],
                i["location"]
            )
            for i in json.loads(open(filename).read())
        ]
    else:
        jobs = get_all_jobs()
        
    summaries = parse_jobs(jobs)
    
    print("Creating skill mirror or data...")
    skills = skill_orient(summaries)
    
    save_skills("skills.json",skills)
    
    # delete old data
    delete_collection(f.db.collection("jobs"),10,"jobs")
    delete_collection(f.db.collection("skills"),10,"skills")
    
    # add new data
    # first jobs
    print("Uploading jobs to firebase...")
    total_jobs = 0
    f.new_batch()
    for i,summary in enumerate(summaries):
        # since batches cannot exceed 500 writes,
        # group them by 500
        if i % 500 == 0 and i != 0:
            print("Sending batch %s of %s to the firestore database." % ((i // 500),(len(summaries) // 500) + 1))
            f.commit_batch()
            f.new_batch()
        f.add_item(summary,"jobs")
        total_jobs += 1
    print("Sending batch {0} of {0} to the firestore database.".format((len(summaries) // 500) + 1))
    f.commit_batch()
    print("A total of %s jobs were successfully uploaded to firebase." % total_jobs)
    # now skills
    print("Uploading skills to firebase...")
    total_skills = 0
    f.new_batch()
    for i,skill in enumerate(skills):
        # since batches cannot exceed 500 writes,
        # group them by 500
        if i % 500 == 0 and i != 0:
            print("Sending batch %s of %s to the firestore database." % ((i // 500),(len(skills) // 500) + 1))
            f.commit_batch()
            f.new_batch()
        f.add_item(skill,"skills")
        total_skills += 1
    print("Sending batch {0} of {0} to the firestore database.".format((len(skills) // 500) + 1))
    f.commit_batch()
    print("A total of %s skills were successfully uploaded to firebase." % total_skills)

def main():
    reset_database(filename="jobs.json")


if __name__ == '__main__':
    main()