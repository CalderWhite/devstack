import requests
import json
from bs4 import BeautifulSoup as soup

class GetMainError(Exception):
    def __init__(self, message):

        super().__init__(message)

class GetJobError(Exception):
    def __init__(self, message):
        
        super().__init__(message)

class Google(object):
    def __init__(self,query):
        self.BASE_URL = "https://careers.google.com/jobs#t=sq&q=j&li=20&l=false&j="
        self.query = query
        self.OK_RESPONSES = [200]
    def get_jobs(self):
        
        # error handling is pretty important here
        r = requests.get(self.BASE_URL + self.query)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
        else:
            b = soup(r.text)
            print(b)
class Manulife(object):
    """This scrapes the first couple results from a query on Manulife's jobs system."""
    def __init__(self,query):
        self.BASE_URL = "http://jobs.manulife.com/ListJobs/ByKeyword/"
        self.query = query
        self.OK_RESPONSES = [200]
    
    def get_jobs(self,max_items=None):
        """Return all the job titles and descriptions based on the class's query. Limited by the page max."""
        
        # get the page of jobs
        page = self.get_jobs_page()
        # scrape the page for the list of jobs (this differs for each class)
        jobs = self.scrape_jobs_page(page)
        
        job_index = []
        
        i = 0
        
        for title,url in jobs.items():
            
            if max_items != None and i >= max_items:
                break
            
            # get the job description from the url
            
            r = requests.get(url)
            
            if r.status_code not in self.OK_RESPONSES:
                raise GetMainError("job description url responded with a code of " + str(r.status_code))
                
            p = soup(r.text)
            
            # add to new index with title and  job description
            desc = self.extract_job_desc_from_page(p)
            
            if desc == "":
                raise GetJobError("No job description found for : " + str(url))
            
            job_index.append({
                "title" : title,
                "description" : desc
            })
            
            # keep track of the iterations in case we pass the max_items
            i += 1
            
        return job_index
        
    def get_jobs_page(self):
        """Get the page containing all the listings (limited to a maximum). Returns a BeautifulSoup object of the page."""
        # error handling is pretty important here
        r = requests.get(self.BASE_URL + self.query)
        
        if r.status_code not in self.OK_RESPONSES:
            raise GetMainError(self.BASE_URL + self.query + " responded with a code of " + str(r.status_code))
        else:
            return soup(r.text)
    
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
            str(desc).replace("<br/>","\n")
        ).get_text()

class HackerRankJobsAPI(object):
    """HackerRank connects developers with devs from their platform. This scrapes all the jobs posted there."""
    def __init__(self,query):
        self.BASE_URL = "https://www.hackerrank.com/jobs/search"
        # query is irrelevant, but we'll keep it anyway
        self.query = query
        self.OK_RESPONSES = [200]
        self.INFO_URL = "https://www.hackerrank.com/rest/companies/%s?_=1523428021296"
        self.JOBS_URL = "https://www.hackerrank.com/api/v1/companies/%s/jobs?page=1&limit=50&area_id=&area_type=&type_slug=&role_slug=&_=1523428021298"
    
    def get_jobs(self,max_items=None):
        """Return all the job titles and descriptions based on the class's query. Limited by the page max."""
        
        # scrape the page for the list of jobs (this differs for each class)
        companies = self.get_jobs_page()
        
        job_index = {}
        
        i = 0
        
        for slug in companies:
            
            if max_items != None and i >= max_items:
                break
            
            # add to new index with title and  job description
            jobs = self.extract_job_desc_from_page(slug)
            
            job_index[slug] = jobs
            
            # keep track of the iterations in case we pass the max_items
            i += 1
            
        return job_index
        
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
        
        r = requests.get('https://www.hackerrank.com/api/v2/jobs', headers=headers, params=params)
        
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
                    companies.append(company["jobs"][0]["company_slug"])
            
            return companies
    
    def extract_job_desc_from_page(self,company_slug):
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
            jobs.append({
                "title" : job["title"],
                "description" : desc
            })
        return jobs
        
def main():
    jobs = {}
    s = Manulife("software")
    mjobs = s.get_jobs()
    jobs["manulife"] = mjobs
    s = HackerRankJobsAPI("software")
    jobs.update(s.get_jobs())
    print(
        json.dumps(jobs)
    )

if __name__ == '__main__':
    main()
