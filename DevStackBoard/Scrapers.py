import requests
import json
import re
from bs4 import BeautifulSoup as soup
import xml.etree.cElementTree as ET
from threading import Thread

class GetMainError(Exception):
    def __init__(self, message):

        super().__init__(message)

class GetJobError(Exception):
    def __init__(self, message):
        
        super().__init__(message)

class Job(object):
    def __init__(self,company,title,description,location,stacks=None):
        self.company = company
        self.title = title
        self.description = description
        self.location = location
        self.stacks = stacks
        
        
    def to_dict(self):
        """Returns the object as a dict. Not going to engineer the crap out of this, for now."""
        
        return {
            "company" : self.company,
            "title" : self.title,
            "description" : self.description,
            "location" : self.location
        }
        

class Manulife(object):
    """This scrapes the first couple results from a query on Manulife's jobs system."""
    def __init__(self,query):
        self.BASE_URL = "http://jobs.manulife.com/ListJobs/ByKeyword/"
        self.query = query
        self.OK_RESPONSES = [200]
    
    def next_job(self):
        """Get the next job in the queue of jobs to get"""
        if self.job_queue_index > len(self.job_queue) - 1:
            return None
        title, url = self.job_queue[self.job_queue_index]
        r = requests.get(url)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError("job description url responded with a code of " + str(r.status_code))
            
        p = soup(r.text,"html.parser")
        
        # add to new index with title and  job description
        desc = self.extract_job_desc_from_page(p)
        
        if desc == "":
            raise GetJobError("No job description found for : " + str(url))
            
        self.job_queue_index += 1
        
        return Job(
            "Manulife",
            title,
            desc,
            None
        )
        
    def load_jobs(self):
        """Load the jobs so that we can get one job at a time."""
        self.job_queue_index = 0
        page = self.get_jobs_page()
        self.job_queue = [[title,url] for title,url in self.scrape_jobs_page(page).items()]
        
    def get_jobs_page(self):
        """Get the page containing all the listings (limited to a maximum). Returns a BeautifulSoup object of the page."""
        # error handling is pretty important here
        r = requests.get(self.BASE_URL + self.query)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
        else:
            return soup(r.text,"html.parser")
    
    def scrape_jobs_page(self,page):
        """Returns all the jobs listed on the main jobs page."""
        # get the first child of each td.coloriginaljobtitle
        jobs = [node.findChildren()[0] for node in page.findAll("td",{"class":"coloriginaljobtitle"})]
        
        if len(jobs) < 1:
            raise GetMainError("There are no jobs listed on the main jobs page!")
        
        descriptions = {}
        
        for job in jobs:
            descriptions[job.get_text()] = "/".join(self.BASE_URL.split("/")[:3]) + job["href"]
        
        return descriptions
    
    def extract_job_desc_from_page(self,page):
        """Returns the description derived from the given BeautifulSoup page, or returns an empty string if no description is provided."""
        
        desc = page.find("div",{"class":"jobdescription-row description"})
        
        if desc == None:
            return ""
        
        # replace the <br> tags with line breaks, so we can funnel this into our general algorithm, which can understand line breaks.
        
        return soup(
            str(desc).replace("<br/>","\n"),
            "html.parser"
        ).get_text()

class HackerRankJobsAPI(object):
    """HackerRank connects developers with devs from their platform. This scrapes all the jobs posted there."""
    def __init__(self,query):
        self.BASE_URL = "https://www.hackerrank.com/api/v2/jobs"
        # query is irrelevant, but we'll keep it anyway
        self.query = query
        self.OK_RESPONSES = [200]
        self.INFO_URL = "https://www.hackerrank.com/rest/companies/%s?_=1523428021296"
        self.JOBS_URL = "https://www.hackerrank.com/api/v1/companies/%s/jobs?page=1&limit=50&area_id=&area_type=&type_slug=&role_slug=&_=1523428021298"
    
    def get_jobs(self,max_items=None):
        """Return all the job titles and descriptions based on the class's query. Limited by the page max."""
        
        # scrape the page for the list of jobs (this differs for each class)
        companies = self.get_jobs_page()
        
        jobs = []
        i = 0
        
        for name, slug in companies:
            
            if max_items != None and i >= max_items:
                break
            
            # add to new index with title and  job description
            _jobs = self.extract_job_desc_from_page(slug,name)
            
            jobs.extend(_jobs)
            
            # keep track of the iterations in case we pass the max_items
            i += 1
            
        return jobs
        
    def get_jobs_page(self):
        """Get the page containing all the listings (limited to a maximum). Returns a BeautifulSoup object of the page."""
        
        # error handling is pretty important here
        # take advantage of HackerRank's unguaded api
        headers = {
            'if-none-match': 'W/"af24e5b8b517cc9bec4604190bc2e490"',
            'accept-encoding': 'gzip, deflate, br',
            'x-csrf-token': 'Z9QMLJJzj0dpVNWrU1+Nk56seVdnpvQjYHz05dlCuvFKiyEnkGK+iSAq97Zl/ui4o2rrv0AmHeb6/F7GuTJWfw==',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 10323.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.209 Safari/537.36',
            'content-type': 'application/json',
            'accept': 'application/json',
            'referer': 'https://www.hackerrank.com/jobs/search',
            'authority': 'www.hackerrank.com',
            'cookie': 'hackerrank_mixpanel_token=2053e1e3-0e3e-4057-861a-3f7c4024037e; _hrank_session=c0540b18708b533087c6231ef8862e75ed776f2d6e8b77b5a7df8f81bb97f77fa2c7e1ebd1b68707056847bb49d9df50ee322ca126aa9572244aa1700e17666d; session_referrer=https%3A%2F%2Fwww.google.ca%2F; session_referring_domain=www.google.ca; default_cdn_url=hrcdn.net; react_var=false__trm6; react_var2=false__trm6; metrics_user_identifier=21c154-cdfea56df6a015485b39ce9024ab3346d6300e87; session_landing_url=https%3A%2F%2Fwww.hackerrank.com%2Fprefetch_data%3Fcontest_slug%3Dmaster%26get_feature_feedback_list%3Dtrue; cdn_url=hrcdn.net; cdn_set=true; __utma=74197771.1690286955.1523426090.1523426090.1523426090.1; __utmc=74197771; __utmz=74197771.1523426090.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt_candidate_company=1; userty.core.s.62789b=%7B%22p%22%3A%22f%22%7D; session_id=bw07gevm-1523426110931; __utmt=1; __utmt_%5Bobject%20Object%5D=1; _hp2_id.undefined=%7B%22userId%22%3A%228568971243337835%22%2C%22pageviewId%22%3A%226031756787943488%22%2C%22sessionId%22%3A%220678739268345918%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%223.0%22%7D; _hp2_ses_props.undefined=%7B%22r%22%3A%22https%3A%2F%2Fwww.hackerrank.com%2Fjobs%2Fsearch%22%2C%22ts%22%3A1523426112904%2C%22d%22%3A%22www.hackerrank.com%22%2C%22h%22%3A%22%2Fcompanies%2Fworkday%2Fjobs%22%7D; _hjIncludedInSample=1; fileDownload=true; _biz_uid=32f5b88ce5de4738d7c935ab1062a5d8; _biz_sid=425bd0; _hp2_id.698647726=%7B%22userId%22%3A%227791660028843395%22%2C%22pageviewId%22%3A%222833819126238957%22%2C%22sessionId%22%3A%228626196966741052%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%223.0%22%7D; _hp2_ses_props.698647726=%7B%22r%22%3A%22https%3A%2F%2Fwww.hackerrank.com%2Fjobs%2Fsearch%22%2C%22ts%22%3A1523426265620%2C%22d%22%3A%22www.hackerrank.com%22%2C%22h%22%3A%22%2Fcompanies%2Fbookingcom%2Fjobs%22%7D; _biz_nA=2; _biz_pendingA=%5B%5D; __utmb=74197771.11.10.1523426262972; mp_bcb75af88bccc92724ac5fd79271e1ff_mixpanel=%7B%22distinct_id%22%3A%20%222053e1e3-0e3e-4057-861a-3f7c4024037e%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.ca%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.ca%22%7D; mp_86cf4681911d3ff600208fdc823c5ff5_mixpanel=%7B%22distinct_id%22%3A%20%22162b3455d191bc-0deb250946fc72-7e24262b-100200-162b3455d1a26e%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.ca%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.ca%22%7D',
        }
        
        params = (
            ('role', ''),
            ('zone_code', ''),
            ('by_company', 'true'),
            ('company_limit', '100'),
        )
        
        r = requests.get(self.BASE_URL, headers=headers, params=params)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
        else:
            data = json.loads(r.text)
            # get the multiple jobs pages listed on HackerRank's jobs page
            if "data" not in data:
                raise GetMainError("The HackerRank Jobs api returned json not including the key [data].")
            
            companies = []
            
            for company in data["data"]:
                if len(company["jobs"]) > 0:
                    companies.append([company["name"],company["jobs"][0]["company_slug"]])
            
            return companies
    
    def extract_job_desc_from_page(self,company_slug,company_name):
        """Returns the description derived from the given BeautifulSoup page, or returns an empty string if no description is provided."""
        r = requests.get(self.INFO_URL % company_slug)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetJobError("Failed to get info about [%s] on HackerRank's Jobs API." % company_slug)
        
        company_id = json.loads(r.text)["model"]["recruit_company_id"]
        
        r = requests.get(self.JOBS_URL % company_id)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetJobError("Failed to get info about [%s] on HackerRank's Jobs API." % company_slug)
        
        jobs = []
        for job in json.loads(r.text)["data"]["response"]:
            # if there is no work_description (which is more specific and preferable),
            # use the plain text smattering of all components of the description
            if job["work_description"] != None:
                desc= job["work_description"]
            else:
                desc = job["jobs_des_plain"]
            jobs.append(Job(
                company_name,
                job["title"],
                desc,
                job["address"]["display_text"]
            ))
        return jobs

class GithubJobsAPI(object):
    """This is for public use, so we don't have to be uber-careful about the scraping methods and potential errors."""
    def __init__(self,query):
        self.BASE_URL = "https://jobs.github.com/positions.json"
        # query is irrelevant, but we'll keep it anyway
        self.query = query
        self.OK_RESPONSES = [200]
    
    def get_jobs(self,max_items=None):
        """Return all the job titles and descriptions. Limited by the page max."""
        
        # scrape the page for the list of jobs (this differs for each class)
        jobs = self.get_jobs_pages()
        
        refined_jobs = []
        
        i = 0
        
        for job in jobs:
            
            if max_items != None and i >= max_items:
                break
            
            # add to new index with title and  job description

            refined_jobs.append(
                self.construct_job(job)
            )
            
            # keep track of the iterations in case we pass the max_items
            i += 1
            
        return refined_jobs
        
    def get_jobs_pages(self):
        """Since each page is limited to 50 entires, go through until you hit an empty page."""
        jobs = self.get_jobs_page(1)
        data = []
        i = 2
        while i == 2 or data != []:
            data = self.get_jobs_page(i)
            jobs.extend(data)
            i += 1
        return jobs
        
    def get_jobs_page(self,page_num):
        # error handling is pretty important here
        r = requests.get(self.BASE_URL + "?page=" + str(page_num))
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
        else:
            data = json.loads(r.text)
            
            return data
    
    def construct_job(self,job):
        return Job(
            job["company"],
            job["title"],
            job["description"],
            job["location"]
        )

class Facebook(object):
    """As long as you make it look like it came from a browser, facebook puts the data right into the response."""
    def __init__(self,query):
        self.BASE_URL = "https://www.facebook.com/careers/search/"
        # query is irrelevant, but we'll keep it anyway
        self.query = query
        self.OK_RESPONSES = [200]
    
    def next_job(self):
        
        if self.job_queue_index > len(self.job_queue) - 1:
            return None
            
        job = self.job_queue[self.job_queue_index]
        
        desc = self.get_job_page(job["url"])
        
        job["description"] = desc
        
        # add to new index with title and  job description
        self.job_queue_index += 1
        
        return self.construct_job(job)
    
    def load_jobs(self):
        self.job_queue_index = 0
        
        page = self.get_jobs_page()
        self.job_queue = self.parse_jobs_page(page)
    
    def get_job_page(self,url):
        
        headers = {
            'accept-encoding': 'utf-8',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 10323.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.209 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'cache-control': 'max-age=0',
            'authority': 'www.facebook.com',
            'cookie': 'datr=ViFVWaEQMdSswGLng54V2mM8; sb=vbliWa3-OlPxcs4_t2DbrQBP; c_user=100013507262874; xs=43%3AlzYxCBbEkASY7g%3A2%3A1499642301%3A1664%3A14914; ; dpr=0.8999999761581421; fr=0oKWsg2SHGy8YGCuw.AWXuCGSy-MmsrAu8zh45GFJJDdE.BZTWvO.aH.FrP.0.0.Ba0CkA.AWVREXEF; wd=1517x698; act=1523592841026%2F1; presence=EDvF3EtimeF1523592949EuserFA21B13507262874A2EstateFDutF1523592949090CEchFDp_5f1B13507262874F100CC',
        }
        
        r = requests.get(url, headers=headers)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetJobError(url + " responded with a code of " + str(r.status_code))
        
        page = soup(r.text,"html.parser")
        
        desc = page.findAll("div",{"class":"_wrz"})
        if len(desc) < 2:
            raise GetJobError(url + "'s page has been altered. The current scraping method no longer works.")
        
        desc = desc[1].get_text()
        
        return desc
        
    def parse_jobs_page(self,page):
        job_nodes = page.findAll("div",{"class":"_3k6i"})
        jobs = []
        fb = "/".join(self.BASE_URL.split("/")[:3])
        for node in job_nodes:
            #print(node)
            a = node.find("a")
            if a == None:continue
            location = node.find("div",{"class":"_3m9 _1n-- _3k6n"})
            if location == None:continue
            jobs.append({
                "title" : a.get_text(),
                "url" : fb + a["href"],
                "location" : location.get_text()
            })
        return jobs
        
    def get_jobs_page(self):
        # error handling is pretty important here

        headers = {
            'accept-encoding': 'utf-8',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 10323.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.209 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'cache-control': 'max-age=0',
            'authority': 'www.facebook.com',
            'cookie': 'datr=ViFVWaEQMdSswGLng54V2mM8; sb=vbliWa3-OlPxcs4_t2DbrQBP; c_user=100013507262874; xs=43%3AlzYxCBbEkASY7g%3A2%3A1499642301%3A1664%3A14914; ; dpr=0.8999999761581421; act=1523568393237%2F3; fr=0oKWsg2SHGy8YGCuw.AWWBGufECzf7qsb3U25gCis-86I.BZTWvO.aH.FrP.0.0.Baz8-c.; wd=304x698; presence=EDvF3EtimeF1523570795EuserFA21B13507262874A2EstateFDutF1523570795208CEchFDp_5f1B13507262874F4CC',
        }
        
        params = (
            ('q', self.query),
        )
        
        r = requests.get(self.BASE_URL, headers=headers, params=params)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
        else:
            page = soup(r.text,"html.parser")
            return page
    
    def construct_job(self,job):
        return Job(
            "Facebook",
            job["title"],
            job["description"],
            job["location"]
        )

class StackOverflowJobsAPI(object):
    def __init__(self,query):
        
        self.BASE_URL = "https://stackoverflow.com/jobs/feed"
        
        self.query = query
        self.OK_RESPONSES = [200]
    def get_jobs(self):
        
        root = self.get_feed()
        
        c = root.getchildren()[0].findall("item")
        
        jobs = [self.create_job(job) for job in c]
        
        return jobs

    def get_feed(self):
        
        r = requests.get(self.BASE_URL)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
            
        return ET.fromstring(r.text)
        
    def create_job(self,xml_node):
        location = xml_node.find("{http://stackoverflow.com/xml_nodes/}location")
        if location != None:
            location = location.text.replace("-","").strip()
        title = xml_node.find("title").text.split(" at ")[0].strip()
        desc = xml_node.find("description").text
        stack = [i.text for i in xml_node.findall("category")]
        company = xml_node.find("{http://www.w3.org/2005/Atom}author").getchildren()[0].text
        
        return Job(
            company,
            title,
            desc,
            location,
            stacks=[stack]
        )

class SpaceX(object):
    def __init__(self,query):
        
        self.BASE_URL = "http://www.spacex.com/careers/list?field_job_category_tid%5B%5D=761"
        
        self.OK_RESPONSES = [200]
        
        self.query = query
    
    def next_job(self):
        
        if self.job_queue_index > len(self.job_queue) - 1:
            return None
        
        job = self.job_queue[self.job_queue_index]
        
        page = self.get_job_page(job["url"])
        desc = self.parse_job_page(page)
        
        job["description"] = desc
        
        self.job_queue_index += 1
        
        return self.construct_job(job)
    
    def parse_job_page(self, page):
        details = page.find("div",{"class":"details"})
        # this could be better, but really the StackParser algorithm should be able to handle the odd spacing/formatting of the text 
        # due to it being ripped out of HTML
        l = details.find("ul").get_text()
        
        return l
    
    def get_job_page(self,url):
        r = requests.get(url)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + " responded with a code of " + str(r.status_code))
        else:
            return soup(r.text,"html.parser")
        
    
    def load_jobs(self):
        
        self.job_queue_index = 0
        
        page = self.get_jobs_page()
        self.job_queue = self.parse_jobs_page(page)
    
    def get_jobs_page(self):
        
        r = requests.get(self.BASE_URL)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + " responded with a code of " + str(r.status_code))
        else:
            return soup(r.text,"html.parser")
    
    def parse_jobs_page(self,page):
        
        locations = [i.get_text() for i in page.findAll("div",{"class":"field field-name-field-job-location field-type-taxonomy-term-reference field-label-hidden"})]
        
        titles = [i.findChildren()[0] for i in page.findAll("td",{"class":"views-field views-field-title"})]
        
        jobs = []
        
        for i in range(len(locations)):
            jobs.append({
                "title" : titles[i].get_text(),
                "url" : "/".join(self.BASE_URL.split("/")[:3]) + titles[i]["href"],
                "location" : locations[i]
            })
        return jobs
    
    def construct_job(self,job):
        return Job(
            "SpaceX",
            job["title"],
            job["description"],
            job["location"]
        )

class HackerNewsWhoIsHiring(object):
    """
    Hacker News has a community "Who's Hiring", and this utilizes the hacker-news api to get all the jobs posted.
    Though this should technically be a generator, the hacker-news api is **WAY** faster than any website.
    Thus it's simply cleaner to thread all the requests like this without any wait time inbetween.
    (Hacker News partnered with Google to make the api in firebase. Their servers can take the traffic as long as it doesn't exceed 1000 requests in under a minute )
    """
    def __init__(self,query):
        self.BASE_URL = "https://news.ycombinator.com/submitted?id=whoishiring"
        self.API_URL = "https://hacker-news.firebaseio.com/v0/item/%s.json"
        # query is irrelevant, but we'll keep it anyway
        self.query = query
        self.OK_RESPONSES = [200]
    
    def get_jobs(self,max_items=None):
        """Return all the job titles and descriptions based on the class's query. Limited by the page max."""
        
        # scrape the page for the list of jobs (this differs for each class)
        page = self.get_jobs_page()
        latest_id = self.get_latest_list(page)
        ids = [
            str(i)
            for i in self.get_item(latest_id)["kids"]
        ]
        jobs = []
        
        for _id in ids:
            #print("(%s/%s) Getting %s..." % (i,len(ids),_id))
            
            if max_items != None and i >= max_items:
                break
            
            # add to new index with title and  job description
            def add(item_id):
                item = self.get_item(_id)
                
                jobs.append(item)
            
            t = Thread(target=add,args=(_id,))
            t.start()
            
            # keep track of the iterations in case we pass the max_items
        while len(jobs) != len(ids):
            pass
        for i in range(len(jobs)-1,-1,-1):
            if jobs[i] == None or ("deleted" in jobs[i] and jobs[i]['deleted']):
                jobs.pop(i)
            else:
                jobs[i] = self.parse_job_desc(jobs[i]["text"])
        return jobs
            
    def get_jobs_page(self):
        """Get the page containing all the listings (limited to a maximum). Returns a BeautifulSoup object of the page."""
        
        r = requests.get(self.BASE_URL)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
        else:
            return soup(r.text, "html.parser")
    
    def get_latest_list(self,page):
        t = page.findAll("a",{"class":"storylink"})
        
        for a in t:
            if a.get_text().lower().find("who is hiring") > -1:
                return a["href"].split("=")[1]
        
        raise GetMainError("No Who's Hiring item for HackerNew's Who's Hiring thread list.")
        
    def get_item(self,_id):
        
        url = self.API_URL % _id
        r = requests.get(url)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetJobError("Cannot get from hacker-news api: " + url)
        
        return json.loads(r.text)
    
    def parse_job_desc(self,desc):
        
        page = soup(desc, "html.parser")
        
        company = None
        location = None
        desc = ""
        
        for i, p in enumerate(page.findAll("p")):
            if i == 0:
                info = p.get_text().split(" | ")
                # though there is always more data than just the company,
                # the company being the first item is the only thing that remains consistant
                # throughout all the postings
                company = info[0]
                for j in info[1:]:
                    if j.find(",") > -1:
                        location = j
            else:
                desc += p.get_text()
        return Job(
            company,
            None,
            desc,
            location
        )

if __name__ == '__main__':
    s = HackerNewsWhoIsHiring("software")
    j = s.get_jobs()
    print(j)