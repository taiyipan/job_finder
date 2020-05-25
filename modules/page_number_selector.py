from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PageNumberSelector:
    def __init__(self, driver, wait_time):
        self.driver = driver
        self.wait_time = wait_time

    def method_1(self):
        current_page = WebDriverWait(WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((
                By.CLASS_NAME,
                'pagination'
            ))
        ), self.wait_time).until(
            EC.presence_of_element_located((
                By.XPATH,
                './/b'
            ))
        )
        return current_page
