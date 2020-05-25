from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DistanceSelector:
    def __init__(self, driver, wait_time, distance):
        self.driver = driver
        self.wait_time = wait_time
        self.distance = distance

    def method_1(self):
        select_distance = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'distance_selector'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/option[text()="{}"]'.format(self.distance)
            ))
        )
        return select_distance

    def method_2(self):
        select_distance = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.ID,
                'filter-distance-menu'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/li/a[contains(@title, "{}")]'.format(self.distance)
            ))
        )
        return select_distance
