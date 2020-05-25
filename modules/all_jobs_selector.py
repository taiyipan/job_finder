from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AllJobsSelector:
    def __init__(self, driver, wait_time):
        self.driver = driver
        self.wait_time = wait_time

    def method_1(self):
        jobs = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'resultsCol'
            ))
        ), self.wait_time).until(
            EC.presence_of_all_elements_located((
                By.CLASS_NAME,
                'jobsearch-SerpJobCard'
            ))
        )
        return jobs
