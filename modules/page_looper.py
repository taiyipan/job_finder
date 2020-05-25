from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from datetime import timedelta
import time
from adaptive_recursor import AdaptiveRecursor
from job_descriptor import JobDescriptor
from next_button import NextButton
from page_number_selector import PageNumberSelector
from all_jobs_selector import AllJobsSelector
from job_date_selector import JobDateSelector
from job_link_selector import JobLinkSelector
from job_title_selector import JobTitleSelector
from clicker import Clicker
# loop through an Indeed pages and gather data
class PageLooper:
    def __init__(self, driver, limit = 2000, duration = 40, wait_time = 5, date_limit = True):
        self.driver = driver
        self.limit = limit
        self.duration = duration
        self.wait_time = wait_time
        self.date_limit = date_limit
        self.input_data = list()
        self.summaries = list()
        self.links = list()
        self.count = 0
        self.last_page = 0
        self.end = self.end_time()
        self.bypass_count = 0
        self.bypass_limit = self.calculate_bypass_limit(limit)

    def calculate_bypass_limit(self, limit: int, fraction = 0.1):
        return round(limit * fraction)

    def update_bypass_count(self):
        self.bypass_count += 1

    def validate_bypass_count(self) -> bool:
        if self.bypass_count >= self.bypass_limit:
            return False
        else:
            return True

    def end_time(self):
        # start timer
        timer = time.time()
        # calculate a fixed end time in the future
        end = datetime.now() + timedelta(minutes = self.duration)
        return end

    def validate_page(self) -> bool:
        # validate current page is after previous page (compensate for indeed website glitch)
        # if validated, update current page
        current_page = AdaptiveRecursor(PageNumberSelector(self.driver, self.wait_time)).get()
        current_page = int(current_page.text)
        if current_page == self.last_page + 1:
            self.last_page = current_page
            return True
        else:
            print('Indeed page glitch detected.')
            return False

    def validate_time(self) -> bool:
        # validate program does not exceed program duration
        if datetime.now() > self.end:
            print('Program exceeded duration of {} minutes, so exiting'.format(self.duration))
            return False
        else:
            return True

    def validate_job_date(self, job) -> bool:
        # validate the job is still posted today
        job_date = AdaptiveRecursor(JobDateSelector(job, self.wait_time)).get()
        if '1 day ago' in job_date.text:
            print('Reached yesterday\'s posting')
            return False
        return True

    def get_jobs(self):
        # get all jobs on the current page
        return AdaptiveRecursor(AllJobsSelector(self.driver, self.wait_time)).get()

    def process_job(self, job) -> str:
        # initialize input_string and save job text
        input_string = str()
        input_string += job.text + '\n\n'

        # save job summary and link
        self.save_job_summary(job)
        self.save_job_link(job)

        # get job title
        job_title = self.get_job_title(job)

        # click on job title and expand job description
        Clicker(self.driver, job_title).click()

        # return input_string
        return input_string

    def save_job_summary(self, job):
        # save job summary
        self.summaries.append(job.text)

    def save_job_link(self, job):
        # find and save job link
        self.links.append(AdaptiveRecursor(JobLinkSelector(job, self.wait_time)).get().get_attribute('href'))

    def get_job_title(self, job):
        # get job title
        job_title = AdaptiveRecursor(JobTitleSelector(job, self.wait_time)).get()
        return job_title

    def process_job_description(self, input_string: str) -> str:
        try:
            # get job description
            description = AdaptiveRecursor(JobDescriptor(self.driver, self.wait_time)).get()
            # save job description
            input_string += description + '\n\n'
        except:
            print('Job description bypass')
            # update bypass count
            self.update_bypass_count()
        return input_string

    def update_job_count(self):
        self.count += 1
        if self.count % 100 == 0:
            print('{} entries'.format(self.count))

    def validate_job_count(self) -> bool:
        if self.count >= self.limit:
            print('limit at {} reached'.format(self.limit))
            return False
        else:
            return True

    def next_page(self) -> bool:
        try:
            # locate next button
            next = AdaptiveRecursor(NextButton(self.driver, self.wait_time)).get()
            # go to next page
            Clicker(self.driver, next).click()
        except:
            print('Next not detected')
            return False
        return True

    # main loop: return boolean value indicates success or failure of loop
    def loop(self) -> bool:
        # main loop
        while self.count < self.limit:
            # validate page number
            if not self.validate_page():
                return False
            # validate time duration
            if not self.validate_time():
                return True

            # get all jobs on the current page
            jobs = self.get_jobs()

            # loop through current jobs
            for job in jobs:
                # validate the job is still posted today
                if self.date_limit and not self.validate_job_date(job):
                    return True

                # initial processing of job
                input_string = self.process_job(job)
                # process job description
                input_string = self.process_job_description(input_string)

                # validate bypass count
                if not self.validate_bypass_count():
                    return False

                # save input_string to input_data
                self.input_data.append(input_string)

                # update job count
                self.update_job_count()
                # validate job count
                if not self.validate_job_count():
                    return True

            # go to next page
            next_page = self.next_page()
            if not next_page:
                return True

        # final step
        print('\nHarvested {} job postings'.format(len(self.input_data)))
        return True

    # various get methods
    def get_input_data(self) -> list:
        return self.input_data

    def get_summaries(self) -> list:
        return self.summaries

    def get_links(self) -> list:
        return self.links

    def get_all(self) -> (list, list, list):
        return self.input_data, self.summaries, self.links

    def get(self, name: str) -> list:
        if name == 'input' or name == 'input_data' or name == 'input data':
            return self.input_data
        elif name == 'summary' or name == 'summaries':
            return self.summaries
        elif name == 'link' or name == 'links':
            return self.links
        else:
            return None
