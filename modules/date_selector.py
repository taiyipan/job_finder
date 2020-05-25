from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DateSelector:
    def __init__(self, driver, wait_time):
        self.driver = driver
        self.wait_time = wait_time

    def method_1(self):
        sort_by_date = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'refineresults'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/div[@class="serp-filters-sort-by-container"]/span[@class="no-wrap"]/a[text()="date"]'
            ))
        )
        return sort_by_date

    def method_2(self):
        sort_by_date = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'resultsCol'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/div[@class="resultsTop"]/div[@class="secondRow"]/div[@class="serp-filters-sort-by-container"]/span[@class="no-wrap"]/a[text()="date"]'
            ))
        )
        return sort_by_date
