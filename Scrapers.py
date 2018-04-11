import requests
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
        
        job_index = {}
        
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
            
            job_index[title] = desc
            
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
        
    
def main():
    s = Manulife("software")
    jobs = s.get_jobs(max_items=1)
    print(jobs)

if __name__ == '__main__':
    main()