from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Clicker:
    def __init__(self, driver, element):
        self.driver = driver
        self.element = element

    def click(self):
        try:
            self.element.click()
        except:
            print('Exception caught: force click')
            self.driver.execute_script("arguments[0].click();", self.element)
