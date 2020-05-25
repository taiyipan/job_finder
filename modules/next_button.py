from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NextButton:
    def __init__(self, driver, wait_time):
        self.driver = driver
        self.wait_time = wait_time

    def method_1(self):
        next = WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.LINK_TEXT,
                'Next »'
            ))
        )
        return next

    def method_2(self):
        next = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'resultsCol'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/nav[@role="navigation"]/div[@class="pagination"]/ul[@class="pagination-list"]/li/a[@aria-label="Next"]'
            ))
        )
        return next
