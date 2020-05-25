from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class JobTitleSelector:
    def __init__(self, job, wait_time):
        self.job = job
        self.wait_time = wait_time

    def method_1(self):
        job_title = WebDriverWait(self.job, self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/h2[@class="title"]/a'
            ))
        )
        return job_title
