from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# log into indeed.com with specific search criteria
class LoginAgent:
    # constructor
    def __init__(self, driver, job_title = None, job_location = 'San Francisco Bay Area'):
        self.driver = driver
        self.job_title = job_title
        self.job_location = job_location
        self.indeed_url = 'https://www.indeed.com'

    # navigate to indeed.com and input search terms 
    def login(self):
        # navigate to webpage
        self.driver.get(self.indeed_url)

        # enter 2 input fields on job search page
        if self.job_title is not None:
            input_what = self.driver.find_element_by_id('text-input-what')
            input_what.send_keys(self.job_title)

        input_where = self.driver.find_element_by_id('text-input-where')
        input_where.send_keys(Keys.CONTROL + 'a')
        input_where.send_keys(Keys.DELETE)

        if self.job_location is not None:
            input_where.send_keys(self.job_location)
        input_where.send_keys('\n')
